// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vtb_combined.h for the primary calling header

#include "Vtb_combined__pch.h"

VL_ATTR_COLD void Vtb_combined___024root___eval_static__TOP__1(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___timing_ready(Vtb_combined___024root* vlSelf);

VL_ATTR_COLD void Vtb_combined___024root___eval_static(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___eval_static\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    {
        // Inlined CFunc: _eval_static__TOP
        Vtb_combined___024root___eval_static__TOP__1(vlSelf);
        {
            // Inlined CFunc: _eval_static__TOP__2
            vlSelfRef.tb_combined__DOT__feature_test__DOT__count = 0U;
        }
        vlSelfRef.tb_combined__DOT__feature_test__DOT__branch_count[0U] = 0U;
        vlSelfRef.tb_combined__DOT__feature_test__DOT__branch_count[1U] = 0U;
        vlSelfRef.tb_combined__DOT__feature_test__DOT__branch_count[2U] = 0U;
        vlSelfRef.tb_combined__DOT__feature_test__DOT__branch_count[3U] = 0U;
    }
    vlSelfRef.__VactTriggered[0U] = (8ULL | vlSelfRef.__VactTriggered[0U]);
    vlSelfRef.__Vtrigprevexpr___TOP__tb_combined__DOT__boundary_test__DOT__clk__0 = 0U;
    vlSelfRef.__Vtrigprevexpr___TOP__tb_combined__DOT__feature_test__DOT__clk__0 = 0U;
    vlSelfRef.__Vtrigprevexpr_h6f3df181__1 = 0U;
    Vtb_combined___024root___timing_ready(vlSelf);
    do {
        vlSelfRef.__VactTriggeredAcc[vlSelfRef.__Vi] 
            = vlSelfRef.__VactTriggered[vlSelfRef.__Vi];
        vlSelfRef.__Vi = ((IData)(1U) + vlSelfRef.__Vi);
    } while ((0U >= vlSelfRef.__Vi));
}

VL_ATTR_COLD void Vtb_combined___024root___eval_static__TOP__0(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___eval_static__TOP__0\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.tb_combined__DOT__boundary_done = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__clk = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__hard_reset = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__abort = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__buffer_owner_pl = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__start_valid = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__start_ready = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__layer_index = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__weight_layer_index = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__input_base_address = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__input_length_bytes = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__input_batch_count = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__input_channels = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__input_height = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__input_width = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__output_base_address = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__output_length_bytes = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__output_batch_count = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__output_channels = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__output_height = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__output_width = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__kernel_height = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__kernel_width = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__stride_y = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__stride_x = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__pad_left = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__pad_right = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__pad_top = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__pad_bottom = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__groups = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__padding_value_int8 = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__weight_package_base_address = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__weight_package_length_bytes = 0U;
}

VL_ATTR_COLD void Vtb_combined___024root___eval_static__TOP__1(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___eval_static__TOP__1\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    Vtb_combined___024root___eval_static__TOP__0(vlSelf);
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__quantized_weight_offset = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__quantized_weight_bytes = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__output_batch = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__activation_mode = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_cancel = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_valid = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_ready = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_write = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_addr = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_wdata = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_rstrb = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_wstrb = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_valid = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_rdata = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_error = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__busy = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__result_valid = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__result_ready = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__result_error_code = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__compare_cycles = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__cycles = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__cases = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__pending = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__delay_count = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__requests = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__error_code = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__error_request = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__raw_invalid = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__abort_mask = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__reset_mask = 0U;
    vlSelfRef.tb_combined__DOT__feature_done = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__clk = 0U;
}

VL_ATTR_COLD void Vtb_combined___024root___eval_final(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___eval_final\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
}

#ifdef VL_DEBUG
VL_ATTR_COLD void Vtb_combined___024root___dump_triggers__stl(const VlUnpacked<QData/*63:0*/, 1> &triggers, const std::string &tag);
#endif  // VL_DEBUG
VL_ATTR_COLD bool Vtb_combined___024root___eval_phase__stl(Vtb_combined___024root* vlSelf);

VL_ATTR_COLD void Vtb_combined___024root___eval_settle(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___eval_settle\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    IData/*31:0*/ __VstlIterCount;
    // Body
    __VstlIterCount = 0U;
    vlSelfRef.__VstlFirstIteration = 1U;
    do {
        if (VL_UNLIKELY(((0x00002710U < __VstlIterCount)))) {
#ifdef VL_DEBUG
            Vtb_combined___024root___dump_triggers__stl(vlSelfRef.__VstlTriggered, "stl"s);
#endif
            VL_FATAL_MT("tb_combined.sv", 3, "", "DIDNOTCONVERGE: Settle region did not converge after '--converge-limit' of 10000 tries");
        }
        __VstlIterCount = ((IData)(1U) + __VstlIterCount);
        vlSelfRef.__VstlPhaseResult = Vtb_combined___024root___eval_phase__stl(vlSelf);
        vlSelfRef.__VstlFirstIteration = 0U;
    } while (vlSelfRef.__VstlPhaseResult);
}

VL_ATTR_COLD bool Vtb_combined___024root___trigger_anySet__stl(const VlUnpacked<QData/*63:0*/, 1> &in);

#ifdef VL_DEBUG
VL_ATTR_COLD void Vtb_combined___024root___dump_triggers__stl(const VlUnpacked<QData/*63:0*/, 1> &triggers, const std::string &tag) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___dump_triggers__stl\n"); );
    // Body
    if ((1U & (~ (IData)(Vtb_combined___024root___trigger_anySet__stl(triggers))))) {
        VL_DBG_MSGS("         No '" + tag + "' region triggers active\n");
    }
    if ((1U & (IData)(triggers[0U]))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 0 is active: Internal 'stl' trigger - first iteration\n");
    }
}
#endif  // VL_DEBUG

VL_ATTR_COLD bool Vtb_combined___024root___trigger_anySet__stl(const VlUnpacked<QData/*63:0*/, 1> &in) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___trigger_anySet__stl\n"); );
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

VL_ATTR_COLD void Vtb_combined___024root___stl_sequent__TOP__0(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___stl_sequent__TOP__0\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__busy 
        = (0U != (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state));
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__result_valid 
        = (0x13U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state));
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_addr 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__request_address_latched;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_wdata 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__request_wdata_latched;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__result_error_code 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__result_error_latched;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__request_byte_lane 
        = (3U & (0x00030210U >> ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__request_strobe_latched) 
                                 << 1U)));
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__request_byte_lane 
        = (3U & (0x00030210U >> ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__request_strobe_latched) 
                                 << 1U)));
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__candidate_backend_req_valid = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__candidate_backend_req_write = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_write = 0U;
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
        } else if ((0x10U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state))) {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_write = 1U;
        }
    }
}

VL_ATTR_COLD void Vtb_combined___024root___stl_sequent__TOP__1(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___stl_sequent__TOP__1\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_valid = 0U;
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
    if ((1U & ((~ (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__hard_reset)) 
               & (~ (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__abort))))) {
        if (((4U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state)) 
             || (8U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state)))) {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_valid = 1U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_rstrb 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__request_strobe_latched;
        } else if ((0x10U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state))) {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_valid = 1U;
        }
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
    }
}

VL_ATTR_COLD void Vtb_combined___024root___stl_sequent__TOP__2(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___stl_sequent__TOP__2\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_wstrb = 0U;
    if ((1U & ((~ (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__hard_reset)) 
               & (~ (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__abort))))) {
        if ((1U & (~ ((4U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state)) 
                      || (8U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state)))))) {
            if ((0x10U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state))) {
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_wstrb 
                    = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__request_strobe_latched;
            }
        }
    }
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__candidate_backend_cancel 
        = ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__hard_reset) 
           | (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__abort));
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_source_address_wide 
        = ((QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_package_base_latched)) 
           + ((QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__quantized_weight_offset_latched)) 
              + ((QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_reduction_index)) 
                 + ((QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__reduction_count_latched)) 
                    * (QData)((IData)((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_group_base 
                                       + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_lane_index)))))));
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_source_address_wide 
        = ((QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_package_base_latched)) 
           + ((QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__quantized_weight_offset_latched)) 
              + ((QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_reduction_index)) 
                 + ((QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__reduction_count_latched)) 
                    * (QData)((IData)((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_group_base 
                                       + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_lane_index)))))));
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_source_address_wide 
        = ((QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_package_base_latched)) 
           + ((QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__quantized_weight_offset_latched)) 
              + ((QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_reduction_index)) 
                 + ((QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__reduction_count_latched)) 
                    * (QData)((IData)((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_group_base 
                                       + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_lane_index)))))));
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_source_address_wide 
        = ((QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_package_base_latched)) 
           + ((QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__quantized_weight_offset_latched)) 
              + ((QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_reduction_index)) 
                 + ((QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__reduction_count_latched)) 
                    * (QData)((IData)((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_group_base 
                                       + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_lane_index)))))));
}

VL_ATTR_COLD void Vtb_combined___024root___stl_sequent__TOP__3(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___stl_sequent__TOP__3\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_byte_offset_wide 
        = (((QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_width_latched)) 
            * ((QData)((IData)((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_group_base 
                                + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_lane_index))) 
               * (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_height_latched)))) 
           + ((QData)((IData)((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_point_scan_x 
                               + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_start_x))) 
              + ((QData)((IData)((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_point_scan_y 
                                  + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_start_y))) 
                 * (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_width_latched)))));
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_byte_offset_wide 
        = ((QData)((IData)((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_point_scan_x 
                            + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_start_x))) 
           + ((QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_width_latched)) 
              * ((QData)((IData)((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_point_scan_y 
                                  + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_start_y))) 
                 + ((QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_height_latched)) 
                    * (QData)((IData)((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_group_base 
                                       + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_lane_index)))))));
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_byte_offset_wide 
        = (((QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_height_latched)) 
            * ((QData)((IData)((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_group_base 
                                + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_lane_index))) 
               * (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_width_latched)))) 
           + ((QData)((IData)((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__tile_start_x 
                               + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_point_scan_x))) 
              + ((QData)((IData)((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__tile_start_y 
                                  + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_point_scan_y))) 
                 * (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_width_latched)))));
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_byte_offset_wide 
        = (((QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_height_latched)) 
            * ((QData)((IData)((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_group_base 
                                + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_lane_index))) 
               * (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_width_latched)))) 
           + ((QData)((IData)((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__tile_start_x 
                               + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_point_scan_x))) 
              + ((QData)((IData)((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__tile_start_y 
                                  + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_point_scan_y))) 
                 * (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_width_latched)))));
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_index = 0U;
}

