// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vtb_s2a_backend_fault_recovery.h for the primary calling header

#include "Vtb_s2a_backend_fault_recovery__pch.h"

extern const VlWide<43>/*1375:0*/ Vtb_s2a_backend_fault_recovery__ConstPool__CONST_h3efedef1_0;

void Vtb_s2a_backend_fault_recovery___024root___nba_comb__TOP__0(Vtb_s2a_backend_fault_recovery___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root___nba_comb__TOP__0\n"); );
    Vtb_s2a_backend_fault_recovery__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_5;
    __VdfgRegularize_h6e95ff9d_0_5 = 0;
    VlWide<3>/*64:0*/ __VdfgRegularize_h6e95ff9d_0_6;
    VL_ZERO_W(65, __VdfgRegularize_h6e95ff9d_0_6);
    VlWide<3>/*95:0*/ __Vtemp_2;
    VlWide<3>/*95:0*/ __Vtemp_3;
    VlWide<3>/*95:0*/ __Vtemp_4;
    VlWide<3>/*95:0*/ __Vtemp_5;
    VlWide<3>/*95:0*/ __Vtemp_6;
    VlWide<3>/*95:0*/ __Vtemp_7;
    VlWide<3>/*95:0*/ __Vtemp_8;
    VlWide<3>/*95:0*/ __Vtemp_9;
    VlWide<3>/*95:0*/ __Vtemp_10;
    VlWide<4>/*127:0*/ __Vtemp_12;
    VlWide<4>/*127:0*/ __Vtemp_13;
    VlWide<4>/*127:0*/ __Vtemp_14;
    VlWide<3>/*95:0*/ __Vtemp_19;
    VlWide<3>/*95:0*/ __Vtemp_20;
    VlWide<3>/*95:0*/ __Vtemp_21;
    VlWide<3>/*95:0*/ __Vtemp_22;
    VlWide<3>/*95:0*/ __Vtemp_23;
    VlWide<3>/*95:0*/ __Vtemp_24;
    VlWide<4>/*127:0*/ __Vtemp_26;
    VlWide<4>/*127:0*/ __Vtemp_27;
    VlWide<4>/*127:0*/ __Vtemp_28;
    VlWide<3>/*95:0*/ __Vtemp_33;
    VlWide<3>/*95:0*/ __Vtemp_34;
    VlWide<3>/*95:0*/ __Vtemp_35;
    VlWide<3>/*95:0*/ __Vtemp_36;
    VlWide<3>/*95:0*/ __Vtemp_37;
    VlWide<3>/*95:0*/ __Vtemp_38;
    VlWide<4>/*127:0*/ __Vtemp_40;
    VlWide<4>/*127:0*/ __Vtemp_41;
    VlWide<4>/*127:0*/ __Vtemp_42;
    VlWide<3>/*95:0*/ __Vtemp_47;
    VlWide<3>/*95:0*/ __Vtemp_48;
    VlWide<3>/*95:0*/ __Vtemp_49;
    VlWide<3>/*95:0*/ __Vtemp_50;
    VlWide<3>/*95:0*/ __Vtemp_51;
    VlWide<3>/*95:0*/ __Vtemp_52;
    VlWide<4>/*127:0*/ __Vtemp_54;
    VlWide<4>/*127:0*/ __Vtemp_55;
    VlWide<4>/*127:0*/ __Vtemp_56;
    VlWide<3>/*95:0*/ __Vtemp_61;
    VlWide<3>/*95:0*/ __Vtemp_62;
    VlWide<3>/*95:0*/ __Vtemp_63;
    VlWide<3>/*95:0*/ __Vtemp_64;
    VlWide<3>/*95:0*/ __Vtemp_65;
    VlWide<3>/*95:0*/ __Vtemp_66;
    VlWide<4>/*127:0*/ __Vtemp_68;
    VlWide<4>/*127:0*/ __Vtemp_69;
    VlWide<4>/*127:0*/ __Vtemp_70;
    VlWide<3>/*95:0*/ __Vtemp_75;
    VlWide<3>/*95:0*/ __Vtemp_76;
    VlWide<3>/*95:0*/ __Vtemp_77;
    VlWide<3>/*95:0*/ __Vtemp_78;
    VlWide<3>/*95:0*/ __Vtemp_79;
    VlWide<3>/*95:0*/ __Vtemp_80;
    VlWide<4>/*127:0*/ __Vtemp_82;
    VlWide<4>/*127:0*/ __Vtemp_83;
    VlWide<4>/*127:0*/ __Vtemp_84;
    VlWide<3>/*95:0*/ __Vtemp_89;
    VlWide<3>/*95:0*/ __Vtemp_90;
    VlWide<3>/*95:0*/ __Vtemp_91;
    VlWide<3>/*95:0*/ __Vtemp_92;
    VlWide<3>/*95:0*/ __Vtemp_93;
    VlWide<3>/*95:0*/ __Vtemp_94;
    VlWide<4>/*127:0*/ __Vtemp_96;
    VlWide<4>/*127:0*/ __Vtemp_97;
    VlWide<4>/*127:0*/ __Vtemp_98;
    VlWide<3>/*95:0*/ __Vtemp_103;
    VlWide<3>/*95:0*/ __Vtemp_104;
    VlWide<3>/*95:0*/ __Vtemp_105;
    VlWide<3>/*95:0*/ __Vtemp_106;
    VlWide<3>/*95:0*/ __Vtemp_107;
    VlWide<3>/*95:0*/ __Vtemp_108;
    VlWide<4>/*127:0*/ __Vtemp_110;
    VlWide<4>/*127:0*/ __Vtemp_111;
    VlWide<4>/*127:0*/ __Vtemp_112;
    VlWide<3>/*95:0*/ __Vtemp_117;
    VlWide<3>/*95:0*/ __Vtemp_118;
    VlWide<3>/*95:0*/ __Vtemp_119;
    VlWide<3>/*95:0*/ __Vtemp_120;
    VlWide<3>/*95:0*/ __Vtemp_121;
    VlWide<3>/*95:0*/ __Vtemp_122;
    VlWide<4>/*127:0*/ __Vtemp_124;
    VlWide<4>/*127:0*/ __Vtemp_125;
    VlWide<4>/*127:0*/ __Vtemp_126;
    VlWide<3>/*95:0*/ __Vtemp_132;
    VlWide<3>/*95:0*/ __Vtemp_133;
    VlWide<3>/*95:0*/ __Vtemp_135;
    VlWide<3>/*95:0*/ __Vtemp_136;
    // Body
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__csr_ready 
        = (1U & (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__hard_reset)));
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
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__backend_rsp_valid 
        = ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_pending) 
           & ((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__hard_reset)) 
              & ((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__backend_abort)) 
                 & (0U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_target_latched)))));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_rstrb = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_rstrb = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_wdata = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_addr = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_wdata = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__selected_read_lane 
        = (0x0000000fU & ((IData)(1U) << (3U & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source_address_latched)));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_rstrb = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_wdata = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_rstrb = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__selected_input_lane = 0U;
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
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_write = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_write = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_write = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_write = 0U;
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
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_wdata = 0U;
    if ((4U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))) {
        if ((1U & (~ ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                      >> 1U)))) {
            if ((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))) {
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
    if ((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))) {
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
            __Vtemp_2[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_base[0U];
            __Vtemp_2[1U] = 0U;
            __Vtemp_2[2U] = 0U;
            __Vtemp_3[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__byte_offset_work);
            __Vtemp_3[1U] = (IData)((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__byte_offset_work 
                                     >> 0x00000020U));
            __Vtemp_3[2U] = 0U;
            VL_ADD_W(3, __Vtemp_4, __Vtemp_2, __Vtemp_3);
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__address_work[0U] 
                = __Vtemp_4[0U];
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__address_work[1U] 
                = __Vtemp_4[1U];
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__address_work[2U] 
                = (1U & __Vtemp_4[2U]);
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
                    __Vtemp_5[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel;
                    __Vtemp_5[1U] = 0U;
                    __Vtemp_5[2U] = 0U;
                    __Vtemp_6[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U];
                    __Vtemp_6[1U] = 0U;
                    __Vtemp_6[2U] = 0U;
                    VL_MUL_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_5, __Vtemp_6);
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask 
                        = (1U | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask));
                    __Vtemp_7[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[0U]);
                    __Vtemp_7[1U] = 0U;
                    __Vtemp_7[2U] = 0U;
                    VL_ADD_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_7);
                    __Vtemp_8[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U];
                    __Vtemp_8[1U] = 0U;
                    __Vtemp_8[2U] = 0U;
                    VL_MUL_W(3, __Vtemp_9, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, __Vtemp_8);
                    __Vtemp_10[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[0U]);
                    __Vtemp_10[1U] = 0U;
                    __Vtemp_10[2U] = 0U;
                    VL_ADD_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, __Vtemp_9, __Vtemp_10);
                    __Vtemp_12[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_base[0U];
                    __Vtemp_12[1U] = 0U;
                    __Vtemp_12[2U] = 0U;
                    __Vtemp_12[3U] = 0U;
                    __Vtemp_13[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U];
                    __Vtemp_13[1U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U];
                    __Vtemp_13[2U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U];
                    __Vtemp_13[3U] = 0U;
                    VL_ADD_W(4, __Vtemp_14, __Vtemp_12, __Vtemp_13);
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U] 
                        = __Vtemp_14[0U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                        = __Vtemp_14[1U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U] 
                        = __Vtemp_14[2U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U] 
                        = (1U & __Vtemp_14[3U]);
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
                    __Vtemp_19[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel;
                    __Vtemp_19[1U] = 0U;
                    __Vtemp_19[2U] = 0U;
                    __Vtemp_20[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U];
                    __Vtemp_20[1U] = 0U;
                    __Vtemp_20[2U] = 0U;
                    VL_MUL_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_19, __Vtemp_20);
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask 
                        = (2U | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask));
                    __Vtemp_21[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[1U]);
                    __Vtemp_21[1U] = 0U;
                    __Vtemp_21[2U] = 0U;
                    VL_ADD_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_21);
                    __Vtemp_22[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U];
                    __Vtemp_22[1U] = 0U;
                    __Vtemp_22[2U] = 0U;
                    VL_MUL_W(3, __Vtemp_23, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, __Vtemp_22);
                    __Vtemp_24[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[1U]);
                    __Vtemp_24[1U] = 0U;
                    __Vtemp_24[2U] = 0U;
                    VL_ADD_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, __Vtemp_23, __Vtemp_24);
                    __Vtemp_26[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_base[0U];
                    __Vtemp_26[1U] = 0U;
                    __Vtemp_26[2U] = 0U;
                    __Vtemp_26[3U] = 0U;
                    __Vtemp_27[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U];
                    __Vtemp_27[1U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U];
                    __Vtemp_27[2U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U];
                    __Vtemp_27[3U] = 0U;
                    VL_ADD_W(4, __Vtemp_28, __Vtemp_26, __Vtemp_27);
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U] 
                        = __Vtemp_28[0U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                        = __Vtemp_28[1U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U] 
                        = __Vtemp_28[2U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U] 
                        = (1U & __Vtemp_28[3U]);
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
                    __Vtemp_33[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel;
                    __Vtemp_33[1U] = 0U;
                    __Vtemp_33[2U] = 0U;
                    __Vtemp_34[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U];
                    __Vtemp_34[1U] = 0U;
                    __Vtemp_34[2U] = 0U;
                    VL_MUL_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_33, __Vtemp_34);
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask 
                        = (4U | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask));
                    __Vtemp_35[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[2U]);
                    __Vtemp_35[1U] = 0U;
                    __Vtemp_35[2U] = 0U;
                    VL_ADD_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_35);
                    __Vtemp_36[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U];
                    __Vtemp_36[1U] = 0U;
                    __Vtemp_36[2U] = 0U;
                    VL_MUL_W(3, __Vtemp_37, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, __Vtemp_36);
                    __Vtemp_38[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[2U]);
                    __Vtemp_38[1U] = 0U;
                    __Vtemp_38[2U] = 0U;
                    VL_ADD_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, __Vtemp_37, __Vtemp_38);
                    __Vtemp_40[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_base[0U];
                    __Vtemp_40[1U] = 0U;
                    __Vtemp_40[2U] = 0U;
                    __Vtemp_40[3U] = 0U;
                    __Vtemp_41[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U];
                    __Vtemp_41[1U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U];
                    __Vtemp_41[2U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U];
                    __Vtemp_41[3U] = 0U;
                    VL_ADD_W(4, __Vtemp_42, __Vtemp_40, __Vtemp_41);
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U] 
                        = __Vtemp_42[0U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                        = __Vtemp_42[1U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U] 
                        = __Vtemp_42[2U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U] 
                        = (1U & __Vtemp_42[3U]);
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
                    __Vtemp_47[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel;
                    __Vtemp_47[1U] = 0U;
                    __Vtemp_47[2U] = 0U;
                    __Vtemp_48[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U];
                    __Vtemp_48[1U] = 0U;
                    __Vtemp_48[2U] = 0U;
                    VL_MUL_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_47, __Vtemp_48);
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask 
                        = (8U | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask));
                    __Vtemp_49[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[3U]);
                    __Vtemp_49[1U] = 0U;
                    __Vtemp_49[2U] = 0U;
                    VL_ADD_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_49);
                    __Vtemp_50[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U];
                    __Vtemp_50[1U] = 0U;
                    __Vtemp_50[2U] = 0U;
                    VL_MUL_W(3, __Vtemp_51, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, __Vtemp_50);
                    __Vtemp_52[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[3U]);
                    __Vtemp_52[1U] = 0U;
                    __Vtemp_52[2U] = 0U;
                    VL_ADD_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, __Vtemp_51, __Vtemp_52);
                    __Vtemp_54[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_base[0U];
                    __Vtemp_54[1U] = 0U;
                    __Vtemp_54[2U] = 0U;
                    __Vtemp_54[3U] = 0U;
                    __Vtemp_55[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U];
                    __Vtemp_55[1U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U];
                    __Vtemp_55[2U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U];
                    __Vtemp_55[3U] = 0U;
                    VL_ADD_W(4, __Vtemp_56, __Vtemp_54, __Vtemp_55);
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U] 
                        = __Vtemp_56[0U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                        = __Vtemp_56[1U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U] 
                        = __Vtemp_56[2U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U] 
                        = (1U & __Vtemp_56[3U]);
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
                    __Vtemp_61[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel;
                    __Vtemp_61[1U] = 0U;
                    __Vtemp_61[2U] = 0U;
                    __Vtemp_62[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U];
                    __Vtemp_62[1U] = 0U;
                    __Vtemp_62[2U] = 0U;
                    VL_MUL_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_61, __Vtemp_62);
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask 
                        = (0x00000010U | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask));
                    __Vtemp_63[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[4U]);
                    __Vtemp_63[1U] = 0U;
                    __Vtemp_63[2U] = 0U;
                    VL_ADD_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_63);
                    __Vtemp_64[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U];
                    __Vtemp_64[1U] = 0U;
                    __Vtemp_64[2U] = 0U;
                    VL_MUL_W(3, __Vtemp_65, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, __Vtemp_64);
                    __Vtemp_66[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[4U]);
                    __Vtemp_66[1U] = 0U;
                    __Vtemp_66[2U] = 0U;
                    VL_ADD_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, __Vtemp_65, __Vtemp_66);
                    __Vtemp_68[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_base[0U];
                    __Vtemp_68[1U] = 0U;
                    __Vtemp_68[2U] = 0U;
                    __Vtemp_68[3U] = 0U;
                    __Vtemp_69[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U];
                    __Vtemp_69[1U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U];
                    __Vtemp_69[2U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U];
                    __Vtemp_69[3U] = 0U;
                    VL_ADD_W(4, __Vtemp_70, __Vtemp_68, __Vtemp_69);
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U] 
                        = __Vtemp_70[0U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                        = __Vtemp_70[1U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U] 
                        = __Vtemp_70[2U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U] 
                        = (1U & __Vtemp_70[3U]);
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
                    __Vtemp_75[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel;
                    __Vtemp_75[1U] = 0U;
                    __Vtemp_75[2U] = 0U;
                    __Vtemp_76[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U];
                    __Vtemp_76[1U] = 0U;
                    __Vtemp_76[2U] = 0U;
                    VL_MUL_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_75, __Vtemp_76);
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask 
                        = (0x00000020U | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask));
                    __Vtemp_77[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[5U]);
                    __Vtemp_77[1U] = 0U;
                    __Vtemp_77[2U] = 0U;
                    VL_ADD_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_77);
                    __Vtemp_78[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U];
                    __Vtemp_78[1U] = 0U;
                    __Vtemp_78[2U] = 0U;
                    VL_MUL_W(3, __Vtemp_79, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, __Vtemp_78);
                    __Vtemp_80[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[5U]);
                    __Vtemp_80[1U] = 0U;
                    __Vtemp_80[2U] = 0U;
                    VL_ADD_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, __Vtemp_79, __Vtemp_80);
                    __Vtemp_82[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_base[0U];
                    __Vtemp_82[1U] = 0U;
                    __Vtemp_82[2U] = 0U;
                    __Vtemp_82[3U] = 0U;
                    __Vtemp_83[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U];
                    __Vtemp_83[1U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U];
                    __Vtemp_83[2U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U];
                    __Vtemp_83[3U] = 0U;
                    VL_ADD_W(4, __Vtemp_84, __Vtemp_82, __Vtemp_83);
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U] 
                        = __Vtemp_84[0U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                        = __Vtemp_84[1U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U] 
                        = __Vtemp_84[2U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U] 
                        = (1U & __Vtemp_84[3U]);
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
                    __Vtemp_89[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel;
                    __Vtemp_89[1U] = 0U;
                    __Vtemp_89[2U] = 0U;
                    __Vtemp_90[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U];
                    __Vtemp_90[1U] = 0U;
                    __Vtemp_90[2U] = 0U;
                    VL_MUL_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_89, __Vtemp_90);
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask 
                        = (0x00000040U | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask));
                    __Vtemp_91[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[6U]);
                    __Vtemp_91[1U] = 0U;
                    __Vtemp_91[2U] = 0U;
                    VL_ADD_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_91);
                    __Vtemp_92[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U];
                    __Vtemp_92[1U] = 0U;
                    __Vtemp_92[2U] = 0U;
                    VL_MUL_W(3, __Vtemp_93, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, __Vtemp_92);
                    __Vtemp_94[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[6U]);
                    __Vtemp_94[1U] = 0U;
                    __Vtemp_94[2U] = 0U;
                    VL_ADD_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, __Vtemp_93, __Vtemp_94);
                    __Vtemp_96[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_base[0U];
                    __Vtemp_96[1U] = 0U;
                    __Vtemp_96[2U] = 0U;
                    __Vtemp_96[3U] = 0U;
                    __Vtemp_97[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U];
                    __Vtemp_97[1U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U];
                    __Vtemp_97[2U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U];
                    __Vtemp_97[3U] = 0U;
                    VL_ADD_W(4, __Vtemp_98, __Vtemp_96, __Vtemp_97);
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U] 
                        = __Vtemp_98[0U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                        = __Vtemp_98[1U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U] 
                        = __Vtemp_98[2U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U] 
                        = (1U & __Vtemp_98[3U]);
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
                    __Vtemp_103[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel;
                    __Vtemp_103[1U] = 0U;
                    __Vtemp_103[2U] = 0U;
                    __Vtemp_104[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U];
                    __Vtemp_104[1U] = 0U;
                    __Vtemp_104[2U] = 0U;
                    VL_MUL_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_103, __Vtemp_104);
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask 
                        = (0x00000080U | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask));
                    __Vtemp_105[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[7U]);
                    __Vtemp_105[1U] = 0U;
                    __Vtemp_105[2U] = 0U;
                    VL_ADD_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_105);
                    __Vtemp_106[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U];
                    __Vtemp_106[1U] = 0U;
                    __Vtemp_106[2U] = 0U;
                    VL_MUL_W(3, __Vtemp_107, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, __Vtemp_106);
                    __Vtemp_108[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[7U]);
                    __Vtemp_108[1U] = 0U;
                    __Vtemp_108[2U] = 0U;
                    VL_ADD_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, __Vtemp_107, __Vtemp_108);
                    __Vtemp_110[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_base[0U];
                    __Vtemp_110[1U] = 0U;
                    __Vtemp_110[2U] = 0U;
                    __Vtemp_110[3U] = 0U;
                    __Vtemp_111[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U];
                    __Vtemp_111[1U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U];
                    __Vtemp_111[2U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U];
                    __Vtemp_111[3U] = 0U;
                    VL_ADD_W(4, __Vtemp_112, __Vtemp_110, __Vtemp_111);
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U] 
                        = __Vtemp_112[0U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                        = __Vtemp_112[1U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U] 
                        = __Vtemp_112[2U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U] 
                        = (1U & __Vtemp_112[3U]);
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
                    __Vtemp_117[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel;
                    __Vtemp_117[1U] = 0U;
                    __Vtemp_117[2U] = 0U;
                    __Vtemp_118[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U];
                    __Vtemp_118[1U] = 0U;
                    __Vtemp_118[2U] = 0U;
                    VL_MUL_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_117, __Vtemp_118);
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask 
                        = (0x00000100U | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask));
                    __Vtemp_119[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[8U]);
                    __Vtemp_119[1U] = 0U;
                    __Vtemp_119[2U] = 0U;
                    VL_ADD_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_119);
                    __Vtemp_120[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U];
                    __Vtemp_120[1U] = 0U;
                    __Vtemp_120[2U] = 0U;
                    VL_MUL_W(3, __Vtemp_121, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, __Vtemp_120);
                    __Vtemp_122[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[8U]);
                    __Vtemp_122[1U] = 0U;
                    __Vtemp_122[2U] = 0U;
                    VL_ADD_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, __Vtemp_121, __Vtemp_122);
                    __Vtemp_124[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_base[0U];
                    __Vtemp_124[1U] = 0U;
                    __Vtemp_124[2U] = 0U;
                    __Vtemp_124[3U] = 0U;
                    __Vtemp_125[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U];
                    __Vtemp_125[1U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U];
                    __Vtemp_125[2U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U];
                    __Vtemp_125[3U] = 0U;
                    VL_ADD_W(4, __Vtemp_126, __Vtemp_124, __Vtemp_125);
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U] 
                        = __Vtemp_126[0U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                        = __Vtemp_126[1U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U] 
                        = __Vtemp_126[2U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U] 
                        = (1U & __Vtemp_126[3U]);
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
    __Vtemp_132[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__output_offset_work);
    __Vtemp_132[1U] = (IData)((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__output_offset_work 
                               >> 0x00000020U));
    __Vtemp_132[2U] = 0U;
    VL_ADD_W(3, __Vtemp_133, __Vtemp_132, __VdfgRegularize_h6e95ff9d_0_6);
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__output_address_work[0U] 
        = __Vtemp_133[0U];
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__output_address_work[1U] 
        = __Vtemp_133[1U];
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__output_address_work[2U] 
        = (1U & __Vtemp_133[2U]);
    __Vtemp_135[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_offset_work);
    __Vtemp_135[1U] = (IData)((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_offset_work 
                               >> 0x00000020U));
    __Vtemp_135[2U] = 0U;
    VL_ADD_W(3, __Vtemp_136, __Vtemp_135, __VdfgRegularize_h6e95ff9d_0_6);
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_address_work[0U] 
        = __Vtemp_136[0U];
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_address_work[1U] 
        = __Vtemp_136[1U];
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_address_work[2U] 
        = (1U & __Vtemp_136[2U]);
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

void Vtb_s2a_backend_fault_recovery___024root___timing_ready(Vtb_s2a_backend_fault_recovery___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root___timing_ready\n"); );
    Vtb_s2a_backend_fault_recovery__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if ((4ULL & vlSelfRef.__VactTriggered[0U])) {
        vlSelfRef.__VtrigSched_h3193e339__0.ready("@(negedge tb_s2a_backend_fault_recovery.clk)");
    }
    if ((1ULL & vlSelfRef.__VactTriggered[0U])) {
        vlSelfRef.__VtrigSched_h3193e288__0.ready("@(posedge tb_s2a_backend_fault_recovery.clk)");
    }
}

void Vtb_s2a_backend_fault_recovery___024root___timing_resume(Vtb_s2a_backend_fault_recovery___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root___timing_resume\n"); );
    Vtb_s2a_backend_fault_recovery__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.__VtrigSched_h3193e339__0.moveToResumeQueue(
                                                          "@(negedge tb_s2a_backend_fault_recovery.clk)");
    vlSelfRef.__VtrigSched_h3193e288__0.moveToResumeQueue(
                                                          "@(posedge tb_s2a_backend_fault_recovery.clk)");
    vlSelfRef.__VtrigSched_h3193e339__0.resume("@(negedge tb_s2a_backend_fault_recovery.clk)");
    vlSelfRef.__VtrigSched_h3193e288__0.resume("@(posedge tb_s2a_backend_fault_recovery.clk)");
    if ((2ULL & vlSelfRef.__VactTriggered[0U])) {
        vlSelfRef.__VdlySched.resume();
    }
}

void Vtb_s2a_backend_fault_recovery___024root___trigger_orInto__act_vec_vec(VlUnpacked<QData/*63:0*/, 1> &out, const VlUnpacked<QData/*63:0*/, 1> &in) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root___trigger_orInto__act_vec_vec\n"); );
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
VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root___dump_triggers__act(const VlUnpacked<QData/*63:0*/, 1> &triggers, const std::string &tag);
#endif  // VL_DEBUG
bool Vtb_s2a_backend_fault_recovery___024root___trigger_anySet__act(const VlUnpacked<QData/*63:0*/, 1> &in);
void Vtb_s2a_backend_fault_recovery___024root___act_comb__TOP__0(Vtb_s2a_backend_fault_recovery___024root* vlSelf);

bool Vtb_s2a_backend_fault_recovery___024root___eval_phase__act(Vtb_s2a_backend_fault_recovery___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root___eval_phase__act\n"); );
    Vtb_s2a_backend_fault_recovery__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    CData/*0:0*/ __VactExecute;
    // Body
    {
        // Inlined CFunc: _eval_triggers_vec__act
        vlSelfRef.__VactTriggered[0U] = (QData)((IData)(
                                                        ((((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__clk)) 
                                                           & (IData)(vlSelfRef.__Vtrigprevexpr___TOP__tb_s2a_backend_fault_recovery__DOT__clk__0)) 
                                                          << 2U) 
                                                         | ((vlSelfRef.__VdlySched.awaitingCurrentTime() 
                                                             << 1U) 
                                                            | ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__clk) 
                                                               & (~ (IData)(vlSelfRef.__Vtrigprevexpr___TOP__tb_s2a_backend_fault_recovery__DOT__clk__0)))))));
        vlSelfRef.__Vtrigprevexpr___TOP__tb_s2a_backend_fault_recovery__DOT__clk__0 
            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__clk;
    }
    Vtb_s2a_backend_fault_recovery___024root___timing_ready(vlSelf);
    Vtb_s2a_backend_fault_recovery___024root___trigger_orInto__act_vec_vec(vlSelfRef.__VactTriggered, vlSelfRef.__VactTriggeredAcc);
