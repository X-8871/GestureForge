// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vtb_s2a_backend_fault_recovery.h for the primary calling header

#include "Vtb_s2a_backend_fault_recovery__pch.h"

void Vtb_s2a_backend_fault_recovery___024root___timing_ready(Vtb_s2a_backend_fault_recovery___024root* vlSelf);

VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root___eval_static(Vtb_s2a_backend_fault_recovery___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root___eval_static\n"); );
    Vtb_s2a_backend_fault_recovery__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    {
        // Inlined CFunc: _eval_static__TOP
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__clk = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__hard_reset = 1U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_write = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_wdata = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__manual_mem_ready = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__automatic_read_responses = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__manual_mem_error_code = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__simulation_cycle_count = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__transaction_start_cycle = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__memory_read_handshakes = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__memory_write_side_effects = 0U;
        const uint64_t __VscopeHash = VL_MURMUR64_HASH(vlSelf->vlNamep);
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__unnamedblk1__DOT__reads_before = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7220630703602385358ull);
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__unnamedblk1__DOT__writes_before = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16306954892115603068ull);
    }
    vlSelfRef.__Vm_traceActivity[1U] = 1U;
    vlSelfRef.__Vtrigprevexpr___TOP__tb_s2a_backend_fault_recovery__DOT__clk__0 = 0U;
    Vtb_s2a_backend_fault_recovery___024root___timing_ready(vlSelf);
    do {
        vlSelfRef.__VactTriggeredAcc[vlSelfRef.__Vi] 
            = vlSelfRef.__VactTriggered[vlSelfRef.__Vi];
        vlSelfRef.__Vi = ((IData)(1U) + vlSelfRef.__Vi);
    } while ((0U >= vlSelfRef.__Vi));
}

VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root___eval_final(Vtb_s2a_backend_fault_recovery___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root___eval_final\n"); );
    Vtb_s2a_backend_fault_recovery__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
}

#ifdef VL_DEBUG
VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root___dump_triggers__stl(const VlUnpacked<QData/*63:0*/, 1> &triggers, const std::string &tag);
#endif  // VL_DEBUG
VL_ATTR_COLD bool Vtb_s2a_backend_fault_recovery___024root___eval_phase__stl(Vtb_s2a_backend_fault_recovery___024root* vlSelf);

VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root___eval_settle(Vtb_s2a_backend_fault_recovery___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root___eval_settle\n"); );
    Vtb_s2a_backend_fault_recovery__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    IData/*31:0*/ __VstlIterCount;
    // Body
    __VstlIterCount = 0U;
    vlSelfRef.__VstlFirstIteration = 1U;
    do {
        if (VL_UNLIKELY(((0x00002710U < __VstlIterCount)))) {
#ifdef VL_DEBUG
            Vtb_s2a_backend_fault_recovery___024root___dump_triggers__stl(vlSelfRef.__VstlTriggered, "stl"s);
#endif
            VL_FATAL_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 2, "", "DIDNOTCONVERGE: Settle region did not converge after '--converge-limit' of 10000 tries");
        }
        __VstlIterCount = ((IData)(1U) + __VstlIterCount);
        vlSelfRef.__VstlPhaseResult = Vtb_s2a_backend_fault_recovery___024root___eval_phase__stl(vlSelf);
        vlSelfRef.__VstlFirstIteration = 0U;
    } while (vlSelfRef.__VstlPhaseResult);
}

VL_ATTR_COLD bool Vtb_s2a_backend_fault_recovery___024root___trigger_anySet__stl(const VlUnpacked<QData/*63:0*/, 1> &in);

#ifdef VL_DEBUG
VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root___dump_triggers__stl(const VlUnpacked<QData/*63:0*/, 1> &triggers, const std::string &tag) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root___dump_triggers__stl\n"); );
    // Body
    if ((1U & (~ (IData)(Vtb_s2a_backend_fault_recovery___024root___trigger_anySet__stl(triggers))))) {
        VL_DBG_MSGS("         No '" + tag + "' region triggers active\n");
    }
    if ((1U & (IData)(triggers[0U]))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 0 is active: Internal 'stl' trigger - first iteration\n");
    }
}
#endif  // VL_DEBUG

VL_ATTR_COLD bool Vtb_s2a_backend_fault_recovery___024root___trigger_anySet__stl(const VlUnpacked<QData/*63:0*/, 1> &in) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root___trigger_anySet__stl\n"); );
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

extern const VlWide<43>/*1375:0*/ Vtb_s2a_backend_fault_recovery__ConstPool__CONST_h3efedef1_0;

VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root___stl_sequent__TOP__0(Vtb_s2a_backend_fault_recovery___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root___stl_sequent__TOP__0\n"); );
    Vtb_s2a_backend_fault_recovery__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    CData/*1:0*/ __Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__map_conv_activation__101__Vfuncout;
    __Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__map_conv_activation__101__Vfuncout = 0;
    CData/*1:0*/ __Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__map_conv_activation__101__descriptor_activation;
    __Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__map_conv_activation__101__descriptor_activation = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_5;
    __VdfgRegularize_h6e95ff9d_0_5 = 0;
    VlWide<3>/*64:0*/ __VdfgRegularize_h6e95ff9d_0_6;
    VL_ZERO_W(65, __VdfgRegularize_h6e95ff9d_0_6);
    VlWide<3>/*95:0*/ __Vtemp_2;
    VlWide<3>/*95:0*/ __Vtemp_3;
    VlWide<3>/*95:0*/ __Vtemp_4;
    VlWide<3>/*95:0*/ __Vtemp_6;
    VlWide<3>/*95:0*/ __Vtemp_7;
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
    VlWide<4>/*127:0*/ __Vtemp_46;
    VlWide<4>/*127:0*/ __Vtemp_47;
    VlWide<4>/*127:0*/ __Vtemp_48;
    VlWide<4>/*127:0*/ __Vtemp_49;
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
    VlWide<4>/*127:0*/ __Vtemp_64;
    VlWide<3>/*95:0*/ __Vtemp_67;
    VlWide<3>/*95:0*/ __Vtemp_68;
    VlWide<3>/*95:0*/ __Vtemp_69;
    VlWide<3>/*95:0*/ __Vtemp_70;
    VlWide<3>/*95:0*/ __Vtemp_72;
    VlWide<3>/*95:0*/ __Vtemp_74;
    VlWide<3>/*95:0*/ __Vtemp_75;
    VlWide<3>/*95:0*/ __Vtemp_76;
    VlWide<3>/*95:0*/ __Vtemp_77;
    VlWide<3>/*95:0*/ __Vtemp_78;
    VlWide<3>/*95:0*/ __Vtemp_79;
    VlWide<3>/*95:0*/ __Vtemp_80;
    VlWide<3>/*95:0*/ __Vtemp_82;
    VlWide<3>/*95:0*/ __Vtemp_83;
    VlWide<3>/*95:0*/ __Vtemp_84;
    VlWide<3>/*95:0*/ __Vtemp_85;
    VlWide<3>/*95:0*/ __Vtemp_86;
    VlWide<3>/*95:0*/ __Vtemp_87;
    VlWide<3>/*95:0*/ __Vtemp_88;
    VlWide<3>/*95:0*/ __Vtemp_89;
    VlWide<3>/*95:0*/ __Vtemp_90;
    VlWide<4>/*127:0*/ __Vtemp_92;
    VlWide<4>/*127:0*/ __Vtemp_93;
    VlWide<4>/*127:0*/ __Vtemp_94;
    VlWide<3>/*95:0*/ __Vtemp_99;
    VlWide<3>/*95:0*/ __Vtemp_100;
    VlWide<3>/*95:0*/ __Vtemp_101;
    VlWide<3>/*95:0*/ __Vtemp_102;
    VlWide<3>/*95:0*/ __Vtemp_103;
    VlWide<3>/*95:0*/ __Vtemp_104;
    VlWide<4>/*127:0*/ __Vtemp_106;
    VlWide<4>/*127:0*/ __Vtemp_107;
    VlWide<4>/*127:0*/ __Vtemp_108;
    VlWide<3>/*95:0*/ __Vtemp_113;
    VlWide<3>/*95:0*/ __Vtemp_114;
    VlWide<3>/*95:0*/ __Vtemp_115;
    VlWide<3>/*95:0*/ __Vtemp_116;
    VlWide<3>/*95:0*/ __Vtemp_117;
    VlWide<3>/*95:0*/ __Vtemp_118;
    VlWide<4>/*127:0*/ __Vtemp_120;
    VlWide<4>/*127:0*/ __Vtemp_121;
    VlWide<4>/*127:0*/ __Vtemp_122;
    VlWide<3>/*95:0*/ __Vtemp_127;
    VlWide<3>/*95:0*/ __Vtemp_128;
    VlWide<3>/*95:0*/ __Vtemp_129;
    VlWide<3>/*95:0*/ __Vtemp_130;
    VlWide<3>/*95:0*/ __Vtemp_131;
    VlWide<3>/*95:0*/ __Vtemp_132;
    VlWide<4>/*127:0*/ __Vtemp_134;
    VlWide<4>/*127:0*/ __Vtemp_135;
    VlWide<4>/*127:0*/ __Vtemp_136;
    VlWide<3>/*95:0*/ __Vtemp_141;
    VlWide<3>/*95:0*/ __Vtemp_142;
    VlWide<3>/*95:0*/ __Vtemp_143;
    VlWide<3>/*95:0*/ __Vtemp_144;
    VlWide<3>/*95:0*/ __Vtemp_145;
    VlWide<3>/*95:0*/ __Vtemp_146;
    VlWide<4>/*127:0*/ __Vtemp_148;
    VlWide<4>/*127:0*/ __Vtemp_149;
    VlWide<4>/*127:0*/ __Vtemp_150;
    VlWide<3>/*95:0*/ __Vtemp_155;
    VlWide<3>/*95:0*/ __Vtemp_156;
    VlWide<3>/*95:0*/ __Vtemp_157;
    VlWide<3>/*95:0*/ __Vtemp_158;
    VlWide<3>/*95:0*/ __Vtemp_159;
    VlWide<3>/*95:0*/ __Vtemp_160;
    VlWide<4>/*127:0*/ __Vtemp_162;
    VlWide<4>/*127:0*/ __Vtemp_163;
    VlWide<4>/*127:0*/ __Vtemp_164;
    VlWide<3>/*95:0*/ __Vtemp_169;
    VlWide<3>/*95:0*/ __Vtemp_170;
    VlWide<3>/*95:0*/ __Vtemp_171;
    VlWide<3>/*95:0*/ __Vtemp_172;
    VlWide<3>/*95:0*/ __Vtemp_173;
    VlWide<3>/*95:0*/ __Vtemp_174;
    VlWide<4>/*127:0*/ __Vtemp_176;
    VlWide<4>/*127:0*/ __Vtemp_177;
    VlWide<4>/*127:0*/ __Vtemp_178;
    VlWide<3>/*95:0*/ __Vtemp_183;
    VlWide<3>/*95:0*/ __Vtemp_184;
    VlWide<3>/*95:0*/ __Vtemp_185;
    VlWide<3>/*95:0*/ __Vtemp_186;
    VlWide<3>/*95:0*/ __Vtemp_187;
    VlWide<3>/*95:0*/ __Vtemp_188;
    VlWide<4>/*127:0*/ __Vtemp_190;
    VlWide<4>/*127:0*/ __Vtemp_191;
    VlWide<4>/*127:0*/ __Vtemp_192;
    VlWide<3>/*95:0*/ __Vtemp_197;
    VlWide<3>/*95:0*/ __Vtemp_198;
    VlWide<3>/*95:0*/ __Vtemp_199;
    VlWide<3>/*95:0*/ __Vtemp_200;
    VlWide<3>/*95:0*/ __Vtemp_201;
    VlWide<3>/*95:0*/ __Vtemp_202;
    VlWide<4>/*127:0*/ __Vtemp_204;
    VlWide<4>/*127:0*/ __Vtemp_205;
    VlWide<4>/*127:0*/ __Vtemp_206;
    VlWide<3>/*95:0*/ __Vtemp_212;
    VlWide<3>/*95:0*/ __Vtemp_213;
    VlWide<3>/*95:0*/ __Vtemp_215;
    VlWide<3>/*95:0*/ __Vtemp_216;
    // Body
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__mapped_response_error = 6U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__mapped_response_error = 6U;
    if ((((1U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_error_latched)) 
          | (2U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_error_latched))) 
         | (6U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_error_latched)))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__mapped_response_error 
            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_error_latched;
    } else if ((0U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_error_latched))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__mapped_response_error = 0U;
    }
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__mapped_response_error = 6U;
    if ((((1U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_error_latched)) 
          | (2U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_error_latched))) 
         | (6U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_error_latched)))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__mapped_response_error 
            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_error_latched;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__mapped_response_error 
            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_error_latched;
    } else if ((0U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_error_latched))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__mapped_response_error = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__mapped_response_error = 0U;
    }
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__csr_ready 
        = (1U & (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__hard_reset)));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__selected_byte_shift 
        = (0x00000018U & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__source_address_latched 
                          << 3U));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__selected_byte_shift 
        = (0x00000018U & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source_address_latched 
                          << 3U));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__request_byte_lane 
        = (3U & (0x00030210U >> ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__request_strobe_latched) 
                                 << 1U)));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__selected_byte_shift 
        = (0x00000018U & ((- (IData)((4U > (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__read_tap_index)))) 
                          & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched
                             [(3U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__read_tap_index))] 
                             << 3U)));
    __Vtemp_2[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_length_latched;
    __Vtemp_2[1U] = 0U;
    __Vtemp_2[2U] = 0U;
    __Vtemp_3[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_base_latched;
    __Vtemp_3[1U] = 0U;
    __Vtemp_3[2U] = 0U;
    VL_ADD_W(3, __Vtemp_4, __Vtemp_2, __Vtemp_3);
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_end_work[0U] 
        = __Vtemp_4[0U];
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_end_work[1U] 
        = __Vtemp_4[1U];
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_end_work[2U] 
        = (1U & __Vtemp_4[2U]);
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_wstrb = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_wstrb = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_wstrb = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_wstrb = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__backend_rsp_valid 
        = ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_pending) 
           & ((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__hard_reset)) 
              & ((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__backend_abort)) 
                 & (1U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_target_latched)))));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__backend_rsp_valid 
        = ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_pending) 
           & ((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__hard_reset)) 
              & ((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__backend_abort)) 
                 & (3U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_target_latched)))));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__backend_rsp_valid 
        = ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_pending) 
           & ((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__hard_reset)) 
              & ((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__backend_abort)) 
                 & (2U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_target_latched)))));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__config_idle 
        = (1U & (~ ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__buffer_owner_pl) 
                    | ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__busy) 
                       | ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__done) 
                          | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__error))))));
    if ((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))) {
        __Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__map_conv_activation__101__descriptor_activation 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_ACTIVATION
            [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor];
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__layer_index 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_LAYER_INDEX
            [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor];
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_upsample_engine__stride 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_UPSAMPLE_STRIDE
            [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor];
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__darknet_padding_parameter 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_MAXPOOL_DARKNET_PADDING
            [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor];
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_x 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_STRIDE_W
            [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor];
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_y 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_STRIDE_H
            [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor];
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_KERNEL_W
            [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor];
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_height 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_KERNEL_H
            [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor];
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_op 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OP
            [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor];
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_input_count 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_COUNT
            [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor];
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_base 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_ADDRESS
            [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor];
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_length 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_LENGTH_BYTES
            [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor];
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_n 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_N
            [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor];
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_c 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_C
            [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor];
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_h 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_H
            [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor];
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_w 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_W
            [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor];
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_ALIAS_LAYER_INDEX
            [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor];
    } else {
        __Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__map_conv_activation__101__descriptor_activation = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__layer_index = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_upsample_engine__stride = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__darknet_padding_parameter = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_x = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_y = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_height = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_op = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_input_count = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_base = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_length = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_n = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_c = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_h = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_w = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index = 0U;
    }
    __Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__map_conv_activation__101__Vfuncout 
        = (3U & (0xd0U >> ((IData)(__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__map_conv_activation__101__descriptor_activation) 
                           << 1U)));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_conv_engine__activation_mode 
        = __Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__map_conv_activation__101__Vfuncout;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_source_address_wide 
        = ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_package_base_latched)) 
           + ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__quantized_weight_offset_latched)) 
              + ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_reduction_index)) 
                 + ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_latched)) 
                    * (QData)((IData)((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base 
                                       + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_lane_index)))))));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__window_max_value = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__window_error_code = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__current_maximum = 0x80U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__candidate_value 
        = (0x000000ffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__candidate_values_latched[0U]);
    if (VL_LTS_III(8, 0x80U, (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__candidate_value))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__current_maximum 
            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__candidate_value;
    }
    if ((0x80U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__candidate_value))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__window_error_code = 1U;
    }
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__candidate_value 
        = (0x000000ffU & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__candidate_values_latched[0U] 
                          >> 8U));
    if ((0x80U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__candidate_value))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__window_error_code = 1U;
    }
    if (VL_GTS_III(8, (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__candidate_value), (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__current_maximum))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__current_maximum 
            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__candidate_value;
    }
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__candidate_value 
        = (0x000000ffU & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__candidate_values_latched[0U] 
                          >> 0x00000010U));
    if ((0x80U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__candidate_value))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__window_error_code = 1U;
    }
    if (VL_GTS_III(8, (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__candidate_value), (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__current_maximum))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__current_maximum 
            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__candidate_value;
    }
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__candidate_value 
        = (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__candidate_values_latched[0U] 
           >> 0x00000018U);
    if (VL_GTS_III(8, (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__candidate_value), (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__current_maximum))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__current_maximum 
            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__candidate_value;
    }
    if ((0x80U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__candidate_value))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__window_error_code = 1U;
    }
    if ((0U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__window_error_code))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__window_max_value 
            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__current_maximum;
    }
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_rstrb = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_rstrb = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_byte_offset_wide 
        = ((QData)((IData)((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_x 
                            + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_point_scan_x))) 
           + ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_latched)) 
              * ((QData)((IData)((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_y 
                                  + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_point_scan_y))) 
                 + ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_latched)) 
                    * (QData)((IData)((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base 
                                       + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_lane_index)))))));
    vlSelfRef.__VdfgRegularize_h6e95ff9d_0_7[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_width_latched;
    vlSelfRef.__VdfgRegularize_h6e95ff9d_0_7[1U] = 0U;
    vlSelfRef.__VdfgRegularize_h6e95ff9d_0_7[2U] = 0U;
    vlSelfRef.__VdfgRegularize_h6e95ff9d_0_8[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_height_latched;
    vlSelfRef.__VdfgRegularize_h6e95ff9d_0_8[1U] = 0U;
    vlSelfRef.__VdfgRegularize_h6e95ff9d_0_8[2U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_wdata = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_addr = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_wdata = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__selected_read_lane 
        = (0x0000000fU & ((IData)(1U) << (3U & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source_address_latched)));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_rstrb = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_wdata = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_rdata = 0U;
    if (((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid) 
         & (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_write)))) {
        if ((0U == (3U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr)))) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_rdata 
                = ((0x00000080U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                    ? 0U : ((0x00000040U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                             ? 0U : ((0x00000020U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                      ? ((0x00000010U 
                                          & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                          ? ((8U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                              ? ((4U 
                                                  & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                  ? 0U
                                                  : 
                                                 ((2U 
                                                   & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                   ? 0U
                                                   : 
                                                  ((1U 
                                                    & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                    ? 0U
                                                    : 0x00004f38U)))
                                              : ((4U 
                                                  & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                  ? 
                                                 ((2U 
                                                   & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                   ? 0U
                                                   : 
                                                  ((1U 
                                                    & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                    ? 0U
                                                    : 0x01ad5e80U))
                                                  : 
                                                 ((2U 
                                                   & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                   ? 0U
                                                   : 
                                                  ((1U 
                                                    & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                    ? 0U
                                                    : 0x000013ceU))))
                                          : ((8U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                              ? ((4U 
                                                  & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                  ? 
                                                 ((2U 
                                                   & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                   ? 0U
                                                   : 
                                                  ((1U 
                                                    & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                    ? 0U
                                                    : 0x01a46100U))
                                                  : 
                                                 ((2U 
                                                   & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                   ? 0U
                                                   : 
                                                  ((1U 
                                                    & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                    ? 0U
                                                    : vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__timeout_cycles)))
                                              : ((4U 
                                                  & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                  ? 
                                                 ((2U 
                                                   & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                   ? 0U
                                                   : 
                                                  ((1U 
                                                    & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                    ? 0U
                                                    : 0x01adadb8U))
                                                  : 
                                                 ((2U 
                                                   & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                   ? 0U
                                                   : 
                                                  ((1U 
                                                    & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                    ? 0U
                                                    : 0x01000000U)))))
                                      : ((0x00000010U 
                                          & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                          ? ((8U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                              ? ((4U 
                                                  & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                  ? 
                                                 ((2U 
                                                   & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                   ? 0U
                                                   : 
                                                  ((1U 
                                                    & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                    ? 0U
                                                    : vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__weight_bytes))
                                                  : 
                                                 ((2U 
                                                   & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                   ? 0U
                                                   : 
                                                  ((1U 
                                                    & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                    ? 0U
                                                    : vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__weight_addr)))
                                              : ((4U 
                                                  & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                  ? 
                                                 ((2U 
                                                   & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                   ? 0U
                                                   : 
                                                  ((1U 
                                                    & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                    ? 0U
                                                    : vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__input_bytes))
                                                  : 
                                                 ((2U 
                                                   & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                   ? 0U
                                                   : 
                                                  ((1U 
                                                    & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                    ? 0U
                                                    : vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__input_addr))))
                                          : ((8U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                              ? ((4U 
                                                  & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                  ? 
                                                 ((2U 
                                                   & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                   ? 0U
                                                   : 
                                                  ((1U 
                                                    & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                    ? 0U
                                                    : vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__frame_id))
                                                  : 
                                                 ((2U 
                                                   & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                   ? 0U
                                                   : 
                                                  ((1U 
                                                    & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                    ? 0U
                                                    : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__error_code))))
                                              : ((4U 
                                                  & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                  ? 
                                                 ((2U 
                                                   & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                   ? 0U
                                                   : 
                                                  ((1U 
                                                    & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                    ? 0U
                                                    : 
                                                   ((((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__buffer_owner_pl) 
                                                      << 3U) 
                                                     | ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__error) 
                                                        << 2U)) 
                                                    | (((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__done) 
                                                        << 1U) 
                                                       | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__busy)))))
                                                  : 0U))))));
        }
    }
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_rstrb = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__selected_input_lane = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_index = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_parameter[0U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_parameter[1U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_parameter[2U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_bias = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_invalid = 0U;
    if (((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_lane 
          < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count) 
         & (0x00000026U > vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_index 
            = ((((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                 [(0x0000003fU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                  : 0U) + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base) 
               + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_lane);
        if ((0x00000c5cU > vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_index)) {
            if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_index))) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_parameter[0U] 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                    [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_index)][0U];
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_parameter[1U] 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                    [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_index)][1U];
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_parameter[2U] 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                    [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_index)][2U];
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_bias 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_CONV_BIAS_ACCUMULATOR_INT32
                    [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_index)];
            } else {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_parameter[0U] = 0U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_parameter[1U] = 0U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_parameter[2U] = 0U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_bias = 0U;
            }
            if (((((((((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_index 
                        >= (((0x25U >= (0x0000003fU 
                                        & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                              ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                             [(0x0000003fU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                              : 0U) + ((0x25U >= (0x0000003fU 
                                                  & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                        ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                                       [(0x0000003fU 
                                         & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                        : 0U))) | (0U 
                                                   == 
                                                   ((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_parameter[2U] 
                                                     << 0x00000010U) 
                                                    | (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_parameter[1U] 
                                                       >> 0x00000010U)))) 
                      | (0U == ((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_parameter[1U] 
                                 << 0x00000018U) | 
                                (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_parameter[0U] 
                                 >> 8U)))) | (0x3fffffffU 
                                              < ((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_parameter[2U] 
                                                  << 0x00000010U) 
                                                 | (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_parameter[1U] 
                                                    >> 0x00000010U)))) 
                    | (0x3fffffffU < ((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_parameter[1U] 
                                       << 0x00000018U) 
                                      | (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_parameter[0U] 
                                         >> 8U)))) 
                   | (0x2fU < (0x000000ffU & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_parameter[1U] 
                                              >> 8U)))) 
                  | (0x2fU < (0x000000ffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_parameter[0U]))) 
                 | ((0U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__activation_mode_latched)) 
                    & ((((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_parameter[2U] 
                          << 0x00000010U) | (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_parameter[1U] 
                                             >> 0x00000010U)) 
                        != ((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_parameter[1U] 
                             << 0x00000018U) | (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_parameter[0U] 
                                                >> 8U))) 
                       | ((0x000000ffU & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_parameter[1U] 
                                          >> 8U)) != 
                          (0x000000ffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_parameter[0U])))))) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_invalid = 1U;
            }
        } else {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_invalid = 1U;
        }
    } else if ((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_lane 
                < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_invalid = 1U;
    }
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__selected_word_address 
        = (0xfffffffcU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source_address_latched);
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_addr = 0U;
    if ((4U > (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__read_tap_index))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__selected_input_lane 
            = (0x0000000fU & ((IData)(1U) << (3U & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched
                                              [(3U 
                                                & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__read_tap_index))])));
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_addr = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__selected_input_word_address = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__selected_input_word_address 
            = (0xfffffffcU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched
               [(3U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__read_tap_index))]);
    } else {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_addr = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__selected_input_word_address = 0U;
    }
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_parameter[0U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_parameter[1U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_parameter[2U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_accumulator = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requantized_value = 0U;
    if (((8U > vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_lane_index) 
         & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_lane_index 
            < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_parameter[0U] 
            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_mq_parameter
            [(7U & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_lane_index)][0U];
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_parameter[1U] 
            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_mq_parameter
            [(7U & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_lane_index)][1U];
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_parameter[2U] 
            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_mq_parameter
            [(7U & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_lane_index)][2U];
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_accumulator 
            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator
            [(7U & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_lane_index)];
        if ((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_accumulator 
             >> 0x1fU)) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier 
                = ((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_parameter[1U] 
                    << 0x00000018U) | (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_parameter[0U] 
                                       >> 8U));
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude 
                = ((IData)(1U) + (~ vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_accumulator));
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift 
                = (0x000000ffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_parameter[0U]);
        } else {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier 
                = ((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_parameter[2U] 
                    << 0x00000010U) | (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_parameter[1U] 
                                       >> 0x00000010U));
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude 
                = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_accumulator;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift 
                = (0x000000ffU & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_parameter[1U] 
                                  >> 8U));
        }
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product 
            = ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude)) 
               * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier)));
        if ((0U != vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift)) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add 
                = VL_SHIFTL_QQI(64,64,32, 1ULL, (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift 
                                                 - (IData)(1U)));
        }
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude 
            = VL_SHIFTR_QQI(64,64,32, (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product 
                                       + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add), vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift);
        __Vtemp_6[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude);
        __Vtemp_6[1U] = (IData)((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude 
                                 >> 0x00000020U));
        __Vtemp_6[2U] = 0U;
        VL_NEGATE_W(3, __Vtemp_7, __Vtemp_6);
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value 
            = ((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_accumulator 
                >> 0x1fU) ? (((QData)((IData)(__Vtemp_7[1U])) 
                              << 0x00000020U) | (QData)((IData)(__Vtemp_7[0U])))
                : vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude);
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requantized_value 
            = (VL_LTS_IQQ(64, 0x000000000000007fULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value)
                ? 0x0000007fU : (VL_GTS_IQQ(64, 0xffffffffffffff81ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value)
                                  ? 0x00000081U : (0x000000ffU 
                                                   & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value))));
    }
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_result_error = 6U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_result_valid = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_result_ready 
        = (((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__hard_reset)) 
            & (2U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))) 
           & (0x13U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__state)));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_result_ready 
        = (((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__hard_reset)) 
            & (3U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))) 
           & (6U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__state)));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_result_ready 
        = (((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__hard_reset)) 
            & (4U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))) 
           & (7U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__state)));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_result_ready 
        = (((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__hard_reset)) 
            & (5U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))) 
           & (5U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__state)));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_write = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_write = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_write = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_write = 0U;
    __Vtemp_9[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_batch_count_latched;
    __Vtemp_9[1U] = 0U;
    __Vtemp_9[2U] = 0U;
    __Vtemp_9[3U] = 0U;
    __Vtemp_10[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_channels_latched;
    __Vtemp_10[1U] = 0U;
    __Vtemp_10[2U] = 0U;
    __Vtemp_10[3U] = 0U;
    VL_MUL_W(4, __Vtemp_11, __Vtemp_9, __Vtemp_10);
    __Vtemp_12[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_height_latched;
    __Vtemp_12[1U] = 0U;
    __Vtemp_12[2U] = 0U;
    __Vtemp_12[3U] = 0U;
    VL_MUL_W(4, __Vtemp_13, __Vtemp_11, __Vtemp_12);
    __Vtemp_14[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_width_latched;
    __Vtemp_14[1U] = 0U;
    __Vtemp_14[2U] = 0U;
    __Vtemp_14[3U] = 0U;
    VL_MUL_W(4, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_elements_wide, __Vtemp_13, __Vtemp_14);
    __Vtemp_15[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_batch_count_latched;
    __Vtemp_15[1U] = 0U;
    __Vtemp_15[2U] = 0U;
    __Vtemp_15[3U] = 0U;
    __Vtemp_16[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_channels_latched;
    __Vtemp_16[1U] = 0U;
    __Vtemp_16[2U] = 0U;
    __Vtemp_16[3U] = 0U;
    VL_MUL_W(4, __Vtemp_17, __Vtemp_15, __Vtemp_16);
    __Vtemp_18[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_latched;
    __Vtemp_18[1U] = 0U;
    __Vtemp_18[2U] = 0U;
    __Vtemp_18[3U] = 0U;
    VL_MUL_W(4, __Vtemp_19, __Vtemp_17, __Vtemp_18);
    __Vtemp_20[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_latched;
    __Vtemp_20[1U] = 0U;
    __Vtemp_20[2U] = 0U;
    __Vtemp_20[3U] = 0U;
    VL_MUL_W(4, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_elements_wide, __Vtemp_19, __Vtemp_20);
    __Vtemp_21[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_channels_latched;
    __Vtemp_21[1U] = 0U;
    __Vtemp_21[2U] = 0U;
    __Vtemp_21[3U] = 0U;
    __Vtemp_22[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_channels_latched;
    __Vtemp_22[1U] = 0U;
    __Vtemp_22[2U] = 0U;
    __Vtemp_22[3U] = 0U;
    VL_MUL_W(4, __Vtemp_23, __Vtemp_21, __Vtemp_22);
    __Vtemp_24[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_height_latched;
    __Vtemp_24[1U] = 0U;
    __Vtemp_24[2U] = 0U;
    __Vtemp_24[3U] = 0U;
    VL_MUL_W(4, __Vtemp_25, __Vtemp_23, __Vtemp_24);
    __Vtemp_26[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_width_latched;
    __Vtemp_26[1U] = 0U;
    __Vtemp_26[2U] = 0U;
    __Vtemp_26[3U] = 0U;
    VL_MUL_W(4, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__expected_weight_bytes_wide, __Vtemp_25, __Vtemp_26);
    __Vtemp_27[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_channels_latched;
    __Vtemp_27[1U] = 0U;
    __Vtemp_27[2U] = 0U;
    __Vtemp_27[3U] = 0U;
    __Vtemp_28[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_height_latched;
    __Vtemp_28[1U] = 0U;
    __Vtemp_28[2U] = 0U;
    __Vtemp_28[3U] = 0U;
    VL_MUL_W(4, __Vtemp_29, __Vtemp_27, __Vtemp_28);
    __Vtemp_30[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_width_latched;
    __Vtemp_30[1U] = 0U;
    __Vtemp_30[2U] = 0U;
    __Vtemp_30[3U] = 0U;
    VL_MUL_W(4, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_wide, __Vtemp_29, __Vtemp_30);
    __Vtemp_31[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_base_latched;
    __Vtemp_31[1U] = 0U;
    __Vtemp_31[2U] = 0U;
    __Vtemp_31[3U] = 0U;
    __Vtemp_32[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_length_latched;
    __Vtemp_32[1U] = 0U;
    __Vtemp_32[2U] = 0U;
    __Vtemp_32[3U] = 0U;
    VL_ADD_W(4, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_end_wide, __Vtemp_31, __Vtemp_32);
    __Vtemp_33[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_base_latched;
    __Vtemp_33[1U] = 0U;
    __Vtemp_33[2U] = 0U;
    __Vtemp_33[3U] = 0U;
    __Vtemp_34[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_length_latched;
    __Vtemp_34[1U] = 0U;
    __Vtemp_34[2U] = 0U;
    __Vtemp_34[3U] = 0U;
    VL_ADD_W(4, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_end_wide, __Vtemp_33, __Vtemp_34);
    __Vtemp_35[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_package_base_latched;
    __Vtemp_35[1U] = 0U;
    __Vtemp_35[2U] = 0U;
    __Vtemp_35[3U] = 0U;
    __Vtemp_36[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_package_length_latched;
    __Vtemp_36[1U] = 0U;
    __Vtemp_36[2U] = 0U;
    __Vtemp_36[3U] = 0U;
    VL_ADD_W(4, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_package_end_wide, __Vtemp_35, __Vtemp_36);
    __Vtemp_37[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__quantized_weight_offset_latched;
    __Vtemp_37[1U] = 0U;
    __Vtemp_37[2U] = 0U;
    __Vtemp_37[3U] = 0U;
    __Vtemp_38[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__quantized_weight_bytes_latched;
    __Vtemp_38[1U] = 0U;
    __Vtemp_38[2U] = 0U;
    __Vtemp_38[3U] = 0U;
    VL_ADD_W(4, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__quantized_weight_end_wide, __Vtemp_37, __Vtemp_38);
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_numerator 
        = (((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_height_latched)) 
            + (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__pad_top_latched))) 
           + (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__pad_bottom_latched)));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_numerator 
        = (((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_width_latched)) 
            + (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__pad_left_latched))) 
           + (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__pad_right_latched)));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_shape_span 
        = (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_numerator 
           - (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_height_latched)));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_shape_span 
        = (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_numerator 
           - (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_width_latched)));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_shape_product 
        = ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_latched)) 
           * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__stride_y_latched)));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_shape_product 
        = ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_latched)) 
           * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__stride_x_latched)));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_span_plus_stride 
        = (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_shape_span 
           + (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__stride_y_latched)));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_span_plus_stride 
        = (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_shape_span 
           + (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__stride_x_latched)));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_height_wide[0U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_height_wide[1U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_height_wide[2U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_height_wide[3U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_width_wide[0U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_width_wide[1U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_width_wide[2U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_width_wide[3U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_bytes_wide[0U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_bytes_wide[1U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_bytes_wide[2U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_bytes_wide[3U] = 0U;
    if (((0U != vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_latched) 
         & (0U != vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_latched))) {
        __Vtemp_39[0U] = (((8U > vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_latched)
                            ? vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_latched
                            : 8U) - (IData)(1U));
        __Vtemp_39[1U] = 0U;
        __Vtemp_39[2U] = 0U;
        __Vtemp_39[3U] = 0U;
        __Vtemp_40[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__stride_y_latched;
        __Vtemp_40[1U] = 0U;
        __Vtemp_40[2U] = 0U;
        __Vtemp_40[3U] = 0U;
        VL_MUL_W(4, __Vtemp_41, __Vtemp_39, __Vtemp_40);
        __Vtemp_42[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_height_latched;
        __Vtemp_42[1U] = 0U;
        __Vtemp_42[2U] = 0U;
        __Vtemp_42[3U] = 0U;
        VL_ADD_W(4, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_height_wide, __Vtemp_41, __Vtemp_42);
        __Vtemp_43[0U] = (((8U > vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_latched)
                            ? vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_latched
                            : 8U) - (IData)(1U));
        __Vtemp_43[1U] = 0U;
        __Vtemp_43[2U] = 0U;
        __Vtemp_43[3U] = 0U;
        __Vtemp_44[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__stride_x_latched;
        __Vtemp_44[1U] = 0U;
        __Vtemp_44[2U] = 0U;
        __Vtemp_44[3U] = 0U;
        VL_MUL_W(4, __Vtemp_45, __Vtemp_43, __Vtemp_44);
        __Vtemp_46[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_width_latched;
        __Vtemp_46[1U] = 0U;
        __Vtemp_46[2U] = 0U;
        __Vtemp_46[3U] = 0U;
        VL_ADD_W(4, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_width_wide, __Vtemp_45, __Vtemp_46);
        VL_MUL_W(4, __Vtemp_47, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_height_wide, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_width_wide);
        __Vtemp_48[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_channels_latched;
        __Vtemp_48[1U] = 0U;
        __Vtemp_48[2U] = 0U;
        __Vtemp_48[3U] = 0U;
        VL_MUL_W(4, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_bytes_wide, __Vtemp_47, __Vtemp_48);
    }
    __Vtemp_49[0U] = ((8U > vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_channels_latched)
                       ? vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_channels_latched
                       : 8U);
    __Vtemp_49[1U] = 0U;
    __Vtemp_49[2U] = 0U;
    __Vtemp_49[3U] = 0U;
    VL_MUL_W(4, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__full_weight_group_bytes_wide, __Vtemp_49, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_wide);
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__validation_ok = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__validation_error = 1U;
    __Vtemp_51[0U] = 0x00001fffU;
    __Vtemp_51[1U] = 0U;
    __Vtemp_51[2U] = 0U;
    __Vtemp_51[3U] = 0U;
    if ((1U & ((((((((((((((((((((((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__buffer_owner_pl)) 
                                   | (1U < (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__activation_mode_latched))) 
                                  | (1U != vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_batch_count_latched)) 
                                 | (1U != vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_batch_count_latched)) 
                                | (0U != vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_batch_latched)) 
                               | (0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_channels_latched)) 
                              | (0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_height_latched)) 
                             | (0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_width_latched)) 
                            | (0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_channels_latched)) 
                           | (0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_latched)) 
                          | (0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_latched)) 
                         | (0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_height_latched)) 
                        | (0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_width_latched)) 
                       | (0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__stride_y_latched)) 
                      | (0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__stride_x_latched)) 
                     | (1U != vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__groups_latched)) 
                    | (0U != vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__padding_latched)) 
                   | (0U == (((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_wide[0U] 
                               | vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_wide[1U]) 
                              | vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_wide[2U]) 
                             | vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_wide[3U]))) 
                  | VL_LT_W(4, __Vtemp_51, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_wide)) 
                 | (0x00000026U <= vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)) 
                | ((0x00000026U > vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched) 
                   & (0U != ((0x25U >= (0x0000003fU 
                                        & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                              ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OP
                             [(0x0000003fU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                              : 0U)))) | (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched 
                                          != vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_layer_index_latched)))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__validation_error 
            = (((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched 
                 != vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_layer_index_latched) 
                | (0x00000026U <= vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                ? 2U : 1U);
    } else {
        __Vtemp_52[0U] = 0xffffffffU;
        __Vtemp_52[1U] = 0U;
        __Vtemp_52[2U] = 0U;
        __Vtemp_52[3U] = 0U;
        __Vtemp_53[0U] = 0xffffffffU;
        __Vtemp_53[1U] = 0U;
        __Vtemp_53[2U] = 0U;
        __Vtemp_53[3U] = 0U;
        __Vtemp_54[0U] = 0xffffffffU;
        __Vtemp_54[1U] = 0U;
        __Vtemp_54[2U] = 0U;
        __Vtemp_54[3U] = 0U;
        if ((((((VL_LT_W(4, __Vtemp_52, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_elements_wide) 
                 | (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_length_latched 
                    != vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_elements_wide[0U])) 
                | VL_LT_W(4, __Vtemp_53, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_elements_wide)) 
               | (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_length_latched 
                  != vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_elements_wide[0U])) 
              | VL_LT_W(4, __Vtemp_54, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__expected_weight_bytes_wide)) 
             | (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__quantized_weight_bytes_latched 
                != vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__expected_weight_bytes_wide[0U]))) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__validation_error = 3U;
        } else {
            __Vtemp_55[0U] = 0U;
            __Vtemp_55[1U] = 1U;
            __Vtemp_55[2U] = 0U;
            __Vtemp_55[3U] = 0U;
            __Vtemp_56[0U] = 0U;
            __Vtemp_56[1U] = 1U;
            __Vtemp_56[2U] = 0U;
            __Vtemp_56[3U] = 0U;
            __Vtemp_57[0U] = 0U;
            __Vtemp_57[1U] = 1U;
            __Vtemp_57[2U] = 0U;
            __Vtemp_57[3U] = 0U;
            __Vtemp_58[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_package_length_latched;
            __Vtemp_58[1U] = 0U;
            __Vtemp_58[2U] = 0U;
            __Vtemp_58[3U] = 0U;
            __Vtemp_59[0U] = 0x00000c5cU;
            __Vtemp_59[1U] = 0U;
            __Vtemp_59[2U] = 0U;
            __Vtemp_59[3U] = 0U;
            __Vtemp_60[0U] = ((0x25U >= (0x0000003fU 
                                         & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                               ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                              [(0x0000003fU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                               : 0U);
            __Vtemp_60[1U] = 0U;
            __Vtemp_60[2U] = 0U;
            __Vtemp_60[3U] = 0U;
            __Vtemp_61[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_channels_latched;
            __Vtemp_61[1U] = 0U;
            __Vtemp_61[2U] = 0U;
            __Vtemp_61[3U] = 0U;
            VL_ADD_W(4, __Vtemp_62, __Vtemp_60, __Vtemp_61);
            __Vtemp_63[0U] = 0x0000c800U;
            __Vtemp_63[1U] = 0U;
            __Vtemp_63[2U] = 0U;
            __Vtemp_63[3U] = 0U;
            __Vtemp_64[0U] = 0x00009000U;
            __Vtemp_64[1U] = 0U;
            __Vtemp_64[2U] = 0U;
            __Vtemp_64[3U] = 0U;
            if (((((((((VL_LT_W(4, __Vtemp_55, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_end_wide) 
                        | VL_LT_W(4, __Vtemp_56, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_end_wide)) 
                       | VL_LT_W(4, __Vtemp_57, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_package_end_wide)) 
                      | (0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_package_length_latched)) 
                     | VL_GT_W(4, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__quantized_weight_end_wide, __Vtemp_58)) 
                    | (((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                         ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                        [(0x0000003fU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                         : 0U) != vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_channels_latched)) 
                   | VL_LT_W(4, __Vtemp_59, __Vtemp_62)) 
                  | VL_LT_W(4, __Vtemp_63, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_bytes_wide)) 
                 | VL_LT_W(4, __Vtemp_64, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__full_weight_group_bytes_wide))) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__validation_error = 2U;
            } else if (((((((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_numerator 
                             < (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_height_latched))) 
                            | (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_numerator 
                               < (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_width_latched)))) 
                           | (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_shape_product 
                              <= vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_shape_span)) 
                          | (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_shape_product 
                             > vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_span_plus_stride)) 
                         | (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_shape_product 
                            <= vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_shape_span)) 
                        | (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_shape_product 
                           > vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_span_plus_stride))) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__validation_error = 1U;
            } else {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__validation_ok = 1U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__validation_error = 0U;
            }
        }
    }
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__backend_rsp_valid 
        = ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_pending) 
           & ((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__hard_reset)) 
              & ((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__backend_abort)) 
                 & (0U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_target_latched)))));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__query_output_channels = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__query_output_height = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__query_output_width = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__query_source_index = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__query_source_channel = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__query_source_address = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__query_output_value = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__query_error_code = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_argument = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_range = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source0_shape_bytes = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_shape_bytes = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_plane_elements = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_object_end = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__expected_group_start = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__expected_group_end = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_selected_count = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_multiplier = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_base_address = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_length_bytes = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_value = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_magnitude = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__scaled_product = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__rounded_magnitude = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__scaled_signed = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_source_index = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_source_channel = 0U;
    if ((1U & ((((((((((~ ((1U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source_count_latched) 
                           | (2U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source_count_latched))) 
                       | (0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__groups_latched)) 
                      | (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__group_id_latched 
                         >= vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__groups_latched)) 
                     | (0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_channels_latched)) 
                    | (0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_height_latched)) 
                   | (0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_width_latched)) 
                  | (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_start_latched 
                     >= vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_end_latched)) 
                 | (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_end_latched 
                    > vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_channels_latched)) 
                | (0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_multiplier_latched)) 
               | (0x80000000U < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_multiplier_latched)))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_argument = 1U;
    }
    if ((2U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source_count_latched)) {
        if ((((((((((0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_channels_latched) 
                    | (0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_height_latched)) 
                   | (0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_width_latched)) 
                  | (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_height_latched 
                     != vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_height_latched)) 
                 | (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_width_latched 
                    != vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_width_latched)) 
                | (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_start_latched 
                   >= vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_end_latched)) 
               | (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_end_latched 
                  > vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_channels_latched)) 
              | (0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_multiplier_latched)) 
             | (0x80000000U < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_multiplier_latched))) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_argument = 1U;
        }
    }
    if (((1U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__groups_latched) 
         & ((0U != vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_start_latched) 
            | (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_end_latched 
               != vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_channels_latched)))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_argument = 1U;
    } else if ((1U < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__groups_latched)) {
        if (((1U != vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source_count_latched) 
             | (0U != VL_MODDIV_III(32, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_channels_latched, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__groups_latched)))) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_argument = 1U;
        } else {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__expected_group_start 
                = ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__group_id_latched)) 
                   * VL_DIV_QQQ(64, (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_channels_latched)), (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__groups_latched))));
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__expected_group_end 
                = (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__expected_group_start 
                   + VL_DIV_QQQ(64, (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_channels_latched)), (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__groups_latched))));
            if (((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_start_latched 
                  != (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__expected_group_start)) 
                 | (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_end_latched 
                    != (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__expected_group_end)))) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_argument = 1U;
            }
        }
    }
    if (((2U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source_count_latched) 
         & (((0U != vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_start_latched) 
             | (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_end_latched 
                != vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_channels_latched)) 
            | (1U != vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__groups_latched)))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_argument = 1U;
    }
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source0_selected_count 
        = (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_end_latched 
           - vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_start_latched);
    if ((2U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source_count_latched)) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_selected_count 
            = (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_end_latched 
               - vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_start_latched);
    }
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__output_channels_wide 
        = ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source0_selected_count)) 
           + (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_selected_count)));
    if ((0x00000000ffffffffULL < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__output_channels_wide)) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_range = 1U;
    }
    if ((((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_y_latched 
           >= vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_height_latched) 
          | (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_x_latched 
             >= vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_width_latched)) 
         | ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_channel_latched)) 
            >= vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__output_channels_wide))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_argument = 1U;
    }
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source0_plane_elements 
        = ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_channels_latched)) 
           * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_height_latched)));
    if ((0x00000000ffffffffULL < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source0_plane_elements)) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_range = 1U;
    } else {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source0_shape_bytes 
            = (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source0_plane_elements 
               * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_width_latched)));
        if ((0x00000000ffffffffULL < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source0_shape_bytes)) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_range = 1U;
        }
    }
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source0_object_end 
        = ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_base_latched)) 
           + (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_length_latched)));
    if ((((0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_length_latched) 
          | ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_length_latched)) 
             < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source0_shape_bytes)) 
         | (0x0000000100000000ULL < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source0_object_end))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_range = 1U;
    }
    if ((2U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source_count_latched)) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_plane_elements 
            = ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_channels_latched)) 
               * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_height_latched)));
        if ((0x00000000ffffffffULL < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_plane_elements)) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_range = 1U;
        } else {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_shape_bytes 
                = (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_plane_elements 
                   * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_width_latched)));
            if ((0x00000000ffffffffULL < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_shape_bytes)) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_range = 1U;
            }
        }
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_object_end 
            = ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_base_latched)) 
               + (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_length_latched)));
        if ((((0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_length_latched) 
              | ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_length_latched)) 
                 < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_shape_bytes)) 
             | (0x0000000100000000ULL < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_object_end))) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_range = 1U;
        }
    }
    if ((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_channel_latched 
         < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source0_selected_count)) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_source_index = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_source_channel 
            = (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_start_latched 
               + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_channel_latched);
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_value 
            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_value_latched;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_multiplier 
            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_multiplier_latched;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_base_address 
            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_base_latched;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_length_bytes 
            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_length_latched;
    } else if ((2U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source_count_latched)) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_source_index = 1U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_source_channel 
            = (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_start_latched 
               + (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_channel_latched 
                  - vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source0_selected_count));
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_value 
            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_value_latched;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_multiplier 
            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_multiplier_latched;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_base_address 
            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_base_latched;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_length_bytes 
            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_length_latched;
    }
    if ((0x80U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_value))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_argument = 1U;
    }
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_offset 
        = (((((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_source_channel)) 
              * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_height_latched))) 
             + (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_y_latched))) 
            * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_width_latched))) 
           + (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_x_latched)));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_address_wide 
        = ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_base_address)) 
           + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_offset);
    if (((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_offset 
          >= (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_length_bytes))) 
         | (0x00000000ffffffffULL < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_address_wide))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_range = 1U;
    }
    if (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_argument) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__query_error_code = 1U;
    } else if (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_range) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__query_error_code = 2U;
    } else {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_magnitude 
            = (0x000000ffU & (VL_GTS_III(8, 0U, (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_value))
                               ? (- (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_value))
                               : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_value)));
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__scaled_product 
            = ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_magnitude)) 
               * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_multiplier)));
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__query_output_channels 
            = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__output_channels_wide);
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__query_output_height 
            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_height_latched;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__query_output_width 
            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_width_latched;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__query_source_index 
            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_source_index;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__query_source_channel 
            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_source_channel;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__query_source_address 
            = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_address_wide);
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__rounded_magnitude 
            = ((0x0000000040000000ULL + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__scaled_product) 
               >> 0x0000001fU);
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__scaled_signed 
            = (VL_GTS_III(8, 0U, (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_value))
                ? (- vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__rounded_magnitude)
                : vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__rounded_magnitude);
        if (VL_LTS_IQQ(64, 0x000000000000007fULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__scaled_signed)) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__scaled_signed = 0x000000000000007fULL;
        } else if (VL_GTS_IQQ(64, 0xffffffffffffff81ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__scaled_signed)) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__scaled_signed = 0xffffffffffffff81ULL;
        }
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__query_output_value 
            = (0x000000ffU & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__scaled_signed));
    }
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_valid = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_valid = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_valid = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_valid = 0U;
    if ((1U & ((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__hard_reset)) 
               & (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__backend_abort))))) {
        if ((1U != (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__state))) {
            if ((4U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__state))) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_wstrb 
                    = (0x0000000fU & ((IData)(1U) << 
                                      (3U & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_address_latched)));
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_wdata 
                    = VL_SHIFTL_III(32,32,32, (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__result_value_latched), 
                                    (0x00000018U & 
                                     (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_address_latched 
                                      << 3U)));
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_write = 1U;
            }
        }
        if ((1U != (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__state))) {
            if ((3U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__state))) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_wstrb 
                    = (0x0000000fU & ((IData)(1U) << 
                                      (3U & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__output_address_latched)));
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_wdata 
                    = VL_SHIFTL_III(32,32,32, (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__copied_value_latched), 
                                    (0x00000018U & 
                                     (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__output_address_latched 
                                      << 3U)));
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_write = 1U;
            }
        }
        if ((2U != (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__state))) {
            if ((5U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__state))) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_wstrb 
                    = (0x0000000fU & ((IData)(1U) << 
                                      (3U & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_address_latched)));
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_wdata 
                    = VL_SHIFTL_III(32,32,32, (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__result_value_latched), 
                                    (0x00000018U & 
                                     (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_address_latched 
                                      << 3U)));
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_write = 1U;
            }
        }
        if ((1U & (~ ((4U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__state)) 
                      || (8U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__state)))))) {
            if ((0x10U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__state))) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_wstrb 
                    = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__request_strobe_latched;
            }
        }
        if ((1U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__state))) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_rstrb 
                = (0x0000000fU & ((IData)(1U) << (3U 
                                                  & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__source_address_latched)));
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_addr 
                = (0xfffffffcU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__source_address_latched);
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_valid = 1U;
        } else if ((3U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__state))) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_addr 
                = (0xfffffffcU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__output_address_latched);
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_valid = 1U;
        }
        if (((4U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__state)) 
             || (8U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__state)))) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_rstrb 
                = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__request_strobe_latched;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_write = 0U;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_valid = 1U;
        } else if ((0x10U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__state))) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_write = 1U;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_valid = 1U;
        }
        if ((2U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__state))) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_rstrb 
                = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__selected_read_lane;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_addr 
                = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__selected_word_address;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_valid = 1U;
        } else if ((5U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__state))) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_addr 
                = (0xfffffffcU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_address_latched);
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_valid = 1U;
        }
        if ((1U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__state))) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_rstrb 
                = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__selected_input_lane;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_addr 
                = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__selected_input_word_address;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_valid = 1U;
        } else if ((4U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__state))) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_addr 
                = (0xfffffffcU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_address_latched);
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_valid = 1U;
        }
    }
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__start_ready 
        = ((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__hard_reset)) 
           & ((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__backend_abort)) 
              & (0U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__state))));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__start_ready 
        = ((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__hard_reset)) 
           & ((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__backend_abort)) 
              & (0U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__state))));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__start_ready 
        = ((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__hard_reset)) 
           & ((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__backend_abort)) 
              & (0U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__state))));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__start_ready 
        = ((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__hard_reset)) 
           & ((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__backend_abort)) 
              & (0U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__state))));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_address_wide 
        = ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_base_latched)) 
           + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_byte_offset_wide);
    __Vtemp_67[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_channels_latched;
    __Vtemp_67[1U] = 0U;
    __Vtemp_67[2U] = 0U;
    VL_MUL_W(3, __Vtemp_68, __Vtemp_67, vlSelfRef.__VdfgRegularize_h6e95ff9d_0_7);
    __Vtemp_69[0U] = __Vtemp_68[0U];
    __Vtemp_69[1U] = __Vtemp_68[1U];
    __Vtemp_69[2U] = (1U & __Vtemp_68[2U]);
    VL_MUL_W(3, __Vtemp_70, vlSelfRef.__VdfgRegularize_h6e95ff9d_0_8, __Vtemp_69);
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_elements_work[0U] 
        = __Vtemp_70[0U];
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_elements_work[1U] 
        = __Vtemp_70[1U];
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_elements_work[2U] 
        = (1U & __Vtemp_70[2U]);
    __Vtemp_72[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_x_latched;
    __Vtemp_72[1U] = 0U;
    __Vtemp_72[2U] = 0U;
    __Vtemp_74[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_y_latched;
    __Vtemp_74[1U] = 0U;
    __Vtemp_74[2U] = 0U;
    __Vtemp_75[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_channel_latched;
    __Vtemp_75[1U] = 0U;
    __Vtemp_75[2U] = 0U;
    VL_MUL_W(3, __Vtemp_76, vlSelfRef.__VdfgRegularize_h6e95ff9d_0_8, __Vtemp_75);
    VL_ADD_W(3, __Vtemp_77, __Vtemp_74, __Vtemp_76);
    __Vtemp_78[0U] = __Vtemp_77[0U];
    __Vtemp_78[1U] = __Vtemp_77[1U];
    __Vtemp_78[2U] = (1U & __Vtemp_77[2U]);
    VL_MUL_W(3, __Vtemp_79, vlSelfRef.__VdfgRegularize_h6e95ff9d_0_7, __Vtemp_78);
    VL_ADD_W(3, __Vtemp_80, __Vtemp_72, __Vtemp_79);
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_offset_work[0U] 
        = __Vtemp_80[0U];
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_offset_work[1U] 
        = __Vtemp_80[1U];
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_offset_work[2U] 
        = (1U & __Vtemp_80[2U]);
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_wdata = 0U;
    if ((4U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))) {
        if ((1U & (~ ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                      >> 1U)))) {
            if ((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_result_error 
                    = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__result_error_latched;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_result_valid 
                    = ((5U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__state)) 
                       & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_result_ready));
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_wdata 
                    = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_wdata;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_wdata 
                    = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_wdata;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_addr = 0U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_addr 
                    = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_addr;
            } else {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_result_error 
                    = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__result_error_latched;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_result_valid 
                    = ((7U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__state)) 
                       & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_result_ready));
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_wdata 
                    = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_wdata;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_wdata 
                    = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_wdata;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_addr = 0U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_addr 
                    = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_addr;
            }
        } else {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_wdata 
                = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_wdata;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_addr = 0U;
        }
    } else if ((2U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))) {
        if ((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_result_error 
                = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__result_error_latched;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_result_valid 
                = ((6U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__state)) 
                   & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_result_ready));
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_wdata 
                = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_wdata;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_wdata 
                = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_wdata;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_addr = 0U;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_addr 
                = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_addr;
        } else {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_result_error 
                = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__result_error_latched;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_result_valid 
                = ((0x13U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__state)) 
                   & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_result_ready));
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_wdata 
                = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__request_wdata_latched;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_wdata 
                = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_wdata;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_addr = 0U;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_addr 
                = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__request_address_latched;
        }
    } else {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_wdata 
            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_wdata;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_addr = 0U;
    }
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_addr 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_addr;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__patch_plane_bytes 
        = ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__patch_height)) 
           * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__patch_width)));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_input_y = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_input_x = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_in_bounds = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_advance = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_source_offset = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_source_address_wide = 0ULL;
    if (((0ULL != vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__patch_plane_bytes) 
         & (0U != vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__patch_width))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_input_y 
            = ((((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_y)) 
                 * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__stride_y_latched))) 
                + (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_y))) 
               - (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__pad_top_latched)));
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_input_x 
            = ((((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_x)) 
                 * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__stride_x_latched))) 
                + (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_x))) 
               - (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__pad_left_latched)));
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_in_bounds 
            = (((VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_input_y) 
                 & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_input_y, (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_height_latched)))) 
                & VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_input_x)) 
               & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_input_x, (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_width_latched))));
        if (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_in_bounds) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_source_offset 
                = (((((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_channel)) 
                      * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_height_latched))) 
                     + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_input_y) 
                    * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_width_latched))) 
                   + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_input_x);
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_source_address_wide 
                = ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_base_latched)) 
                   + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_source_offset);
        }
    }
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_area 
        = (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_height_latched 
           * vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_width_latched);
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_y = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_x = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_input_y = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_input_x = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_tap_in_bounds = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index_wide = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_bad_argument = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_overflow = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[0U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[0U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[0U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[0U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[1U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[1U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[1U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[1U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[2U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[2U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[2U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[2U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[3U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[3U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[3U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[3U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[4U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[4U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[4U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[4U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[5U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[5U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[5U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[5U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[6U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[6U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[6U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[6U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[7U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[7U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[7U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[7U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__comb_lane = 8U;
    if (((0U != vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_area) 
         & (0U != vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__tile_width))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_y 
            = VL_DIV_III(32, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_index, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__tile_width);
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__comb_lane = 8U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_x 
            = VL_MODDIV_III(32, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_index, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__tile_width);
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_input_y 
            = (((((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_y)) 
                  * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__stride_y_latched))) 
                 + ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_y)) 
                    * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__stride_y_latched)))) 
                + (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_y))) 
               - (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__pad_top_latched)));
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_input_x 
            = (((((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_x)) 
                  * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__stride_x_latched))) 
                 + ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_x)) 
                    * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__stride_x_latched)))) 
                + (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_x))) 
               - (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__pad_left_latched)));
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_tap_in_bounds 
            = (((VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_input_y) 
                 & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_input_y, (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_height_latched)))) 
                & VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_input_x)) 
               & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_input_x, (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_width_latched))));
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index_wide 
            = (((((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_input_channel)) 
                  * vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__patch_plane_bytes) 
                 + ((((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_y)) 
                      * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__stride_y_latched))) 
                     + (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_y))) 
                    * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__patch_width)))) 
                + ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_x)) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__stride_x_latched)))) 
               + (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_x)));
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index 
            = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index_wide);
        if ((0U < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[0U] 
                = ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_tap_in_bounds)
                    ? ((0xc7ffU >= (0x0000ffffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index))
                        ? vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_patch
                       [(0x0000ffffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index)]
                        : 0U) : 0U);
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[0U] 
                = ((0x8fffU >= (0x0000ffffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_reduction_index))
                    ? vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_group
                   [(0x0000ffffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_reduction_index)]
                    : 0U);
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[0U] 
                = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                                   & ((- (IData)(
                                                                 (1U 
                                                                  & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[0U] 
                                                                     >> 7U)))) 
                                                      << 8U)) 
                                                  | vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[0U]), 
                                             ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[0U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[0U])));
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[0U] 
                = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                              (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[0U] 
                                                               >> 0x1fU))) 
                                              << 0x00000020U) 
                                             | (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[0U]))) 
                                            + (((QData)((IData)(
                                                                (0x0001ffffU 
                                                                 & (- (IData)(
                                                                              (1U 
                                                                               & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[0U] 
                                                                                >> 0x0fU))))))) 
                                                << 0x00000010U) 
                                               | (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[0U])))));
            if (((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_tap_in_bounds) 
                 & ((0x80U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[0U]) 
                    | (0x80U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[0U])))) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_bad_argument = 1U;
            }
            if (((1U & (IData)((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[0U] 
                                >> 0x20U))) != (1U 
                                                & (IData)(
                                                          (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[0U] 
                                                           >> 0x1fU))))) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_overflow = 1U;
            }
        } else {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[0U] = 0U;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[0U] = 0U;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[0U] = 0U;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[0U] = 0ULL;
        }
        if ((1U < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[1U] 
                = ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_tap_in_bounds)
                    ? ((0xc7ffU >= (0x0000ffffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index))
                        ? vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_patch
                       [(0x0000ffffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index)]
                        : 0U) : 0U);
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[1U] 
                = ((0x8fffU >= (0x0000ffffU & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_latched 
                                               + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_reduction_index)))
                    ? vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_group
                   [(0x0000ffffU & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_latched 
                                    + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_reduction_index))]
                    : 0U);
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[1U] 
                = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                                   & ((- (IData)(
                                                                 (1U 
                                                                  & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[1U] 
                                                                     >> 7U)))) 
                                                      << 8U)) 
                                                  | vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[1U]), 
                                             ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[1U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[1U])));
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[1U] 
                = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                              (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[1U] 
                                                               >> 0x1fU))) 
                                              << 0x00000020U) 
                                             | (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[1U]))) 
                                            + (((QData)((IData)(
                                                                (0x0001ffffU 
                                                                 & (- (IData)(
                                                                              (1U 
                                                                               & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[1U] 
                                                                                >> 0x0fU))))))) 
                                                << 0x00000010U) 
                                               | (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[1U])))));
            if (((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_tap_in_bounds) 
                 & ((0x80U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[1U]) 
                    | (0x80U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[1U])))) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_bad_argument = 1U;
            }
            if (((1U & (IData)((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[1U] 
                                >> 0x20U))) != (1U 
                                                & (IData)(
                                                          (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[1U] 
                                                           >> 0x1fU))))) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_overflow = 1U;
            }
        } else {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[1U] = 0U;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[1U] = 0U;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[1U] = 0U;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[1U] = 0ULL;
        }
        if ((2U < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[2U] 
                = ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_tap_in_bounds)
                    ? ((0xc7ffU >= (0x0000ffffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index))
                        ? vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_patch
                       [(0x0000ffffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index)]
                        : 0U) : 0U);
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[2U] 
                = ((0x8fffU >= (0x0000ffffU & ((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_latched 
                                                << 1U) 
                                               + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_reduction_index)))
                    ? vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_group
                   [(0x0000ffffU & ((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_latched 
                                     << 1U) + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_reduction_index))]
                    : 0U);
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[2U] 
                = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                                   & ((- (IData)(
                                                                 (1U 
                                                                  & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[2U] 
                                                                     >> 7U)))) 
                                                      << 8U)) 
                                                  | vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[2U]), 
                                             ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[2U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[2U])));
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[2U] 
                = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                              (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[2U] 
                                                               >> 0x1fU))) 
                                              << 0x00000020U) 
                                             | (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[2U]))) 
                                            + (((QData)((IData)(
                                                                (0x0001ffffU 
                                                                 & (- (IData)(
                                                                              (1U 
                                                                               & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[2U] 
                                                                                >> 0x0fU))))))) 
                                                << 0x00000010U) 
                                               | (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[2U])))));
            if (((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_tap_in_bounds) 
                 & ((0x80U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[2U]) 
                    | (0x80U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[2U])))) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_bad_argument = 1U;
            }
            if (((1U & (IData)((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[2U] 
                                >> 0x20U))) != (1U 
                                                & (IData)(
                                                          (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[2U] 
                                                           >> 0x1fU))))) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_overflow = 1U;
            }
        } else {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[2U] = 0U;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[2U] = 0U;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[2U] = 0U;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[2U] = 0ULL;
        }
        if ((3U < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[3U] 
                = ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_tap_in_bounds)
                    ? ((0xc7ffU >= (0x0000ffffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index))
                        ? vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_patch
                       [(0x0000ffffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index)]
                        : 0U) : 0U);
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[3U] 
                = ((0x8fffU >= (0x0000ffffU & (((IData)(3U) 
                                                * vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_latched) 
                                               + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_reduction_index)))
                    ? vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_group
                   [(0x0000ffffU & (((IData)(3U) * vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_latched) 
                                    + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_reduction_index))]
                    : 0U);
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[3U] 
                = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                                   & ((- (IData)(
                                                                 (1U 
                                                                  & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[3U] 
                                                                     >> 7U)))) 
                                                      << 8U)) 
                                                  | vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[3U]), 
                                             ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[3U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[3U])));
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[3U] 
                = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                              (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[3U] 
                                                               >> 0x1fU))) 
                                              << 0x00000020U) 
                                             | (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[3U]))) 
                                            + (((QData)((IData)(
                                                                (0x0001ffffU 
                                                                 & (- (IData)(
                                                                              (1U 
                                                                               & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[3U] 
                                                                                >> 0x0fU))))))) 
                                                << 0x00000010U) 
                                               | (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[3U])))));
            if (((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_tap_in_bounds) 
                 & ((0x80U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[3U]) 
                    | (0x80U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[3U])))) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_bad_argument = 1U;
            }
            if (((1U & (IData)((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[3U] 
                                >> 0x20U))) != (1U 
                                                & (IData)(
                                                          (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[3U] 
                                                           >> 0x1fU))))) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_overflow = 1U;
            }
        } else {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[3U] = 0U;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[3U] = 0U;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[3U] = 0U;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[3U] = 0ULL;
        }
        if ((4U < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[4U] 
                = ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_tap_in_bounds)
                    ? ((0xc7ffU >= (0x0000ffffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index))
                        ? vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_patch
                       [(0x0000ffffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index)]
                        : 0U) : 0U);
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[4U] 
                = ((0x8fffU >= (0x0000ffffU & ((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_latched 
                                                << 2U) 
                                               + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_reduction_index)))
                    ? vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_group
                   [(0x0000ffffU & ((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_latched 
                                     << 2U) + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_reduction_index))]
                    : 0U);
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[4U] 
                = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                                   & ((- (IData)(
                                                                 (1U 
                                                                  & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[4U] 
                                                                     >> 7U)))) 
                                                      << 8U)) 
                                                  | vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[4U]), 
                                             ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[4U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[4U])));
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[4U] 
                = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                              (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[4U] 
                                                               >> 0x1fU))) 
                                              << 0x00000020U) 
                                             | (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[4U]))) 
                                            + (((QData)((IData)(
                                                                (0x0001ffffU 
                                                                 & (- (IData)(
                                                                              (1U 
                                                                               & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[4U] 
                                                                                >> 0x0fU))))))) 
                                                << 0x00000010U) 
                                               | (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[4U])))));
            if (((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_tap_in_bounds) 
                 & ((0x80U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[4U]) 
                    | (0x80U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[4U])))) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_bad_argument = 1U;
            }
            if (((1U & (IData)((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[4U] 
                                >> 0x20U))) != (1U 
                                                & (IData)(
                                                          (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[4U] 
                                                           >> 0x1fU))))) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_overflow = 1U;
            }
        } else {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[4U] = 0U;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[4U] = 0U;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[4U] = 0U;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[4U] = 0ULL;
        }
        if ((5U < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[5U] 
                = ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_tap_in_bounds)
                    ? ((0xc7ffU >= (0x0000ffffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index))
                        ? vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_patch
                       [(0x0000ffffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index)]
                        : 0U) : 0U);
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[5U] 
                = ((0x8fffU >= (0x0000ffffU & (((IData)(5U) 
                                                * vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_latched) 
                                               + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_reduction_index)))
                    ? vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_group
                   [(0x0000ffffU & (((IData)(5U) * vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_latched) 
                                    + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_reduction_index))]
                    : 0U);
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[5U] 
                = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                                   & ((- (IData)(
                                                                 (1U 
                                                                  & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[5U] 
                                                                     >> 7U)))) 
                                                      << 8U)) 
                                                  | vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[5U]), 
                                             ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[5U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[5U])));
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[5U] 
                = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                              (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[5U] 
                                                               >> 0x1fU))) 
                                              << 0x00000020U) 
                                             | (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[5U]))) 
                                            + (((QData)((IData)(
                                                                (0x0001ffffU 
                                                                 & (- (IData)(
                                                                              (1U 
                                                                               & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[5U] 
                                                                                >> 0x0fU))))))) 
                                                << 0x00000010U) 
                                               | (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[5U])))));
            if (((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_tap_in_bounds) 
                 & ((0x80U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[5U]) 
                    | (0x80U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[5U])))) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_bad_argument = 1U;
            }
            if (((1U & (IData)((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[5U] 
                                >> 0x20U))) != (1U 
                                                & (IData)(
                                                          (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[5U] 
                                                           >> 0x1fU))))) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_overflow = 1U;
            }
        } else {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[5U] = 0U;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[5U] = 0U;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[5U] = 0U;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[5U] = 0ULL;
        }
        if ((6U < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[6U] 
                = ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_tap_in_bounds)
                    ? ((0xc7ffU >= (0x0000ffffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index))
                        ? vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_patch
                       [(0x0000ffffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index)]
                        : 0U) : 0U);
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[6U] 
                = ((0x8fffU >= (0x0000ffffU & (((IData)(6U) 
                                                * vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_latched) 
                                               + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_reduction_index)))
                    ? vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_group
                   [(0x0000ffffU & (((IData)(6U) * vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_latched) 
                                    + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_reduction_index))]
                    : 0U);
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[6U] 
                = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                                   & ((- (IData)(
                                                                 (1U 
                                                                  & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[6U] 
                                                                     >> 7U)))) 
                                                      << 8U)) 
                                                  | vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[6U]), 
                                             ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[6U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[6U])));
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[6U] 
                = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                              (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[6U] 
                                                               >> 0x1fU))) 
                                              << 0x00000020U) 
                                             | (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[6U]))) 
                                            + (((QData)((IData)(
                                                                (0x0001ffffU 
                                                                 & (- (IData)(
                                                                              (1U 
                                                                               & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[6U] 
                                                                                >> 0x0fU))))))) 
                                                << 0x00000010U) 
                                               | (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[6U])))));
            if (((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_tap_in_bounds) 
                 & ((0x80U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[6U]) 
                    | (0x80U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[6U])))) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_bad_argument = 1U;
            }
            if (((1U & (IData)((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[6U] 
                                >> 0x20U))) != (1U 
                                                & (IData)(
                                                          (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[6U] 
                                                           >> 0x1fU))))) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_overflow = 1U;
            }
        } else {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[6U] = 0U;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[6U] = 0U;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[6U] = 0U;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[6U] = 0ULL;
        }
        if ((7U < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[7U] 
                = ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_tap_in_bounds)
                    ? ((0xc7ffU >= (0x0000ffffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index))
                        ? vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_patch
                       [(0x0000ffffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index)]
                        : 0U) : 0U);
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[7U] 
                = ((0x8fffU >= (0x0000ffffU & (((IData)(7U) 
                                                * vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_latched) 
                                               + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_reduction_index)))
                    ? vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_group
                   [(0x0000ffffU & (((IData)(7U) * vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_latched) 
                                    + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_reduction_index))]
                    : 0U);
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[7U] 
                = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                                   & ((- (IData)(
                                                                 (1U 
                                                                  & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[7U] 
                                                                     >> 7U)))) 
                                                      << 8U)) 
                                                  | vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[7U]), 
                                             ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[7U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[7U])));
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[7U] 
                = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                              (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[7U] 
                                                               >> 0x1fU))) 
                                              << 0x00000020U) 
                                             | (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[7U]))) 
                                            + (((QData)((IData)(
                                                                (0x0001ffffU 
                                                                 & (- (IData)(
                                                                              (1U 
                                                                               & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[7U] 
                                                                                >> 0x0fU))))))) 
                                                << 0x00000010U) 
                                               | (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[7U])))));
            if (((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_tap_in_bounds) 
                 & ((0x80U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[7U]) 
                    | (0x80U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[7U])))) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_bad_argument = 1U;
            }
            if (((1U & (IData)((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[7U] 
                                >> 0x20U))) != (1U 
                                                & (IData)(
                                                          (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[7U] 
                                                           >> 0x1fU))))) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_overflow = 1U;
            }
        } else {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[7U] = 0U;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[7U] = 0U;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[7U] = 0U;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[7U] = 0ULL;
        }
    }
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mapped_response_error = 6U;
    if ((0U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_error_latched))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mapped_response_error = 0U;
    } else if ((((1U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_error_latched)) 
                 | (2U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_error_latched))) 
                | (6U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_error_latched)))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mapped_response_error 
            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_error_latched;
    }
    if ((((3U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__state)) 
          & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_index 
             < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__patch_byte_count)) 
         & (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_in_bounds)))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_advance = 1U;
    } else if ((((5U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__state)) 
                 & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__backend_rsp_valid)) 
                & (0U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mapped_response_error)))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_advance = 1U;
    }
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid 
        = (((4U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
             ? ((~ ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                    >> 1U)) & ((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                                ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_valid)
                                : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_valid)))
             : (((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                 >> 1U) & ((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                            ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_valid)
                            : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_valid)))) 
           & ((~ ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_pending) 
                  | ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__hard_reset) 
                     | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__backend_abort)))) 
              & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__buffer_owner_pl)));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_plane_elements 
        = ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_h)) 
           * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_w)));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_batch_elements 
        = ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_c)) 
           * vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_plane_elements);
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_element_count 
        = ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_n)) 
           * vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_batch_elements);
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_y = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_x = 0U;
    if ((((0ULL != vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_plane_elements) 
          & (0ULL != vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_batch_elements)) 
         & (0U != (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_w)))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel 
            = (IData)(VL_MODDIV_QQQ(64, VL_DIV_QQQ(64, (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_element_index)), vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_plane_elements), (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_c))));
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_y 
            = (IData)(VL_MODDIV_QQQ(64, VL_DIV_QQQ(64, (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_element_index)), (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_w))), (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_h))));
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_x 
            = VL_MODDIV_III(32, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_element_index, (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_w));
    }
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_base[0U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_length[0U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_n[0U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_c[0U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_route_start[0U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_route_end[0U] = 0U;
    if ((0U < (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_input_count))) {
        if (((0U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor)) 
             & (~ (IData)(vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_KIND
                          [((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
                             ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor)
                             : 0U)][0U])))) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_base[0U] = 0U;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_length[0U] = 0x0007ec00U;
        } else {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_base[0U] 
                = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_ADDRESS
                [((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
                   ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor)
                   : 0U)][0U];
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_length[0U] 
                = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_LENGTH_BYTES
                [((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
                   ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor)
                   : 0U)][0U];
        }
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_n[0U] 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_N
            [((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
               ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor)
               : 0U)][0U];
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_c[0U] 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_C
            [((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
               ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor)
               : 0U)][0U];
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U] 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_H
            [((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
               ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor)
               : 0U)][0U];
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U] 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_W
            [((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
               ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor)
               : 0U)][0U];
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_route_start[0U] 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_ROUTE_CHANNEL_START
            [((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
               ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor)
               : 0U)][0U];
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_route_end[0U] 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_ROUTE_CHANNEL_END
            [((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
               ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor)
               : 0U)][0U];
    }
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_base[1U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_length[1U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_n[1U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_c[1U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[1U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[1U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_route_start[1U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_route_end[1U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mq_index 
        = (((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
             ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
            [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor]
             : 0U) + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel);
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__is_alias_row 
        = (4U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_op));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_valid = 0U;
    if (((((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__is_alias_row) 
           & (~ ((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor)) 
                 && vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_MEMORY_WRITE_REQUIRED
                 [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor]))) 
          & ((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor)) 
             && vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_ALLOCATION_KIND
             [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor])) 
         & (0x26U > (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index)))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_output_plane_elements 
            = ((QData)((IData)(((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index))
                                 ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_H
                                [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index]
                                 : 0U))) * (QData)((IData)(
                                                           ((0x25U 
                                                             >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index))
                                                             ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_W
                                                            [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index]
                                                             : 0U))));
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_output_element_count 
            = (((QData)((IData)(((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index))
                                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_N
                                 [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index]
                                  : 0U))) * (QData)((IData)(
                                                            ((0x25U 
                                                              >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index))
                                                              ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_C
                                                             [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index]
                                                              : 0U)))) 
               * vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_output_plane_elements);
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_valid 
            = ((((((((((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index))
                        ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_TENSOR_INDEX
                       [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index]
                        : 0U) == ((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
                                   ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_TENSOR_INDEX
                                  [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor]
                                   : 0U)) & (((0x25U 
                                               >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index))
                                               ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_ADDRESS
                                              [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index]
                                               : 0U) 
                                             == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_base)) 
                    & (((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index))
                         ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_LENGTH_BYTES
                        [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index]
                         : 0U) == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_length)) 
                   & (((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index))
                        ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_N
                       [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index]
                        : 0U) == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_n))) 
                  & (((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index))
                       ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_C
                      [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index]
                       : 0U) == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_c))) 
                 & (((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index))
                      ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_H
                     [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index]
                      : 0U) == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_h))) 
                & (((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index))
                     ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_W
                    [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index]
                     : 0U) == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_w))) 
               & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_output_element_count 
                  == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_element_count));
    } else {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_output_plane_elements = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_output_element_count = 0ULL;
    }
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__descriptor_valid = 1U;
    if ((((((((((((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
                   ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_LAYER_INDEX
                  [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor]
                   : 0U) != (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor)) 
                | (0U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_input_count))) 
               | (2U < (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_input_count))) 
              | (1U != (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_n))) 
             | (0U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_c))) 
            | (0U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_h))) 
           | (0U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_w))) 
          | (0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_length)) 
         | (0ULL == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_element_count))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__descriptor_valid = 0U;
    }
    if ((1U < (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_input_count))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_base[1U] 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_ADDRESS
            [((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
               ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor)
               : 0U)][1U];
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_length[1U] 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_LENGTH_BYTES
            [((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
               ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor)
               : 0U)][1U];
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_n[1U] 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_N
            [((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
               ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor)
               : 0U)][1U];
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_c[1U] 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_C
            [((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
               ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor)
               : 0U)][1U];
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[1U] 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_H
            [((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
               ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor)
               : 0U)][1U];
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[1U] 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_W
            [((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
               ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor)
               : 0U)][1U];
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_route_start[1U] 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_ROUTE_CHANNEL_START
            [((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
               ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor)
               : 0U)][1U];
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_route_end[1U] 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_ROUTE_CHANNEL_END
            [((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
               ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor)
               : 0U)][1U];
    }
    if ((0U < (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_input_count))) {
        if ((((((1U != vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_n[0U]) 
                | (0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_c[0U])) 
               | (0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U])) 
              | (0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U])) 
             | (0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_length[0U]))) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__descriptor_valid = 0U;
        }
        if (((~ (IData)(vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_KIND
                        [((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
                           ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor)
                           : 0U)][0U])) & (0U != (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor)))) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__descriptor_valid = 0U;
        }
    }
    if ((1U < (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_input_count))) {
        if ((((((1U != vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_n[1U]) 
                | (0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_c[1U])) 
               | (0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[1U])) 
              | (0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[1U])) 
             | (0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_length[1U]))) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__descriptor_valid = 0U;
        }
        if ((1U & (~ (IData)(vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_KIND
                             [((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
                                ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor)
                                : 0U)][1U])))) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__descriptor_valid = 0U;
        }
    }
    if (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__is_alias_row) {
        if ((1U & (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_valid)))) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__descriptor_valid = 0U;
        }
    } else if ((1U & ((~ ((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor)) 
                          && vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_MEMORY_WRITE_REQUIRED
                          [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor])) 
                      | ((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor)) 
                         && vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_ALLOCATION_KIND
                         [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor])))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__descriptor_valid = 0U;
    }
    if ((0U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_op))) {
        vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__map_conv_activation__96__descriptor_activation 
            = ((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_ACTIVATION
               [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor]
                : 0U);
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____VlemCall_0__map_conv_activation 
            = (3U & (0xd0U >> ((IData)(vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__map_conv_activation__96__descriptor_activation) 
                               << 1U)));
        if (((((((1U != (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_input_count)) 
                 | (((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
                      ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                     [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor]
                      : 0U) != (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_c))) 
                | (0x00000c5cU <= vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mq_index)) 
               | (0x00000c5cU < (((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
                                   ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                  [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor]
                                   : 0U) + ((0x25U 
                                             >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
                                             ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                                            [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor]
                                             : 0U)))) 
              | (3U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____VlemCall_0__map_conv_activation))) 
             | (((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_WEIGHT_LAYER_INDEX
                 [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor]
                  : 0U) != ((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
                             ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_LAYER_INDEX
                            [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor]
                             : 0U)))) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__descriptor_valid = 0U;
        }
    } else if (((1U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_op)) 
                | (3U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_op)))) {
        if ((1U != (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_input_count))) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__descriptor_valid = 0U;
        }
    } else if ((2U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_op))) {
        if (((1U != (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_input_count)) 
             & (2U != (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_input_count)))) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__descriptor_valid = 0U;
        }
    } else if ((1U & (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__is_alias_row)))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__descriptor_valid = 0U;
    }
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__descriptor_fault 
        = (1U & (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__descriptor_valid)));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_start_valid 
        = ((((1U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state)) 
             & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__buffer_owner_pl)) 
            & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__descriptor_valid)) 
           & (0U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_op)));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_start_valid 
        = ((((1U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state)) 
             & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__buffer_owner_pl)) 
            & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__descriptor_valid)) 
           & (1U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_op)));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_start_valid 
        = ((((1U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state)) 
             & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__buffer_owner_pl)) 
            & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__descriptor_valid)) 
           & (2U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_op)));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_start_valid 
        = ((((1U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state)) 
             & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__buffer_owner_pl)) 
            & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__descriptor_valid)) 
           & (3U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_op)));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_start_ready 
        = ((1U & (~ ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_op) 
                     >> 2U))) && ((2U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_op))
                                   ? ((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_op))
                                       ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__start_ready)
                                       : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__start_ready))
                                   : ((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_op))
                                       ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__start_ready)
                                       : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__start_ready))));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_rstrb 
        = (((4U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
             ? (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                  ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_rstrb)
                  : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_rstrb)) 
                & (- (IData)((1U & (~ ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                       >> 1U)))))) : 
            (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
               ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_rstrb)
               : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_rstrb)) 
             & (- (IData)((1U & ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                 >> 1U)))))) & (- (IData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid))));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_write 
        = (((4U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
             ? ((~ ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                    >> 1U)) & ((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                                ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_write)
                                : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_write)))
             : (((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                 >> 1U) & ((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                            ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_write)
                            : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_write)))) 
           & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid));
    __VdfgRegularize_h6e95ff9d_0_6[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_base;
    __VdfgRegularize_h6e95ff9d_0_6[1U] = 0U;
    __VdfgRegularize_h6e95ff9d_0_6[2U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__operator_result_valid = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__operator_error_code = 0U;
    if ((((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__hard_reset)) 
          & (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__backend_abort))) 
         & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__buffer_owner_pl))) {
        if ((4U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))) {
            if ((2U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__operator_result_valid = 1U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__operator_error_code = 6U;
            } else {
                vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__97__code 
                    = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_result_error;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____VlemCall_1__normalize_engine_error 
                    = ((4U & (IData)(vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__97__code))
                        ? (IData)(vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__97__code)
                        : ((2U & (IData)(vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__97__code))
                            ? (IData)(vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__97__code)
                            : ((1U & (IData)(vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__97__code))
                                ? (IData)(vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__97__code)
                                : 0U)));
                if (((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_result_valid) 
                     & (0U != (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____VlemCall_1__normalize_engine_error)))) {
                    vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__98__code 
                        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_result_error;
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__operator_result_valid = 1U;
                    vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__98__Vfuncout 
                        = ((4U & (IData)(vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__98__code))
                            ? (IData)(vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__98__code)
                            : ((2U & (IData)(vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__98__code))
                                ? (IData)(vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__98__code)
                                : ((1U & (IData)(vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__98__code))
                                    ? (IData)(vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__98__code)
                                    : 0U)));
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__operator_error_code 
                        = vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__98__Vfuncout;
                } else if ((((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_result_valid) 
                             & ((0U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_op)) 
                                | ((1ULL + (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_element_index))) 
                                   >= vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_element_count))) 
                            & (0x00000026U <= ((IData)(1U) 
                                               + (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))))) {
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__operator_result_valid = 1U;
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__operator_error_code = 0U;
                }
            }
        } else if ((2U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))) {
            vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__99__code 
                = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_result_error;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____VlemCall_1__normalize_engine_error 
                = ((4U & (IData)(vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__99__code))
                    ? (IData)(vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__99__code)
                    : ((2U & (IData)(vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__99__code))
                        ? (IData)(vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__99__code)
                        : ((1U & (IData)(vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__99__code))
                            ? (IData)(vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__99__code)
                            : 0U)));
            if (((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_result_valid) 
                 & (0U != (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____VlemCall_1__normalize_engine_error)))) {
                vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__100__code 
                    = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_result_error;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__operator_result_valid = 1U;
                vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__100__Vfuncout 
                    = ((4U & (IData)(vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__100__code))
                        ? (IData)(vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__100__code)
                        : ((2U & (IData)(vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__100__code))
                            ? (IData)(vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__100__code)
                            : ((1U & (IData)(vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__100__code))
                                ? (IData)(vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__100__code)
                                : 0U)));
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__operator_error_code 
                    = vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__100__Vfuncout;
            } else if ((((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_result_valid) 
                         & ((0U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_op)) 
                            | ((1ULL + (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_element_index))) 
                               >= vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_element_count))) 
                        & (0x00000026U <= ((IData)(1U) 
                                           + (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))))) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__operator_result_valid = 1U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__operator_error_code = 0U;
            }
        } else if ((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))) {
            if ((1U & ((((0x26U <= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor)) 
                         | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__descriptor_fault)) 
                        | ((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__is_alias_row)) 
                           & (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_start_ready)))) 
                       | ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__is_alias_row) 
                          & (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_valid)))))) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__operator_result_valid = 1U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__operator_error_code = 6U;
            } else if (((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__is_alias_row) 
                        & (0x00000026U <= ((IData)(1U) 
                                           + (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))))) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__operator_result_valid = 1U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__operator_error_code = 0U;
            }
        }
    }
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_inputs_valid 
        = ((9U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__layer_index)
            ? ((2U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_height) 
               & ((2U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width) 
                  & ((2U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_y) 
                     & ((2U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_x) 
                        & ((1U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__darknet_padding_parameter) 
                           & ((0x0080U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_c[0U]) 
                              & ((0x0068U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U]) 
                                 & ((0x0068U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U]) 
                                    & ((0x0080U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_c)) 
                                       & ((0x0034U 
                                           == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_h)) 
                                          & (0x0034U 
                                             == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_w))))))))))))
            : ((0x00000011U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__layer_index)
                ? ((2U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_height) 
                   & ((2U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width) 
                      & ((2U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_y) 
                         & ((2U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_x) 
                            & ((1U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__darknet_padding_parameter) 
                               & ((0x0100U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_c[0U]) 
                                  & ((0x0034U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U]) 
                                     & ((0x0034U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U]) 
                                        & ((0x0100U 
                                            == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_c)) 
                                           & ((0x001aU 
                                               == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_h)) 
                                              & (0x001aU 
                                                 == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_w))))))))))))
                : ((2U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_height) 
                   & ((2U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width) 
                      & ((2U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_y) 
                         & ((2U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_x) 
                            & ((1U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__darknet_padding_parameter) 
                               & ((0x00000019U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__layer_index) 
                                  & ((0x0200U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_c[0U]) 
                                     & ((0x001aU == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U]) 
                                        & ((0x001aU 
                                            == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U]) 
                                           & ((0x0200U 
                                               == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_c)) 
                                              & ((0x000dU 
                                                  == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_h)) 
                                                 & (0x000dU 
                                                    == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_w)))))))))))))));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__output_offset_work 
        = ((0x000000000000001aULL * ((0x000000000000001aULL 
                                      * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel))) 
                                     + (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_y)))) 
           + (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_x)));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_offset_work 
        = ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_x)) 
           + (((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_y)) 
               + ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel)) 
                  * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_h)))) 
              * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_w))));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__output_height_work = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__output_width_work = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__channel_row_work = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__row_work = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__byte_offset_work = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__plane_index_work = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__address_work[0U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__address_work[1U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__address_work[2U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_output_height = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_output_width = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_channel = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_y = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_x = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_address = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_unused_value = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_error_code = 0U;
    if (((((((0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_c[0U]) 
             | (0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U])) 
            | (0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U])) 
           | (0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_upsample_engine__stride)) 
          | (0x000dU < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U])) 
         | (0x000dU < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U]))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_error_code = 1U;
    } else {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__output_height_work 
            = ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U])) 
               * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_upsample_engine__stride)));
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__output_width_work 
            = ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U])) 
               * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_upsample_engine__stride)));
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_output_height 
            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__output_height_work;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_output_width 
            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__output_width_work;
        if ((((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel 
               >= vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_c[0U]) 
              | ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_y)) 
                 >= vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__output_height_work)) 
             | ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_x)) 
                >= vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__output_width_work))) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_error_code = 1U;
        } else {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_channel 
                = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_y 
                = VL_DIV_III(32, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_y, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_upsample_engine__stride);
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_x 
                = VL_DIV_III(32, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_x, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_upsample_engine__stride);
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__plane_index_work 
                = ((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_y 
                    * vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U]) 
                   + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_x);
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__channel_row_work 
                = ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel)) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U])));
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__row_work 
                = (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__channel_row_work 
                   + (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_y)));
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__byte_offset_work 
                = ((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__row_work 
                    * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U]))) 
                   + (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_x)));
            __Vtemp_82[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_base[0U];
            __Vtemp_82[1U] = 0U;
            __Vtemp_82[2U] = 0U;
            __Vtemp_83[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__byte_offset_work);
            __Vtemp_83[1U] = (IData)((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__byte_offset_work 
                                      >> 0x00000020U));
            __Vtemp_83[2U] = 0U;
            VL_ADD_W(3, __Vtemp_84, __Vtemp_82, __Vtemp_83);
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__address_work[0U] 
                = __Vtemp_84[0U];
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__address_work[1U] 
                = __Vtemp_84[1U];
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__address_work[2U] 
                = (1U & __Vtemp_84[2U]);
            if ((0ULL != (0x00000001ffffffffULL & (
                                                   ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__address_work[2U])) 
                                                    << 0x00000020U) 
                                                   | (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__address_work[1U])))))) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_error_code = 2U;
            } else {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_address 
                    = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__address_work[0U];
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_unused_value 
                    = ((0x0547U >= (0x000007ffU & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__plane_index_work 
                                                   << 3U)))
                        ? (0x000000ffU & (((0U == (0x0000001fU 
                                                   & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__plane_index_work 
                                                      << 3U)))
                                            ? 0U : 
                                           (Vtb_s2a_backend_fault_recovery__ConstPool__CONST_h3efedef1_0
                                            [(((IData)(7U) 
                                               + (0x000007ffU 
                                                  & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__plane_index_work 
                                                     << 3U))) 
                                              >> 5U)] 
                                            << ((IData)(0x00000020U) 
                                                - (0x0000001fU 
                                                   & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__plane_index_work 
                                                      << 3U))))) 
                                          | (Vtb_s2a_backend_fault_recovery__ConstPool__CONST_h3efedef1_0
                                             [(0x0000003fU 
                                               & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__plane_index_work 
                                                  >> 2U))] 
                                             >> (0x0000001fU 
                                                 & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__plane_index_work 
                                                    << 3U)))))
                        : 0U);
            }
        }
    }
    if ((0U != (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_error_code))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_output_height = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_output_width = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_channel = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_y = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_x = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_address = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_unused_value = 0U;
    }
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__extent_y 
        = (0x00000001ffffffffULL & ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U])) 
                                    + (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__darknet_padding_parameter))));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__extent_x 
        = (0x00000001ffffffffULL & ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U])) 
                                    + (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__darknet_padding_parameter))));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_height_work = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_width_work = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_y_step = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_x_step = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_y_work = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_x_work = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work[0U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work[1U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work[2U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work[0U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work[1U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work[2U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__tap_range_error = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_output_height = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_output_width = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_count = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_error_code = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__origin_y = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__origin_x = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[0U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[0U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[0U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[0U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[1U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[1U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[1U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[1U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[2U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[2U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[2U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[2U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[3U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[3U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[3U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[3U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[4U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[4U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[4U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[4U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[5U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[5U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[5U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[5U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[6U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[6U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[6U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[6U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[7U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[7U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[7U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[7U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[8U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[8U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[8U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[8U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__tap_index = 9U;
    if ((1U & ((((((~ (((2U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_height) 
                        & (2U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width)) 
                       | ((3U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_height) 
                          & (3U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width)))) 
                   | (0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_y)) 
                  | (0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_x)) 
                 | (0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_c[0U])) 
                | (0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U])) 
               | (0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U])))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_error_code = 1U;
    } else if (((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__extent_y 
                 < (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_height))) 
                | (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__extent_x 
                   < (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width))))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_error_code = 1U;
    } else {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_height_work 
            = (0x00000001ffffffffULL & (1ULL + VL_DIV_QQQ(33, 
                                                          (0x00000001ffffffffULL 
                                                           & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__extent_y 
                                                              - (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_height)))), (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_y)))));
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_width_work 
            = (0x00000001ffffffffULL & (1ULL + VL_DIV_QQQ(33, 
                                                          (0x00000001ffffffffULL 
                                                           & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__extent_x 
                                                              - (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width)))), (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_x)))));
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_output_height 
            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_height_work;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_output_width 
            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_width_work;
        if ((((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel 
               >= vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_c[0U]) 
              | ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_y)) 
                 >= vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_height_work)) 
             | ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_x)) 
                >= vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_width_work))) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_error_code = 1U;
        } else {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_count 
                = ((2U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_height)
                    ? 4U : 9U);
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__origin_y 
                = (- VL_EXTENDS_QQ(64,63, (QData)((IData)(
                                                          (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__darknet_padding_parameter 
                                                           >> 1U)))));
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__origin_x 
                = (- VL_EXTENDS_QQ(64,63, (QData)((IData)(
                                                          (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__darknet_padding_parameter 
                                                           >> 1U)))));
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_y_step 
                = ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_y)) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_y)));
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_x_step 
                = ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_x)) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_x)));
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_y_work 
                = (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__origin_y 
                   + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_y_step);
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_x_work 
                = (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__origin_x 
                   + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_x_step);
            if ((0U < (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_count))) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work 
                    = VL_MODDIV_III(32, (IData)(0U), vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width);
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work = 0U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[0U] 
                    = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[0U] 
                    = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_y_work;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[0U] 
                    = (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_x_work 
                       + VL_EXTENDS_QI(64,32, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work));
                if ((((VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[0U]) 
                       & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[0U], (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U])))) 
                      & VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[0U])) 
                     & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[0U], (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U]))))) {
                    __Vtemp_85[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel;
                    __Vtemp_85[1U] = 0U;
                    __Vtemp_85[2U] = 0U;
                    __Vtemp_86[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U];
                    __Vtemp_86[1U] = 0U;
                    __Vtemp_86[2U] = 0U;
                    VL_MUL_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_85, __Vtemp_86);
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask 
                        = (1U | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask));
                    __Vtemp_87[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[0U]);
                    __Vtemp_87[1U] = 0U;
                    __Vtemp_87[2U] = 0U;
                    VL_ADD_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_87);
                    __Vtemp_88[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U];
                    __Vtemp_88[1U] = 0U;
                    __Vtemp_88[2U] = 0U;
                    VL_MUL_W(3, __Vtemp_89, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, __Vtemp_88);
                    __Vtemp_90[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[0U]);
                    __Vtemp_90[1U] = 0U;
                    __Vtemp_90[2U] = 0U;
                    VL_ADD_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, __Vtemp_89, __Vtemp_90);
                    __Vtemp_92[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_base[0U];
                    __Vtemp_92[1U] = 0U;
                    __Vtemp_92[2U] = 0U;
                    __Vtemp_92[3U] = 0U;
                    __Vtemp_93[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U];
                    __Vtemp_93[1U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U];
                    __Vtemp_93[2U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U];
                    __Vtemp_93[3U] = 0U;
                    VL_ADD_W(4, __Vtemp_94, __Vtemp_92, __Vtemp_93);
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U] 
                        = __Vtemp_94[0U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                        = __Vtemp_94[1U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U] 
                        = __Vtemp_94[2U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U] 
                        = (1U & __Vtemp_94[3U]);
                    if ((0U != ((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                                 | vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U]) 
                                | (1U & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U])))) {
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__tap_range_error = 1U;
                    } else {
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[0U] 
                            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U];
                    }
                }
            }
            if ((1U < (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_count))) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work 
                    = VL_DIV_III(32, (IData)(1U), vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width);
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work 
                    = VL_MODDIV_III(32, (IData)(1U), vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width);
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[1U] 
                    = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[1U] 
                    = (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_y_work 
                       + VL_EXTENDS_QI(64,32, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work));
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[1U] 
                    = (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_x_work 
                       + VL_EXTENDS_QI(64,32, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work));
                if ((((VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[1U]) 
                       & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[1U], (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U])))) 
                      & VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[1U])) 
                     & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[1U], (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U]))))) {
                    __Vtemp_99[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel;
                    __Vtemp_99[1U] = 0U;
                    __Vtemp_99[2U] = 0U;
                    __Vtemp_100[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U];
                    __Vtemp_100[1U] = 0U;
                    __Vtemp_100[2U] = 0U;
                    VL_MUL_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_99, __Vtemp_100);
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask 
                        = (2U | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask));
                    __Vtemp_101[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[1U]);
                    __Vtemp_101[1U] = 0U;
                    __Vtemp_101[2U] = 0U;
                    VL_ADD_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_101);
                    __Vtemp_102[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U];
                    __Vtemp_102[1U] = 0U;
                    __Vtemp_102[2U] = 0U;
                    VL_MUL_W(3, __Vtemp_103, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, __Vtemp_102);
                    __Vtemp_104[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[1U]);
                    __Vtemp_104[1U] = 0U;
                    __Vtemp_104[2U] = 0U;
                    VL_ADD_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, __Vtemp_103, __Vtemp_104);
                    __Vtemp_106[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_base[0U];
                    __Vtemp_106[1U] = 0U;
                    __Vtemp_106[2U] = 0U;
                    __Vtemp_106[3U] = 0U;
                    __Vtemp_107[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U];
                    __Vtemp_107[1U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U];
                    __Vtemp_107[2U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U];
                    __Vtemp_107[3U] = 0U;
                    VL_ADD_W(4, __Vtemp_108, __Vtemp_106, __Vtemp_107);
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U] 
                        = __Vtemp_108[0U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                        = __Vtemp_108[1U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U] 
                        = __Vtemp_108[2U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U] 
                        = (1U & __Vtemp_108[3U]);
                    if ((0U != ((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                                 | vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U]) 
                                | (1U & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U])))) {
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__tap_range_error = 1U;
                    } else {
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[1U] 
                            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U];
                    }
                }
            }
            if ((2U < (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_count))) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work 
                    = VL_DIV_III(32, (IData)(2U), vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width);
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work 
                    = VL_MODDIV_III(32, (IData)(2U), vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width);
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[2U] 
                    = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[2U] 
                    = (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_y_work 
                       + VL_EXTENDS_QI(64,32, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work));
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[2U] 
                    = (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_x_work 
                       + VL_EXTENDS_QI(64,32, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work));
                if ((((VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[2U]) 
                       & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[2U], (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U])))) 
                      & VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[2U])) 
                     & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[2U], (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U]))))) {
                    __Vtemp_113[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel;
                    __Vtemp_113[1U] = 0U;
                    __Vtemp_113[2U] = 0U;
                    __Vtemp_114[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U];
                    __Vtemp_114[1U] = 0U;
                    __Vtemp_114[2U] = 0U;
                    VL_MUL_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_113, __Vtemp_114);
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask 
                        = (4U | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask));
                    __Vtemp_115[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[2U]);
                    __Vtemp_115[1U] = 0U;
                    __Vtemp_115[2U] = 0U;
                    VL_ADD_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_115);
                    __Vtemp_116[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U];
                    __Vtemp_116[1U] = 0U;
                    __Vtemp_116[2U] = 0U;
                    VL_MUL_W(3, __Vtemp_117, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, __Vtemp_116);
                    __Vtemp_118[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[2U]);
                    __Vtemp_118[1U] = 0U;
                    __Vtemp_118[2U] = 0U;
                    VL_ADD_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, __Vtemp_117, __Vtemp_118);
                    __Vtemp_120[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_base[0U];
                    __Vtemp_120[1U] = 0U;
                    __Vtemp_120[2U] = 0U;
                    __Vtemp_120[3U] = 0U;
                    __Vtemp_121[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U];
                    __Vtemp_121[1U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U];
                    __Vtemp_121[2U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U];
                    __Vtemp_121[3U] = 0U;
                    VL_ADD_W(4, __Vtemp_122, __Vtemp_120, __Vtemp_121);
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U] 
                        = __Vtemp_122[0U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                        = __Vtemp_122[1U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U] 
                        = __Vtemp_122[2U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U] 
                        = (1U & __Vtemp_122[3U]);
                    if ((0U != ((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                                 | vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U]) 
                                | (1U & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U])))) {
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__tap_range_error = 1U;
                    } else {
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[2U] 
                            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U];
                    }
                }
            }
            if ((3U < (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_count))) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work 
                    = VL_DIV_III(32, (IData)(3U), vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width);
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work 
                    = VL_MODDIV_III(32, (IData)(3U), vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width);
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[3U] 
                    = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[3U] 
                    = (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_y_work 
                       + VL_EXTENDS_QI(64,32, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work));
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[3U] 
                    = (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_x_work 
                       + VL_EXTENDS_QI(64,32, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work));
                if ((((VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[3U]) 
                       & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[3U], (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U])))) 
                      & VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[3U])) 
                     & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[3U], (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U]))))) {
                    __Vtemp_127[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel;
                    __Vtemp_127[1U] = 0U;
                    __Vtemp_127[2U] = 0U;
                    __Vtemp_128[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U];
                    __Vtemp_128[1U] = 0U;
                    __Vtemp_128[2U] = 0U;
                    VL_MUL_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_127, __Vtemp_128);
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask 
                        = (8U | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask));
                    __Vtemp_129[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[3U]);
                    __Vtemp_129[1U] = 0U;
                    __Vtemp_129[2U] = 0U;
                    VL_ADD_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_129);
                    __Vtemp_130[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U];
                    __Vtemp_130[1U] = 0U;
                    __Vtemp_130[2U] = 0U;
                    VL_MUL_W(3, __Vtemp_131, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, __Vtemp_130);
                    __Vtemp_132[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[3U]);
                    __Vtemp_132[1U] = 0U;
                    __Vtemp_132[2U] = 0U;
                    VL_ADD_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, __Vtemp_131, __Vtemp_132);
                    __Vtemp_134[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_base[0U];
                    __Vtemp_134[1U] = 0U;
                    __Vtemp_134[2U] = 0U;
                    __Vtemp_134[3U] = 0U;
                    __Vtemp_135[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U];
                    __Vtemp_135[1U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U];
                    __Vtemp_135[2U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U];
                    __Vtemp_135[3U] = 0U;
                    VL_ADD_W(4, __Vtemp_136, __Vtemp_134, __Vtemp_135);
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U] 
                        = __Vtemp_136[0U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                        = __Vtemp_136[1U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U] 
                        = __Vtemp_136[2U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U] 
                        = (1U & __Vtemp_136[3U]);
                    if ((0U != ((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                                 | vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U]) 
                                | (1U & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U])))) {
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__tap_range_error = 1U;
                    } else {
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[3U] 
                            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U];
                    }
                }
            }
            if ((4U < (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_count))) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work 
                    = VL_DIV_III(32, (IData)(4U), vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width);
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work 
                    = VL_MODDIV_III(32, (IData)(4U), vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width);
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[4U] 
                    = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[4U] 
                    = (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_y_work 
                       + VL_EXTENDS_QI(64,32, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work));
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[4U] 
                    = (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_x_work 
                       + VL_EXTENDS_QI(64,32, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work));
                if ((((VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[4U]) 
                       & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[4U], (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U])))) 
                      & VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[4U])) 
                     & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[4U], (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U]))))) {
                    __Vtemp_141[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel;
                    __Vtemp_141[1U] = 0U;
                    __Vtemp_141[2U] = 0U;
                    __Vtemp_142[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U];
                    __Vtemp_142[1U] = 0U;
                    __Vtemp_142[2U] = 0U;
                    VL_MUL_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_141, __Vtemp_142);
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask 
                        = (0x00000010U | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask));
                    __Vtemp_143[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[4U]);
                    __Vtemp_143[1U] = 0U;
                    __Vtemp_143[2U] = 0U;
                    VL_ADD_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_143);
                    __Vtemp_144[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U];
                    __Vtemp_144[1U] = 0U;
                    __Vtemp_144[2U] = 0U;
                    VL_MUL_W(3, __Vtemp_145, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, __Vtemp_144);
                    __Vtemp_146[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[4U]);
                    __Vtemp_146[1U] = 0U;
                    __Vtemp_146[2U] = 0U;
                    VL_ADD_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, __Vtemp_145, __Vtemp_146);
                    __Vtemp_148[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_base[0U];
                    __Vtemp_148[1U] = 0U;
                    __Vtemp_148[2U] = 0U;
                    __Vtemp_148[3U] = 0U;
                    __Vtemp_149[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U];
                    __Vtemp_149[1U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U];
                    __Vtemp_149[2U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U];
                    __Vtemp_149[3U] = 0U;
                    VL_ADD_W(4, __Vtemp_150, __Vtemp_148, __Vtemp_149);
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U] 
                        = __Vtemp_150[0U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                        = __Vtemp_150[1U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U] 
                        = __Vtemp_150[2U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U] 
                        = (1U & __Vtemp_150[3U]);
                    if ((0U != ((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                                 | vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U]) 
                                | (1U & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U])))) {
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__tap_range_error = 1U;
                    } else {
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[4U] 
                            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U];
                    }
                }
            }
            if ((5U < (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_count))) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work 
                    = VL_DIV_III(32, (IData)(5U), vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width);
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work 
                    = VL_MODDIV_III(32, (IData)(5U), vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width);
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[5U] 
                    = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[5U] 
                    = (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_y_work 
                       + VL_EXTENDS_QI(64,32, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work));
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[5U] 
                    = (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_x_work 
                       + VL_EXTENDS_QI(64,32, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work));
                if ((((VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[5U]) 
                       & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[5U], (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U])))) 
                      & VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[5U])) 
                     & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[5U], (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U]))))) {
                    __Vtemp_155[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel;
                    __Vtemp_155[1U] = 0U;
                    __Vtemp_155[2U] = 0U;
                    __Vtemp_156[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U];
                    __Vtemp_156[1U] = 0U;
                    __Vtemp_156[2U] = 0U;
                    VL_MUL_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_155, __Vtemp_156);
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask 
                        = (0x00000020U | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask));
                    __Vtemp_157[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[5U]);
                    __Vtemp_157[1U] = 0U;
                    __Vtemp_157[2U] = 0U;
                    VL_ADD_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_157);
                    __Vtemp_158[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U];
                    __Vtemp_158[1U] = 0U;
                    __Vtemp_158[2U] = 0U;
                    VL_MUL_W(3, __Vtemp_159, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, __Vtemp_158);
                    __Vtemp_160[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[5U]);
                    __Vtemp_160[1U] = 0U;
                    __Vtemp_160[2U] = 0U;
                    VL_ADD_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, __Vtemp_159, __Vtemp_160);
                    __Vtemp_162[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_base[0U];
                    __Vtemp_162[1U] = 0U;
                    __Vtemp_162[2U] = 0U;
                    __Vtemp_162[3U] = 0U;
                    __Vtemp_163[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U];
                    __Vtemp_163[1U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U];
                    __Vtemp_163[2U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U];
                    __Vtemp_163[3U] = 0U;
                    VL_ADD_W(4, __Vtemp_164, __Vtemp_162, __Vtemp_163);
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U] 
                        = __Vtemp_164[0U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                        = __Vtemp_164[1U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U] 
                        = __Vtemp_164[2U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U] 
                        = (1U & __Vtemp_164[3U]);
                    if ((0U != ((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                                 | vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U]) 
                                | (1U & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U])))) {
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__tap_range_error = 1U;
                    } else {
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[5U] 
                            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U];
                    }
                }
            }
            if ((6U < (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_count))) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work 
                    = VL_DIV_III(32, (IData)(6U), vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width);
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work 
                    = VL_MODDIV_III(32, (IData)(6U), vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width);
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[6U] 
                    = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[6U] 
                    = (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_y_work 
                       + VL_EXTENDS_QI(64,32, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work));
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[6U] 
                    = (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_x_work 
                       + VL_EXTENDS_QI(64,32, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work));
                if ((((VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[6U]) 
                       & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[6U], (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U])))) 
                      & VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[6U])) 
                     & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[6U], (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U]))))) {
                    __Vtemp_169[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel;
                    __Vtemp_169[1U] = 0U;
                    __Vtemp_169[2U] = 0U;
                    __Vtemp_170[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U];
                    __Vtemp_170[1U] = 0U;
                    __Vtemp_170[2U] = 0U;
                    VL_MUL_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_169, __Vtemp_170);
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask 
                        = (0x00000040U | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask));
                    __Vtemp_171[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[6U]);
                    __Vtemp_171[1U] = 0U;
                    __Vtemp_171[2U] = 0U;
                    VL_ADD_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_171);
                    __Vtemp_172[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U];
                    __Vtemp_172[1U] = 0U;
                    __Vtemp_172[2U] = 0U;
                    VL_MUL_W(3, __Vtemp_173, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, __Vtemp_172);
                    __Vtemp_174[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[6U]);
                    __Vtemp_174[1U] = 0U;
                    __Vtemp_174[2U] = 0U;
                    VL_ADD_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, __Vtemp_173, __Vtemp_174);
                    __Vtemp_176[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_base[0U];
                    __Vtemp_176[1U] = 0U;
                    __Vtemp_176[2U] = 0U;
                    __Vtemp_176[3U] = 0U;
                    __Vtemp_177[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U];
                    __Vtemp_177[1U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U];
                    __Vtemp_177[2U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U];
                    __Vtemp_177[3U] = 0U;
                    VL_ADD_W(4, __Vtemp_178, __Vtemp_176, __Vtemp_177);
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U] 
                        = __Vtemp_178[0U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                        = __Vtemp_178[1U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U] 
                        = __Vtemp_178[2U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U] 
                        = (1U & __Vtemp_178[3U]);
                    if ((0U != ((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                                 | vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U]) 
                                | (1U & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U])))) {
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__tap_range_error = 1U;
                    } else {
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[6U] 
                            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U];
                    }
                }
            }
            if ((7U < (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_count))) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work 
                    = VL_DIV_III(32, (IData)(7U), vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width);
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work 
                    = VL_MODDIV_III(32, (IData)(7U), vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width);
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[7U] 
                    = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[7U] 
                    = (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_y_work 
                       + VL_EXTENDS_QI(64,32, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work));
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[7U] 
                    = (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_x_work 
                       + VL_EXTENDS_QI(64,32, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work));
                if ((((VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[7U]) 
                       & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[7U], (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U])))) 
                      & VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[7U])) 
                     & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[7U], (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U]))))) {
                    __Vtemp_183[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel;
                    __Vtemp_183[1U] = 0U;
                    __Vtemp_183[2U] = 0U;
                    __Vtemp_184[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U];
                    __Vtemp_184[1U] = 0U;
                    __Vtemp_184[2U] = 0U;
                    VL_MUL_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_183, __Vtemp_184);
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask 
                        = (0x00000080U | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask));
                    __Vtemp_185[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[7U]);
                    __Vtemp_185[1U] = 0U;
                    __Vtemp_185[2U] = 0U;
                    VL_ADD_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_185);
                    __Vtemp_186[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U];
                    __Vtemp_186[1U] = 0U;
                    __Vtemp_186[2U] = 0U;
                    VL_MUL_W(3, __Vtemp_187, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, __Vtemp_186);
                    __Vtemp_188[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[7U]);
                    __Vtemp_188[1U] = 0U;
                    __Vtemp_188[2U] = 0U;
                    VL_ADD_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, __Vtemp_187, __Vtemp_188);
                    __Vtemp_190[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_base[0U];
                    __Vtemp_190[1U] = 0U;
                    __Vtemp_190[2U] = 0U;
                    __Vtemp_190[3U] = 0U;
                    __Vtemp_191[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U];
                    __Vtemp_191[1U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U];
                    __Vtemp_191[2U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U];
                    __Vtemp_191[3U] = 0U;
                    VL_ADD_W(4, __Vtemp_192, __Vtemp_190, __Vtemp_191);
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U] 
                        = __Vtemp_192[0U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                        = __Vtemp_192[1U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U] 
                        = __Vtemp_192[2U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U] 
                        = (1U & __Vtemp_192[3U]);
                    if ((0U != ((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                                 | vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U]) 
                                | (1U & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U])))) {
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__tap_range_error = 1U;
                    } else {
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[7U] 
                            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U];
                    }
                }
            }
            if ((8U < (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_count))) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work 
                    = VL_DIV_III(32, (IData)(8U), vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width);
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work 
                    = VL_MODDIV_III(32, (IData)(8U), vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width);
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[8U] 
                    = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[8U] 
                    = (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_y_work 
                       + VL_EXTENDS_QI(64,32, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work));
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[8U] 
                    = (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_x_work 
                       + VL_EXTENDS_QI(64,32, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work));
                if ((((VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[8U]) 
                       & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[8U], (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U])))) 
                      & VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[8U])) 
                     & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[8U], (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U]))))) {
                    __Vtemp_197[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel;
                    __Vtemp_197[1U] = 0U;
                    __Vtemp_197[2U] = 0U;
                    __Vtemp_198[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U];
                    __Vtemp_198[1U] = 0U;
                    __Vtemp_198[2U] = 0U;
                    VL_MUL_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_197, __Vtemp_198);
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask 
                        = (0x00000100U | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask));
                    __Vtemp_199[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[8U]);
                    __Vtemp_199[1U] = 0U;
                    __Vtemp_199[2U] = 0U;
                    VL_ADD_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_199);
                    __Vtemp_200[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U];
                    __Vtemp_200[1U] = 0U;
                    __Vtemp_200[2U] = 0U;
                    VL_MUL_W(3, __Vtemp_201, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, __Vtemp_200);
                    __Vtemp_202[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[8U]);
                    __Vtemp_202[1U] = 0U;
                    __Vtemp_202[2U] = 0U;
                    VL_ADD_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, __Vtemp_201, __Vtemp_202);
                    __Vtemp_204[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_base[0U];
                    __Vtemp_204[1U] = 0U;
                    __Vtemp_204[2U] = 0U;
                    __Vtemp_204[3U] = 0U;
                    __Vtemp_205[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U];
                    __Vtemp_205[1U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U];
                    __Vtemp_205[2U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U];
                    __Vtemp_205[3U] = 0U;
                    VL_ADD_W(4, __Vtemp_206, __Vtemp_204, __Vtemp_205);
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U] 
                        = __Vtemp_206[0U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                        = __Vtemp_206[1U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U] 
                        = __Vtemp_206[2U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U] 
                        = (1U & __Vtemp_206[3U]);
                    if ((0U != ((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                                 | vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U]) 
                                | (1U & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U])))) {
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__tap_range_error = 1U;
                    } else {
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[8U] 
                            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U];
                    }
                }
            }
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__tap_index = 9U;
            if (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__tap_range_error) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_error_code = 2U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_output_height = 0ULL;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_output_width = 0ULL;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_count = 0U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask = 0U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[0U] = 0U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[0U] = 0U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[0U] = 0ULL;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[0U] = 0ULL;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__tap_index = 9U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[1U] = 0U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[1U] = 0U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[1U] = 0ULL;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[1U] = 0ULL;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[2U] = 0U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[2U] = 0U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[2U] = 0ULL;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[2U] = 0ULL;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[3U] = 0U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[3U] = 0U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[3U] = 0ULL;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[3U] = 0ULL;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[4U] = 0U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[4U] = 0U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[4U] = 0ULL;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[4U] = 0ULL;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[5U] = 0U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[5U] = 0U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[5U] = 0ULL;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[5U] = 0ULL;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[6U] = 0U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[6U] = 0U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[6U] = 0ULL;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[6U] = 0ULL;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[7U] = 0U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[7U] = 0U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[7U] = 0ULL;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[7U] = 0ULL;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[8U] = 0U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[8U] = 0U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[8U] = 0ULL;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[8U] = 0ULL;
            }
        }
    }
    if ((1U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_error_code))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_output_height = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_output_width = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_count = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[0U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[0U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[0U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[0U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__tap_index = 9U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[1U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[1U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[1U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[1U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[2U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[2U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[2U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[2U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[3U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[3U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[3U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[3U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[4U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[4U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[4U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[4U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[5U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[5U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[5U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[5U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[6U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[6U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[6U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[6U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[7U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[7U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[7U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[7U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[8U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[8U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[8U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[8U] = 0ULL;
    }
    __VdfgRegularize_h6e95ff9d_0_5 = ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__automatic_read_responses) 
                                      & ((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_write)) 
                                         & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid)));
    __Vtemp_212[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__output_offset_work);
    __Vtemp_212[1U] = (IData)((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__output_offset_work 
                               >> 0x00000020U));
    __Vtemp_212[2U] = 0U;
    VL_ADD_W(3, __Vtemp_213, __Vtemp_212, __VdfgRegularize_h6e95ff9d_0_6);
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__output_address_work[0U] 
        = __Vtemp_213[0U];
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__output_address_work[1U] 
        = __Vtemp_213[1U];
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__output_address_work[2U] 
        = (1U & __Vtemp_213[2U]);
    __Vtemp_215[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_offset_work);
    __Vtemp_215[1U] = (IData)((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_offset_work 
                               >> 0x00000020U));
    __Vtemp_215[2U] = 0U;
    VL_ADD_W(3, __Vtemp_216, __Vtemp_215, __VdfgRegularize_h6e95ff9d_0_6);
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_address_work[0U] 
        = __Vtemp_216[0U];
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_address_work[1U] 
        = __Vtemp_216[1U];
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_address_work[2U] 
        = (1U & __Vtemp_216[2U]);
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__backend_memory_error_code 
        = ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__manual_mem_error_code) 
           & (- (IData)((1U & (~ (IData)(__VdfgRegularize_h6e95ff9d_0_5))))));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_ready 
        = ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__manual_mem_ready) 
           | (IData)(__VdfgRegularize_h6e95ff9d_0_5));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__memory_handshake 
        = ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_ready) 
           & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__backend_req_ready 
        = ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid) 
           & ((3U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state)) 
              & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_ready)));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__backend_req_ready 
        = ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid) 
           & ((5U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state)) 
              & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_ready)));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__backend_req_ready 
        = ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid) 
           & ((4U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state)) 
              & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_ready)));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__backend_req_ready 
        = ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid) 
           & ((2U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state)) 
              & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_ready)));
}

VL_ATTR_COLD bool Vtb_s2a_backend_fault_recovery___024root___eval_phase__stl(Vtb_s2a_backend_fault_recovery___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root___eval_phase__stl\n"); );
    Vtb_s2a_backend_fault_recovery__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
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
        Vtb_s2a_backend_fault_recovery___024root___dump_triggers__stl(vlSelfRef.__VstlTriggered, "stl"s);
    }
#endif
    __VstlExecute = Vtb_s2a_backend_fault_recovery___024root___trigger_anySet__stl(vlSelfRef.__VstlTriggered);
    if (__VstlExecute) {
        {
            // Inlined CFunc: _eval_stl
            if ((1ULL & vlSelfRef.__VstlTriggered[0U])) {
                Vtb_s2a_backend_fault_recovery___024root___stl_sequent__TOP__0(vlSelf);
                {
                    // Inlined CFunc: __Vm_traceActivitySetAll
                    vlSelfRef.__Vm_traceActivity[0U] = 1U;
                    vlSelfRef.__Vm_traceActivity[1U] = 1U;
                    vlSelfRef.__Vm_traceActivity[2U] = 1U;
                    vlSelfRef.__Vm_traceActivity[3U] = 1U;
                    vlSelfRef.__Vm_traceActivity[4U] = 1U;
                    vlSelfRef.__Vm_traceActivity[5U] = 1U;
                    vlSelfRef.__Vm_traceActivity[6U] = 1U;
                }
            }
        }
    }
    return (__VstlExecute);
}

bool Vtb_s2a_backend_fault_recovery___024root___trigger_anySet__act(const VlUnpacked<QData/*63:0*/, 1> &in);

#ifdef VL_DEBUG
VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root___dump_triggers__act(const VlUnpacked<QData/*63:0*/, 1> &triggers, const std::string &tag) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root___dump_triggers__act\n"); );
    // Body
    if ((1U & (~ (IData)(Vtb_s2a_backend_fault_recovery___024root___trigger_anySet__act(triggers))))) {
        VL_DBG_MSGS("         No '" + tag + "' region triggers active\n");
    }
    if ((1U & (IData)(triggers[0U]))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 0 is active: @(posedge tb_s2a_backend_fault_recovery.clk)\n");
    }
    if ((1U & (IData)((triggers[0U] >> 1U)))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 1 is active: @([true] __VdlySched.awaitingCurrentTime())\n");
    }
    if ((1U & (IData)((triggers[0U] >> 2U)))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 2 is active: @(negedge tb_s2a_backend_fault_recovery.clk)\n");
    }
}
#endif  // VL_DEBUG

VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root___ctor_var_reset(Vtb_s2a_backend_fault_recovery___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root___ctor_var_reset\n"); );
    Vtb_s2a_backend_fault_recovery__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    const uint64_t __VscopeHash = VL_MURMUR64_HASH(vlSelf->vlNamep);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__csr_rdata = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2230028280195105455ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__operator_result_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 945301752331004765ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__operator_error_code = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 11692968540694261182ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__backend_start = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 3176038329200163404ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__backend_abort = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 5129139845124539287ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__busy = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 5563873840561047714ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__done = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 8606140970590962076ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__error = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 14407988617970081033ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__buffer_owner_pl = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 9675798143390124455ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__head_output_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 562491892733068062ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__mem_addr = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7974895254378462070ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__mem_wdata = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2331095788742164053ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 5876964700479532046ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_write = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 2372243047793947668ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_rstrb = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 1671416424037619221ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 15124111888772947407ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 6929541213646511396ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor = VL_SCOPED_RAND_RESET_I(6, __VscopeHash, 12418690731688588229ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_element_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10378220872242979612ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_pending = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 4356114394098153102ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_data_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14138369589800938252ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_error_latched = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 15023162897935931225ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_target_latched = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 6103600619472446435ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_op = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 1981781129754157272ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_input_count = VL_SCOPED_RAND_RESET_I(2, __VscopeHash, 15971875220833428969ull);
    for (int __Vi0 = 0; __Vi0 < 2; ++__Vi0) {
        vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_base[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10696046464258251441ull);
    }
    for (int __Vi0 = 0; __Vi0 < 2; ++__Vi0) {
        vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_length[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12673035177295869388ull);
    }
    for (int __Vi0 = 0; __Vi0 < 2; ++__Vi0) {
        vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_n[__Vi0] = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 4923501871272053294ull);
    }
    for (int __Vi0 = 0; __Vi0 < 2; ++__Vi0) {
        vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_c[__Vi0] = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 13630791466133379585ull);
    }
    for (int __Vi0 = 0; __Vi0 < 2; ++__Vi0) {
        vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[__Vi0] = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 1672217636180682817ull);
    }
    for (int __Vi0 = 0; __Vi0 < 2; ++__Vi0) {
        vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[__Vi0] = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 15383825631150592266ull);
    }
    for (int __Vi0 = 0; __Vi0 < 2; ++__Vi0) {
        vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_route_start[__Vi0] = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 16619958615751354390ull);
    }
    for (int __Vi0 = 0; __Vi0 < 2; ++__Vi0) {
        vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_route_end[__Vi0] = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 2561033619220680738ull);
    }
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_base = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14275611418570326880ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_length = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4143518257627048993ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_n = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 3016623861465507936ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_c = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 3369245796181925565ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_h = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 4925708171328460836ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_w = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 8083731816234480446ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_plane_elements = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 14694336342803292289ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_batch_elements = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 5162968265888288843ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_element_count = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 6447386311533511642ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15633667865251584457ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9038848498597286723ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11749145933923542803ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mq_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3732396142017517581ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__descriptor_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 12032544482352340787ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 9596929237935897034ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__descriptor_fault = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 2237009001221084107ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__is_alias_row = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 16223479264518327644ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index = VL_SCOPED_RAND_RESET_I(6, __VscopeHash, 18365111187487389015ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_output_plane_elements = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 4022509322805309150ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_output_element_count = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 10410837099994675535ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_start_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 13691589597108600580ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_start_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 4729156392934882375ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_start_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 14021783555692816506ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_start_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 14083663309048253921ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 17546916403564528868ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_write = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 12267397678645882895ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_rstrb = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 8773463534061263394ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_wstrb = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 16028384677110952104ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 2417352509182736376ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_write = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 15591752420571796515ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_addr = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12536134877316766536ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_wdata = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17445436809990391131ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_rstrb = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 13470252530901313514ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_wstrb = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 3491664911602724203ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 7845180572915227611ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_write = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 16194229338941156105ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_addr = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5649039786893600306ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_wdata = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1510177380331931022ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_rstrb = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 5901188202723286744ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_wstrb = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 8165321221120739988ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 2414866530499944642ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_write = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 8529834521356206496ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_addr = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3418319623442471843ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_wdata = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9730235553833177457ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_rstrb = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 12104324106438472466ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_wstrb = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 778924265436819751ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_result_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 11649694341788494725ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_result_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 17802039736266141893ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_result_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 8851694030884754459ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_result_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 201945397717327525ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_addr = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14533896170443679821ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_wdata = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12465925344982581204ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_result_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 13785796770772881809ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_result_error = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 6956813425943538871ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__memory_handshake = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 12178129985400374577ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_start_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 5441119171621358311ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_conv_engine__activation_mode = 0;
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__darknet_padding_parameter = 0;
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_x = 0;
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_y = 0;
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width = 0;
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_height = 0;
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__layer_index = 0;
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_upsample_engine__stride = 0;
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__start_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 1442820185963773930ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__backend_req_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 14866648096488789046ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__backend_rsp_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 13012199446223080318ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__state = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 13115790640413570203ull);
    for (int __Vi0 = 0; __Vi0 < 4; ++__Vi0) {
        vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7801955469578730284ull);
    }
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_address_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11151010087943728505ull);
    VL_SCOPED_RAND_RESET_W(72, vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__candidate_values_latched, __VscopeHash, 12313952252701148165ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__read_tap_index = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 9625282956027806075ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__result_value_latched = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 10521153066427210509ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__result_error_latched = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 15650625117333511582ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_output_height = VL_SCOPED_RAND_RESET_Q(33, __VscopeHash, 5667002660268219511ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_output_width = VL_SCOPED_RAND_RESET_Q(33, __VscopeHash, 2182627544194941689ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_count = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 8022844966401148225ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask = VL_SCOPED_RAND_RESET_I(9, __VscopeHash, 3724992013019081744ull);
    for (int __Vi0 = 0; __Vi0 < 9; ++__Vi0) {
        vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 18325677709624945951ull);
    }
    for (int __Vi0 = 0; __Vi0 < 9; ++__Vi0) {
        vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8209223126399266049ull);
    }
    for (int __Vi0 = 0; __Vi0 < 9; ++__Vi0) {
        vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[__Vi0] = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 10305747072396994317ull);
    }
    for (int __Vi0 = 0; __Vi0 < 9; ++__Vi0) {
        vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[__Vi0] = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 11143565144736999697ull);
    }
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_error_code = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 8048591759146387801ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_inputs_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 11378973411482245293ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_offset_work = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 10684861224319008408ull);
    VL_SCOPED_RAND_RESET_W(65, vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_address_work, __VscopeHash, 6669720684231783280ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__selected_byte_shift = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13497131798958244642ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__selected_input_word_address = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 520499068955425469ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__selected_input_lane = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 16869590161052938774ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__mapped_response_error = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 3038561374591799638ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__window_max_value = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 8274095621443865467ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__window_error_code = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 17330782757134174916ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9643430106706678653ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__candidate_value = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 5707033164723568683ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__current_maximum = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 6835097259275014764ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__extent_y = VL_SCOPED_RAND_RESET_Q(33, __VscopeHash, 17210008350018321967ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__extent_x = VL_SCOPED_RAND_RESET_Q(33, __VscopeHash, 740635476546036853ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_height_work = VL_SCOPED_RAND_RESET_Q(33, __VscopeHash, 15125291627997161393ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_width_work = VL_SCOPED_RAND_RESET_Q(33, __VscopeHash, 12570024116977556982ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__origin_y = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 7343866109326896211ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__origin_x = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 10425668660153093056ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_y_step = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 14512305274495755759ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_x_step = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 16808794893868000526ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_y_work = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 1485493632942566515ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_x_work = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 14304897437216100296ull);
    VL_SCOPED_RAND_RESET_W(96, vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __VscopeHash, 13011925745705298124ull);
    VL_SCOPED_RAND_RESET_W(96, vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, __VscopeHash, 17166602896496950855ull);
    VL_SCOPED_RAND_RESET_W(96, vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, __VscopeHash, 5479598460010008490ull);
    VL_SCOPED_RAND_RESET_W(97, vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work, __VscopeHash, 12326222921125647897ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__tap_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13462650417783302147ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11125058738690632875ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 330825719838776448ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__tap_range_error = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 15974591529932190527ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__start_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 10262964882922518001ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__backend_req_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 14564862308023877491ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__backend_rsp_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 9700829817844860991ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__state = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 12038888723445510804ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__source_address_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11535087384426194548ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__output_address_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 326721141324426389ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__copied_value_latched = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 5471283637228498800ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__result_error_latched = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 11312752144179156915ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_output_height = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 5315071605238597865ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_output_width = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 7425987825759592294ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_channel = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8124137385137151137ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 361165581646162028ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6060576978730264446ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_address = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16141636474347255091ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_unused_value = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 8917385357855068996ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_error_code = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 830546156805003797ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__output_offset_work = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 3204216941745257449ull);
    VL_SCOPED_RAND_RESET_W(65, vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__output_address_work, __VscopeHash, 1751747260189672393ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__selected_byte_shift = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4511824509987469419ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__mapped_response_error = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 5019139513263156798ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__output_height_work = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 5119842575090425337ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__output_width_work = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 5943436959174596103ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__channel_row_work = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 17037806331387936902ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__row_work = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 18406005198982946708ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__byte_offset_work = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 9145146369583624315ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__plane_index_work = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 18378469653812700590ull);
    VL_SCOPED_RAND_RESET_W(65, vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__address_work, __VscopeHash, 12150067548070654078ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__start_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 12500914858616204751ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__backend_req_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 15121881359703136751ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__backend_rsp_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 2157788115813520111ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__state = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 11502423998283252458ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source_count_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12088994028110889415ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__groups_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10489492761043815716ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__group_id_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 184435147325561288ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_channel_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2610451251694508829ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_y_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2136713420863662384ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_x_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 738549836135471985ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_base_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9112448627660879561ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_length_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10439367193547369852ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_channels_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6535491529777826791ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_height_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6383949133660479114ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_width_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5012081448965003162ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_start_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14769539559056589757ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_end_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7696201985022320684ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_multiplier_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15150892937301136425ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_value_latched = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 6081678529120526995ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_base_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11321341822202873725ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_length_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12253112312592632559ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_channels_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 178871508982804200ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_height_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5105188643348462328ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_width_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16557932581924083859ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_start_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10584717358071597322ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_end_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16748044317841666980ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_multiplier_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12867464382022620876ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_value_latched = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 5623884266719232729ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_base_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6386219214516895105ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_length_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14532252727706298200ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_channels_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1339076347038924126ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_height_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17680336879063518110ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_width_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16683209903912950741ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source_index_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14253174189035202819ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source_address_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3844078733420539382ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_address_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17447058482326622637ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__result_value_latched = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 1939738683718081062ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__result_error_latched = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 16345653072213600869ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__query_output_channels = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9184722388531561348ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__query_output_height = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16283377761467222765ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__query_output_width = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4460189787820106366ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__query_source_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8300398609504358009ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__query_source_channel = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8742563698224652542ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__query_source_address = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2647567147588758129ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__query_output_value = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 14977553970749073742ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__query_error_code = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 12309589415169080925ull);
    VL_SCOPED_RAND_RESET_W(65, vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_elements_work, __VscopeHash, 216817272214433196ull);
    VL_SCOPED_RAND_RESET_W(65, vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_offset_work, __VscopeHash, 10227743364023054839ull);
    VL_SCOPED_RAND_RESET_W(65, vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_end_work, __VscopeHash, 17782611397457717968ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__selected_word_address = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7712218438159694991ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__selected_read_lane = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 16295276059952350482ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__selected_byte_shift = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11427235559410555306ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__mapped_response_error = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 17724640715689511241ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_argument = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 3081366778800580192ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_range = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 3779939829101829936ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source0_shape_bytes = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 1004690488996813340ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_shape_bytes = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 3013857455348419943ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source0_plane_elements = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 2246923686723438357ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_plane_elements = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 13382317304691826907ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source0_object_end = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 3932363228962199751ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_object_end = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 1329012148044769120ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__output_channels_wide = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 11333568388438997052ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__expected_group_start = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 2158265426181701978ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__expected_group_end = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 10676649448856505685ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_offset = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 3541644949754263345ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_address_wide = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 18369311227383500509ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source0_selected_count = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17008100193728949689ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_selected_count = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9144573905117857325ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_multiplier = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16388251851756547660ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_base_address = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12871354322291465481ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_length_bytes = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1940797604946313023ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_value = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 4095340212652609159ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_magnitude = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 17782722260560373337ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__scaled_product = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 12682252705484006752ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__rounded_magnitude = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 2652523606331010298ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__scaled_signed = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 5435177038866550418ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_source_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2992747201091733170ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_source_channel = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13894903349604212187ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__start_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 7404921881958948697ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__backend_req_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 11926244810469817417ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__backend_rsp_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 4320897150063879863ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__state = VL_SCOPED_RAND_RESET_I(5, __VscopeHash, 6045273827333709454ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10710862418520573034ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_layer_index_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7804548011249005317ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_base_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3729841278890536507ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_length_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8087958227841842922ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_batch_count_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5698215607795227318ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_channels_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4303228225416654894ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_height_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3182999040033676915ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_width_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1364089744629901922ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_base_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 460470484376674193ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_length_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4256390464913069923ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_batch_count_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9102611098304434658ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_channels_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9600864409922580558ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7399795626350160795ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10690868517460968911ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_height_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6289858295390080520ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_width_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11486644189270219655ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__stride_y_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16059664352288041589ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__stride_x_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3936025955765271879ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__pad_left_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17150088776376753183ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__pad_right_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16980402492456717383ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__pad_top_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4186244002447104205ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__pad_bottom_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 18082921573122683925ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__groups_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16166602547936948068ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__padding_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14014644956271760496ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_package_base_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13134314035020726858ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_package_length_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16089286589238663446ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__quantized_weight_offset_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15977565726654044479ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__quantized_weight_bytes_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10070866215644509781ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_batch_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13693814833093828168ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__activation_mode_latched = VL_SCOPED_RAND_RESET_I(2, __VscopeHash, 1552762952022931020ull);
    for (int __Vi0 = 0; __Vi0 < 51200; ++__Vi0) {
        vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_patch[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 17759649128178728815ull);
    }
    for (int __Vi0 = 0; __Vi0 < 36864; ++__Vi0) {
        vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_group[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 8931746362077184592ull);
    }
    for (int __Vi0 = 0; __Vi0 < 512; ++__Vi0) {
        vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_block[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 9010112618248158986ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4159904438363913609ull);
    }
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 18024520153527792905ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9043828821255074993ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10660098177796130933ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16607237042188288724ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__tile_height = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2859376472233374402ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__tile_width = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9754202870993912666ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__patch_height = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12606393018359569389ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__patch_width = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11965726922579589688ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__patch_byte_count = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10499486433981415110ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__tile_point_count = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1170483913705570669ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10058283270326938288ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7835691423883358168ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_lane_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16272183445686512452ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_reduction_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9930467377462192742ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9416795547069621590ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_reduction_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12384930003847776636ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_lane_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4717224215512095418ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_point_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3315685404964734153ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__request_address_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16627557811352493629ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__request_strobe_latched = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 3170732645635428005ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__request_write_latched = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 17251325373637387289ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__request_wdata_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 684137598389709551ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_address_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2898548327667715212ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_value_latched = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 15209405282270194582ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__result_error_latched = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 1805219112949716692ull);
    VL_SCOPED_RAND_RESET_W(128, vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_elements_wide, __VscopeHash, 2274457451906327662ull);
    VL_SCOPED_RAND_RESET_W(128, vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_elements_wide, __VscopeHash, 13528814100271775422ull);
    VL_SCOPED_RAND_RESET_W(128, vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__expected_weight_bytes_wide, __VscopeHash, 9005948582407565203ull);
    VL_SCOPED_RAND_RESET_W(128, vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_wide, __VscopeHash, 3058266481963643912ull);
    VL_SCOPED_RAND_RESET_W(128, vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_end_wide, __VscopeHash, 13433826402940553373ull);
    VL_SCOPED_RAND_RESET_W(128, vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_end_wide, __VscopeHash, 16980322448348742545ull);
    VL_SCOPED_RAND_RESET_W(128, vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_package_end_wide, __VscopeHash, 462471027736514477ull);
    VL_SCOPED_RAND_RESET_W(128, vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__quantized_weight_end_wide, __VscopeHash, 17265036765659315401ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_numerator = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 17745125031277711080ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_numerator = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 6398574051333803788ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_shape_span = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 11173272116564036706ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_shape_span = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 14544457708741955575ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_shape_product = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 12399352435385745751ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_shape_product = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 6251283934965858854ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_span_plus_stride = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 4667491813852986037ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_span_plus_stride = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 8347369200814312640ull);
    VL_SCOPED_RAND_RESET_W(128, vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_height_wide, __VscopeHash, 15570002937017090650ull);
    VL_SCOPED_RAND_RESET_W(128, vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_width_wide, __VscopeHash, 9569898747728921895ull);
    VL_SCOPED_RAND_RESET_W(128, vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_bytes_wide, __VscopeHash, 4613851478652573604ull);
    VL_SCOPED_RAND_RESET_W(128, vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__full_weight_group_bytes_wide, __VscopeHash, 16279701114592210499ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__validation_ok = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 13204378780573683817ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__validation_error = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 12639190687866931540ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__patch_plane_bytes = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 11413237238962632349ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_channel = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16994717284971651080ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7899375530483430982ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 18309784473337246764ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_advance = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 6730633210791222309ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_input_y = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 13928051230447419171ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_input_x = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 5197450407666347201ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_in_bounds = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 1286710422885463140ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_source_offset = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 16712452322811831972ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_source_address_wide = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 17834424136553329997ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_source_address_wide = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 851888967882421469ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_area = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6230434630328806728ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_input_channel = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13455892559253899997ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13176006934350057822ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17899649498313085114ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9046483308971551817ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6496950876659369722ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_input_y = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 3158747835800437478ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_input_x = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 4848999401559408104ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_tap_in_bounds = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 16242507636719168766ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index_wide = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 5541473231138654772ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3911708028345836907ull);
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 14234039650130488760ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 16146704684016613493ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[__Vi0] = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 15733043348677942883ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[__Vi0] = VL_SCOPED_RAND_RESET_Q(33, __VscopeHash, 10294298098376951935ull);
    }
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_bad_argument = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 51965741926993924ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_overflow = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 4577499459605275732ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_lane = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12200983599969254027ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15034917863471372298ull);
    VL_SCOPED_RAND_RESET_W(80, vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_parameter, __VscopeHash, 16489681519597491825ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_bias = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8658350570573935228ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_invalid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 9614926200451434266ull);
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        VL_SCOPED_RAND_RESET_W(80, vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_mq_parameter[__Vi0], __VscopeHash, 163650727486202901ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_bias[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15192339967767501618ull);
    }
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_lane_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14422916824516856012ull);
    VL_SCOPED_RAND_RESET_W(80, vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_parameter, __VscopeHash, 16268937298891442333ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_accumulator = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15031927986085368340ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 259835599266314623ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13462778465518428378ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4978732638861720750ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 13296344249829596689ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 8499826287158832910ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 553363734801488661ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 2830038925576266115ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requantized_value = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 4465912919325729159ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_point_scan_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5130689603330742715ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_point_scan_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5254305037918922249ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_byte_offset_wide = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 17719212861652574233ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_address_wide = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 6472993812494644231ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mapped_response_error = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 16779742067079052356ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__request_byte_lane = VL_SCOPED_RAND_RESET_I(2, __VscopeHash, 5433151678748007642ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__comb_lane = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15010331549900798752ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__seq_lane = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13459639427557788290ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__csr_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 15130806013021348136ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__backend_memory_error_code = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 14432578796450941236ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__error_code = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 2264950914891105351ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__frame_id = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12206741371267893170ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__active_frame_id = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12147466300530455537ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__input_addr = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2798664554832168717ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__input_bytes = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13030910272193799615ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__weight_addr = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1620688082659107546ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__weight_bytes = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3431200877656295937ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__timeout_cycles = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14168203505315556096ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__elapsed_cycles = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5318243418692743940ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__config_idle = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 5988385107242915811ull);
    vlSelf->__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__map_conv_activation__96__descriptor_activation = 0;
    vlSelf->__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__97__code = 0;
    vlSelf->__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__98__Vfuncout = 0;
    vlSelf->__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__98__code = 0;
    vlSelf->__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__99__code = 0;
    vlSelf->__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__100__Vfuncout = 0;
    vlSelf->__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__100__code = 0;
    VL_ZERO_RESET_W(65, vlSelf->__VdfgRegularize_h6e95ff9d_0_7);
    VL_ZERO_RESET_W(65, vlSelf->__VdfgRegularize_h6e95ff9d_0_8);
    for (int __Vi0 = 0; __Vi0 < 1; ++__Vi0) {
        vlSelf->__VstlTriggered[__Vi0] = 0;
    }
    for (int __Vi0 = 0; __Vi0 < 1; ++__Vi0) {
        vlSelf->__VactTriggered[__Vi0] = 0;
    }
    for (int __Vi0 = 0; __Vi0 < 1; ++__Vi0) {
        vlSelf->__VactTriggeredAcc[__Vi0] = 0;
    }
    vlSelf->__Vtrigprevexpr___TOP__tb_s2a_backend_fault_recovery__DOT__clk__0 = 0;
    for (int __Vi0 = 0; __Vi0 < 1; ++__Vi0) {
        vlSelf->__VnbaTriggered[__Vi0] = 0;
    }
    vlSelf->__Vi = 0;
    for (int __Vi0 = 0; __Vi0 < 7; ++__Vi0) {
        vlSelf->__Vm_traceActivity[__Vi0] = 0;
    }
}