VL_ATTR_COLD void Vtb_combined___024root___stl_sequent__TOP__4(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___stl_sequent__TOP__4\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_parameter[0U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_parameter[1U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_parameter[2U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_bias = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_invalid = 0U;
    if (((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_lane 
          < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__group_lane_count) 
         & (0x00000026U > vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__layer_index_latched))) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_index 
            = ((((0x25U >= (0x0000003fU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__layer_index_latched))
                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                 [(0x0000003fU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__layer_index_latched)]
                  : 0U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_group_base) 
               + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_lane);
        if ((0x00000c5cU > vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_index)) {
            if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_index))) {
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_parameter[0U] 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                    [(0x00000fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_index)][0U];
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_parameter[1U] 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                    [(0x00000fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_index)][1U];
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_parameter[2U] 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                    [(0x00000fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_index)][2U];
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_bias 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_CONV_BIAS_ACCUMULATOR_INT32
                    [(0x00000fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_index)];
            } else {
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_parameter[0U] = 0U;
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_parameter[1U] = 0U;
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_parameter[2U] = 0U;
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_bias = 0U;
            }
            if (((((((((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_index 
                        >= (((0x25U >= (0x0000003fU 
                                        & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__layer_index_latched))
                              ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                             [(0x0000003fU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__layer_index_latched)]
                              : 0U) + ((0x25U >= (0x0000003fU 
                                                  & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__layer_index_latched))
                                        ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                                       [(0x0000003fU 
                                         & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__layer_index_latched)]
                                        : 0U))) | (0U 
                                                   == 
                                                   ((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_parameter[2U] 
                                                     << 0x00000010U) 
                                                    | (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_parameter[1U] 
                                                       >> 0x00000010U)))) 
                      | (0U == ((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_parameter[1U] 
                                 << 0x00000018U) | 
                                (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_parameter[0U] 
                                 >> 8U)))) | (0x3fffffffU 
                                              < ((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_parameter[2U] 
                                                  << 0x00000010U) 
                                                 | (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_parameter[1U] 
                                                    >> 0x00000010U)))) 
                    | (0x3fffffffU < ((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_parameter[1U] 
                                       << 0x00000018U) 
                                      | (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_parameter[0U] 
                                         >> 8U)))) 
                   | (0x2fU < (0x000000ffU & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_parameter[1U] 
                                              >> 8U)))) 
                  | (0x2fU < (0x000000ffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_parameter[0U]))) 
                 | ((0U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__activation_mode_latched)) 
                    & ((((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_parameter[2U] 
                          << 0x00000010U) | (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_parameter[1U] 
                                             >> 0x00000010U)) 
                        != ((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_parameter[1U] 
                             << 0x00000018U) | (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_parameter[0U] 
                                                >> 8U))) 
                       | ((0x000000ffU & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_parameter[1U] 
                                          >> 8U)) != 
                          (0x000000ffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_parameter[0U])))))) {
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_invalid = 1U;
            }
        } else {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_invalid = 1U;
        }
    } else if ((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_lane 
                < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__group_lane_count)) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_invalid = 1U;
    }
}

VL_ATTR_COLD void Vtb_combined___024root___stl_sequent__TOP__5(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___stl_sequent__TOP__5\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    IData/*31:0*/ tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_index;
    tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_index = 0;
    // Body
    tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_index = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_parameter[0U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_parameter[1U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_parameter[2U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_bias = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_invalid = 0U;
    if (((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_lane 
          < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__group_lane_count) 
         & (0x00000026U > vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__layer_index_latched))) {
        tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_index 
            = ((((0x25U >= (0x0000003fU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__layer_index_latched))
                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                 [(0x0000003fU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__layer_index_latched)]
                  : 0U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_group_base) 
               + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_lane);
        if ((0x00000c5cU > tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_index)) {
            if ((0x0c5bU >= (0x00000fffU & tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_index))) {
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_parameter[0U] 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                    [(0x00000fffU & tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_index)][0U];
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_parameter[1U] 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                    [(0x00000fffU & tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_index)][1U];
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_parameter[2U] 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                    [(0x00000fffU & tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_index)][2U];
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_bias 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_CONV_BIAS_ACCUMULATOR_INT32
                    [(0x00000fffU & tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_index)];
            } else {
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_parameter[0U] = 0U;
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_parameter[1U] = 0U;
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_parameter[2U] = 0U;
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_bias = 0U;
            }
            if (((((((((tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_index 
                        >= (((0x25U >= (0x0000003fU 
                                        & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__layer_index_latched))
                              ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                             [(0x0000003fU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__layer_index_latched)]
                              : 0U) + ((0x25U >= (0x0000003fU 
                                                  & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__layer_index_latched))
                                        ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                                       [(0x0000003fU 
                                         & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__layer_index_latched)]
                                        : 0U))) | (0U 
                                                   == 
                                                   ((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_parameter[2U] 
                                                     << 0x00000010U) 
                                                    | (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_parameter[1U] 
                                                       >> 0x00000010U)))) 
                      | (0U == ((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_parameter[1U] 
                                 << 0x00000018U) | 
                                (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_parameter[0U] 
                                 >> 8U)))) | (0x3fffffffU 
                                              < ((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_parameter[2U] 
                                                  << 0x00000010U) 
                                                 | (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_parameter[1U] 
                                                    >> 0x00000010U)))) 
                    | (0x3fffffffU < ((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_parameter[1U] 
                                       << 0x00000018U) 
                                      | (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_parameter[0U] 
                                         >> 8U)))) 
                   | (0x2fU < (0x000000ffU & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_parameter[1U] 
                                              >> 8U)))) 
                  | (0x2fU < (0x000000ffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_parameter[0U]))) 
                 | ((0U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__activation_mode_latched)) 
                    & ((((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_parameter[2U] 
                          << 0x00000010U) | (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_parameter[1U] 
                                             >> 0x00000010U)) 
                        != ((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_parameter[1U] 
                             << 0x00000018U) | (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_parameter[0U] 
                                                >> 8U))) 
                       | ((0x000000ffU & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_parameter[1U] 
                                          >> 8U)) != 
                          (0x000000ffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_parameter[0U])))))) {
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_invalid = 1U;
            }
        } else {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_invalid = 1U;
        }
    } else if ((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_lane 
                < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__group_lane_count)) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_invalid = 1U;
    }
}

VL_ATTR_COLD void Vtb_combined___024root___stl_sequent__TOP__6(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___stl_sequent__TOP__6\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    IData/*31:0*/ tb_combined__DOT__feature_test__DOT__u_dut__DOT__mq_prefetch_index;
    tb_combined__DOT__feature_test__DOT__u_dut__DOT__mq_prefetch_index = 0;
    // Body
    tb_combined__DOT__feature_test__DOT__u_dut__DOT__mq_prefetch_index = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__mq_prefetch_parameter[0U] = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__mq_prefetch_parameter[1U] = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__mq_prefetch_parameter[2U] = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__mq_prefetch_bias = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__mq_prefetch_invalid = 0U;
    if (((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__mq_prefetch_lane 
          < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__group_lane_count) 
         & (0x00000026U > vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__layer_index_latched))) {
        tb_combined__DOT__feature_test__DOT__u_dut__DOT__mq_prefetch_index 
            = ((((0x25U >= (0x0000003fU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__layer_index_latched))
                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                 [(0x0000003fU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__layer_index_latched)]
                  : 0U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_group_base) 
               + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__mq_prefetch_lane);
        if ((0x00000c5cU > tb_combined__DOT__feature_test__DOT__u_dut__DOT__mq_prefetch_index)) {
            if ((0x0c5bU >= (0x00000fffU & tb_combined__DOT__feature_test__DOT__u_dut__DOT__mq_prefetch_index))) {
                vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__mq_prefetch_parameter[0U] 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                    [(0x00000fffU & tb_combined__DOT__feature_test__DOT__u_dut__DOT__mq_prefetch_index)][0U];
                vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__mq_prefetch_parameter[1U] 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                    [(0x00000fffU & tb_combined__DOT__feature_test__DOT__u_dut__DOT__mq_prefetch_index)][1U];
                vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__mq_prefetch_parameter[2U] 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                    [(0x00000fffU & tb_combined__DOT__feature_test__DOT__u_dut__DOT__mq_prefetch_index)][2U];
                vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__mq_prefetch_bias 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_CONV_BIAS_ACCUMULATOR_INT32
                    [(0x00000fffU & tb_combined__DOT__feature_test__DOT__u_dut__DOT__mq_prefetch_index)];
            } else {
                vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__mq_prefetch_parameter[0U] = 0U;
                vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__mq_prefetch_parameter[1U] = 0U;
                vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__mq_prefetch_parameter[2U] = 0U;
                vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__mq_prefetch_bias = 0U;
            }
            if (((((((((tb_combined__DOT__feature_test__DOT__u_dut__DOT__mq_prefetch_index 
                        >= (((0x25U >= (0x0000003fU 
                                        & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__layer_index_latched))
                              ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                             [(0x0000003fU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__layer_index_latched)]
                              : 0U) + ((0x25U >= (0x0000003fU 
                                                  & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__layer_index_latched))
                                        ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                                       [(0x0000003fU 
                                         & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__layer_index_latched)]
                                        : 0U))) | (0U 
                                                   == 
                                                   ((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__mq_prefetch_parameter[2U] 
                                                     << 0x00000010U) 
                                                    | (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__mq_prefetch_parameter[1U] 
                                                       >> 0x00000010U)))) 
                      | (0U == ((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__mq_prefetch_parameter[1U] 
                                 << 0x00000018U) | 
                                (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__mq_prefetch_parameter[0U] 
                                 >> 8U)))) | (0x3fffffffU 
                                              < ((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__mq_prefetch_parameter[2U] 
                                                  << 0x00000010U) 
                                                 | (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__mq_prefetch_parameter[1U] 
                                                    >> 0x00000010U)))) 
                    | (0x3fffffffU < ((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__mq_prefetch_parameter[1U] 
                                       << 0x00000018U) 
                                      | (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__mq_prefetch_parameter[0U] 
                                         >> 8U)))) 
                   | (0x2fU < (0x000000ffU & (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__mq_prefetch_parameter[1U] 
                                              >> 8U)))) 
                  | (0x2fU < (0x000000ffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__mq_prefetch_parameter[0U]))) 
                 | ((0U == (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__activation_mode_latched)) 
                    & ((((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__mq_prefetch_parameter[2U] 
                          << 0x00000010U) | (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__mq_prefetch_parameter[1U] 
                                             >> 0x00000010U)) 
                        != ((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__mq_prefetch_parameter[1U] 
                             << 0x00000018U) | (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__mq_prefetch_parameter[0U] 
                                                >> 8U))) 
                       | ((0x000000ffU & (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__mq_prefetch_parameter[1U] 
                                          >> 8U)) != 
                          (0x000000ffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__mq_prefetch_parameter[0U])))))) {
                vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__mq_prefetch_invalid = 1U;
            }
        } else {
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__mq_prefetch_invalid = 1U;
        }
    } else if ((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__mq_prefetch_lane 
                < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__group_lane_count)) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__mq_prefetch_invalid = 1U;
    }
}