#ifdef VL_DEBUG
    if (VL_UNLIKELY(vlSymsp->_vm_contextp__->debug())) {
        Vtb_s2a_backend_fault_recovery___024root___dump_triggers__act(vlSelfRef.__VactTriggered, "act"s);
    }
#endif
    Vtb_s2a_backend_fault_recovery___024root___trigger_orInto__act_vec_vec(vlSelfRef.__VnbaTriggered, vlSelfRef.__VactTriggered);
    __VactExecute = Vtb_s2a_backend_fault_recovery___024root___trigger_anySet__act(vlSelfRef.__VactTriggered);
    if (__VactExecute) {
        vlSelfRef.__VactTriggeredAcc.fill(0ULL);
        Vtb_s2a_backend_fault_recovery___024root___timing_resume(vlSelf);
        {
            // Inlined CFunc: _eval_act
            if ((7ULL & vlSelfRef.__VactTriggered[0U])) {
                Vtb_s2a_backend_fault_recovery___024root___act_comb__TOP__0(vlSelf);
                vlSelfRef.__Vm_traceActivity[4U] = 1U;
            }
        }
    }
    return (__VactExecute);
}

bool Vtb_s2a_backend_fault_recovery___024root___eval_phase__inact(Vtb_s2a_backend_fault_recovery___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root___eval_phase__inact\n"); );
    Vtb_s2a_backend_fault_recovery__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    CData/*0:0*/ __VinactExecute;
    // Body
    __VinactExecute = vlSelfRef.__VdlySched.awaitingZeroDelay();
    if (__VinactExecute) {
        VL_FATAL_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 2, "", "ZERODLY: Design Verilated with '--no-sched-zero-delay', but #0 delay executed at runtime");
    }
    return (__VinactExecute);
}