VL_ATTR_COLD void Vtb_combined___024root___stl_sequent__TOP__7(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___stl_sequent__TOP__7\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    IData/*31:0*/ tb_combined__DOT__feature_test__DOT__u_old__DOT__mq_prefetch_index;
    tb_combined__DOT__feature_test__DOT__u_old__DOT__mq_prefetch_index = 0;
    // Body
    tb_combined__DOT__feature_test__DOT__u_old__DOT__mq_prefetch_index = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__mq_prefetch_parameter[0U] = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__mq_prefetch_parameter[1U] = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__mq_prefetch_parameter[2U] = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__mq_prefetch_bias = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__mq_prefetch_invalid = 0U;
    if (((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__mq_prefetch_lane 
          < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__group_lane_count) 
         & (0x00000026U > vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__layer_index_latched))) {
        tb_combined__DOT__feature_test__DOT__u_old__DOT__mq_prefetch_index 
            = ((((0x25U >= (0x0000003fU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__layer_index_latched))
                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                 [(0x0000003fU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__layer_index_latched)]
                  : 0U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_group_base) 
               + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__mq_prefetch_lane);
        if ((0x00000c5cU > tb_combined__DOT__feature_test__DOT__u_old__DOT__mq_prefetch_index)) {
            if ((0x0c5bU >= (0x00000fffU & tb_combined__DOT__feature_test__DOT__u_old__DOT__mq_prefetch_index))) {
                vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__mq_prefetch_parameter[0U] 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                    [(0x00000fffU & tb_combined__DOT__feature_test__DOT__u_old__DOT__mq_prefetch_index)][0U];
                vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__mq_prefetch_parameter[1U] 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                    [(0x00000fffU & tb_combined__DOT__feature_test__DOT__u_old__DOT__mq_prefetch_index)][1U];
                vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__mq_prefetch_parameter[2U] 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                    [(0x00000fffU & tb_combined__DOT__feature_test__DOT__u_old__DOT__mq_prefetch_index)][2U];
                vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__mq_prefetch_bias 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_CONV_BIAS_ACCUMULATOR_INT32
                    [(0x00000fffU & tb_combined__DOT__feature_test__DOT__u_old__DOT__mq_prefetch_index)];
            } else {
                vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__mq_prefetch_parameter[0U] = 0U;
                vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__mq_prefetch_parameter[1U] = 0U;
                vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__mq_prefetch_parameter[2U] = 0U;
                vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__mq_prefetch_bias = 0U;
            }
            if (((((((((tb_combined__DOT__feature_test__DOT__u_old__DOT__mq_prefetch_index 
                        >= (((0x25U >= (0x0000003fU 
                                        & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__layer_index_latched))
                              ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                             [(0x0000003fU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__layer_index_latched)]
                              : 0U) + ((0x25U >= (0x0000003fU 
                                                  & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__layer_index_latched))
                                        ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                                       [(0x0000003fU 
                                         & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__layer_index_latched)]
                                        : 0U))) | (0U 
                                                   == 
                                                   ((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__mq_prefetch_parameter[2U] 
                                                     << 0x00000010U) 
                                                    | (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__mq_prefetch_parameter[1U] 
                                                       >> 0x00000010U)))) 
                      | (0U == ((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__mq_prefetch_parameter[1U] 
                                 << 0x00000018U) | 
                                (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__mq_prefetch_parameter[0U] 
                                 >> 8U)))) | (0x3fffffffU 
                                              < ((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__mq_prefetch_parameter[2U] 
                                                  << 0x00000010U) 
                                                 | (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__mq_prefetch_parameter[1U] 
                                                    >> 0x00000010U)))) 
                    | (0x3fffffffU < ((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__mq_prefetch_parameter[1U] 
                                       << 0x00000018U) 
                                      | (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__mq_prefetch_parameter[0U] 
                                         >> 8U)))) 
                   | (0x2fU < (0x000000ffU & (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__mq_prefetch_parameter[1U] 
                                              >> 8U)))) 
                  | (0x2fU < (0x000000ffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__mq_prefetch_parameter[0U]))) 
                 | ((0U == (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__activation_mode_latched)) 
                    & ((((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__mq_prefetch_parameter[2U] 
                          << 0x00000010U) | (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__mq_prefetch_parameter[1U] 
                                             >> 0x00000010U)) 
                        != ((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__mq_prefetch_parameter[1U] 
                             << 0x00000018U) | (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__mq_prefetch_parameter[0U] 
                                                >> 8U))) 
                       | ((0x000000ffU & (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__mq_prefetch_parameter[1U] 
                                          >> 8U)) != 
                          (0x000000ffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__mq_prefetch_parameter[0U])))))) {
                vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__mq_prefetch_invalid = 1U;
            }
        } else {
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__mq_prefetch_invalid = 1U;
        }
    } else if ((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__mq_prefetch_lane 
                < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__group_lane_count)) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__mq_prefetch_invalid = 1U;
    }
}

VL_ATTR_COLD void Vtb_combined___024root___stl_sequent__TOP__26(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___stl_sequent__TOP__26\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
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
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__patch_plane_bytes 
        = ((QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__patch_height)) 
           * (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__patch_width)));
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_input_y = 0ULL;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_input_x = 0ULL;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_in_bounds = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_advance = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_source_offset = 0ULL;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_source_address_wide = 0ULL;
    if (((0ULL != vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__patch_plane_bytes) 
         & (0U != vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__patch_width))) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_input_y 
            = ((((QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__tile_start_y)) 
                 * (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__stride_y_latched))) 
                + (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_y))) 
               - (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__pad_top_latched)));
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_input_x 
            = ((((QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__tile_start_x)) 
                 * (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__stride_x_latched))) 
                + (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_x))) 
               - (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__pad_left_latched)));
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_in_bounds 
            = (((VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_input_y) 
                 & VL_LTS_IQQ(64, vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_input_y, (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__input_height_latched)))) 
                & VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_input_x)) 
               & VL_LTS_IQQ(64, vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_input_x, (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__input_width_latched))));
        if (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_in_bounds) {
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_source_offset 
                = (((((QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_channel)) 
                      * (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__input_height_latched))) 
                     + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_input_y) 
                    * (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__input_width_latched))) 
                   + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_input_x);
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_source_address_wide 
                = ((QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__input_base_latched)) 
                   + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_source_offset);
        }
    }
}

VL_ATTR_COLD void Vtb_combined___024root___stl_sequent__TOP__37(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___stl_sequent__TOP__37\n"); );
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
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__mapped_response_error = 6U;
    if ((0U == (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__v_rsp_error))) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__mapped_response_error = 0U;
    } else if ((((1U == (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__v_rsp_error)) 
                 | (2U == (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__v_rsp_error))) 
                | (6U == (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__v_rsp_error)))) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__mapped_response_error 
            = vlSelfRef.tb_combined__DOT__feature_test__DOT__v_rsp_error;
    }
    if ((((3U == (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__state)) 
          & (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_index 
             < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__patch_byte_count)) 
         & (~ (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_in_bounds)))) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_advance = 1U;
    } else if ((((5U == (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__state)) 
                 & (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__v_rsp_valid)) 
                & (0U == (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__mapped_response_error)))) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_advance = 1U;
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

VL_ATTR_COLD void Vtb_combined___024root___stl_sequent__TOP__48(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___stl_sequent__TOP__48\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    QData/*63:0*/ tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_channel_plane_offset;
    tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_channel_plane_offset = 0;
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
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__patch_plane_bytes 
        = ((QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__patch_height)) 
           * (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__patch_width)));
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_input_y = 0ULL;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_input_x = 0ULL;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_in_bounds = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_advance = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_geometry_plane = 0ULL;
    tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_channel_plane_offset = 0ULL;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_row_offset = 0ULL;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_source_offset = 0ULL;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_source_address_wide = 0ULL;
    if (((0ULL != vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__patch_plane_bytes) 
         & (0U != vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__patch_width))) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_input_y 
            = ((((QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__tile_start_y)) 
                 * (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__stride_y_latched))) 
                + (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_y))) 
               - (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__pad_top_latched)));
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_input_x 
            = ((((QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__tile_start_x)) 
                 * (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__stride_x_latched))) 
                + (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_x))) 
               - (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__pad_left_latched)));
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_in_bounds 
            = (((VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_input_y) 
                 & VL_LTS_IQQ(64, vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_input_y, (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__input_height_latched)))) 
                & VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_input_x)) 
               & VL_LTS_IQQ(64, vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_input_x, (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__input_width_latched))));
        if (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_in_bounds) {
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_geometry_plane 
                = ((QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__input_height_latched)) 
                   * (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__input_width_latched)));
            tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_channel_plane_offset 
                = ((QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_channel)) 
                   * vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_geometry_plane);
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_row_offset 
                = ((QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_input_y)) 
                   * (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__input_width_latched)));
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_source_offset 
                = ((tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_channel_plane_offset 
                    + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_row_offset) 
                   + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_input_x);
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_source_address_wide 
                = ((QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__input_base_latched)) 
                   + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_source_offset);
        }
    }
}