void Vtb_s2a_backend_fault_recovery___024root___trigger_clear__act(VlUnpacked<QData/*63:0*/, 1> &out) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root___trigger_clear__act\n"); );
    // Locals
    IData/*31:0*/ n;
    // Body
    n = 0U;
    do {
        out[n] = 0ULL;
        n = ((IData)(1U) + n);
    } while ((1U > n));
}

void Vtb_s2a_backend_fault_recovery___024root___nba_sequent__TOP__0(Vtb_s2a_backend_fault_recovery___024root* vlSelf);

bool Vtb_s2a_backend_fault_recovery___024root___eval_phase__nba(Vtb_s2a_backend_fault_recovery___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root___eval_phase__nba\n"); );
    Vtb_s2a_backend_fault_recovery__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    CData/*0:0*/ __VnbaExecute;
    // Body
    __VnbaExecute = Vtb_s2a_backend_fault_recovery___024root___trigger_anySet__act(vlSelfRef.__VnbaTriggered);
    if (__VnbaExecute) {
        {
            // Inlined CFunc: _eval_nba
            if ((1ULL & vlSelfRef.__VnbaTriggered[0U])) {
                Vtb_s2a_backend_fault_recovery___024root___nba_sequent__TOP__0(vlSelf);
                vlSelfRef.__Vm_traceActivity[5U] = 1U;
            }
            if ((7ULL & vlSelfRef.__VnbaTriggered[0U])) {
                Vtb_s2a_backend_fault_recovery___024root___nba_comb__TOP__0(vlSelf);
                vlSelfRef.__Vm_traceActivity[6U] = 1U;
            }
        }
        Vtb_s2a_backend_fault_recovery___024root___trigger_clear__act(vlSelfRef.__VnbaTriggered);
    }
    return (__VnbaExecute);
}

void Vtb_s2a_backend_fault_recovery___024root___eval(Vtb_s2a_backend_fault_recovery___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root___eval\n"); );
    Vtb_s2a_backend_fault_recovery__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    IData/*31:0*/ __VnbaIterCount;
    // Body
    __VnbaIterCount = 0U;
    do {
        if (VL_UNLIKELY(((0x00002710U < __VnbaIterCount)))) {
#ifdef VL_DEBUG
            Vtb_s2a_backend_fault_recovery___024root___dump_triggers__act(vlSelfRef.__VnbaTriggered, "nba"s);
#endif
            VL_FATAL_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 2, "", "DIDNOTCONVERGE: NBA region did not converge after '--converge-limit' of 10000 tries");
        }
        __VnbaIterCount = ((IData)(1U) + __VnbaIterCount);
        vlSelfRef.__VinactIterCount = 0U;
        do {
            if (VL_UNLIKELY(((0x00002710U < vlSelfRef.__VinactIterCount)))) {
                VL_FATAL_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 2, "", "DIDNOTCONVERGE: Inactive region did not converge after '--converge-limit' of 10000 tries");
            }
            vlSelfRef.__VinactIterCount = ((IData)(1U) 
                                           + vlSelfRef.__VinactIterCount);
            vlSelfRef.__VactIterCount = 0U;
            do {
                if (VL_UNLIKELY(((0x00002710U < vlSelfRef.__VactIterCount)))) {
#ifdef VL_DEBUG
                    Vtb_s2a_backend_fault_recovery___024root___dump_triggers__act(vlSelfRef.__VactTriggered, "act"s);
#endif
                    VL_FATAL_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 2, "", "DIDNOTCONVERGE: Active region did not converge after '--converge-limit' of 10000 tries");
                }
                vlSelfRef.__VactIterCount = ((IData)(1U) 
                                             + vlSelfRef.__VactIterCount);
                vlSelfRef.__VactPhaseResult = Vtb_s2a_backend_fault_recovery___024root___eval_phase__act(vlSelf);
            } while (vlSelfRef.__VactPhaseResult);
            vlSelfRef.__VinactPhaseResult = Vtb_s2a_backend_fault_recovery___024root___eval_phase__inact(vlSelf);
        } while (vlSelfRef.__VinactPhaseResult);
        vlSelfRef.__VnbaPhaseResult = Vtb_s2a_backend_fault_recovery___024root___eval_phase__nba(vlSelf);
    } while (vlSelfRef.__VnbaPhaseResult);
}

void Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(Vtb_s2a_backend_fault_recovery___024root* vlSelf, const char* __VeventDescription) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0\n"); );
    Vtb_s2a_backend_fault_recovery__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    VlUnpacked<QData/*63:0*/, 1> __VTmp;
    // Body
    __VTmp[0U] = (QData)((IData)(((((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__clk)) 
                                    & (IData)(vlSelfRef.__Vtrigprevexpr___TOP__tb_s2a_backend_fault_recovery__DOT__clk__0)) 
                                   << 2U) | ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__clk) 
                                             & (~ (IData)(vlSelfRef.__Vtrigprevexpr___TOP__tb_s2a_backend_fault_recovery__DOT__clk__0))))));
    vlSelfRef.__Vtrigprevexpr___TOP__tb_s2a_backend_fault_recovery__DOT__clk__0 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__clk;
    if ((1ULL & __VTmp[0U])) {
        vlSelfRef.__VtrigSched_h3193e288__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e288__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e288__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e288__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e288__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e288__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e288__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e288__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e288__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e288__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e288__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e288__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e288__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e288__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e288__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e288__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e288__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e288__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e288__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e288__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e288__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e288__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e288__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e288__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e288__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e288__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e288__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e288__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e288__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e288__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e288__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e288__0.ready(__VeventDescription);
    }
    if ((4ULL & __VTmp[0U])) {
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
    }
    vlSelfRef.__VactTriggeredAcc[0U] = (vlSelfRef.__VactTriggeredAcc[0U] 
                                        | __VTmp[0U]);
}

void Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e288__0(Vtb_s2a_backend_fault_recovery___024root* vlSelf, const char* __VeventDescription) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e288__0\n"); );
    Vtb_s2a_backend_fault_recovery__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    VlUnpacked<QData/*63:0*/, 1> __VTmp;
    // Body
    __VTmp[0U] = (QData)((IData)(((((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__clk)) 
                                    & (IData)(vlSelfRef.__Vtrigprevexpr___TOP__tb_s2a_backend_fault_recovery__DOT__clk__0)) 
                                   << 2U) | ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__clk) 
                                             & (~ (IData)(vlSelfRef.__Vtrigprevexpr___TOP__tb_s2a_backend_fault_recovery__DOT__clk__0))))));
    vlSelfRef.__Vtrigprevexpr___TOP__tb_s2a_backend_fault_recovery__DOT__clk__0 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__clk;
    if ((1ULL & __VTmp[0U])) {
        vlSelfRef.__VtrigSched_h3193e288__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e288__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e288__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e288__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e288__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e288__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e288__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e288__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e288__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e288__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e288__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e288__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e288__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e288__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e288__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e288__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e288__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e288__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e288__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e288__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e288__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e288__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e288__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e288__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e288__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e288__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e288__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e288__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e288__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e288__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e288__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e288__0.ready(__VeventDescription);
    }
    if ((4ULL & __VTmp[0U])) {
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h3193e339__0.ready(__VeventDescription);
    }
    vlSelfRef.__VactTriggeredAcc[0U] = (vlSelfRef.__VactTriggeredAcc[0U] 
                                        | __VTmp[0U]);
}

#ifdef VL_DEBUG
void Vtb_s2a_backend_fault_recovery___024root___eval_debug_assertions(Vtb_s2a_backend_fault_recovery___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root___eval_debug_assertions\n"); );
    Vtb_s2a_backend_fault_recovery__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
}
#endif  // VL_DEBUG