VL_ATTR_COLD void Vtb_combined___024root___stl_sequent__TOP__59(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___stl_sequent__TOP__59\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__mapped_response_error = 6U;
    if ((0U == (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__v_rsp_error))) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__mapped_response_error = 0U;
    } else if ((((1U == (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__v_rsp_error)) 
                 | (2U == (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__v_rsp_error))) 
                | (6U == (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__v_rsp_error)))) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__mapped_response_error 
            = vlSelfRef.tb_combined__DOT__feature_test__DOT__v_rsp_error;
    }
    if ((((3U == (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__state)) 
          & (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_index 
             < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__patch_byte_count)) 
         & (~ (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_in_bounds)))) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_advance = 1U;
    } else if ((((5U == (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__state)) 
                 & (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__v_rsp_valid)) 
                & (0U == (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__mapped_response_error)))) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_advance = 1U;
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

VL_ATTR_COLD void Vtb_combined___024root___stl_sequent__TOP__63(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___stl_sequent__TOP__63\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_cancel 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__candidate_backend_cancel;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_address_wide 
        = ((QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_base_latched)) 
           + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_byte_offset_wide);
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_address_wide 
        = ((QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_base_latched)) 
           + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_byte_offset_wide);
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_address_wide 
        = ((QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_base_latched)) 
           + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_byte_offset_wide);
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_address_wide 
        = ((QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_base_latched)) 
           + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_byte_offset_wide);
}

void Vtb_combined___024root___nba_sequent__TOP__65(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__63(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__27(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__25(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_comb__TOP__24(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_comb__TOP__25(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_comb__TOP__4(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_comb__TOP__5(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_comb__TOP__6(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_comb__TOP__7(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_comb__TOP__8(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_comb__TOP__9(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_comb__TOP__10(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_comb__TOP__11(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_comb__TOP__12(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_comb__TOP__13(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_comb__TOP__14(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_comb__TOP__15(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_sequent__TOP__1(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_sequent__TOP__2(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_sequent__TOP__3(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_sequent__TOP__4(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_sequent__TOP__5(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_sequent__TOP__6(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_sequent__TOP__7(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_sequent__TOP__8(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_sequent__TOP__9(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_sequent__TOP__10(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_comb__TOP__17(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_comb__TOP__18(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_comb__TOP__19(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_comb__TOP__20(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_comb__TOP__21(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_comb__TOP__22(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_comb__TOP__23(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_comb__TOP__24(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_comb__TOP__25(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_comb__TOP__26(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_sequent__TOP__12(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_sequent__TOP__13(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_sequent__TOP__14(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_sequent__TOP__15(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_sequent__TOP__16(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_sequent__TOP__17(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_sequent__TOP__18(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_sequent__TOP__19(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_sequent__TOP__20(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_sequent__TOP__21(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_comb__TOP__28(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_comb__TOP__29(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_comb__TOP__30(Vtb_combined___024root* vlSelf);

VL_ATTR_COLD void Vtb_combined___024root___eval_stl__0(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___eval_stl__0\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if ((1ULL & vlSelfRef.__VstlTriggered[0U])) {
        Vtb_combined___024root___stl_sequent__TOP__0(vlSelf);
        Vtb_combined___024root___stl_sequent__TOP__1(vlSelf);
        Vtb_combined___024root___stl_sequent__TOP__2(vlSelf);
        Vtb_combined___024root___stl_sequent__TOP__3(vlSelf);
        Vtb_combined___024root___stl_sequent__TOP__4(vlSelf);
        Vtb_combined___024root___stl_sequent__TOP__5(vlSelf);
        Vtb_combined___024root___stl_sequent__TOP__6(vlSelf);
        Vtb_combined___024root___stl_sequent__TOP__7(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__65(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__63(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__27(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__25(vlSelf);
        Vtb_combined___024root___nba_comb__TOP__24(vlSelf);
        Vtb_combined___024root___nba_comb__TOP__25(vlSelf);
        Vtb_combined___024root___act_comb__TOP__4(vlSelf);
        Vtb_combined___024root___act_comb__TOP__5(vlSelf);
        Vtb_combined___024root___act_comb__TOP__6(vlSelf);
        Vtb_combined___024root___act_comb__TOP__7(vlSelf);
        Vtb_combined___024root___act_comb__TOP__8(vlSelf);
        Vtb_combined___024root___act_comb__TOP__9(vlSelf);
        Vtb_combined___024root___act_comb__TOP__10(vlSelf);
        Vtb_combined___024root___act_comb__TOP__11(vlSelf);
        Vtb_combined___024root___act_comb__TOP__12(vlSelf);
        Vtb_combined___024root___act_comb__TOP__13(vlSelf);
        Vtb_combined___024root___act_comb__TOP__14(vlSelf);
        Vtb_combined___024root___act_comb__TOP__15(vlSelf);
        Vtb_combined___024root___stl_sequent__TOP__26(vlSelf);
        Vtb_combined___024root___act_sequent__TOP__1(vlSelf);
        Vtb_combined___024root___act_sequent__TOP__2(vlSelf);
        Vtb_combined___024root___act_sequent__TOP__3(vlSelf);
        Vtb_combined___024root___act_sequent__TOP__4(vlSelf);
        Vtb_combined___024root___act_sequent__TOP__5(vlSelf);
        Vtb_combined___024root___act_sequent__TOP__6(vlSelf);
        Vtb_combined___024root___act_sequent__TOP__7(vlSelf);
        Vtb_combined___024root___act_sequent__TOP__8(vlSelf);
        Vtb_combined___024root___act_sequent__TOP__9(vlSelf);
        Vtb_combined___024root___act_sequent__TOP__10(vlSelf);
        Vtb_combined___024root___stl_sequent__TOP__37(vlSelf);
        Vtb_combined___024root___act_comb__TOP__17(vlSelf);
        Vtb_combined___024root___act_comb__TOP__18(vlSelf);
        Vtb_combined___024root___act_comb__TOP__19(vlSelf);
        Vtb_combined___024root___act_comb__TOP__20(vlSelf);
        Vtb_combined___024root___act_comb__TOP__21(vlSelf);
        Vtb_combined___024root___act_comb__TOP__22(vlSelf);
        Vtb_combined___024root___act_comb__TOP__23(vlSelf);
        Vtb_combined___024root___act_comb__TOP__24(vlSelf);
        Vtb_combined___024root___act_comb__TOP__25(vlSelf);
        Vtb_combined___024root___act_comb__TOP__26(vlSelf);
        Vtb_combined___024root___stl_sequent__TOP__48(vlSelf);
        Vtb_combined___024root___act_sequent__TOP__12(vlSelf);
        Vtb_combined___024root___act_sequent__TOP__13(vlSelf);
        Vtb_combined___024root___act_sequent__TOP__14(vlSelf);
        Vtb_combined___024root___act_sequent__TOP__15(vlSelf);
        Vtb_combined___024root___act_sequent__TOP__16(vlSelf);
        Vtb_combined___024root___act_sequent__TOP__17(vlSelf);
        Vtb_combined___024root___act_sequent__TOP__18(vlSelf);
        Vtb_combined___024root___act_sequent__TOP__19(vlSelf);
        Vtb_combined___024root___act_sequent__TOP__20(vlSelf);
        Vtb_combined___024root___act_sequent__TOP__21(vlSelf);
        Vtb_combined___024root___stl_sequent__TOP__59(vlSelf);
        Vtb_combined___024root___act_comb__TOP__28(vlSelf);
        Vtb_combined___024root___act_comb__TOP__29(vlSelf);
        Vtb_combined___024root___act_comb__TOP__30(vlSelf);
        Vtb_combined___024root___stl_sequent__TOP__63(vlSelf);
    }
}

VL_ATTR_COLD bool Vtb_combined___024root___eval_phase__stl(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___eval_phase__stl\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
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
        Vtb_combined___024root___dump_triggers__stl(vlSelfRef.__VstlTriggered, "stl"s);
    }
#endif
    __VstlExecute = Vtb_combined___024root___trigger_anySet__stl(vlSelfRef.__VstlTriggered);
    if (__VstlExecute) {
        {
            // Inlined CFunc: _eval_stl
            Vtb_combined___024root___eval_stl__0(vlSelf);
        }
    }
    return (__VstlExecute);
}

bool Vtb_combined___024root___trigger_anySet__act(const VlUnpacked<QData/*63:0*/, 1> &in);

#ifdef VL_DEBUG
VL_ATTR_COLD void Vtb_combined___024root___dump_triggers__act(const VlUnpacked<QData/*63:0*/, 1> &triggers, const std::string &tag) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___dump_triggers__act\n"); );
    // Body
    if ((1U & (~ (IData)(Vtb_combined___024root___trigger_anySet__act(triggers))))) {
        VL_DBG_MSGS("         No '" + tag + "' region triggers active\n");
    }
    if ((1U & (IData)(triggers[0U]))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 0 is active: @(negedge tb_combined.boundary_test.clk)\n");
    }
    if ((1U & (IData)((triggers[0U] >> 1U)))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 1 is active: @(posedge tb_combined.boundary_test.clk)\n");
    }
    if ((1U & (IData)((triggers[0U] >> 2U)))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 2 is active: @(posedge tb_combined.feature_test.clk)\n");
    }
    if ((1U & (IData)((triggers[0U] >> 3U)))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 3 is active: @( (tb_combined.feature_done & tb_combined.boundary_done))\n");
    }
    if ((1U & (IData)((triggers[0U] >> 4U)))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 4 is active: @([true] __VdlySched.awaitingCurrentTime())\n");
    }
}
#endif  // VL_DEBUG

VL_ATTR_COLD void Vtb_combined___024root___ctor_var_reset_0(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___ctor_var_reset_0\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    const uint64_t __VscopeHash = VL_MURMUR64_HASH(vlSelf->vlNamep);
    vlSelf->tb_combined__DOT__feature_done = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 11581759408887081278ull);
    vlSelf->tb_combined__DOT__boundary_done = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 7216252637186891190ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__candidate_start_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 486042651856286017ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__candidate_backend_cancel = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 14353311278472071054ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__candidate_backend_req_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 13355794643333532380ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__candidate_backend_req_write = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 4724344846100540626ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__candidate_backend_req_rstrb = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 16409670491248116658ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__candidate_backend_req_wstrb = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 8494186294768524140ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__fd = 0;
    vlSelf->tb_combined__DOT__boundary_test__DOT__scanned = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4185624452485366772ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__expected_error = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8339488318830153631ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__timeout_count = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9680922391838203930ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__unnamedblk1__DOT__action = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5175792965136261786ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__unnamedblk1__DOT__unnamedblk2__DOT__state_id = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5491972961569401965ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__unnamedblk3__DOT__code = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11865609933142834377ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__unnamedblk3__DOT__unnamedblk4__DOT__request_target = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10370848541232818206ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state = VL_SCOPED_RAND_RESET_I(5, __VscopeHash, 1803662337469099346ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__layer_index_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4659979774716166784ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_layer_index_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10501504143801122236ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__input_base_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7111765266298515780ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__input_length_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11585117432306135685ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__input_batch_count_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12067939191661100861ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__input_channels_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16162454189787014722ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__input_height_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8820067964943917243ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__input_width_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15030762042005194718ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_base_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14862858880129229688ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_length_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2212866141788266040ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_batch_count_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3848751392777922381ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_channels_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17748118816695520898ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_height_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1365277761945726455ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_width_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17035365069948277666ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__kernel_height_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7761801829138993302ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__kernel_width_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17365433879948675808ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__stride_y_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16670541904358136348ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__stride_x_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15019659522292733199ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__pad_left_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12111880125210067821ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__pad_right_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15600872205983917261ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__pad_top_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3309193406057387267ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__pad_bottom_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9556647074559803950ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__groups_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8726836629728741417ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__padding_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8856043932526195553ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_package_base_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10774092781220065228ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_package_length_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9154038180320082448ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__quantized_weight_offset_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17111171846536942902ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__quantized_weight_bytes_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2755177888060384273ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_batch_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 480860082893052781ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__activation_mode_latched = VL_SCOPED_RAND_RESET_I(2, __VscopeHash, 16730010008009518727ull);
    for (int __Vi0 = 0; __Vi0 < 51200; ++__Vi0) {
        vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_patch[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 7158389799060669642ull);
    }
    for (int __Vi0 = 0; __Vi0 < 512; ++__Vi0) {
        vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_block[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 5229190127517306570ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3100444566227139725ull);
    }
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_read_data = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 17949096783879391962ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_read_in_bounds = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 7748459859569526541ull);
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 17719006150227820652ull);
    }
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__reduction_count_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3486103979022520975ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_group_base = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2646085143382634779ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_start_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10598196843718075617ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_start_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2873988107840666026ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_height = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11644007778496455503ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_width = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15272494295310337583ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__patch_height = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3675602553092170667ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__patch_width = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17489379849799903424ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__patch_byte_count = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13562387124000713487ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_point_count = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 18335486646292811596ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__group_lane_count = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13578303915268604531ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16187608692351606948ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_lane_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9675342117311237949ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_reduction_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2554623745062515347ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_point_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11322822322120092411ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_point_scan_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4793699424893962466ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_point_scan_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9328988435409608132ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_reduction_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11700548553583310200ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_lane_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4525461220249756085ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_point_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11538812810252268898ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__request_address_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 890541034384552614ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__request_strobe_latched = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 3461616716806508799ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__request_wdata_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4672815522280373572ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__result_error_latched = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 11637013053255234100ull);
    VL_SCOPED_RAND_RESET_W(128, vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__input_elements_wide, __VscopeHash, 16590041713471456314ull);
    VL_SCOPED_RAND_RESET_W(128, vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_elements_wide, __VscopeHash, 8332997158510505880ull);
    VL_SCOPED_RAND_RESET_W(128, vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__expected_weight_bytes_wide, __VscopeHash, 4772563440509644268ull);
    VL_SCOPED_RAND_RESET_W(128, vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__reduction_count_wide, __VscopeHash, 17461989296836122318ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__input_element_plane = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 12736005150012093664ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_element_plane = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 11918051735177018349ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__input_element_product = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 9790513440829774393ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_element_product = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 15233650279105676793ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__reduction_plane_narrow = VL_SCOPED_RAND_RESET_I(26, __VscopeHash, 9793693282359891595ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__expected_weight_bytes_narrow = VL_SCOPED_RAND_RESET_Q(45, __VscopeHash, 7384679151102484732ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__reduction_count_bad = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 8714989532881145881ull);
    VL_SCOPED_RAND_RESET_W(128, vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__input_end_wide, __VscopeHash, 15890036277679652678ull);
    VL_SCOPED_RAND_RESET_W(128, vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_end_wide, __VscopeHash, 3587542926880632000ull);
    VL_SCOPED_RAND_RESET_W(128, vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_package_end_wide, __VscopeHash, 11402824878312372503ull);
    VL_SCOPED_RAND_RESET_W(128, vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__quantized_weight_end_wide, __VscopeHash, 10578013035263596708ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_height_numerator = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 4883475673030979997ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_width_numerator = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 15500594939555128573ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_height_shape_span = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 10712128249707608040ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_width_shape_span = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 15694160954581430242ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_height_shape_product = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 2770090121386973636ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_width_shape_product = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 9040065733693710447ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_height_span_plus_stride = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 7295659866910474048ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_width_span_plus_stride = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 12069379927034141286ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__full_tile_patch_delta_x = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 18112711574407966874ull);
}

VL_ATTR_COLD void Vtb_combined___024root___ctor_var_reset_1(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___ctor_var_reset_1\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    const uint64_t __VscopeHash = VL_MURMUR64_HASH(vlSelf->vlNamep);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__full_tile_patch_height_narrow = VL_SCOPED_RAND_RESET_I(19, __VscopeHash, 10236901160341815655ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__full_tile_patch_width_narrow = VL_SCOPED_RAND_RESET_I(19, __VscopeHash, 11207201577514649578ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__full_tile_patch_height_bad = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 7307723204255372944ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__validation_ok = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 14876566855455683237ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__validation_error = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 17400324807124120481ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__patch_plane_bytes = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 17972574963845242733ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_channel = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2057774164712203504ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15867494912659123533ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15333178465727816872ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_advance = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 6912547409774814504ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_in_bounds = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 2758753606648575310ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_source_address_wide = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 14282698913127176488ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_source_address_wide = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 4495214116427306902ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_kernel_area = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 341631688297751900ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_input_channel = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7164047232975673345ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_kernel_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9956699784859490384ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_kernel_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4751803428441966560ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_next_input_channel = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12493585928875046256ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_next_kernel_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16808349135679301936ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_next_kernel_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11700878647751008896ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_next_reduction_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11587508757873150143ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_point_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9075374902407649057ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_point_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11906330031224277437ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_input_channel = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8673427949051291795ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_kernel_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14738783875396638178ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_kernel_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8050646639621951043ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_reduction_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2998790738243706894ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_input_y = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 15820190658608170957ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_input_x = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 6062615588900926652ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_tap_in_bounds = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 8326568263477226354ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_feature_index_wide = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 18421210982566052252ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_feature_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4556571558374595978ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_enable = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 14669855978240437990ull);
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_feature_byte[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 6598401990593429925ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_weight_byte[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 10684348107646187878ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_product[__Vi0] = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 5032927943491738974ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_sum[__Vi0] = VL_SCOPED_RAND_RESET_Q(33, __VscopeHash, 7108392758331110430ull);
    }
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_bad_argument = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 17072913277497214833ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_overflow = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 7690604298674274336ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_lane = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16480807697275839566ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17476631254967899340ull);
    VL_SCOPED_RAND_RESET_W(80, vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_parameter, __VscopeHash, 10410163012992304636ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_bias = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16308421693714942638ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_invalid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 1656973710533552259ull);
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        VL_SCOPED_RAND_RESET_W(80, vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter[__Vi0], __VscopeHash, 2143006287132611944ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_bias[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 737202918317013490ull);
    }
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_lane_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 279130779764287791ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requantized_value = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 10128108020363941853ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_point_scan_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14143901944550025051ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_point_scan_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14691910020221623659ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_byte_offset_wide = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 8078157066068790077ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_address_wide = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 7263992672652452234ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mapped_response_error = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 15862822691597354486ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__request_byte_lane = VL_SCOPED_RAND_RESET_I(2, __VscopeHash, 10342764223491381207ull);
    for (int __Vi0 = 0; __Vi0 < 4608; ++__Vi0) {
        vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 2656541154731665323ull);
    }
    for (int __Vi0 = 0; __Vi0 < 4608; ++__Vi0) {
        vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 6346443627481721924ull);
    }
    for (int __Vi0 = 0; __Vi0 < 4608; ++__Vi0) {
        vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 14197810635720165669ull);
    }
    for (int __Vi0 = 0; __Vi0 < 4608; ++__Vi0) {
        vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 13946961219940746120ull);
    }
    for (int __Vi0 = 0; __Vi0 < 4608; ++__Vi0) {
        vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 4591705065278813882ull);
    }
    for (int __Vi0 = 0; __Vi0 < 4608; ++__Vi0) {
        vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 7942621277991022292ull);
    }
    for (int __Vi0 = 0; __Vi0 < 4608; ++__Vi0) {
        vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 4603604589819353032ull);
    }
    for (int __Vi0 = 0; __Vi0 < 4608; ++__Vi0) {
        vlSelf->tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 5329330653565768513ull);
    }
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state = VL_SCOPED_RAND_RESET_I(5, __VscopeHash, 15266673141134626941ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__layer_index_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10834948584192192430ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_layer_index_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 18332113440939008073ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__input_base_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14205103767610484717ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__input_length_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4043502480924742794ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__input_batch_count_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16747716168016265063ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__input_channels_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10012577450598494682ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__input_height_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3040259219995709270ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__input_width_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11920582635293862654ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_base_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16708485469055060340ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_length_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10000616611740600513ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_batch_count_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10800660563223915526ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_channels_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13270502380910635757ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_height_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14476008869890238765ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_width_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15093471602098256874ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__kernel_height_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7385081575395101202ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__kernel_width_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15977760085496808850ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__stride_y_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12516074764854425190ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__stride_x_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14788873238217010474ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__pad_left_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2646266234373801696ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__pad_right_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15297138374416632264ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__pad_top_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5964642420691225610ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__pad_bottom_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14932724759307377061ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__groups_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4209213759909011490ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__padding_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9413304068818534899ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_package_base_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13701254135056225682ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_package_length_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8059489573037119351ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__quantized_weight_offset_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1265264951673533607ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__quantized_weight_bytes_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16778878879609721722ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_batch_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12588788830403321426ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__activation_mode_latched = VL_SCOPED_RAND_RESET_I(2, __VscopeHash, 10002593463963185732ull);
    for (int __Vi0 = 0; __Vi0 < 51200; ++__Vi0) {
        vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_patch[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 7545594936687393400ull);
    }
    for (int __Vi0 = 0; __Vi0 < 512; ++__Vi0) {
        vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_block[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 4179128007661241522ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7994713539101770480ull);
    }
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_read_data = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 5282088729423396873ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_read_in_bounds = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 2724668562912158639ull);
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 13850673133085434005ull);
    }
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__reduction_count_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3601134934609741185ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_group_base = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 18163957081536285984ull);
}

VL_ATTR_COLD void Vtb_combined___024root___ctor_var_reset_2(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___ctor_var_reset_2\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    const uint64_t __VscopeHash = VL_MURMUR64_HASH(vlSelf->vlNamep);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_start_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4569785683358509917ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_start_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12297959957719610501ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_height = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1819938844101425870ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_width = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12115897828918200152ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__patch_height = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2763634422050193089ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__patch_width = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9637604242450963909ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__patch_byte_count = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5326746963914132423ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_point_count = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12999952015986990151ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__group_lane_count = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1625582682806929834ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 819356493784971960ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_lane_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8957414095567864730ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_reduction_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7675151524169329302ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_point_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10230196601771092594ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_point_scan_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6743906073733419957ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_point_scan_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 374962019280856182ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_reduction_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 18118965973988228751ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_lane_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 447913762757016393ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_point_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 62502014565883238ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__request_address_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6471080681800588557ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__request_strobe_latched = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 5430990289286281083ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__request_wdata_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13231614209077166784ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__result_error_latched = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 7854736905894789958ull);
    VL_SCOPED_RAND_RESET_W(128, vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__input_elements_wide, __VscopeHash, 18119668477114663530ull);
    VL_SCOPED_RAND_RESET_W(128, vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_elements_wide, __VscopeHash, 12610618499281185580ull);
    VL_SCOPED_RAND_RESET_W(128, vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__expected_weight_bytes_wide, __VscopeHash, 4701315342381046841ull);
    VL_SCOPED_RAND_RESET_W(128, vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__reduction_count_wide, __VscopeHash, 2940161487745619049ull);
    VL_SCOPED_RAND_RESET_W(128, vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__input_end_wide, __VscopeHash, 17073107667011929743ull);
    VL_SCOPED_RAND_RESET_W(128, vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_end_wide, __VscopeHash, 15423086947524520978ull);
    VL_SCOPED_RAND_RESET_W(128, vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_package_end_wide, __VscopeHash, 2739905058370757800ull);
    VL_SCOPED_RAND_RESET_W(128, vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__quantized_weight_end_wide, __VscopeHash, 17025137023669911419ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_height_numerator = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 6038165233253346817ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_width_numerator = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 6955027930606412889ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_height_shape_span = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 11212615478893858568ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_width_shape_span = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 4710297579310062196ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_height_shape_product = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 3863928799505315725ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_width_shape_product = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 11430085921072608651ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_height_span_plus_stride = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 6053455931311649677ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_width_span_plus_stride = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 18203519686163605384ull);
    VL_SCOPED_RAND_RESET_W(128, vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__full_tile_patch_bytes_wide, __VscopeHash, 1684199416632221192ull);
    VL_SCOPED_RAND_RESET_W(128, vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__full_weight_group_bytes_wide, __VscopeHash, 7324287670217345046ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__validation_ok = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 5372349958111549955ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__validation_error = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 17338221356975373037ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__patch_plane_bytes = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 2657873037942806631ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_channel = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3240657021608746638ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6937205920502891152ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7992816476798376640ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_advance = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 9990758831493424755ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_in_bounds = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 1017562991983737053ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_source_address_wide = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 8555883644165064469ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_source_address_wide = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 16127470198522303216ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_kernel_area = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4476106412328533117ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_input_channel = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1412538602550729440ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_kernel_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3820764050018500046ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_kernel_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3838361304249481972ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_next_input_channel = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17534855763516750313ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_next_kernel_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7664330404912558657ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_next_kernel_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6310646246112246496ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_next_reduction_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16369772466457053327ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_point_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15141838270769058311ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_point_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12226556437545364533ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_input_channel = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13207501289438001668ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_kernel_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 18275943898128029149ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_kernel_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 638301666930787684ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_reduction_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13821576115483542076ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_input_y = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 15363047768823203430ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_input_x = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 11349342594985585251ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_tap_in_bounds = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 15208872405076994ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_feature_index_wide = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 11563882734214700801ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_feature_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12917435010772520232ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_enable = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 17499225078593040959ull);
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_feature_byte[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 10445149123513228931ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_weight_byte[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 8828056973918941057ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_product[__Vi0] = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 14122729753112931143ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_sum[__Vi0] = VL_SCOPED_RAND_RESET_Q(33, __VscopeHash, 10119011838630023553ull);
    }
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_bad_argument = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 14074661296955593982ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_overflow = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 1798465651631183493ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_lane = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10466345298062402146ull);
    VL_SCOPED_RAND_RESET_W(80, vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_parameter, __VscopeHash, 4195144539962040267ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_bias = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1336873926963650535ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_invalid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 6808875834893035675ull);
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        VL_SCOPED_RAND_RESET_W(80, vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter[__Vi0], __VscopeHash, 13663183878342040489ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_bias[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10403552179076782254ull);
    }
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_lane_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 18170726661041933680ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requantized_value = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 3318934344542985438ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_point_scan_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15979665953679629786ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_point_scan_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12093435785612148672ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_byte_offset_wide = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 4471587127190591330ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_address_wide = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 14628767238339590783ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mapped_response_error = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 1464957415619394050ull);
    vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__request_byte_lane = VL_SCOPED_RAND_RESET_I(2, __VscopeHash, 4291701168534459199ull);
    for (int __Vi0 = 0; __Vi0 < 4608; ++__Vi0) {
        vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 13710830944159042906ull);
    }
    for (int __Vi0 = 0; __Vi0 < 4608; ++__Vi0) {
        vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 7017003085474527181ull);
    }
    for (int __Vi0 = 0; __Vi0 < 4608; ++__Vi0) {
        vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 9627261868292694289ull);
    }
    for (int __Vi0 = 0; __Vi0 < 4608; ++__Vi0) {
        vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 12762532935619190069ull);
    }
    for (int __Vi0 = 0; __Vi0 < 4608; ++__Vi0) {
        vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 12548075847534813987ull);
    }
    for (int __Vi0 = 0; __Vi0 < 4608; ++__Vi0) {
        vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 6338207732440000600ull);
    }
    for (int __Vi0 = 0; __Vi0 < 4608; ++__Vi0) {
        vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 5230036493086338496ull);
    }
    for (int __Vi0 = 0; __Vi0 < 4608; ++__Vi0) {
        vlSelf->tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 17687166007914861257ull);
    }
    vlSelf->tb_combined__DOT__feature_test__DOT__v_state = VL_SCOPED_RAND_RESET_I(2, __VscopeHash, 6862260803529347781ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__v_rsp_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 10540104316494168679ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__v_rsp_error = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 11892318961457115695ull);
}

VL_ATTR_COLD void Vtb_combined___024root___ctor_var_reset_3(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___ctor_var_reset_3\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    const uint64_t __VscopeHash = VL_MURMUR64_HASH(vlSelf->vlNamep);
    vlSelf->tb_combined__DOT__feature_test__DOT__v_feature_scan_channel = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6839020597773147643ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__v_input_height_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3232024914985503403ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__v_input_width_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10358185015927025304ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__v_tile_start_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5809832063217819307ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__v_stride_y_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12184290028228211815ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__v_feature_scan_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10605171723443075877ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__v_pad_top_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12883392751577533209ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__v_tile_start_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8079527091318244168ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__v_stride_x_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13476351557116881492ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__v_feature_scan_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3891116832261219725ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__v_pad_left_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 218100240088440862ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__v_input_base_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7119445904890527591ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__v_patch_height = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15673017558838435405ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__v_patch_width = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12349741004331364877ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__v_feature_scan_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2338054054106022253ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__v_patch_byte_count = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2253865759033311716ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__gold_plane = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 7935004319855117534ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__gold_y = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 12906429700255601781ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__gold_x = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 15073755004448559931ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__gold_bounds = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 17590908323232518997ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__gold_offset = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 1832196995438838992ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__gold_address = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 362285802857615946ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__gold_range = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 1723309648381961855ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__gold_action = VL_SCOPED_RAND_RESET_I(2, __VscopeHash, 6293821297263611917ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__gold_advance = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 598203571045014837ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__gold_aligned = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7177921998747383042ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__gold_strobe = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 17805370300053368844ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__gold_row = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 13265464540476546392ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__fd = 0;
    vlSelf->tb_combined__DOT__feature_test__DOT__scanned = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12243704722963674433ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__state = VL_SCOPED_RAND_RESET_I(5, __VscopeHash, 9444866971604079938ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__layer_index_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2823378692846871850ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__input_base_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3651434940902323208ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__input_channels_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16213004077380705372ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__input_height_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3860521039515033978ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__input_width_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2426081677426915629ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_base_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17696507577240525494ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_channels_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14577402153644246695ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_height_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1545730437019666942ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_width_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4676625868749615563ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__kernel_height_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7906310483028776587ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__kernel_width_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12528450534457342969ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__stride_y_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2049753603380856532ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__stride_x_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16683873351291369246ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__pad_left_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6272654728474763436ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__pad_top_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2795536530400011001ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_package_base_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3289401032602244780ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__quantized_weight_offset_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2807343859338726093ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__activation_mode_latched = VL_SCOPED_RAND_RESET_I(2, __VscopeHash, 8795584205060338139ull);
    for (int __Vi0 = 0; __Vi0 < 51200; ++__Vi0) {
        vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_patch[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 9445244383826650947ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5920836144721235044ull);
    }
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_read_data = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 2900822777760166338ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_read_in_bounds = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 9689146332715460392ull);
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 5766852986681160855ull);
    }
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__reduction_count_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7909117645801051762ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_group_base = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10042083011454999787ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__tile_start_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13149607601390742114ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__tile_start_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3973190294909245177ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__tile_height = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4219335156139307229ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__tile_width = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11618102093852878005ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__patch_height = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12780953214270073158ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__patch_width = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2661076683893690116ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__patch_byte_count = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14877010601382185222ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__tile_point_count = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4652717540040110613ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__group_lane_count = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1744888272659001881ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17794399588036592008ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_lane_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12290301567965732716ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_reduction_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2741306182308334236ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_point_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13476405842800452412ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_point_scan_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10112857001481460727ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_point_scan_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11259754655289732537ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_reduction_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3505766619010945937ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_lane_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3937301537738062138ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_point_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15308589797032582199ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__request_strobe_latched = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 1812662181739445151ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__patch_plane_bytes = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 12351505177050501165ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_channel = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17666310810958952242ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1926764962010302355ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9310469803779942688ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_advance = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 16876247170214044515ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_input_y = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 9747867465484514364ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_input_x = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 16933225004855018704ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_in_bounds = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 14503893449790821546ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_geometry_plane = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 9494188776881915889ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_row_offset = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 17022525980491024222ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_source_offset = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 7637940011137376323ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_source_address_wide = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 16589029825043872662ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_source_address_wide = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 4195034817048025544ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_kernel_area = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11915576466453218386ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_input_channel = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10774377476812872312ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_kernel_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2452056991046030581ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_kernel_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7963235784408357839ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_next_input_channel = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9670784691809792951ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_next_kernel_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11183003273020160133ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_next_kernel_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17497701139910499841ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_next_reduction_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14625708540010837655ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_point_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9432870230768081045ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_point_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16016791133408857093ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_input_channel = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14644743363345589328ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_kernel_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5080213396623454850ull);
}

VL_ATTR_COLD void Vtb_combined___024root___ctor_var_reset_4(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___ctor_var_reset_4\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    const uint64_t __VscopeHash = VL_MURMUR64_HASH(vlSelf->vlNamep);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_kernel_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3536989273211595456ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_reduction_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1265885961884623622ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_input_y = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 15829815527529929202ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_input_x = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 12120377152729677708ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_tap_in_bounds = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 9939179178002238412ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_feature_index_wide = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 13127305671010318765ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_feature_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6448721424708013913ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_enable = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 992694266093553163ull);
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_feature_byte[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 14218786882106970995ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_weight_byte[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 15246649993014282705ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_product[__Vi0] = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 1482065253935249724ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_sum[__Vi0] = VL_SCOPED_RAND_RESET_Q(33, __VscopeHash, 14071998948716309840ull);
    }
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_bad_argument = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 12956907324982220390ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_overflow = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 16678242681446439556ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__mq_prefetch_lane = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10513804134149100608ull);
    VL_SCOPED_RAND_RESET_W(80, vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__mq_prefetch_parameter, __VscopeHash, 11240991368010869705ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__mq_prefetch_bias = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2102378851764947830ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__mq_prefetch_invalid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 7894476337103720694ull);
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        VL_SCOPED_RAND_RESET_W(80, vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_mq_parameter[__Vi0], __VscopeHash, 10885390363361551318ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_bias[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9861846542790269731ull);
    }
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_lane_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1311101113814618075ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__requantized_value = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 724735537155192970ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_point_scan_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17368056319164363495ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_point_scan_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13171192701623327978ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_byte_offset_wide = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 15563014839210791633ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_address_wide = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 8944657705803415379ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__mapped_response_error = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 332471668310794975ull);
    for (int __Vi0 = 0; __Vi0 < 4608; ++__Vi0) {
        vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 16816139187946111877ull);
    }
    for (int __Vi0 = 0; __Vi0 < 4608; ++__Vi0) {
        vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 9316892003499319941ull);
    }
    for (int __Vi0 = 0; __Vi0 < 4608; ++__Vi0) {
        vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 1784229464208756627ull);
    }
    for (int __Vi0 = 0; __Vi0 < 4608; ++__Vi0) {
        vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 8225576711694719063ull);
    }
    for (int __Vi0 = 0; __Vi0 < 4608; ++__Vi0) {
        vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 2114023129712748053ull);
    }
    for (int __Vi0 = 0; __Vi0 < 4608; ++__Vi0) {
        vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 13334994381549058659ull);
    }
    for (int __Vi0 = 0; __Vi0 < 4608; ++__Vi0) {
        vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 13353093175480626651ull);
    }
    for (int __Vi0 = 0; __Vi0 < 4608; ++__Vi0) {
        vlSelf->tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 17539208647974561907ull);
    }
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__state = VL_SCOPED_RAND_RESET_I(5, __VscopeHash, 14070853634128553713ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__layer_index_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7233921725635714117ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__input_base_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15951615672313553821ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__input_channels_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12735380067995251451ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__input_height_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1862357629607269486ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__input_width_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13148630386594021600ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__output_base_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13292051842583736246ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__output_channels_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15762848454967031059ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__output_height_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3909069502764172262ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__output_width_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13960699651615015819ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__kernel_height_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6596955506442273221ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__kernel_width_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10784049186439637169ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__stride_y_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13020038287262359712ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__stride_x_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7933089494173603189ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__pad_left_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1674496282082414962ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__pad_top_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16276548274030500871ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_package_base_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4331527658310394187ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__quantized_weight_offset_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4366261846302382025ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__activation_mode_latched = VL_SCOPED_RAND_RESET_I(2, __VscopeHash, 1065951825669948162ull);
    for (int __Vi0 = 0; __Vi0 < 51200; ++__Vi0) {
        vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_patch[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 8569820216976881458ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2054989541028711788ull);
    }
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_read_data = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 4515248954424805753ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_read_in_bounds = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 14672025518842582246ull);
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 2355645780674924299ull);
    }
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__reduction_count_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12017451254846985625ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__output_group_base = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10960998101338532615ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__tile_start_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17355350631298366301ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__tile_start_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6959530454904133797ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__tile_height = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6633792008294438674ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__tile_width = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6294403385096574183ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__patch_height = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5851041896819085939ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__patch_width = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10020524683626280574ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__patch_byte_count = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7574523573034616298ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__tile_point_count = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2453944371795811733ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__group_lane_count = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17364301875115805680ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2553958493823208105ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_lane_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4000647203522915982ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_reduction_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14084136589030353419ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_point_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3727005540290068604ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_point_scan_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10004418554260660138ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_point_scan_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1950667592219670350ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_reduction_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12829165953869187400ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__output_lane_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11788403601482755880ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__output_point_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14168289894851275433ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__request_strobe_latched = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 4307689621981462488ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__patch_plane_bytes = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 5901338452853185121ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_channel = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10059528620516950728ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4416033865207393913ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7216795112838998226ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_advance = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 10698362653983825423ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_input_y = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 7028099551785977939ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_input_x = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 1018521828406164022ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_in_bounds = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 1310778447886349239ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_source_offset = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 1909088655186082558ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_source_address_wide = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 12944442840786239391ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_source_address_wide = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 9473589584425724168ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_kernel_area = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3959808074452093193ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_input_channel = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2943975975167615893ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_kernel_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 208367467456549016ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_kernel_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12420885788329851005ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_next_input_channel = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3760748541157795731ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_next_kernel_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8721884658143752230ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_next_kernel_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3367255148052459583ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_next_reduction_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15127351666476026690ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_point_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11736500733507233020ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_point_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7825957240304349951ull);
}

VL_ATTR_COLD void Vtb_combined___024root___ctor_var_reset_5(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___ctor_var_reset_5\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    const uint64_t __VscopeHash = VL_MURMUR64_HASH(vlSelf->vlNamep);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_input_channel = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1575334722485302717ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_kernel_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16092497801218736243ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_kernel_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13729219542373116369ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_reduction_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3713608211996238990ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_input_y = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 13027335234667867143ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_input_x = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 13325907537291405167ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_tap_in_bounds = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 8293387204401585035ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_feature_index_wide = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 2143897163333485549ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_feature_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 313817449531417570ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_enable = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 10858000431007906075ull);
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_feature_byte[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 6295863409673685473ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_weight_byte[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 4437853506217816863ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_product[__Vi0] = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 17311431141052052078ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_sum[__Vi0] = VL_SCOPED_RAND_RESET_Q(33, __VscopeHash, 9732702688423547000ull);
    }
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_bad_argument = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 9388051830264343643ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_overflow = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 2571486952985142593ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__mq_prefetch_lane = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9874804279692636908ull);
    VL_SCOPED_RAND_RESET_W(80, vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__mq_prefetch_parameter, __VscopeHash, 6660726498493248805ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__mq_prefetch_bias = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15658968839927772233ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__mq_prefetch_invalid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 1498858298675410751ull);
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        VL_SCOPED_RAND_RESET_W(80, vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_mq_parameter[__Vi0], __VscopeHash, 16408369022885944626ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_bias[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15692918853852256484ull);
    }
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_lane_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11106419677350673794ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__requantized_value = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 3631273390082747843ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__output_point_scan_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12677605439840474322ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__output_point_scan_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14561510164701858215ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__output_byte_offset_wide = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 10192415168980400389ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__output_address_wide = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 17273117146113834163ull);
    vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__mapped_response_error = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 13244142613976862293ull);
    for (int __Vi0 = 0; __Vi0 < 4608; ++__Vi0) {
        vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 1736390838768729331ull);
    }
    for (int __Vi0 = 0; __Vi0 < 4608; ++__Vi0) {
        vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 9301649140604372878ull);
    }
    for (int __Vi0 = 0; __Vi0 < 4608; ++__Vi0) {
        vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 11918109982498347246ull);
    }
    for (int __Vi0 = 0; __Vi0 < 4608; ++__Vi0) {
        vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 7994288872302537320ull);
    }
    for (int __Vi0 = 0; __Vi0 < 4608; ++__Vi0) {
        vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 11014355620615705973ull);
    }
    for (int __Vi0 = 0; __Vi0 < 4608; ++__Vi0) {
        vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 15632234694555314179ull);
    }
    for (int __Vi0 = 0; __Vi0 < 4608; ++__Vi0) {
        vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 14482509368955841980ull);
    }
    for (int __Vi0 = 0; __Vi0 < 4608; ++__Vi0) {
        vlSelf->tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 12911351928707569849ull);
    }
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__input_channels_latched = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_channels_latched = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_height_latched = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_width_latched = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__kernel_height_latched = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__kernel_width_latched = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__stride_y_latched = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__stride_x_latched = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__reduction_count_latched = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_group_base = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_start_y = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_start_x = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_height = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_width = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__patch_height = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__patch_width = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__patch_byte_count = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_point_count = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__group_lane_count = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_index = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_channel = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_y = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_x = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_lane_index = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_reduction_index = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_point_index = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_point_scan_y = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_point_scan_x = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_reduction_index = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_input_channel = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_kernel_y = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_kernel_x = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_lane_index = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_point_index = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_point_scan_y = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_point_scan_x = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_lane = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_lane_index = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__input_channels_latched = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_channels_latched = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_height_latched = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_width_latched = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__kernel_height_latched = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__kernel_width_latched = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__stride_y_latched = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__stride_x_latched = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__reduction_count_latched = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_group_base = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_start_y = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_start_x = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_height = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_width = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__patch_height = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__patch_width = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__patch_byte_count = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_point_count = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__group_lane_count = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_index = 0;
}

VL_ATTR_COLD void Vtb_combined___024root___ctor_var_reset_6(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___ctor_var_reset_6\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_channel = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_y = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_x = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_lane_index = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_reduction_index = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_point_index = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_point_scan_y = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_point_scan_x = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_reduction_index = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_input_channel = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_kernel_y = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_kernel_x = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_lane_index = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_point_index = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_point_scan_y = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_point_scan_x = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_lane = 0;
    vlSelf->__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_lane_index = 0;
    vlSelf->__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_channel = 0;
    vlSelf->__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_channel = 0;
    vlSelf->__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_y = 0;
    vlSelf->__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_y = 0;
    vlSelf->__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_x = 0;
    vlSelf->__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_x = 0;
    vlSelf->__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__state = 0;
    vlSelf->__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__state = 0;
    vlSelf->__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_group_base = 0;
    vlSelf->__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__tile_start_x = 0;
    vlSelf->__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__tile_start_x = 0;
    vlSelf->__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__tile_start_y = 0;
    vlSelf->__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__tile_start_y = 0;
    vlSelf->__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_point_index = 0;
    vlSelf->__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_point_scan_x = 0;
    vlSelf->__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_point_scan_x = 0;
    vlSelf->__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_reduction_index = 0;
    vlSelf->__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_kernel_y = 0;
    vlSelf->__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_kernel_x = 0;
    vlSelf->__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_reduction_index = 0;
    vlSelf->__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_index = 0;
    vlSelf->__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_index = 0;
    vlSelf->__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__patch_height = 0;
    vlSelf->__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__patch_height = 0;
    vlSelf->__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__patch_width = 0;
    vlSelf->__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__patch_width = 0;
    vlSelf->__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__patch_byte_count = 0;
    vlSelf->__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__patch_byte_count = 0;
    vlSelf->__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_channel = 0;
    vlSelf->__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_channel = 0;
    vlSelf->__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_y = 0;
    vlSelf->__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_y = 0;
    vlSelf->__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_x = 0;
    vlSelf->__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_x = 0;
    vlSelf->__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__state = 0;
    vlSelf->__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__state = 0;
    vlSelf->__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__output_group_base = 0;
    vlSelf->__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__tile_start_x = 0;
    vlSelf->__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__tile_start_x = 0;
    vlSelf->__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__tile_start_y = 0;
    vlSelf->__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__tile_start_y = 0;
    vlSelf->__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__output_point_index = 0;
    vlSelf->__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__output_point_scan_x = 0;
    vlSelf->__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_point_scan_x = 0;
    vlSelf->__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_reduction_index = 0;
    vlSelf->__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_kernel_y = 0;
    vlSelf->__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_kernel_x = 0;
    vlSelf->__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_reduction_index = 0;
    vlSelf->__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_index = 0;
    vlSelf->__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_index = 0;
    vlSelf->__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__patch_height = 0;
    vlSelf->__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__patch_height = 0;
    vlSelf->__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__patch_width = 0;
    vlSelf->__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__patch_width = 0;
    vlSelf->__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__patch_byte_count = 0;
    vlSelf->__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__patch_byte_count = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter__v0 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter__v8 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_block__v0 = 0;
    vlSelf->__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_block__v0 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_block__v0 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v0 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v0 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v1 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v1 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v2 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v2 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v3 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v3 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v4 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v4 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v5 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v5 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v6 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v6 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v7 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v7 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v8 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v8 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v9 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v9 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v10 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v11 = 0;
}

VL_ATTR_COLD void Vtb_combined___024root___ctor_var_reset_7(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___ctor_var_reset_7\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v12 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v13 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v14 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v15 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v16 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v16 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v17 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v17 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v18 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v19 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v20 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v21 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v22 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v23 = 0;
    VL_ZERO_RESET_W(80, vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter__v16);
    vlSelf->__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter__v16 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter__v16 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_bias__v16 = 0;
    vlSelf->__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_bias__v16 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_patch__v0 = 0;
    vlSelf->__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_patch__v0 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_patch__v0 = 0;
    vlSelf->__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_patch__v1 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_patch__v1 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v0 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v1 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v1 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v2 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v3 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v3 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v4 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v5 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v5 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v6 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v7 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v7 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v8 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v9 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v9 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v10 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v11 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v11 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v12 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v13 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v13 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v14 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v15 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v15 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter__v0 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter__v8 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_block__v0 = 0;
    vlSelf->__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_block__v0 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_block__v0 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v0 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v0 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v1 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v1 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v2 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v2 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v3 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v3 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v4 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v4 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v5 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v5 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v6 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v6 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v7 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v7 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v8 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v8 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v9 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v9 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v10 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v11 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v12 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v13 = 0;
}

VL_ATTR_COLD void Vtb_combined___024root___ctor_var_reset_8(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___ctor_var_reset_8\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v14 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v15 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v16 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v16 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v17 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v17 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v18 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v19 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v20 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v21 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v22 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v23 = 0;
    VL_ZERO_RESET_W(80, vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter__v16);
    vlSelf->__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter__v16 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter__v16 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_bias__v16 = 0;
    vlSelf->__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_bias__v16 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_patch__v0 = 0;
    vlSelf->__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_patch__v0 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_patch__v0 = 0;
    vlSelf->__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_patch__v1 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_patch__v1 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v0 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v1 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v1 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v2 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v3 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v3 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v4 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v5 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v5 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v6 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v7 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v7 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v8 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v9 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v9 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v10 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v11 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v11 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v12 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v13 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v13 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v14 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v15 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v15 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_block__v0 = 0;
    vlSelf->__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_block__v0 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_block__v0 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v0 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v0 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v1 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v1 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v2 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v2 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v3 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v3 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v4 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v4 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v5 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v5 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v6 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v6 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v7 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v7 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v8 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v8 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v9 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v9 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v10 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v11 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v12 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v13 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v14 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v15 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v16 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v16 = 0;
}

VL_ATTR_COLD void Vtb_combined___024root___ctor_var_reset_9(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___ctor_var_reset_9\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v17 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v17 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v18 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v19 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v20 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v21 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v22 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v23 = 0;
    VL_ZERO_RESET_W(80, vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_mq_parameter__v0);
    vlSelf->__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_mq_parameter__v0 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_mq_parameter__v0 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_bias__v0 = 0;
    vlSelf->__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_bias__v0 = 0;
    vlSelf->__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_patch__v0 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_patch__v0 = 0;
    vlSelf->__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_patch__v1 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_patch__v1 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte__v0 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte__v0 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte__v1 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte__v1 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte__v2 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte__v2 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte__v3 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte__v3 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte__v4 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte__v4 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte__v5 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte__v5 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte__v6 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte__v6 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte__v7 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte__v7 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__output_block__v0 = 0;
    vlSelf->__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_old__DOT__output_block__v0 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__output_block__v0 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v0 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v0 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v1 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v1 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v2 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v2 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v3 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v3 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v4 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v4 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v5 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v5 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v6 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v6 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v7 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v7 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v8 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v8 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v9 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v9 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v10 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v11 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v12 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v13 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v14 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v15 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v16 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v16 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v17 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v17 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v18 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v19 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v20 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v21 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v22 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v23 = 0;
    VL_ZERO_RESET_W(80, vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_mq_parameter__v0);
    vlSelf->__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_mq_parameter__v0 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_mq_parameter__v0 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_bias__v0 = 0;
    vlSelf->__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_bias__v0 = 0;
}

VL_ATTR_COLD void Vtb_combined___024root___ctor_var_reset_10(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___ctor_var_reset_10\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelf->__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_patch__v0 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_patch__v0 = 0;
    vlSelf->__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_patch__v1 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_patch__v1 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte__v0 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte__v0 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte__v1 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte__v1 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte__v2 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte__v2 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte__v3 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte__v3 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte__v4 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte__v4 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte__v5 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte__v5 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte__v6 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte__v6 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0 = 0;
    vlSelf->__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte__v7 = 0;
    vlSelf->__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte__v7 = 0;
    for (int __Vi0 = 0; __Vi0 < 1; ++__Vi0) {
        vlSelf->__VstlTriggered[__Vi0] = 0;
    }
    for (int __Vi0 = 0; __Vi0 < 1; ++__Vi0) {
        vlSelf->__VactTriggered[__Vi0] = 0;
    }
    for (int __Vi0 = 0; __Vi0 < 1; ++__Vi0) {
        vlSelf->__VactTriggeredAcc[__Vi0] = 0;
    }
    vlSelf->__Vtrigprevexpr___TOP__tb_combined__DOT__boundary_test__DOT__clk__0 = 0;
    vlSelf->__Vtrigprevexpr___TOP__tb_combined__DOT__feature_test__DOT__clk__0 = 0;
    vlSelf->__Vtrigprevexpr_h6f3df181__0 = 0;
    vlSelf->__Vtrigprevexpr_h6f3df181__1 = 0;
    for (int __Vi0 = 0; __Vi0 < 1; ++__Vi0) {
        vlSelf->__VnbaTriggered[__Vi0] = 0;
    }
    vlSelf->__Vi = 0;
}

VL_ATTR_COLD void Vtb_combined___024root___ctor_var_reset(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___ctor_var_reset\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    Vtb_combined___024root___ctor_var_reset_0(vlSelf);
    Vtb_combined___024root___ctor_var_reset_1(vlSelf);
    Vtb_combined___024root___ctor_var_reset_2(vlSelf);
    Vtb_combined___024root___ctor_var_reset_3(vlSelf);
    Vtb_combined___024root___ctor_var_reset_4(vlSelf);
    Vtb_combined___024root___ctor_var_reset_5(vlSelf);
    Vtb_combined___024root___ctor_var_reset_6(vlSelf);
    Vtb_combined___024root___ctor_var_reset_7(vlSelf);
    Vtb_combined___024root___ctor_var_reset_8(vlSelf);
    Vtb_combined___024root___ctor_var_reset_9(vlSelf);
    Vtb_combined___024root___ctor_var_reset_10(vlSelf);
}
