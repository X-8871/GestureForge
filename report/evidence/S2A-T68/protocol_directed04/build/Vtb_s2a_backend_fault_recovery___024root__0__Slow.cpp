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

VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root___stl_sequent__TOP__0(Vtb_s2a_backend_fault_recovery___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root___stl_sequent__TOP__0\n"); );
    Vtb_s2a_backend_fault_recovery__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    QData/*63:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_plane_elements;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_plane_elements = 0;
    QData/*63:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_batch_elements;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_batch_elements = 0;
    IData/*31:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mq_index;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mq_index = 0;
    CData/*0:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__descriptor_valid;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__descriptor_valid = 0;
    CData/*5:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index = 0;
    CData/*0:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_write;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_write = 0;
    CData/*3:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_rstrb;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_rstrb = 0;
    CData/*0:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_write;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_write = 0;
    IData/*31:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_addr;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_addr = 0;
    IData/*31:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_wdata;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_wdata = 0;
    CData/*3:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_rstrb;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_rstrb = 0;
    CData/*0:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_write;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_write = 0;
    IData/*31:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_addr;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_addr = 0;
    IData/*31:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_wdata;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_wdata = 0;
    CData/*3:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_rstrb;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_rstrb = 0;
    CData/*0:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_write;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_write = 0;
    IData/*31:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_addr;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_addr = 0;
    IData/*31:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_wdata;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_wdata = 0;
    CData/*3:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_rstrb;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_rstrb = 0;
    IData/*31:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_addr;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_addr = 0;
    IData/*31:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_wdata;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_wdata = 0;
    VlUnpacked<IData/*31:0*/, 9> tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel;
    for (int __Vi0 = 0; __Vi0 < 9; ++__Vi0) {
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[__Vi0] = 0;
    }
    IData/*31:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__selected_input_word_address;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__selected_input_word_address = 0;
    CData/*3:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__selected_input_lane;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__selected_input_lane = 0;
    CData/*7:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__candidate_value;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__candidate_value = 0;
    CData/*7:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__current_maximum;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__current_maximum = 0;
    QData/*32:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__extent_y;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__extent_y = 0;
    QData/*32:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__extent_x;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__extent_x = 0;
    QData/*32:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_height_work;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_height_work = 0;
    QData/*32:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_width_work;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_width_work = 0;
    QData/*63:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__origin_y;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__origin_y = 0;
    QData/*63:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__origin_x;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__origin_x = 0;
    QData/*63:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_y_step;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_y_step = 0;
    QData/*63:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_x_step;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_x_step = 0;
    QData/*63:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_y_work;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_y_work = 0;
    QData/*63:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_x_work;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_x_work = 0;
    VlWide<3>/*95:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work;
    VL_ZERO_W(96, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work);
    VlWide<3>/*95:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work;
    VL_ZERO_W(96, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work);
    VlWide<3>/*95:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work;
    VL_ZERO_W(96, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work);
    VlWide<4>/*96:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work;
    VL_ZERO_W(97, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work);
    IData/*31:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work = 0;
    IData/*31:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work = 0;
    CData/*0:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__tap_range_error;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__tap_range_error = 0;
    IData/*31:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_y;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_y = 0;
    IData/*31:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_x;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_x = 0;
    QData/*63:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__output_height_work;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__output_height_work = 0;
    QData/*63:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__output_width_work;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__output_width_work = 0;
    QData/*63:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__channel_row_work;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__channel_row_work = 0;
    QData/*63:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__row_work;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__row_work = 0;
    QData/*63:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__byte_offset_work;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__byte_offset_work = 0;
    VlWide<3>/*64:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__address_work;
    VL_ZERO_W(65, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__address_work);
    IData/*31:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__selected_word_address;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__selected_word_address = 0;
    CData/*3:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__selected_read_lane;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__selected_read_lane = 0;
    CData/*0:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_argument;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_argument = 0;
    CData/*0:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_range;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_range = 0;
    QData/*63:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source0_shape_bytes;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source0_shape_bytes = 0;
    QData/*63:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_shape_bytes;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_shape_bytes = 0;
    QData/*63:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source0_plane_elements;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source0_plane_elements = 0;
    QData/*63:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_plane_elements;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_plane_elements = 0;
    QData/*63:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source0_object_end;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source0_object_end = 0;
    QData/*63:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_object_end;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_object_end = 0;
    QData/*63:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__output_channels_wide;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__output_channels_wide = 0;
    QData/*63:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__expected_group_start;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__expected_group_start = 0;
    QData/*63:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__expected_group_end;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__expected_group_end = 0;
    QData/*63:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_offset;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_offset = 0;
    QData/*63:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_address_wide;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_address_wide = 0;
    IData/*31:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source0_selected_count;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source0_selected_count = 0;
    IData/*31:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_selected_count;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_selected_count = 0;
    IData/*31:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_multiplier;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_multiplier = 0;
    IData/*31:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_base_address;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_base_address = 0;
    IData/*31:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_length_bytes;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_length_bytes = 0;
    CData/*7:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_value;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_value = 0;
    CData/*7:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_magnitude;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_magnitude = 0;
    QData/*63:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__scaled_product;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__scaled_product = 0;
    QData/*63:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__rounded_magnitude;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__rounded_magnitude = 0;
    QData/*63:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__scaled_signed;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__scaled_signed = 0;
    IData/*31:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_source_index;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_source_index = 0;
    IData/*31:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_source_channel;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_source_channel = 0;
    VlWide<4>/*127:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_elements_wide;
    VL_ZERO_W(128, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_elements_wide);
    VlWide<4>/*127:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__expected_weight_bytes_wide;
    VL_ZERO_W(128, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__expected_weight_bytes_wide);
    VlWide<4>/*127:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_end_wide;
    VL_ZERO_W(128, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_end_wide);
    VlWide<4>/*127:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_end_wide;
    VL_ZERO_W(128, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_end_wide);
    VlWide<4>/*127:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_package_end_wide;
    VL_ZERO_W(128, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_package_end_wide);
    VlWide<4>/*127:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__quantized_weight_end_wide;
    VL_ZERO_W(128, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__quantized_weight_end_wide);
    QData/*63:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_numerator;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_numerator = 0;
    QData/*63:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_numerator;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_numerator = 0;
    VlWide<4>/*127:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_height_wide;
    VL_ZERO_W(128, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_height_wide);
    VlWide<4>/*127:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_width_wide;
    VL_ZERO_W(128, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_width_wide);
    VlWide<4>/*127:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_bytes_wide;
    VL_ZERO_W(128, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_bytes_wide);
    VlWide<4>/*127:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__full_weight_group_bytes_wide;
    VL_ZERO_W(128, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__full_weight_group_bytes_wide);
    QData/*63:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__patch_plane_bytes;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__patch_plane_bytes = 0;
    IData/*31:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_channel;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_channel = 0;
    IData/*31:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_rem;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_rem = 0;
    IData/*31:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_y;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_y = 0;
    IData/*31:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_x;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_x = 0;
    QData/*63:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_input_y;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_input_y = 0;
    QData/*63:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_input_x;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_input_x = 0;
    QData/*63:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_source_offset;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_source_offset = 0;
    IData/*31:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_area;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_area = 0;
    IData/*31:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_input_channel;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_input_channel = 0;
    IData/*31:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_y;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_y = 0;
    IData/*31:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_x;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_x = 0;
    IData/*31:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_y;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_y = 0;
    IData/*31:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_x;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_x = 0;
    QData/*63:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_input_y;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_input_y = 0;
    QData/*63:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_input_x;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_input_x = 0;
    CData/*0:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_tap_in_bounds;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_tap_in_bounds = 0;
    QData/*63:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index_wide;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index_wide = 0;
    IData/*31:0*/ tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index = 0;
    CData/*1:0*/ __Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__map_conv_activation__101__Vfuncout;
    __Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__map_conv_activation__101__Vfuncout = 0;
    CData/*1:0*/ __Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__map_conv_activation__101__descriptor_activation;
    __Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__map_conv_activation__101__descriptor_activation = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_5;
    __VdfgRegularize_h6e95ff9d_0_5 = 0;
    VlWide<3>/*64:0*/ __VdfgRegularize_h6e95ff9d_0_6;
    VL_ZERO_W(65, __VdfgRegularize_h6e95ff9d_0_6);
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
    VlWide<3>/*95:0*/ __Vtemp_202;
    VlWide<3>/*95:0*/ __Vtemp_204;
    VlWide<3>/*95:0*/ __Vtemp_205;
    VlWide<3>/*95:0*/ __Vtemp_206;
    VlWide<3>/*95:0*/ __Vtemp_207;
    VlWide<3>/*95:0*/ __Vtemp_208;
    VlWide<3>/*95:0*/ __Vtemp_209;
    VlWide<3>/*95:0*/ __Vtemp_210;
    VlWide<3>/*95:0*/ __Vtemp_212;
    VlWide<3>/*95:0*/ __Vtemp_213;
    VlWide<3>/*95:0*/ __Vtemp_214;
    VlWide<3>/*95:0*/ __Vtemp_215;
    VlWide<3>/*95:0*/ __Vtemp_216;
    VlWide<3>/*95:0*/ __Vtemp_217;
    VlWide<3>/*95:0*/ __Vtemp_218;
    VlWide<3>/*95:0*/ __Vtemp_219;
    VlWide<3>/*95:0*/ __Vtemp_220;
    VlWide<4>/*127:0*/ __Vtemp_222;
    VlWide<4>/*127:0*/ __Vtemp_223;
    VlWide<4>/*127:0*/ __Vtemp_224;
    VlWide<3>/*95:0*/ __Vtemp_229;
    VlWide<3>/*95:0*/ __Vtemp_230;
    VlWide<3>/*95:0*/ __Vtemp_231;
    VlWide<3>/*95:0*/ __Vtemp_232;
    VlWide<3>/*95:0*/ __Vtemp_233;
    VlWide<3>/*95:0*/ __Vtemp_234;
    VlWide<4>/*127:0*/ __Vtemp_236;
    VlWide<4>/*127:0*/ __Vtemp_237;
    VlWide<4>/*127:0*/ __Vtemp_238;
    VlWide<3>/*95:0*/ __Vtemp_243;
    VlWide<3>/*95:0*/ __Vtemp_244;
    VlWide<3>/*95:0*/ __Vtemp_245;
    VlWide<3>/*95:0*/ __Vtemp_246;
    VlWide<3>/*95:0*/ __Vtemp_247;
    VlWide<3>/*95:0*/ __Vtemp_248;
    VlWide<4>/*127:0*/ __Vtemp_250;
    VlWide<4>/*127:0*/ __Vtemp_251;
    VlWide<4>/*127:0*/ __Vtemp_252;
    VlWide<3>/*95:0*/ __Vtemp_257;
    VlWide<3>/*95:0*/ __Vtemp_258;
    VlWide<3>/*95:0*/ __Vtemp_259;
    VlWide<3>/*95:0*/ __Vtemp_260;
    VlWide<3>/*95:0*/ __Vtemp_261;
    VlWide<3>/*95:0*/ __Vtemp_262;
    VlWide<4>/*127:0*/ __Vtemp_264;
    VlWide<4>/*127:0*/ __Vtemp_265;
    VlWide<4>/*127:0*/ __Vtemp_266;
    VlWide<3>/*95:0*/ __Vtemp_271;
    VlWide<3>/*95:0*/ __Vtemp_272;
    VlWide<3>/*95:0*/ __Vtemp_273;
    VlWide<3>/*95:0*/ __Vtemp_274;
    VlWide<3>/*95:0*/ __Vtemp_275;
    VlWide<3>/*95:0*/ __Vtemp_276;
    VlWide<4>/*127:0*/ __Vtemp_278;
    VlWide<4>/*127:0*/ __Vtemp_279;
    VlWide<4>/*127:0*/ __Vtemp_280;
    VlWide<3>/*95:0*/ __Vtemp_285;
    VlWide<3>/*95:0*/ __Vtemp_286;
    VlWide<3>/*95:0*/ __Vtemp_287;
    VlWide<3>/*95:0*/ __Vtemp_288;
    VlWide<3>/*95:0*/ __Vtemp_289;
    VlWide<3>/*95:0*/ __Vtemp_290;
    VlWide<4>/*127:0*/ __Vtemp_292;
    VlWide<4>/*127:0*/ __Vtemp_293;
    VlWide<4>/*127:0*/ __Vtemp_294;
    VlWide<3>/*95:0*/ __Vtemp_299;
    VlWide<3>/*95:0*/ __Vtemp_300;
    VlWide<3>/*95:0*/ __Vtemp_301;
    VlWide<3>/*95:0*/ __Vtemp_302;
    VlWide<3>/*95:0*/ __Vtemp_303;
    VlWide<3>/*95:0*/ __Vtemp_304;
    VlWide<4>/*127:0*/ __Vtemp_306;
    VlWide<4>/*127:0*/ __Vtemp_307;
    VlWide<4>/*127:0*/ __Vtemp_308;
    VlWide<3>/*95:0*/ __Vtemp_313;
    VlWide<3>/*95:0*/ __Vtemp_314;
    VlWide<3>/*95:0*/ __Vtemp_315;
    VlWide<3>/*95:0*/ __Vtemp_316;
    VlWide<3>/*95:0*/ __Vtemp_317;
    VlWide<3>/*95:0*/ __Vtemp_318;
    VlWide<4>/*127:0*/ __Vtemp_320;
    VlWide<4>/*127:0*/ __Vtemp_321;
    VlWide<4>/*127:0*/ __Vtemp_322;
    VlWide<3>/*95:0*/ __Vtemp_327;
    VlWide<3>/*95:0*/ __Vtemp_328;
    VlWide<3>/*95:0*/ __Vtemp_329;
    VlWide<3>/*95:0*/ __Vtemp_330;
    VlWide<3>/*95:0*/ __Vtemp_331;
    VlWide<3>/*95:0*/ __Vtemp_332;
    VlWide<4>/*127:0*/ __Vtemp_334;
    VlWide<4>/*127:0*/ __Vtemp_335;
    VlWide<4>/*127:0*/ __Vtemp_336;
    VlWide<3>/*95:0*/ __Vtemp_342;
    VlWide<3>/*95:0*/ __Vtemp_343;
    VlWide<3>/*95:0*/ __Vtemp_345;
    VlWide<3>/*95:0*/ __Vtemp_346;
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
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mapped_response_error = 6U;
    if ((0U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_error_latched))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mapped_response_error = 0U;
    } else if ((((1U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_error_latched)) 
                 | (2U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_error_latched))) 
                | (6U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_error_latched)))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mapped_response_error 
            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_error_latched;
    }
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_ready 
        = (1U & (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__hard_reset)));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__selected_byte_shift 
        = (0x00000018U & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source_address_latched 
                          << 3U));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__request_byte_lane 
        = (3U & (0x00030210U >> ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__request_strobe_latched) 
                                 << 1U)));
    if ((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__layer_index 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_LAYER_INDEX
            [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor];
        __Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__map_conv_activation__101__descriptor_activation 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_ACTIVATION
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
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_ALIAS_LAYER_INDEX
            [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor];
    } else {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__layer_index = 0U;
        __Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__map_conv_activation__101__descriptor_activation = 0U;
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
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index = 0U;
    }
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_wstrb = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_wstrb = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_wstrb = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_wstrb = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_rsp_valid 
        = ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_pending) 
           & ((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__hard_reset)) 
              & ((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__backend_abort)) 
                 & (1U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_target_latched)))));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_rsp_valid 
        = ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_pending) 
           & ((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__hard_reset)) 
              & ((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__backend_abort)) 
                 & (3U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_target_latched)))));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_rsp_valid 
        = ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_pending) 
           & ((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__hard_reset)) 
              & ((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__backend_abort)) 
                 & (2U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_target_latched)))));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_rsp_valid 
        = ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_pending) 
           & ((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__hard_reset)) 
              & ((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__backend_abort)) 
                 & (0U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_target_latched)))));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__config_idle 
        = (1U & (~ ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__buffer_owner_pl) 
                    | ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__busy) 
                       | ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__done) 
                          | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__error))))));
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
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__current_maximum = 0x80U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__candidate_value 
        = (0x000000ffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__candidate_values_latched[0U]);
    if (VL_LTS_III(8, 0x80U, (IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__candidate_value))) {
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__current_maximum 
            = tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__candidate_value;
    }
    if ((0x80U == (IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__candidate_value))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__window_error_code = 1U;
    }
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__candidate_value 
        = (0x000000ffU & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__candidate_values_latched[0U] 
                          >> 8U));
    if ((0x80U == (IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__candidate_value))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__window_error_code = 1U;
    }
    if (VL_GTS_III(8, (IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__candidate_value), (IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__current_maximum))) {
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__current_maximum 
            = tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__candidate_value;
    }
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__candidate_value 
        = (0x000000ffU & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__candidate_values_latched[0U] 
                          >> 0x00000010U));
    if ((0x80U == (IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__candidate_value))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__window_error_code = 1U;
    }
    if (VL_GTS_III(8, (IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__candidate_value), (IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__current_maximum))) {
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__current_maximum 
            = tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__candidate_value;
    }
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__candidate_value 
        = (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__candidate_values_latched[0U] 
           >> 0x00000018U);
    if (VL_GTS_III(8, (IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__candidate_value), (IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__current_maximum))) {
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__current_maximum 
            = tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__candidate_value;
    }
    if ((0x80U == (IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__candidate_value))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__window_error_code = 1U;
    }
    if ((0U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__window_error_code))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__window_max_value 
            = tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__current_maximum;
    }
    vlSelfRef.__VdfgRegularize_h6e95ff9d_0_7[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_width_latched;
    vlSelfRef.__VdfgRegularize_h6e95ff9d_0_7[1U] = 0U;
    vlSelfRef.__VdfgRegularize_h6e95ff9d_0_7[2U] = 0U;
    vlSelfRef.__VdfgRegularize_h6e95ff9d_0_8[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_height_latched;
    vlSelfRef.__VdfgRegularize_h6e95ff9d_0_8[1U] = 0U;
    vlSelfRef.__VdfgRegularize_h6e95ff9d_0_8[2U] = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_rstrb = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_rstrb = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_byte_offset_wide 
        = ((QData)((IData)((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_x 
                            + (VL_MODDIV_III(32, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_point_index, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__tile_width) 
                               & (- (IData)((0U != vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__tile_width))))))) 
           + ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_latched)) 
              * ((QData)((IData)((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_y 
                                  + (VL_DIV_III(32, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_point_index, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__tile_width) 
                                     & (- (IData)((0U 
                                                   != vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__tile_width))))))) 
                 + ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_latched)) 
                    * (QData)((IData)((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base 
                                       + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_lane_index)))))));
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_wdata = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_addr = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_wdata = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__selected_read_lane 
        = (0x0000000fU & ((IData)(1U) << (3U & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source_address_latched)));
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_rstrb = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_wdata = 0U;
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
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_rstrb = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__selected_input_lane = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__selected_word_address 
        = (0xfffffffcU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source_address_latched);
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_addr = 0U;
    if ((4U > (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__read_tap_index))) {
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__selected_input_lane 
            = (0x0000000fU & ((IData)(1U) << (3U & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched
                                              [(3U 
                                                & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__read_tap_index))])));
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_addr = 0U;
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__selected_input_word_address = 0U;
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__selected_input_word_address 
            = (0xfffffffcU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched
               [(3U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__read_tap_index))]);
    } else {
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_addr = 0U;
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__selected_input_word_address = 0U;
    }
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_group_invalid = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[0U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[0U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[0U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product[0U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add[0U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[0U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[0U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requantized_value[0U] = 0U;
    if ((0x00000026U > vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U] 
            = (((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                 ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                [(0x0000003fU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                 : 0U) + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base);
        if ((0x00000c5cU > vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])) {
            if ((0U < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U]))) {
                    __Vtemp_1[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_1[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_1[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][2U];
                    __Vtemp_2[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_2[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_2[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][2U];
                    __Vtemp_3[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_3[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_3[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][2U];
                    __Vtemp_4[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_4[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_4[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][2U];
                    __Vtemp_5[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_5[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_5[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][2U];
                    __Vtemp_6[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_6[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_6[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][2U];
                    __Vtemp_7[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_7[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_7[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][2U];
                    __Vtemp_8[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_8[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_8[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][2U];
                    __Vtemp_9[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_9[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_9[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][2U];
                    __Vtemp_10[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_10[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_10[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][2U];
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
                if (((((((((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U] 
                            >= (((0x25U >= (0x0000003fU 
                                            & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                 [(0x0000003fU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                  : 0U) + ((0x25U >= 
                                            (0x0000003fU 
                                             & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                            ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                                           [(0x0000003fU 
                                             & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
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
                     | ((0U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__activation_mode_latched)) 
                        & ((((__Vtemp_7[2U] << 0x00000010U) 
                             | (__Vtemp_7[1U] >> 0x00000010U)) 
                            != ((__Vtemp_8[1U] << 0x00000018U) 
                                | (__Vtemp_8[0U] >> 8U))) 
                           | ((0x000000ffU & (__Vtemp_9[1U] 
                                              >> 8U)) 
                              != (0x000000ffU & __Vtemp_10[0U])))))) {
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_group_invalid = 1U;
                }
            }
            if ((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[0U] 
                 >> 0x1fU)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U]))) {
                    __Vtemp_11[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_11[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_11[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][2U];
                    __Vtemp_12[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_12[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_12[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][2U];
                } else {
                    __Vtemp_11[0U] = 0U;
                    __Vtemp_11[1U] = 0U;
                    __Vtemp_12[0U] = 0U;
                }
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[0U] 
                    = ((__Vtemp_11[1U] << 0x00000018U) 
                       | (__Vtemp_11[0U] >> 8U));
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[0U] 
                    = ((IData)(1U) + (~ vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[0U]));
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[0U] 
                    = (0x000000ffU & __Vtemp_12[0U]);
            } else {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U]))) {
                    __Vtemp_13[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_13[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_13[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][2U];
                    __Vtemp_14[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_14[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_14[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][2U];
                } else {
                    __Vtemp_13[1U] = 0U;
                    __Vtemp_13[2U] = 0U;
                    __Vtemp_14[1U] = 0U;
                }
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[0U] 
                    = ((__Vtemp_13[2U] << 0x00000010U) 
                       | (__Vtemp_13[1U] >> 0x00000010U));
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[0U] 
                    = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[0U];
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[0U] 
                    = (0x000000ffU & (__Vtemp_14[1U] 
                                      >> 8U));
            }
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product[0U] 
                = ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[0U])) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[0U])));
            if ((0U != vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[0U])) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add[0U] 
                    = VL_SHIFTL_QQI(64,64,32, 1ULL, 
                                    (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[0U] 
                                     - (IData)(1U)));
            }
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[0U] 
                = VL_SHIFTR_QQI(64,64,32, (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product[0U] 
                                           + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add[0U]), vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[0U]);
            __Vtemp_16[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[0U]);
            __Vtemp_16[1U] = (IData)((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[0U] 
                                      >> 0x00000020U));
            __Vtemp_16[2U] = 0U;
            VL_NEGATE_W(3, __Vtemp_17, __Vtemp_16);
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[0U] 
                = ((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[0U] 
                    >> 0x1fU) ? (((QData)((IData)(__Vtemp_17[1U])) 
                                  << 0x00000020U) | (QData)((IData)(__Vtemp_17[0U])))
                    : vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[0U]);
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requantized_value[0U] 
                = (VL_LTS_IQQ(64, 0x000000000000007fULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[0U])
                    ? 0x0000007fU : (VL_GTS_IQQ(64, 0xffffffffffffff81ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[0U])
                                      ? 0x00000081U
                                      : (0x000000ffU 
                                         & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[0U]))));
        } else if ((0U < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[1U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[1U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[1U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product[1U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add[1U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[1U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[1U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requantized_value[1U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U] 
            = ((IData)(1U) + (((0x25U >= (0x0000003fU 
                                          & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                               [(0x0000003fU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                : 0U) + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base));
        if ((0x00000c5cU > vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])) {
            if ((1U < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U]))) {
                    __Vtemp_19[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_19[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_19[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][2U];
                    __Vtemp_20[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_20[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_20[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][2U];
                    __Vtemp_21[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_21[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_21[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][2U];
                    __Vtemp_22[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_22[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_22[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][2U];
                    __Vtemp_23[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_23[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_23[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][2U];
                    __Vtemp_24[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_24[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_24[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][2U];
                    __Vtemp_25[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_25[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_25[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][2U];
                    __Vtemp_26[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_26[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_26[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][2U];
                    __Vtemp_27[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_27[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_27[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][2U];
                    __Vtemp_28[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_28[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_28[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][2U];
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
                if (((((((((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U] 
                            >= (((0x25U >= (0x0000003fU 
                                            & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                 [(0x0000003fU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                  : 0U) + ((0x25U >= 
                                            (0x0000003fU 
                                             & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                            ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                                           [(0x0000003fU 
                                             & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
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
                     | ((0U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__activation_mode_latched)) 
                        & ((((__Vtemp_25[2U] << 0x00000010U) 
                             | (__Vtemp_25[1U] >> 0x00000010U)) 
                            != ((__Vtemp_26[1U] << 0x00000018U) 
                                | (__Vtemp_26[0U] >> 8U))) 
                           | ((0x000000ffU & (__Vtemp_27[1U] 
                                              >> 8U)) 
                              != (0x000000ffU & __Vtemp_28[0U])))))) {
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_group_invalid = 1U;
                }
            }
            if ((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[1U] 
                 >> 0x1fU)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U]))) {
                    __Vtemp_29[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_29[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_29[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][2U];
                    __Vtemp_30[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_30[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_30[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][2U];
                } else {
                    __Vtemp_29[0U] = 0U;
                    __Vtemp_29[1U] = 0U;
                    __Vtemp_30[0U] = 0U;
                }
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[1U] 
                    = ((__Vtemp_29[1U] << 0x00000018U) 
                       | (__Vtemp_29[0U] >> 8U));
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[1U] 
                    = ((IData)(1U) + (~ vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[1U]));
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[1U] 
                    = (0x000000ffU & __Vtemp_30[0U]);
            } else {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U]))) {
                    __Vtemp_31[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_31[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_31[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][2U];
                    __Vtemp_32[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_32[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_32[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][2U];
                } else {
                    __Vtemp_31[1U] = 0U;
                    __Vtemp_31[2U] = 0U;
                    __Vtemp_32[1U] = 0U;
                }
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[1U] 
                    = ((__Vtemp_31[2U] << 0x00000010U) 
                       | (__Vtemp_31[1U] >> 0x00000010U));
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[1U] 
                    = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[1U];
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[1U] 
                    = (0x000000ffU & (__Vtemp_32[1U] 
                                      >> 8U));
            }
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product[1U] 
                = ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[1U])) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[1U])));
            if ((0U != vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[1U])) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add[1U] 
                    = VL_SHIFTL_QQI(64,64,32, 1ULL, 
                                    (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[1U] 
                                     - (IData)(1U)));
            }
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[1U] 
                = VL_SHIFTR_QQI(64,64,32, (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product[1U] 
                                           + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add[1U]), vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[1U]);
            __Vtemp_34[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[1U]);
            __Vtemp_34[1U] = (IData)((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[1U] 
                                      >> 0x00000020U));
            __Vtemp_34[2U] = 0U;
            VL_NEGATE_W(3, __Vtemp_35, __Vtemp_34);
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[1U] 
                = ((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[1U] 
                    >> 0x1fU) ? (((QData)((IData)(__Vtemp_35[1U])) 
                                  << 0x00000020U) | (QData)((IData)(__Vtemp_35[0U])))
                    : vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[1U]);
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requantized_value[1U] 
                = (VL_LTS_IQQ(64, 0x000000000000007fULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[1U])
                    ? 0x0000007fU : (VL_GTS_IQQ(64, 0xffffffffffffff81ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[1U])
                                      ? 0x00000081U
                                      : (0x000000ffU 
                                         & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[1U]))));
        } else if ((1U < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[2U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[2U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[2U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product[2U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add[2U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[2U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[2U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requantized_value[2U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U] 
            = ((IData)(2U) + (((0x25U >= (0x0000003fU 
                                          & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                               [(0x0000003fU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                : 0U) + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base));
        if ((0x00000c5cU > vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])) {
            if ((2U < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U]))) {
                    __Vtemp_37[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_37[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_37[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][2U];
                    __Vtemp_38[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_38[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_38[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][2U];
                    __Vtemp_39[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_39[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_39[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][2U];
                    __Vtemp_40[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_40[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_40[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][2U];
                    __Vtemp_41[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_41[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_41[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][2U];
                    __Vtemp_42[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_42[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_42[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][2U];
                    __Vtemp_43[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_43[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_43[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][2U];
                    __Vtemp_44[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_44[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_44[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][2U];
                    __Vtemp_45[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_45[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_45[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][2U];
                    __Vtemp_46[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_46[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_46[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][2U];
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
                if (((((((((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U] 
                            >= (((0x25U >= (0x0000003fU 
                                            & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                 [(0x0000003fU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                  : 0U) + ((0x25U >= 
                                            (0x0000003fU 
                                             & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                            ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                                           [(0x0000003fU 
                                             & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
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
                     | ((0U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__activation_mode_latched)) 
                        & ((((__Vtemp_43[2U] << 0x00000010U) 
                             | (__Vtemp_43[1U] >> 0x00000010U)) 
                            != ((__Vtemp_44[1U] << 0x00000018U) 
                                | (__Vtemp_44[0U] >> 8U))) 
                           | ((0x000000ffU & (__Vtemp_45[1U] 
                                              >> 8U)) 
                              != (0x000000ffU & __Vtemp_46[0U])))))) {
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_group_invalid = 1U;
                }
            }
            if ((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[2U] 
                 >> 0x1fU)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U]))) {
                    __Vtemp_47[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_47[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_47[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][2U];
                    __Vtemp_48[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_48[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_48[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][2U];
                } else {
                    __Vtemp_47[0U] = 0U;
                    __Vtemp_47[1U] = 0U;
                    __Vtemp_48[0U] = 0U;
                }
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[2U] 
                    = ((__Vtemp_47[1U] << 0x00000018U) 
                       | (__Vtemp_47[0U] >> 8U));
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[2U] 
                    = ((IData)(1U) + (~ vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[2U]));
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[2U] 
                    = (0x000000ffU & __Vtemp_48[0U]);
            } else {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U]))) {
                    __Vtemp_49[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_49[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_49[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][2U];
                    __Vtemp_50[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_50[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_50[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][2U];
                } else {
                    __Vtemp_49[1U] = 0U;
                    __Vtemp_49[2U] = 0U;
                    __Vtemp_50[1U] = 0U;
                }
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[2U] 
                    = ((__Vtemp_49[2U] << 0x00000010U) 
                       | (__Vtemp_49[1U] >> 0x00000010U));
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[2U] 
                    = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[2U];
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[2U] 
                    = (0x000000ffU & (__Vtemp_50[1U] 
                                      >> 8U));
            }
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product[2U] 
                = ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[2U])) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[2U])));
            if ((0U != vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[2U])) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add[2U] 
                    = VL_SHIFTL_QQI(64,64,32, 1ULL, 
                                    (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[2U] 
                                     - (IData)(1U)));
            }
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[2U] 
                = VL_SHIFTR_QQI(64,64,32, (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product[2U] 
                                           + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add[2U]), vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[2U]);
            __Vtemp_52[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[2U]);
            __Vtemp_52[1U] = (IData)((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[2U] 
                                      >> 0x00000020U));
            __Vtemp_52[2U] = 0U;
            VL_NEGATE_W(3, __Vtemp_53, __Vtemp_52);
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[2U] 
                = ((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[2U] 
                    >> 0x1fU) ? (((QData)((IData)(__Vtemp_53[1U])) 
                                  << 0x00000020U) | (QData)((IData)(__Vtemp_53[0U])))
                    : vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[2U]);
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requantized_value[2U] 
                = (VL_LTS_IQQ(64, 0x000000000000007fULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[2U])
                    ? 0x0000007fU : (VL_GTS_IQQ(64, 0xffffffffffffff81ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[2U])
                                      ? 0x00000081U
                                      : (0x000000ffU 
                                         & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[2U]))));
        } else if ((2U < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[3U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[3U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[3U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product[3U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add[3U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[3U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[3U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requantized_value[3U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U] 
            = ((IData)(3U) + (((0x25U >= (0x0000003fU 
                                          & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                               [(0x0000003fU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                : 0U) + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base));
        if ((0x00000c5cU > vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])) {
            if ((3U < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U]))) {
                    __Vtemp_55[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_55[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_55[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][2U];
                    __Vtemp_56[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_56[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_56[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][2U];
                    __Vtemp_57[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_57[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_57[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][2U];
                    __Vtemp_58[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_58[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_58[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][2U];
                    __Vtemp_59[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_59[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_59[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][2U];
                    __Vtemp_60[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_60[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_60[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][2U];
                    __Vtemp_61[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_61[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_61[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][2U];
                    __Vtemp_62[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_62[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_62[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][2U];
                    __Vtemp_63[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_63[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_63[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][2U];
                    __Vtemp_64[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_64[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_64[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][2U];
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
                if (((((((((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U] 
                            >= (((0x25U >= (0x0000003fU 
                                            & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                 [(0x0000003fU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                  : 0U) + ((0x25U >= 
                                            (0x0000003fU 
                                             & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                            ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                                           [(0x0000003fU 
                                             & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
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
                     | ((0U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__activation_mode_latched)) 
                        & ((((__Vtemp_61[2U] << 0x00000010U) 
                             | (__Vtemp_61[1U] >> 0x00000010U)) 
                            != ((__Vtemp_62[1U] << 0x00000018U) 
                                | (__Vtemp_62[0U] >> 8U))) 
                           | ((0x000000ffU & (__Vtemp_63[1U] 
                                              >> 8U)) 
                              != (0x000000ffU & __Vtemp_64[0U])))))) {
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_group_invalid = 1U;
                }
            }
            if ((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[3U] 
                 >> 0x1fU)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U]))) {
                    __Vtemp_65[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_65[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_65[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][2U];
                    __Vtemp_66[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_66[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_66[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][2U];
                } else {
                    __Vtemp_65[0U] = 0U;
                    __Vtemp_65[1U] = 0U;
                    __Vtemp_66[0U] = 0U;
                }
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[3U] 
                    = ((__Vtemp_65[1U] << 0x00000018U) 
                       | (__Vtemp_65[0U] >> 8U));
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[3U] 
                    = ((IData)(1U) + (~ vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[3U]));
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[3U] 
                    = (0x000000ffU & __Vtemp_66[0U]);
            } else {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U]))) {
                    __Vtemp_67[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_67[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_67[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][2U];
                    __Vtemp_68[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_68[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_68[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][2U];
                } else {
                    __Vtemp_67[1U] = 0U;
                    __Vtemp_67[2U] = 0U;
                    __Vtemp_68[1U] = 0U;
                }
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[3U] 
                    = ((__Vtemp_67[2U] << 0x00000010U) 
                       | (__Vtemp_67[1U] >> 0x00000010U));
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[3U] 
                    = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[3U];
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[3U] 
                    = (0x000000ffU & (__Vtemp_68[1U] 
                                      >> 8U));
            }
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product[3U] 
                = ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[3U])) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[3U])));
            if ((0U != vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[3U])) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add[3U] 
                    = VL_SHIFTL_QQI(64,64,32, 1ULL, 
                                    (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[3U] 
                                     - (IData)(1U)));
            }
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[3U] 
                = VL_SHIFTR_QQI(64,64,32, (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product[3U] 
                                           + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add[3U]), vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[3U]);
            __Vtemp_70[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[3U]);
            __Vtemp_70[1U] = (IData)((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[3U] 
                                      >> 0x00000020U));
            __Vtemp_70[2U] = 0U;
            VL_NEGATE_W(3, __Vtemp_71, __Vtemp_70);
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[3U] 
                = ((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[3U] 
                    >> 0x1fU) ? (((QData)((IData)(__Vtemp_71[1U])) 
                                  << 0x00000020U) | (QData)((IData)(__Vtemp_71[0U])))
                    : vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[3U]);
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requantized_value[3U] 
                = (VL_LTS_IQQ(64, 0x000000000000007fULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[3U])
                    ? 0x0000007fU : (VL_GTS_IQQ(64, 0xffffffffffffff81ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[3U])
                                      ? 0x00000081U
                                      : (0x000000ffU 
                                         & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[3U]))));
        } else if ((3U < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[4U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[4U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[4U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product[4U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add[4U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[4U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[4U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requantized_value[4U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U] 
            = ((IData)(4U) + (((0x25U >= (0x0000003fU 
                                          & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                               [(0x0000003fU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                : 0U) + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base));
        if ((0x00000c5cU > vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])) {
            if ((4U < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U]))) {
                    __Vtemp_73[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_73[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_73[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][2U];
                    __Vtemp_74[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_74[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_74[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][2U];
                    __Vtemp_75[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_75[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_75[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][2U];
                    __Vtemp_76[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_76[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_76[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][2U];
                    __Vtemp_77[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_77[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_77[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][2U];
                    __Vtemp_78[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_78[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_78[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][2U];
                    __Vtemp_79[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_79[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_79[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][2U];
                    __Vtemp_80[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_80[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_80[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][2U];
                    __Vtemp_81[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_81[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_81[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][2U];
                    __Vtemp_82[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_82[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_82[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][2U];
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
                if (((((((((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U] 
                            >= (((0x25U >= (0x0000003fU 
                                            & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                 [(0x0000003fU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                  : 0U) + ((0x25U >= 
                                            (0x0000003fU 
                                             & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                            ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                                           [(0x0000003fU 
                                             & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
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
                     | ((0U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__activation_mode_latched)) 
                        & ((((__Vtemp_79[2U] << 0x00000010U) 
                             | (__Vtemp_79[1U] >> 0x00000010U)) 
                            != ((__Vtemp_80[1U] << 0x00000018U) 
                                | (__Vtemp_80[0U] >> 8U))) 
                           | ((0x000000ffU & (__Vtemp_81[1U] 
                                              >> 8U)) 
                              != (0x000000ffU & __Vtemp_82[0U])))))) {
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_group_invalid = 1U;
                }
            }
            if ((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[4U] 
                 >> 0x1fU)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U]))) {
                    __Vtemp_83[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_83[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_83[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][2U];
                    __Vtemp_84[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_84[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_84[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][2U];
                } else {
                    __Vtemp_83[0U] = 0U;
                    __Vtemp_83[1U] = 0U;
                    __Vtemp_84[0U] = 0U;
                }
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[4U] 
                    = ((__Vtemp_83[1U] << 0x00000018U) 
                       | (__Vtemp_83[0U] >> 8U));
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[4U] 
                    = ((IData)(1U) + (~ vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[4U]));
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[4U] 
                    = (0x000000ffU & __Vtemp_84[0U]);
            } else {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U]))) {
                    __Vtemp_85[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_85[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_85[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][2U];
                    __Vtemp_86[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_86[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_86[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][2U];
                } else {
                    __Vtemp_85[1U] = 0U;
                    __Vtemp_85[2U] = 0U;
                    __Vtemp_86[1U] = 0U;
                }
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[4U] 
                    = ((__Vtemp_85[2U] << 0x00000010U) 
                       | (__Vtemp_85[1U] >> 0x00000010U));
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[4U] 
                    = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[4U];
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[4U] 
                    = (0x000000ffU & (__Vtemp_86[1U] 
                                      >> 8U));
            }
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product[4U] 
                = ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[4U])) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[4U])));
            if ((0U != vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[4U])) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add[4U] 
                    = VL_SHIFTL_QQI(64,64,32, 1ULL, 
                                    (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[4U] 
                                     - (IData)(1U)));
            }
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[4U] 
                = VL_SHIFTR_QQI(64,64,32, (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product[4U] 
                                           + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add[4U]), vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[4U]);
            __Vtemp_88[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[4U]);
            __Vtemp_88[1U] = (IData)((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[4U] 
                                      >> 0x00000020U));
            __Vtemp_88[2U] = 0U;
            VL_NEGATE_W(3, __Vtemp_89, __Vtemp_88);
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[4U] 
                = ((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[4U] 
                    >> 0x1fU) ? (((QData)((IData)(__Vtemp_89[1U])) 
                                  << 0x00000020U) | (QData)((IData)(__Vtemp_89[0U])))
                    : vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[4U]);
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requantized_value[4U] 
                = (VL_LTS_IQQ(64, 0x000000000000007fULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[4U])
                    ? 0x0000007fU : (VL_GTS_IQQ(64, 0xffffffffffffff81ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[4U])
                                      ? 0x00000081U
                                      : (0x000000ffU 
                                         & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[4U]))));
        } else if ((4U < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[5U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[5U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[5U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product[5U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add[5U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[5U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[5U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requantized_value[5U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U] 
            = ((IData)(5U) + (((0x25U >= (0x0000003fU 
                                          & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                               [(0x0000003fU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                : 0U) + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base));
        if ((0x00000c5cU > vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])) {
            if ((5U < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U]))) {
                    __Vtemp_91[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_91[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_91[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][2U];
                    __Vtemp_92[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_92[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_92[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][2U];
                    __Vtemp_93[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_93[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_93[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][2U];
                    __Vtemp_94[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_94[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_94[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][2U];
                    __Vtemp_95[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_95[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_95[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][2U];
                    __Vtemp_96[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_96[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_96[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][2U];
                    __Vtemp_97[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_97[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_97[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][2U];
                    __Vtemp_98[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_98[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_98[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][2U];
                    __Vtemp_99[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_99[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_99[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][2U];
                    __Vtemp_100[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_100[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_100[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][2U];
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
                if (((((((((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U] 
                            >= (((0x25U >= (0x0000003fU 
                                            & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                 [(0x0000003fU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                  : 0U) + ((0x25U >= 
                                            (0x0000003fU 
                                             & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                            ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                                           [(0x0000003fU 
                                             & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
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
                     | ((0U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__activation_mode_latched)) 
                        & ((((__Vtemp_97[2U] << 0x00000010U) 
                             | (__Vtemp_97[1U] >> 0x00000010U)) 
                            != ((__Vtemp_98[1U] << 0x00000018U) 
                                | (__Vtemp_98[0U] >> 8U))) 
                           | ((0x000000ffU & (__Vtemp_99[1U] 
                                              >> 8U)) 
                              != (0x000000ffU & __Vtemp_100[0U])))))) {
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_group_invalid = 1U;
                }
            }
            if ((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[5U] 
                 >> 0x1fU)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U]))) {
                    __Vtemp_101[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_101[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_101[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][2U];
                    __Vtemp_102[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_102[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_102[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][2U];
                } else {
                    __Vtemp_101[0U] = 0U;
                    __Vtemp_101[1U] = 0U;
                    __Vtemp_102[0U] = 0U;
                }
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[5U] 
                    = ((__Vtemp_101[1U] << 0x00000018U) 
                       | (__Vtemp_101[0U] >> 8U));
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[5U] 
                    = ((IData)(1U) + (~ vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[5U]));
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[5U] 
                    = (0x000000ffU & __Vtemp_102[0U]);
            } else {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U]))) {
                    __Vtemp_103[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_103[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_103[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][2U];
                    __Vtemp_104[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_104[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_104[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][2U];
                } else {
                    __Vtemp_103[1U] = 0U;
                    __Vtemp_103[2U] = 0U;
                    __Vtemp_104[1U] = 0U;
                }
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[5U] 
                    = ((__Vtemp_103[2U] << 0x00000010U) 
                       | (__Vtemp_103[1U] >> 0x00000010U));
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[5U] 
                    = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[5U];
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[5U] 
                    = (0x000000ffU & (__Vtemp_104[1U] 
                                      >> 8U));
            }
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product[5U] 
                = ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[5U])) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[5U])));
            if ((0U != vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[5U])) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add[5U] 
                    = VL_SHIFTL_QQI(64,64,32, 1ULL, 
                                    (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[5U] 
                                     - (IData)(1U)));
            }
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[5U] 
                = VL_SHIFTR_QQI(64,64,32, (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product[5U] 
                                           + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add[5U]), vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[5U]);
            __Vtemp_106[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[5U]);
            __Vtemp_106[1U] = (IData)((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[5U] 
                                       >> 0x00000020U));
            __Vtemp_106[2U] = 0U;
            VL_NEGATE_W(3, __Vtemp_107, __Vtemp_106);
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[5U] 
                = ((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[5U] 
                    >> 0x1fU) ? (((QData)((IData)(__Vtemp_107[1U])) 
                                  << 0x00000020U) | (QData)((IData)(__Vtemp_107[0U])))
                    : vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[5U]);
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requantized_value[5U] 
                = (VL_LTS_IQQ(64, 0x000000000000007fULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[5U])
                    ? 0x0000007fU : (VL_GTS_IQQ(64, 0xffffffffffffff81ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[5U])
                                      ? 0x00000081U
                                      : (0x000000ffU 
                                         & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[5U]))));
        } else if ((5U < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[6U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[6U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[6U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product[6U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add[6U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[6U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[6U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requantized_value[6U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U] 
            = ((IData)(6U) + (((0x25U >= (0x0000003fU 
                                          & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                               [(0x0000003fU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                : 0U) + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base));
        if ((0x00000c5cU > vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])) {
            if ((6U < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U]))) {
                    __Vtemp_109[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_109[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_109[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][2U];
                    __Vtemp_110[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_110[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_110[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][2U];
                    __Vtemp_111[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_111[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_111[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][2U];
                    __Vtemp_112[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_112[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_112[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][2U];
                    __Vtemp_113[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_113[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_113[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][2U];
                    __Vtemp_114[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_114[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_114[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][2U];
                    __Vtemp_115[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_115[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_115[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][2U];
                    __Vtemp_116[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_116[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_116[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][2U];
                    __Vtemp_117[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_117[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_117[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][2U];
                    __Vtemp_118[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_118[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_118[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][2U];
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
                if (((((((((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U] 
                            >= (((0x25U >= (0x0000003fU 
                                            & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                 [(0x0000003fU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                  : 0U) + ((0x25U >= 
                                            (0x0000003fU 
                                             & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                            ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                                           [(0x0000003fU 
                                             & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
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
                     | ((0U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__activation_mode_latched)) 
                        & ((((__Vtemp_115[2U] << 0x00000010U) 
                             | (__Vtemp_115[1U] >> 0x00000010U)) 
                            != ((__Vtemp_116[1U] << 0x00000018U) 
                                | (__Vtemp_116[0U] 
                                   >> 8U))) | ((0x000000ffU 
                                                & (__Vtemp_117[1U] 
                                                   >> 8U)) 
                                               != (0x000000ffU 
                                                   & __Vtemp_118[0U])))))) {
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_group_invalid = 1U;
                }
            }
            if ((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[6U] 
                 >> 0x1fU)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U]))) {
                    __Vtemp_119[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_119[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_119[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][2U];
                    __Vtemp_120[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_120[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_120[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][2U];
                } else {
                    __Vtemp_119[0U] = 0U;
                    __Vtemp_119[1U] = 0U;
                    __Vtemp_120[0U] = 0U;
                }
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[6U] 
                    = ((__Vtemp_119[1U] << 0x00000018U) 
                       | (__Vtemp_119[0U] >> 8U));
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[6U] 
                    = ((IData)(1U) + (~ vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[6U]));
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[6U] 
                    = (0x000000ffU & __Vtemp_120[0U]);
            } else {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U]))) {
                    __Vtemp_121[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_121[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_121[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][2U];
                    __Vtemp_122[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_122[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_122[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][2U];
                } else {
                    __Vtemp_121[1U] = 0U;
                    __Vtemp_121[2U] = 0U;
                    __Vtemp_122[1U] = 0U;
                }
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[6U] 
                    = ((__Vtemp_121[2U] << 0x00000010U) 
                       | (__Vtemp_121[1U] >> 0x00000010U));
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[6U] 
                    = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[6U];
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[6U] 
                    = (0x000000ffU & (__Vtemp_122[1U] 
                                      >> 8U));
            }
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product[6U] 
                = ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[6U])) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[6U])));
            if ((0U != vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[6U])) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add[6U] 
                    = VL_SHIFTL_QQI(64,64,32, 1ULL, 
                                    (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[6U] 
                                     - (IData)(1U)));
            }
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[6U] 
                = VL_SHIFTR_QQI(64,64,32, (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product[6U] 
                                           + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add[6U]), vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[6U]);
            __Vtemp_124[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[6U]);
            __Vtemp_124[1U] = (IData)((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[6U] 
                                       >> 0x00000020U));
            __Vtemp_124[2U] = 0U;
            VL_NEGATE_W(3, __Vtemp_125, __Vtemp_124);
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[6U] 
                = ((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[6U] 
                    >> 0x1fU) ? (((QData)((IData)(__Vtemp_125[1U])) 
                                  << 0x00000020U) | (QData)((IData)(__Vtemp_125[0U])))
                    : vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[6U]);
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requantized_value[6U] 
                = (VL_LTS_IQQ(64, 0x000000000000007fULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[6U])
                    ? 0x0000007fU : (VL_GTS_IQQ(64, 0xffffffffffffff81ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[6U])
                                      ? 0x00000081U
                                      : (0x000000ffU 
                                         & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[6U]))));
        } else if ((6U < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[7U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[7U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[7U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product[7U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add[7U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[7U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[7U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requantized_value[7U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U] 
            = ((IData)(7U) + (((0x25U >= (0x0000003fU 
                                          & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                               [(0x0000003fU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                : 0U) + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base));
        if ((0x00000c5cU > vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])) {
            if ((7U < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U]))) {
                    __Vtemp_127[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_127[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_127[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][2U];
                    __Vtemp_128[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_128[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_128[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][2U];
                    __Vtemp_129[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_129[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_129[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][2U];
                    __Vtemp_130[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_130[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_130[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][2U];
                    __Vtemp_131[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_131[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_131[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][2U];
                    __Vtemp_132[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_132[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_132[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][2U];
                    __Vtemp_133[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_133[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_133[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][2U];
                    __Vtemp_134[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_134[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_134[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][2U];
                    __Vtemp_135[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_135[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_135[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][2U];
                    __Vtemp_136[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_136[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_136[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][2U];
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
                if (((((((((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U] 
                            >= (((0x25U >= (0x0000003fU 
                                            & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                 [(0x0000003fU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                  : 0U) + ((0x25U >= 
                                            (0x0000003fU 
                                             & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                            ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                                           [(0x0000003fU 
                                             & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
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
                     | ((0U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__activation_mode_latched)) 
                        & ((((__Vtemp_133[2U] << 0x00000010U) 
                             | (__Vtemp_133[1U] >> 0x00000010U)) 
                            != ((__Vtemp_134[1U] << 0x00000018U) 
                                | (__Vtemp_134[0U] 
                                   >> 8U))) | ((0x000000ffU 
                                                & (__Vtemp_135[1U] 
                                                   >> 8U)) 
                                               != (0x000000ffU 
                                                   & __Vtemp_136[0U])))))) {
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_group_invalid = 1U;
                }
            }
            if ((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[7U] 
                 >> 0x1fU)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U]))) {
                    __Vtemp_137[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_137[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_137[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][2U];
                    __Vtemp_138[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_138[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_138[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][2U];
                } else {
                    __Vtemp_137[0U] = 0U;
                    __Vtemp_137[1U] = 0U;
                    __Vtemp_138[0U] = 0U;
                }
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[7U] 
                    = ((__Vtemp_137[1U] << 0x00000018U) 
                       | (__Vtemp_137[0U] >> 8U));
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[7U] 
                    = ((IData)(1U) + (~ vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[7U]));
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[7U] 
                    = (0x000000ffU & __Vtemp_138[0U]);
            } else {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U]))) {
                    __Vtemp_139[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_139[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_139[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][2U];
                    __Vtemp_140[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_140[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_140[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][2U];
                } else {
                    __Vtemp_139[1U] = 0U;
                    __Vtemp_139[2U] = 0U;
                    __Vtemp_140[1U] = 0U;
                }
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[7U] 
                    = ((__Vtemp_139[2U] << 0x00000010U) 
                       | (__Vtemp_139[1U] >> 0x00000010U));
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[7U] 
                    = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[7U];
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[7U] 
                    = (0x000000ffU & (__Vtemp_140[1U] 
                                      >> 8U));
            }
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product[7U] 
                = ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[7U])) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[7U])));
            if ((0U != vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[7U])) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add[7U] 
                    = VL_SHIFTL_QQI(64,64,32, 1ULL, 
                                    (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[7U] 
                                     - (IData)(1U)));
            }
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[7U] 
                = VL_SHIFTR_QQI(64,64,32, (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product[7U] 
                                           + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add[7U]), vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[7U]);
            __Vtemp_142[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[7U]);
            __Vtemp_142[1U] = (IData)((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[7U] 
                                       >> 0x00000020U));
            __Vtemp_142[2U] = 0U;
            VL_NEGATE_W(3, __Vtemp_143, __Vtemp_142);
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[7U] 
                = ((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[7U] 
                    >> 0x1fU) ? (((QData)((IData)(__Vtemp_143[1U])) 
                                  << 0x00000020U) | (QData)((IData)(__Vtemp_143[0U])))
                    : vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[7U]);
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requantized_value[7U] 
                = (VL_LTS_IQQ(64, 0x000000000000007fULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[7U])
                    ? 0x0000007fU : (VL_GTS_IQQ(64, 0xffffffffffffff81ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[7U])
                                      ? 0x00000081U
                                      : (0x000000ffU 
                                         & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[7U]))));
        } else if ((7U < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_group_invalid = 1U;
        }
    } else {
        if ((0U < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[1U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[1U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[1U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product[1U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add[1U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[1U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[1U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requantized_value[1U] = 0U;
        if ((1U < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[2U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[2U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[2U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product[2U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add[2U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[2U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[2U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requantized_value[2U] = 0U;
        if ((2U < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[3U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[3U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[3U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product[3U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add[3U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[3U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[3U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requantized_value[3U] = 0U;
        if ((3U < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[4U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[4U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[4U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product[4U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add[4U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[4U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[4U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requantized_value[4U] = 0U;
        if ((4U < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[5U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[5U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[5U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product[5U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add[5U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[5U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[5U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requantized_value[5U] = 0U;
        if ((5U < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[6U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[6U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[6U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product[6U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add[6U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[6U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[6U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requantized_value[6U] = 0U;
        if ((6U < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[7U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[7U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[7U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product[7U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add[7U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[7U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[7U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requantized_value[7U] = 0U;
        if ((7U < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_group_invalid = 1U;
        }
    }
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_result_error = 6U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_result_valid = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_result_ready 
        = (((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__hard_reset)) 
            & (2U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))) 
           & (0x12U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__state)));
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
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_write = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_write = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_write = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_write = 0U;
    __Vtemp_145[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_batch_count_latched;
    __Vtemp_145[1U] = 0U;
    __Vtemp_145[2U] = 0U;
    __Vtemp_145[3U] = 0U;
    __Vtemp_146[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_channels_latched;
    __Vtemp_146[1U] = 0U;
    __Vtemp_146[2U] = 0U;
    __Vtemp_146[3U] = 0U;
    VL_MUL_W(4, __Vtemp_147, __Vtemp_145, __Vtemp_146);
    __Vtemp_148[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_height_latched;
    __Vtemp_148[1U] = 0U;
    __Vtemp_148[2U] = 0U;
    __Vtemp_148[3U] = 0U;
    VL_MUL_W(4, __Vtemp_149, __Vtemp_147, __Vtemp_148);
    __Vtemp_150[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_width_latched;
    __Vtemp_150[1U] = 0U;
    __Vtemp_150[2U] = 0U;
    __Vtemp_150[3U] = 0U;
    VL_MUL_W(4, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_elements_wide, __Vtemp_149, __Vtemp_150);
    __Vtemp_151[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_batch_count_latched;
    __Vtemp_151[1U] = 0U;
    __Vtemp_151[2U] = 0U;
    __Vtemp_151[3U] = 0U;
    __Vtemp_152[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_channels_latched;
    __Vtemp_152[1U] = 0U;
    __Vtemp_152[2U] = 0U;
    __Vtemp_152[3U] = 0U;
    VL_MUL_W(4, __Vtemp_153, __Vtemp_151, __Vtemp_152);
    __Vtemp_154[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_latched;
    __Vtemp_154[1U] = 0U;
    __Vtemp_154[2U] = 0U;
    __Vtemp_154[3U] = 0U;
    VL_MUL_W(4, __Vtemp_155, __Vtemp_153, __Vtemp_154);
    __Vtemp_156[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_latched;
    __Vtemp_156[1U] = 0U;
    __Vtemp_156[2U] = 0U;
    __Vtemp_156[3U] = 0U;
    VL_MUL_W(4, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_elements_wide, __Vtemp_155, __Vtemp_156);
    __Vtemp_157[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_channels_latched;
    __Vtemp_157[1U] = 0U;
    __Vtemp_157[2U] = 0U;
    __Vtemp_157[3U] = 0U;
    __Vtemp_158[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_channels_latched;
    __Vtemp_158[1U] = 0U;
    __Vtemp_158[2U] = 0U;
    __Vtemp_158[3U] = 0U;
    VL_MUL_W(4, __Vtemp_159, __Vtemp_157, __Vtemp_158);
    __Vtemp_160[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_height_latched;
    __Vtemp_160[1U] = 0U;
    __Vtemp_160[2U] = 0U;
    __Vtemp_160[3U] = 0U;
    VL_MUL_W(4, __Vtemp_161, __Vtemp_159, __Vtemp_160);
    __Vtemp_162[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_width_latched;
    __Vtemp_162[1U] = 0U;
    __Vtemp_162[2U] = 0U;
    __Vtemp_162[3U] = 0U;
    VL_MUL_W(4, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__expected_weight_bytes_wide, __Vtemp_161, __Vtemp_162);
    __Vtemp_163[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_channels_latched;
    __Vtemp_163[1U] = 0U;
    __Vtemp_163[2U] = 0U;
    __Vtemp_163[3U] = 0U;
    __Vtemp_164[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_height_latched;
    __Vtemp_164[1U] = 0U;
    __Vtemp_164[2U] = 0U;
    __Vtemp_164[3U] = 0U;
    VL_MUL_W(4, __Vtemp_165, __Vtemp_163, __Vtemp_164);
    __Vtemp_166[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_width_latched;
    __Vtemp_166[1U] = 0U;
    __Vtemp_166[2U] = 0U;
    __Vtemp_166[3U] = 0U;
    VL_MUL_W(4, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_wide, __Vtemp_165, __Vtemp_166);
    __Vtemp_167[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_base_latched;
    __Vtemp_167[1U] = 0U;
    __Vtemp_167[2U] = 0U;
    __Vtemp_167[3U] = 0U;
    __Vtemp_168[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_length_latched;
    __Vtemp_168[1U] = 0U;
    __Vtemp_168[2U] = 0U;
    __Vtemp_168[3U] = 0U;
    VL_ADD_W(4, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_end_wide, __Vtemp_167, __Vtemp_168);
    __Vtemp_169[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_base_latched;
    __Vtemp_169[1U] = 0U;
    __Vtemp_169[2U] = 0U;
    __Vtemp_169[3U] = 0U;
    __Vtemp_170[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_length_latched;
    __Vtemp_170[1U] = 0U;
    __Vtemp_170[2U] = 0U;
    __Vtemp_170[3U] = 0U;
    VL_ADD_W(4, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_end_wide, __Vtemp_169, __Vtemp_170);
    __Vtemp_171[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_package_base_latched;
    __Vtemp_171[1U] = 0U;
    __Vtemp_171[2U] = 0U;
    __Vtemp_171[3U] = 0U;
    __Vtemp_172[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_package_length_latched;
    __Vtemp_172[1U] = 0U;
    __Vtemp_172[2U] = 0U;
    __Vtemp_172[3U] = 0U;
    VL_ADD_W(4, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_package_end_wide, __Vtemp_171, __Vtemp_172);
    __Vtemp_173[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__quantized_weight_offset_latched;
    __Vtemp_173[1U] = 0U;
    __Vtemp_173[2U] = 0U;
    __Vtemp_173[3U] = 0U;
    __Vtemp_174[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__quantized_weight_bytes_latched;
    __Vtemp_174[1U] = 0U;
    __Vtemp_174[2U] = 0U;
    __Vtemp_174[3U] = 0U;
    VL_ADD_W(4, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__quantized_weight_end_wide, __Vtemp_173, __Vtemp_174);
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_numerator 
        = (((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_height_latched)) 
            + (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__pad_top_latched))) 
           + (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__pad_bottom_latched)));
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_numerator 
        = (((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_width_latched)) 
            + (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__pad_left_latched))) 
           + (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__pad_right_latched)));
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_height_wide[0U] = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_height_wide[1U] = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_height_wide[2U] = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_height_wide[3U] = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_width_wide[0U] = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_width_wide[1U] = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_width_wide[2U] = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_width_wide[3U] = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_bytes_wide[0U] = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_bytes_wide[1U] = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_bytes_wide[2U] = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_bytes_wide[3U] = 0U;
    if (((0U != vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_latched) 
         & (0U != vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_latched))) {
        __Vtemp_175[0U] = (((8U > vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_latched)
                             ? vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_latched
                             : 8U) - (IData)(1U));
        __Vtemp_175[1U] = 0U;
        __Vtemp_175[2U] = 0U;
        __Vtemp_175[3U] = 0U;
        __Vtemp_176[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__stride_y_latched;
        __Vtemp_176[1U] = 0U;
        __Vtemp_176[2U] = 0U;
        __Vtemp_176[3U] = 0U;
        VL_MUL_W(4, __Vtemp_177, __Vtemp_175, __Vtemp_176);
        __Vtemp_178[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_height_latched;
        __Vtemp_178[1U] = 0U;
        __Vtemp_178[2U] = 0U;
        __Vtemp_178[3U] = 0U;
        VL_ADD_W(4, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_height_wide, __Vtemp_177, __Vtemp_178);
        __Vtemp_179[0U] = (((8U > vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_latched)
                             ? vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_latched
                             : 8U) - (IData)(1U));
        __Vtemp_179[1U] = 0U;
        __Vtemp_179[2U] = 0U;
        __Vtemp_179[3U] = 0U;
        __Vtemp_180[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__stride_x_latched;
        __Vtemp_180[1U] = 0U;
        __Vtemp_180[2U] = 0U;
        __Vtemp_180[3U] = 0U;
        VL_MUL_W(4, __Vtemp_181, __Vtemp_179, __Vtemp_180);
        __Vtemp_182[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_width_latched;
        __Vtemp_182[1U] = 0U;
        __Vtemp_182[2U] = 0U;
        __Vtemp_182[3U] = 0U;
        VL_ADD_W(4, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_width_wide, __Vtemp_181, __Vtemp_182);
        VL_MUL_W(4, __Vtemp_183, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_height_wide, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_width_wide);
        __Vtemp_184[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_channels_latched;
        __Vtemp_184[1U] = 0U;
        __Vtemp_184[2U] = 0U;
        __Vtemp_184[3U] = 0U;
        VL_MUL_W(4, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_bytes_wide, __Vtemp_183, __Vtemp_184);
    }
    __Vtemp_185[0U] = ((8U > vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_channels_latched)
                        ? vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_channels_latched
                        : 8U);
    __Vtemp_185[1U] = 0U;
    __Vtemp_185[2U] = 0U;
    __Vtemp_185[3U] = 0U;
    VL_MUL_W(4, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__full_weight_group_bytes_wide, __Vtemp_185, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_wide);
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__validation_ok = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__validation_error = 1U;
    __Vtemp_187[0U] = 0x00001fffU;
    __Vtemp_187[1U] = 0U;
    __Vtemp_187[2U] = 0U;
    __Vtemp_187[3U] = 0U;
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
                  | VL_LT_W(4, __Vtemp_187, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_wide)) 
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
        if ((((((VL_LT_W(4, __Vtemp_188, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_elements_wide) 
                 | (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_length_latched 
                    != tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_elements_wide[0U])) 
                | VL_LT_W(4, __Vtemp_189, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_elements_wide)) 
               | (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_length_latched 
                  != vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_elements_wide[0U])) 
              | VL_LT_W(4, __Vtemp_190, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__expected_weight_bytes_wide)) 
             | (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__quantized_weight_bytes_latched 
                != tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__expected_weight_bytes_wide[0U]))) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__validation_error = 3U;
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
            __Vtemp_194[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_package_length_latched;
            __Vtemp_194[1U] = 0U;
            __Vtemp_194[2U] = 0U;
            __Vtemp_194[3U] = 0U;
            __Vtemp_195[0U] = 0x00000c5cU;
            __Vtemp_195[1U] = 0U;
            __Vtemp_195[2U] = 0U;
            __Vtemp_195[3U] = 0U;
            __Vtemp_196[0U] = ((0x25U >= (0x0000003fU 
                                          & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                               [(0x0000003fU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                : 0U);
            __Vtemp_196[1U] = 0U;
            __Vtemp_196[2U] = 0U;
            __Vtemp_196[3U] = 0U;
            __Vtemp_197[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_channels_latched;
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
            if (((((((((VL_LT_W(4, __Vtemp_191, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_end_wide) 
                        | VL_LT_W(4, __Vtemp_192, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_end_wide)) 
                       | VL_LT_W(4, __Vtemp_193, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_package_end_wide)) 
                      | (0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_package_length_latched)) 
                     | VL_GT_W(4, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__quantized_weight_end_wide, __Vtemp_194)) 
                    | (((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                         ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                        [(0x0000003fU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                         : 0U) != vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_channels_latched)) 
                   | VL_LT_W(4, __Vtemp_195, __Vtemp_198)) 
                  | VL_LT_W(4, __Vtemp_199, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_bytes_wide)) 
                 | VL_LT_W(4, __Vtemp_200, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__full_weight_group_bytes_wide))) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__validation_error = 2U;
            } else if (((((tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_numerator 
                           < (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_height_latched))) 
                          | (tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_numerator 
                             < (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_width_latched)))) 
                         | ((1ULL + VL_DIV_QQQ(64, 
                                               (tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_numerator 
                                                - (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_height_latched))), (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__stride_y_latched)))) 
                            != (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_latched)))) 
                        | ((1ULL + VL_DIV_QQQ(64, (tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_numerator 
                                                   - (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_width_latched))), (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__stride_x_latched)))) 
                           != (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_latched))))) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__validation_error = 1U;
            } else {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__validation_ok = 1U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__validation_error = 0U;
            }
        }
    }
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__patch_plane_bytes 
        = ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__patch_height)) 
           * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__patch_width)));
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_channel = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_rem = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_y = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_x = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_input_y = 0ULL;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_input_x = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_in_bounds = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_source_offset = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_source_address_wide = 0ULL;
    if (((0ULL != tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__patch_plane_bytes) 
         & (0U != vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__patch_width))) {
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_channel 
            = (IData)(VL_DIV_QQQ(64, (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_index)), tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__patch_plane_bytes));
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_rem 
            = (IData)(VL_MODDIV_QQQ(64, (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_index)), tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__patch_plane_bytes));
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_y 
            = VL_DIV_III(32, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_rem, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__patch_width);
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_x 
            = VL_MODDIV_III(32, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_rem, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__patch_width);
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_input_y 
            = ((((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_y)) 
                 * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__stride_y_latched))) 
                + (QData)((IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_y))) 
               - (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__pad_top_latched)));
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_input_x 
            = ((((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_x)) 
                 * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__stride_x_latched))) 
                + (QData)((IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_x))) 
               - (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__pad_left_latched)));
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_in_bounds 
            = (((VL_LTES_IQQ(64, 0ULL, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_input_y) 
                 & VL_LTS_IQQ(64, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_input_y, (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_height_latched)))) 
                & VL_LTES_IQQ(64, 0ULL, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_input_x)) 
               & VL_LTS_IQQ(64, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_input_x, (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_width_latched))));
        if (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_in_bounds) {
            tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_source_offset 
                = (((((QData)((IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_channel)) 
                      * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_height_latched))) 
                     + tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_input_y) 
                    * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_width_latched))) 
                   + tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_input_x);
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_source_address_wide 
                = ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_base_latched)) 
                   + tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_source_offset);
        }
    }
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_area 
        = (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_height_latched 
           * vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_width_latched);
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_input_channel = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_y = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_x = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_y = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_x = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_input_y = 0ULL;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_input_x = 0ULL;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_tap_in_bounds = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index_wide = 0ULL;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index = 0U;
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
    if (((0U != tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_area) 
         & (0U != vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__tile_width))) {
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_input_channel 
            = VL_DIV_III(32, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_reduction_index, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_area);
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_y 
            = VL_DIV_III(32, VL_MODDIV_III(32, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_reduction_index, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_area), vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_width_latched);
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_x 
            = VL_MODDIV_III(32, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_reduction_index, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_width_latched);
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_y 
            = VL_DIV_III(32, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_index, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__tile_width);
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_x 
            = VL_MODDIV_III(32, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_index, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__tile_width);
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_input_y 
            = (((((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_y)) 
                  * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__stride_y_latched))) 
                 + ((QData)((IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_y)) 
                    * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__stride_y_latched)))) 
                + (QData)((IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_y))) 
               - (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__pad_top_latched)));
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_input_x 
            = (((((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_x)) 
                  * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__stride_x_latched))) 
                 + ((QData)((IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_x)) 
                    * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__stride_x_latched)))) 
                + (QData)((IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_x))) 
               - (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__pad_left_latched)));
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_tap_in_bounds 
            = (((VL_LTES_IQQ(64, 0ULL, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_input_y) 
                 & VL_LTS_IQQ(64, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_input_y, (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_height_latched)))) 
                & VL_LTES_IQQ(64, 0ULL, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_input_x)) 
               & VL_LTS_IQQ(64, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_input_x, (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_width_latched))));
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index_wide 
            = (((((QData)((IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_input_channel)) 
                  * tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__patch_plane_bytes) 
                 + ((((QData)((IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_y)) 
                      * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__stride_y_latched))) 
                     + (QData)((IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_y))) 
                    * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__patch_width)))) 
                + ((QData)((IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_x)) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__stride_x_latched)))) 
               + (QData)((IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_x)));
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index 
            = (IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index_wide);
        if ((0U < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[0U] 
                = ((IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_tap_in_bounds)
                    ? ((0xc7ffU >= (0x0000ffffU & tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index))
                        ? vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_patch
                       [(0x0000ffffU & tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index)]
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
            if (((IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_tap_in_bounds) 
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
                = ((IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_tap_in_bounds)
                    ? ((0xc7ffU >= (0x0000ffffU & tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index))
                        ? vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_patch
                       [(0x0000ffffU & tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index)]
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
            if (((IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_tap_in_bounds) 
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
                = ((IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_tap_in_bounds)
                    ? ((0xc7ffU >= (0x0000ffffU & tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index))
                        ? vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_patch
                       [(0x0000ffffU & tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index)]
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
            if (((IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_tap_in_bounds) 
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
                = ((IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_tap_in_bounds)
                    ? ((0xc7ffU >= (0x0000ffffU & tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index))
                        ? vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_patch
                       [(0x0000ffffU & tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index)]
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
            if (((IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_tap_in_bounds) 
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
                = ((IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_tap_in_bounds)
                    ? ((0xc7ffU >= (0x0000ffffU & tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index))
                        ? vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_patch
                       [(0x0000ffffU & tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index)]
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
            if (((IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_tap_in_bounds) 
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
                = ((IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_tap_in_bounds)
                    ? ((0xc7ffU >= (0x0000ffffU & tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index))
                        ? vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_patch
                       [(0x0000ffffU & tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index)]
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
            if (((IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_tap_in_bounds) 
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
                = ((IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_tap_in_bounds)
                    ? ((0xc7ffU >= (0x0000ffffU & tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index))
                        ? vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_patch
                       [(0x0000ffffU & tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index)]
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
            if (((IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_tap_in_bounds) 
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
                = ((IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_tap_in_bounds)
                    ? ((0xc7ffU >= (0x0000ffffU & tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index))
                        ? vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_patch
                       [(0x0000ffffU & tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index)]
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
            if (((IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_tap_in_bounds) 
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
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__query_output_channels = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__query_output_height = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__query_output_width = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__query_source_index = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__query_source_address = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__query_output_value = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__query_error_code = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_argument = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_range = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source0_shape_bytes = 0ULL;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_shape_bytes = 0ULL;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_plane_elements = 0ULL;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_object_end = 0ULL;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__expected_group_start = 0ULL;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__expected_group_end = 0ULL;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_selected_count = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_multiplier = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_base_address = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_length_bytes = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_value = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_magnitude = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__scaled_product = 0ULL;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__rounded_magnitude = 0ULL;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__scaled_signed = 0ULL;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_source_index = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_source_channel = 0U;
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
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_argument = 1U;
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
            tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_argument = 1U;
        }
    }
    if (((1U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__groups_latched) 
         & ((0U != vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_start_latched) 
            | (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_end_latched 
               != vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_channels_latched)))) {
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_argument = 1U;
    } else if ((1U < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__groups_latched)) {
        if (((1U != vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source_count_latched) 
             | (0U != VL_MODDIV_III(32, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_channels_latched, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__groups_latched)))) {
            tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_argument = 1U;
        } else {
            tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__expected_group_start 
                = ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__group_id_latched)) 
                   * VL_DIV_QQQ(64, (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_channels_latched)), (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__groups_latched))));
            tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__expected_group_end 
                = (tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__expected_group_start 
                   + VL_DIV_QQQ(64, (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_channels_latched)), (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__groups_latched))));
            if (((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_start_latched 
                  != (IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__expected_group_start)) 
                 | (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_end_latched 
                    != (IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__expected_group_end)))) {
                tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_argument = 1U;
            }
        }
    }
    if (((2U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source_count_latched) 
         & (((0U != vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_start_latched) 
             | (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_end_latched 
                != vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_channels_latched)) 
            | (1U != vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__groups_latched)))) {
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_argument = 1U;
    }
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source0_selected_count 
        = (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_end_latched 
           - vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_start_latched);
    if ((2U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source_count_latched)) {
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_selected_count 
            = (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_end_latched 
               - vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_start_latched);
    }
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__output_channels_wide 
        = ((QData)((IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source0_selected_count)) 
           + (QData)((IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_selected_count)));
    if ((0x00000000ffffffffULL < tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__output_channels_wide)) {
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_range = 1U;
    }
    if ((((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_y_latched 
           >= vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_height_latched) 
          | (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_x_latched 
             >= vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_width_latched)) 
         | ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_channel_latched)) 
            >= tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__output_channels_wide))) {
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_argument = 1U;
    }
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source0_plane_elements 
        = ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_channels_latched)) 
           * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_height_latched)));
    if ((0x00000000ffffffffULL < tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source0_plane_elements)) {
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_range = 1U;
    } else {
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source0_shape_bytes 
            = (tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source0_plane_elements 
               * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_width_latched)));
        if ((0x00000000ffffffffULL < tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source0_shape_bytes)) {
            tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_range = 1U;
        }
    }
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source0_object_end 
        = ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_base_latched)) 
           + (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_length_latched)));
    if ((((0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_length_latched) 
          | ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_length_latched)) 
             < tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source0_shape_bytes)) 
         | (0x0000000100000000ULL < tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source0_object_end))) {
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_range = 1U;
    }
    if ((2U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source_count_latched)) {
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_plane_elements 
            = ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_channels_latched)) 
               * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_height_latched)));
        if ((0x00000000ffffffffULL < tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_plane_elements)) {
            tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_range = 1U;
        } else {
            tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_shape_bytes 
                = (tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_plane_elements 
                   * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_width_latched)));
            if ((0x00000000ffffffffULL < tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_shape_bytes)) {
                tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_range = 1U;
            }
        }
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_object_end 
            = ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_base_latched)) 
               + (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_length_latched)));
        if ((((0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_length_latched) 
              | ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_length_latched)) 
                 < tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_shape_bytes)) 
             | (0x0000000100000000ULL < tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_object_end))) {
            tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_range = 1U;
        }
    }
    if ((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_channel_latched 
         < tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source0_selected_count)) {
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_source_index = 0U;
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_source_channel 
            = (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_start_latched 
               + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_channel_latched);
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_value 
            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_value_latched;
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_multiplier 
            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_multiplier_latched;
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_base_address 
            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_base_latched;
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_length_bytes 
            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_length_latched;
    } else if ((2U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source_count_latched)) {
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_source_index = 1U;
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_source_channel 
            = (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_start_latched 
               + (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_channel_latched 
                  - tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source0_selected_count));
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_value 
            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_value_latched;
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_multiplier 
            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_multiplier_latched;
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_base_address 
            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_base_latched;
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_length_bytes 
            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_length_latched;
    }
    if ((0x80U == (IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_value))) {
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_argument = 1U;
    }
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_offset 
        = (((((QData)((IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_source_channel)) 
              * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_height_latched))) 
             + (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_y_latched))) 
            * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_width_latched))) 
           + (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_x_latched)));
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_address_wide 
        = ((QData)((IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_base_address)) 
           + tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_offset);
    if (((tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_offset 
          >= (QData)((IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_length_bytes))) 
         | (0x00000000ffffffffULL < tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_address_wide))) {
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_range = 1U;
    }
    if (tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_argument) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__query_error_code = 1U;
    } else if (tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_range) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__query_error_code = 2U;
    } else {
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_magnitude 
            = (0x000000ffU & (VL_GTS_III(8, 0U, (IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_value))
                               ? (- (IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_value))
                               : (IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_value)));
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__scaled_product 
            = ((QData)((IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_magnitude)) 
               * (QData)((IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_multiplier)));
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__query_output_channels 
            = (IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__output_channels_wide);
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__query_output_height 
            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_height_latched;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__query_output_width 
            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_width_latched;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__query_source_index 
            = tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_source_index;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__query_source_address 
            = (IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_address_wide);
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__rounded_magnitude 
            = ((0x0000000040000000ULL + tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__scaled_product) 
               >> 0x0000001fU);
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__scaled_signed 
            = (VL_GTS_III(8, 0U, (IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_value))
                ? (- tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__rounded_magnitude)
                : tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__rounded_magnitude);
        if (VL_LTS_IQQ(64, 0x000000000000007fULL, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__scaled_signed)) {
            tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__scaled_signed = 0x000000000000007fULL;
        } else if (VL_GTS_IQQ(64, 0xffffffffffffff81ULL, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__scaled_signed)) {
            tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__scaled_signed = 0xffffffffffffff81ULL;
        }
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__query_output_value 
            = (0x000000ffU & (IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__scaled_signed));
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
                tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_wdata 
                    = VL_SHIFTL_III(32,32,32, (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__result_value_latched), 
                                    (0x00000018U & 
                                     (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_address_latched 
                                      << 3U)));
                tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_write = 1U;
            }
        }
        if ((1U != (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__state))) {
            if ((3U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__state))) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_wstrb 
                    = (0x0000000fU & ((IData)(1U) << 
                                      (3U & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__output_address_latched)));
                tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_wdata 
                    = VL_SHIFTL_III(32,32,32, (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__copied_value_latched), 
                                    (0x00000018U & 
                                     (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__output_address_latched 
                                      << 3U)));
                tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_write = 1U;
            }
        }
        if ((2U != (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__state))) {
            if ((5U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__state))) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_wstrb 
                    = (0x0000000fU & ((IData)(1U) << 
                                      (3U & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_address_latched)));
                tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_wdata 
                    = VL_SHIFTL_III(32,32,32, (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__result_value_latched), 
                                    (0x00000018U & 
                                     (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_address_latched 
                                      << 3U)));
                tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_write = 1U;
            }
        }
        if ((1U & (~ ((4U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__state)) 
                      || (8U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__state)))))) {
            if ((0x0fU == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__state))) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_wstrb 
                    = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__request_strobe_latched;
            }
        }
        if ((1U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__state))) {
            tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_rstrb 
                = (0x0000000fU & ((IData)(1U) << (3U 
                                                  & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__source_address_latched)));
            tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_addr 
                = (0xfffffffcU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__source_address_latched);
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_valid = 1U;
        } else if ((3U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__state))) {
            tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_addr 
                = (0xfffffffcU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__output_address_latched);
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_valid = 1U;
        }
        if (((4U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__state)) 
             || (8U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__state)))) {
            tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_rstrb 
                = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__request_strobe_latched;
            tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_write = 0U;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_valid = 1U;
        } else if ((0x0fU == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__state))) {
            tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_write = 1U;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_valid = 1U;
        }
        if ((2U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__state))) {
            tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_rstrb 
                = tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__selected_read_lane;
            tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_addr 
                = tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__selected_word_address;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_valid = 1U;
        } else if ((5U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__state))) {
            tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_addr 
                = (0xfffffffcU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_address_latched);
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_valid = 1U;
        }
        if ((1U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__state))) {
            tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_rstrb 
                = tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__selected_input_lane;
            tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_addr 
                = tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__selected_input_word_address;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_valid = 1U;
        } else if ((4U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__state))) {
            tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_addr 
                = (0xfffffffcU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_address_latched);
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_valid = 1U;
        }
    }
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_start_ready 
        = ((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__hard_reset)) 
           & ((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__backend_abort)) 
              & (0U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__state))));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_start_ready 
        = ((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__hard_reset)) 
           & ((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__backend_abort)) 
              & (0U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__state))));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_start_ready 
        = ((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__hard_reset)) 
           & ((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__backend_abort)) 
              & (0U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__state))));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_start_ready 
        = ((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__hard_reset)) 
           & ((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__backend_abort)) 
              & (0U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__state))));
    __Vtemp_202[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_x_latched;
    __Vtemp_202[1U] = 0U;
    __Vtemp_202[2U] = 0U;
    __Vtemp_204[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_y_latched;
    __Vtemp_204[1U] = 0U;
    __Vtemp_204[2U] = 0U;
    __Vtemp_205[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_channel_latched;
    __Vtemp_205[1U] = 0U;
    __Vtemp_205[2U] = 0U;
    VL_MUL_W(3, __Vtemp_206, vlSelfRef.__VdfgRegularize_h6e95ff9d_0_8, __Vtemp_205);
    VL_ADD_W(3, __Vtemp_207, __Vtemp_204, __Vtemp_206);
    __Vtemp_208[0U] = __Vtemp_207[0U];
    __Vtemp_208[1U] = __Vtemp_207[1U];
    __Vtemp_208[2U] = (1U & __Vtemp_207[2U]);
    VL_MUL_W(3, __Vtemp_209, vlSelfRef.__VdfgRegularize_h6e95ff9d_0_7, __Vtemp_208);
    VL_ADD_W(3, __Vtemp_210, __Vtemp_202, __Vtemp_209);
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_offset_work[0U] 
        = __Vtemp_210[0U];
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_offset_work[1U] 
        = __Vtemp_210[1U];
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_offset_work[2U] 
        = (1U & __Vtemp_210[2U]);
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_address_wide 
        = ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_base_latched)) 
           + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_byte_offset_wide);
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_wdata = 0U;
    if ((4U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))) {
        if ((1U & (~ ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                      >> 1U)))) {
            if ((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_result_error 
                    = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__result_error_latched;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_result_valid 
                    = ((5U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__state)) 
                       & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_result_ready));
                tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_wdata 
                    = tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_wdata;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_wdata 
                    = tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_wdata;
                tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_addr = 0U;
                tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_addr 
                    = tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_addr;
            } else {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_result_error 
                    = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__result_error_latched;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_result_valid 
                    = ((7U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__state)) 
                       & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_result_ready));
                tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_wdata 
                    = tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_wdata;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_wdata 
                    = tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_wdata;
                tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_addr = 0U;
                tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_addr 
                    = tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_addr;
            }
        } else {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_wdata 
                = tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_wdata;
            tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_addr = 0U;
        }
    } else if ((2U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))) {
        if ((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_result_error 
                = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__result_error_latched;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_result_valid 
                = ((6U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__state)) 
                   & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_result_ready));
            tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_wdata 
                = tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_wdata;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_wdata 
                = tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_wdata;
            tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_addr = 0U;
            tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_addr 
                = tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_addr;
        } else {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_result_error 
                = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__result_error_latched;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_result_valid 
                = ((0x12U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__state)) 
                   & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_result_ready));
            tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_wdata 
                = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__request_wdata_latched;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_wdata 
                = tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_wdata;
            tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_addr = 0U;
            tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_addr 
                = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__request_address_latched;
        }
    } else {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_wdata 
            = tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_wdata;
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_addr = 0U;
    }
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_addr 
        = tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_addr;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_valid 
        = ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__buffer_owner_pl) 
           & ((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__hard_reset)) 
              & ((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__backend_abort)) 
                 & ((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_pending)) 
                    & ((4U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                        ? ((~ ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                               >> 1U)) & ((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                                           ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_valid)
                                           : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_valid)))
                        : (((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                            >> 1U) & ((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                                       ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_valid)
                                       : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_valid))))))));
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_plane_elements 
        = ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_h)) 
           * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_w)));
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_batch_elements 
        = ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_c)) 
           * tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_plane_elements);
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_element_count 
        = ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_n)) 
           * tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_batch_elements);
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_y = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_x = 0U;
    if ((((0ULL != tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_plane_elements) 
          & (0ULL != tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_batch_elements)) 
         & (0U != (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_w)))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel 
            = (IData)(VL_MODDIV_QQQ(64, VL_DIV_QQQ(64, (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_element_index)), tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_plane_elements), (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_c))));
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
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mq_index 
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
         & (0x26U > (IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index)))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_output_plane_elements 
            = ((QData)((IData)(((0x25U >= (IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index))
                                 ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_H
                                [tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index]
                                 : 0U))) * (QData)((IData)(
                                                           ((0x25U 
                                                             >= (IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index))
                                                             ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_W
                                                            [tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index]
                                                             : 0U))));
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_output_element_count 
            = (((QData)((IData)(((0x25U >= (IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index))
                                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_N
                                 [tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index]
                                  : 0U))) * (QData)((IData)(
                                                            ((0x25U 
                                                              >= (IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index))
                                                              ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_C
                                                             [tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index]
                                                              : 0U)))) 
               * vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_output_plane_elements);
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_valid 
            = ((((((((((0x25U >= (IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index))
                        ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_TENSOR_INDEX
                       [tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index]
                        : 0U) == ((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
                                   ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_TENSOR_INDEX
                                  [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor]
                                   : 0U)) & (((0x25U 
                                               >= (IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index))
                                               ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_ADDRESS
                                              [tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index]
                                               : 0U) 
                                             == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_base)) 
                    & (((0x25U >= (IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index))
                         ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_LENGTH_BYTES
                        [tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index]
                         : 0U) == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_length)) 
                   & (((0x25U >= (IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index))
                        ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_N
                       [tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index]
                        : 0U) == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_n))) 
                  & (((0x25U >= (IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index))
                       ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_C
                      [tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index]
                       : 0U) == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_c))) 
                 & (((0x25U >= (IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index))
                      ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_H
                     [tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index]
                      : 0U) == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_h))) 
                & (((0x25U >= (IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index))
                     ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_W
                    [tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index]
                     : 0U) == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_w))) 
               & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_output_element_count 
                  == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_element_count));
    } else {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_output_plane_elements = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_output_element_count = 0ULL;
    }
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__descriptor_valid = 1U;
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
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__descriptor_valid = 0U;
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
            tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__descriptor_valid = 0U;
        }
        if (((~ (IData)(vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_KIND
                        [((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
                           ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor)
                           : 0U)][0U])) & (0U != (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor)))) {
            tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__descriptor_valid = 0U;
        }
    }
    if ((1U < (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_input_count))) {
        if ((((((1U != vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_n[1U]) 
                | (0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_c[1U])) 
               | (0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[1U])) 
              | (0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[1U])) 
             | (0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_length[1U]))) {
            tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__descriptor_valid = 0U;
        }
        if ((1U & (~ (IData)(vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_KIND
                             [((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
                                ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor)
                                : 0U)][1U])))) {
            tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__descriptor_valid = 0U;
        }
    }
    if (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__is_alias_row) {
        if ((1U & (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_valid)))) {
            tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__descriptor_valid = 0U;
        }
    } else if ((1U & ((~ ((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor)) 
                          && vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_MEMORY_WRITE_REQUIRED
                          [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor])) 
                      | ((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor)) 
                         && vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_ALLOCATION_KIND
                         [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor])))) {
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__descriptor_valid = 0U;
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
                | (0x00000c5cU <= tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mq_index)) 
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
            tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__descriptor_valid = 0U;
        }
    } else if (((1U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_op)) 
                | (3U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_op)))) {
        if ((1U != (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_input_count))) {
            tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__descriptor_valid = 0U;
        }
    } else if ((2U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_op))) {
        if (((1U != (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_input_count)) 
             & (2U != (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_input_count)))) {
            tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__descriptor_valid = 0U;
        }
    } else if ((1U & (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__is_alias_row)))) {
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__descriptor_valid = 0U;
    }
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__descriptor_fault 
        = (1U & (~ (IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__descriptor_valid)));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_start_valid 
        = ((((1U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state)) 
             & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__buffer_owner_pl)) 
            & (IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__descriptor_valid)) 
           & (0U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_op)));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_start_valid 
        = ((((1U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state)) 
             & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__buffer_owner_pl)) 
            & (IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__descriptor_valid)) 
           & (1U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_op)));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_start_valid 
        = ((((1U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state)) 
             & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__buffer_owner_pl)) 
            & (IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__descriptor_valid)) 
           & (2U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_op)));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_start_valid 
        = ((((1U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state)) 
             & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__buffer_owner_pl)) 
            & (IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__descriptor_valid)) 
           & (3U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_op)));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_start_ready 
        = ((1U & (~ ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_op) 
                     >> 2U))) && ((2U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_op))
                                   ? ((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_op))
                                       ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_start_ready)
                                       : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_start_ready))
                                   : ((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_op))
                                       ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_start_ready)
                                       : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_start_ready))));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_rstrb 
        = (((4U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
             ? (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                  ? (IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_rstrb)
                  : (IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_rstrb)) 
                & (- (IData)((1U & (~ ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                       >> 1U)))))) : 
            (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
               ? (IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_rstrb)
               : (IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_rstrb)) 
             & (- (IData)((1U & ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                 >> 1U)))))) & (- (IData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_valid))));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_write 
        = (((4U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
             ? ((~ ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                    >> 1U)) & ((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                                ? (IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_write)
                                : (IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_write)))
             : (((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                 >> 1U) & ((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                            ? (IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_write)
                            : (IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_write)))) 
           & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_valid));
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
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__output_height_work = 0ULL;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__output_width_work = 0ULL;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__channel_row_work = 0ULL;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__row_work = 0ULL;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__byte_offset_work = 0ULL;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__address_work[0U] = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__address_work[1U] = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__address_work[2U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_channel = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_y = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_x = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_address = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_error_code = 0U;
    if (((((((0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_c[0U]) 
             | (0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U])) 
            | (0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U])) 
           | (0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_upsample_engine__stride)) 
          | (0x000dU < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U])) 
         | (0x000dU < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U]))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_error_code = 1U;
    } else {
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__output_height_work 
            = ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U])) 
               * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_upsample_engine__stride)));
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__output_width_work 
            = ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U])) 
               * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_upsample_engine__stride)));
        if ((((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel 
               >= vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_c[0U]) 
              | ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_y)) 
                 >= tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__output_height_work)) 
             | ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_x)) 
                >= tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__output_width_work))) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_error_code = 1U;
        } else {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_channel 
                = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel;
            tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_y 
                = VL_DIV_III(32, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_y, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_upsample_engine__stride);
            tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_x 
                = VL_DIV_III(32, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_x, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_upsample_engine__stride);
            tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__channel_row_work 
                = ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel)) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U])));
            tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__row_work 
                = (tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__channel_row_work 
                   + (QData)((IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_y)));
            tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__byte_offset_work 
                = ((tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__row_work 
                    * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U]))) 
                   + (QData)((IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_x)));
            __Vtemp_212[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_base[0U];
            __Vtemp_212[1U] = 0U;
            __Vtemp_212[2U] = 0U;
            __Vtemp_213[0U] = (IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__byte_offset_work);
            __Vtemp_213[1U] = (IData)((tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__byte_offset_work 
                                       >> 0x00000020U));
            __Vtemp_213[2U] = 0U;
            VL_ADD_W(3, __Vtemp_214, __Vtemp_212, __Vtemp_213);
            tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__address_work[0U] 
                = __Vtemp_214[0U];
            tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__address_work[1U] 
                = __Vtemp_214[1U];
            tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__address_work[2U] 
                = (1U & __Vtemp_214[2U]);
            if ((0ULL != (0x00000001ffffffffULL & (
                                                   ((QData)((IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__address_work[2U])) 
                                                    << 0x00000020U) 
                                                   | (QData)((IData)(tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__address_work[1U])))))) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_error_code = 2U;
            } else {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_address 
                    = tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__address_work[0U];
            }
        }
    }
    if ((0U != (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_error_code))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_channel = 0U;
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_y = 0U;
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_x = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_address = 0U;
    }
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__extent_y 
        = (0x00000001ffffffffULL & ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U])) 
                                    + (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__darknet_padding_parameter))));
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__extent_x 
        = (0x00000001ffffffffULL & ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U])) 
                                    + (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__darknet_padding_parameter))));
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_height_work = 0ULL;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_width_work = 0ULL;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_y_step = 0ULL;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_x_step = 0ULL;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_y_work = 0ULL;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_x_work = 0ULL;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work[0U] = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work[1U] = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work[2U] = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work[0U] = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work[1U] = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work[2U] = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U] = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U] = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U] = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U] = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U] = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U] = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__tap_range_error = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_output_height = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_output_width = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_count = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_error_code = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__origin_y = 0ULL;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__origin_x = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[0U] = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[0U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[0U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[0U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[1U] = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[1U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[1U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[1U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[2U] = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[2U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[2U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[2U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[3U] = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[3U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[3U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[3U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[4U] = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[4U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[4U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[4U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[5U] = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[5U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[5U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[5U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[6U] = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[6U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[6U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[6U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[7U] = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[7U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[7U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[7U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[8U] = 0U;
    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[8U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[8U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[8U] = 0ULL;
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
    } else if (((tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__extent_y 
                 < (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_height))) 
                | (tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__extent_x 
                   < (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width))))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_error_code = 1U;
    } else {
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_height_work 
            = (0x00000001ffffffffULL & (1ULL + VL_DIV_QQQ(33, 
                                                          (0x00000001ffffffffULL 
                                                           & (tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__extent_y 
                                                              - (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_height)))), (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_y)))));
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_width_work 
            = (0x00000001ffffffffULL & (1ULL + VL_DIV_QQQ(33, 
                                                          (0x00000001ffffffffULL 
                                                           & (tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__extent_x 
                                                              - (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width)))), (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_x)))));
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_output_height 
            = tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_height_work;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_output_width 
            = tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_width_work;
        if ((((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel 
               >= vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_c[0U]) 
              | ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_y)) 
                 >= tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_height_work)) 
             | ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_x)) 
                >= tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_width_work))) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_error_code = 1U;
        } else {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_count 
                = ((2U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_height)
                    ? 4U : 9U);
            tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__origin_y 
                = (- VL_EXTENDS_QQ(64,63, (QData)((IData)(
                                                          (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__darknet_padding_parameter 
                                                           >> 1U)))));
            tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__origin_x 
                = (- VL_EXTENDS_QQ(64,63, (QData)((IData)(
                                                          (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__darknet_padding_parameter 
                                                           >> 1U)))));
            tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_y_step 
                = ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_y)) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_y)));
            tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_x_step 
                = ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_x)) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_x)));
            tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_y_work 
                = (tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__origin_y 
                   + tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_y_step);
            tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_x_work 
                = (tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__origin_x 
                   + tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_x_step);
            if ((0U < (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_count))) {
                tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work 
                    = VL_MODDIV_III(32, (IData)(0U), vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width);
                tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work = 0U;
                tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[0U] 
                    = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[0U] 
                    = tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_y_work;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[0U] 
                    = (tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_x_work 
                       + VL_EXTENDS_QI(64,32, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work));
                if ((((VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[0U]) 
                       & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[0U], (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U])))) 
                      & VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[0U])) 
                     & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[0U], (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U]))))) {
                    __Vtemp_215[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel;
                    __Vtemp_215[1U] = 0U;
                    __Vtemp_215[2U] = 0U;
                    __Vtemp_216[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U];
                    __Vtemp_216[1U] = 0U;
                    __Vtemp_216[2U] = 0U;
                    VL_MUL_W(3, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_215, __Vtemp_216);
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask 
                        = (1U | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask));
                    __Vtemp_217[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[0U]);
                    __Vtemp_217[1U] = 0U;
                    __Vtemp_217[2U] = 0U;
                    VL_ADD_W(3, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_217);
                    __Vtemp_218[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U];
                    __Vtemp_218[1U] = 0U;
                    __Vtemp_218[2U] = 0U;
                    VL_MUL_W(3, __Vtemp_219, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, __Vtemp_218);
                    __Vtemp_220[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[0U]);
                    __Vtemp_220[1U] = 0U;
                    __Vtemp_220[2U] = 0U;
                    VL_ADD_W(3, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, __Vtemp_219, __Vtemp_220);
                    __Vtemp_222[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_base[0U];
                    __Vtemp_222[1U] = 0U;
                    __Vtemp_222[2U] = 0U;
                    __Vtemp_222[3U] = 0U;
                    __Vtemp_223[0U] = tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U];
                    __Vtemp_223[1U] = tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U];
                    __Vtemp_223[2U] = tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U];
                    __Vtemp_223[3U] = 0U;
                    VL_ADD_W(4, __Vtemp_224, __Vtemp_222, __Vtemp_223);
                    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U] 
                        = __Vtemp_224[0U];
                    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                        = __Vtemp_224[1U];
                    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U] 
                        = __Vtemp_224[2U];
                    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U] 
                        = (1U & __Vtemp_224[3U]);
                    if ((0U != ((tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                                 | tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U]) 
                                | (1U & tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U])))) {
                        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__tap_range_error = 1U;
                    } else {
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[0U] 
                            = tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U];
                    }
                }
            }
            if ((1U < (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_count))) {
                tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work 
                    = VL_DIV_III(32, (IData)(1U), vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width);
                tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work 
                    = VL_MODDIV_III(32, (IData)(1U), vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width);
                tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[1U] 
                    = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[1U] 
                    = (tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_y_work 
                       + VL_EXTENDS_QI(64,32, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work));
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[1U] 
                    = (tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_x_work 
                       + VL_EXTENDS_QI(64,32, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work));
                if ((((VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[1U]) 
                       & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[1U], (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U])))) 
                      & VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[1U])) 
                     & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[1U], (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U]))))) {
                    __Vtemp_229[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel;
                    __Vtemp_229[1U] = 0U;
                    __Vtemp_229[2U] = 0U;
                    __Vtemp_230[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U];
                    __Vtemp_230[1U] = 0U;
                    __Vtemp_230[2U] = 0U;
                    VL_MUL_W(3, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_229, __Vtemp_230);
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask 
                        = (2U | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask));
                    __Vtemp_231[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[1U]);
                    __Vtemp_231[1U] = 0U;
                    __Vtemp_231[2U] = 0U;
                    VL_ADD_W(3, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_231);
                    __Vtemp_232[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U];
                    __Vtemp_232[1U] = 0U;
                    __Vtemp_232[2U] = 0U;
                    VL_MUL_W(3, __Vtemp_233, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, __Vtemp_232);
                    __Vtemp_234[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[1U]);
                    __Vtemp_234[1U] = 0U;
                    __Vtemp_234[2U] = 0U;
                    VL_ADD_W(3, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, __Vtemp_233, __Vtemp_234);
                    __Vtemp_236[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_base[0U];
                    __Vtemp_236[1U] = 0U;
                    __Vtemp_236[2U] = 0U;
                    __Vtemp_236[3U] = 0U;
                    __Vtemp_237[0U] = tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U];
                    __Vtemp_237[1U] = tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U];
                    __Vtemp_237[2U] = tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U];
                    __Vtemp_237[3U] = 0U;
                    VL_ADD_W(4, __Vtemp_238, __Vtemp_236, __Vtemp_237);
                    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U] 
                        = __Vtemp_238[0U];
                    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                        = __Vtemp_238[1U];
                    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U] 
                        = __Vtemp_238[2U];
                    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U] 
                        = (1U & __Vtemp_238[3U]);
                    if ((0U != ((tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                                 | tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U]) 
                                | (1U & tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U])))) {
                        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__tap_range_error = 1U;
                    } else {
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[1U] 
                            = tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U];
                    }
                }
            }
            if ((2U < (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_count))) {
                tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work 
                    = VL_DIV_III(32, (IData)(2U), vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width);
                tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work 
                    = VL_MODDIV_III(32, (IData)(2U), vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width);
                tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[2U] 
                    = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[2U] 
                    = (tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_y_work 
                       + VL_EXTENDS_QI(64,32, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work));
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[2U] 
                    = (tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_x_work 
                       + VL_EXTENDS_QI(64,32, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work));
                if ((((VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[2U]) 
                       & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[2U], (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U])))) 
                      & VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[2U])) 
                     & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[2U], (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U]))))) {
                    __Vtemp_243[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel;
                    __Vtemp_243[1U] = 0U;
                    __Vtemp_243[2U] = 0U;
                    __Vtemp_244[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U];
                    __Vtemp_244[1U] = 0U;
                    __Vtemp_244[2U] = 0U;
                    VL_MUL_W(3, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_243, __Vtemp_244);
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask 
                        = (4U | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask));
                    __Vtemp_245[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[2U]);
                    __Vtemp_245[1U] = 0U;
                    __Vtemp_245[2U] = 0U;
                    VL_ADD_W(3, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_245);
                    __Vtemp_246[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U];
                    __Vtemp_246[1U] = 0U;
                    __Vtemp_246[2U] = 0U;
                    VL_MUL_W(3, __Vtemp_247, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, __Vtemp_246);
                    __Vtemp_248[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[2U]);
                    __Vtemp_248[1U] = 0U;
                    __Vtemp_248[2U] = 0U;
                    VL_ADD_W(3, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, __Vtemp_247, __Vtemp_248);
                    __Vtemp_250[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_base[0U];
                    __Vtemp_250[1U] = 0U;
                    __Vtemp_250[2U] = 0U;
                    __Vtemp_250[3U] = 0U;
                    __Vtemp_251[0U] = tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U];
                    __Vtemp_251[1U] = tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U];
                    __Vtemp_251[2U] = tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U];
                    __Vtemp_251[3U] = 0U;
                    VL_ADD_W(4, __Vtemp_252, __Vtemp_250, __Vtemp_251);
                    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U] 
                        = __Vtemp_252[0U];
                    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                        = __Vtemp_252[1U];
                    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U] 
                        = __Vtemp_252[2U];
                    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U] 
                        = (1U & __Vtemp_252[3U]);
                    if ((0U != ((tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                                 | tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U]) 
                                | (1U & tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U])))) {
                        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__tap_range_error = 1U;
                    } else {
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[2U] 
                            = tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U];
                    }
                }
            }
            if ((3U < (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_count))) {
                tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work 
                    = VL_DIV_III(32, (IData)(3U), vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width);
                tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work 
                    = VL_MODDIV_III(32, (IData)(3U), vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width);
                tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[3U] 
                    = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[3U] 
                    = (tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_y_work 
                       + VL_EXTENDS_QI(64,32, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work));
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[3U] 
                    = (tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_x_work 
                       + VL_EXTENDS_QI(64,32, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work));
                if ((((VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[3U]) 
                       & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[3U], (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U])))) 
                      & VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[3U])) 
                     & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[3U], (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U]))))) {
                    __Vtemp_257[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel;
                    __Vtemp_257[1U] = 0U;
                    __Vtemp_257[2U] = 0U;
                    __Vtemp_258[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U];
                    __Vtemp_258[1U] = 0U;
                    __Vtemp_258[2U] = 0U;
                    VL_MUL_W(3, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_257, __Vtemp_258);
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask 
                        = (8U | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask));
                    __Vtemp_259[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[3U]);
                    __Vtemp_259[1U] = 0U;
                    __Vtemp_259[2U] = 0U;
                    VL_ADD_W(3, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_259);
                    __Vtemp_260[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U];
                    __Vtemp_260[1U] = 0U;
                    __Vtemp_260[2U] = 0U;
                    VL_MUL_W(3, __Vtemp_261, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, __Vtemp_260);
                    __Vtemp_262[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[3U]);
                    __Vtemp_262[1U] = 0U;
                    __Vtemp_262[2U] = 0U;
                    VL_ADD_W(3, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, __Vtemp_261, __Vtemp_262);
                    __Vtemp_264[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_base[0U];
                    __Vtemp_264[1U] = 0U;
                    __Vtemp_264[2U] = 0U;
                    __Vtemp_264[3U] = 0U;
                    __Vtemp_265[0U] = tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U];
                    __Vtemp_265[1U] = tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U];
                    __Vtemp_265[2U] = tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U];
                    __Vtemp_265[3U] = 0U;
                    VL_ADD_W(4, __Vtemp_266, __Vtemp_264, __Vtemp_265);
                    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U] 
                        = __Vtemp_266[0U];
                    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                        = __Vtemp_266[1U];
                    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U] 
                        = __Vtemp_266[2U];
                    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U] 
                        = (1U & __Vtemp_266[3U]);
                    if ((0U != ((tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                                 | tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U]) 
                                | (1U & tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U])))) {
                        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__tap_range_error = 1U;
                    } else {
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[3U] 
                            = tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U];
                    }
                }
            }
            if ((4U < (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_count))) {
                tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work 
                    = VL_DIV_III(32, (IData)(4U), vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width);
                tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work 
                    = VL_MODDIV_III(32, (IData)(4U), vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width);
                tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[4U] 
                    = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[4U] 
                    = (tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_y_work 
                       + VL_EXTENDS_QI(64,32, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work));
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[4U] 
                    = (tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_x_work 
                       + VL_EXTENDS_QI(64,32, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work));
                if ((((VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[4U]) 
                       & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[4U], (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U])))) 
                      & VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[4U])) 
                     & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[4U], (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U]))))) {
                    __Vtemp_271[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel;
                    __Vtemp_271[1U] = 0U;
                    __Vtemp_271[2U] = 0U;
                    __Vtemp_272[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U];
                    __Vtemp_272[1U] = 0U;
                    __Vtemp_272[2U] = 0U;
                    VL_MUL_W(3, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_271, __Vtemp_272);
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask 
                        = (0x00000010U | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask));
                    __Vtemp_273[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[4U]);
                    __Vtemp_273[1U] = 0U;
                    __Vtemp_273[2U] = 0U;
                    VL_ADD_W(3, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_273);
                    __Vtemp_274[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U];
                    __Vtemp_274[1U] = 0U;
                    __Vtemp_274[2U] = 0U;
                    VL_MUL_W(3, __Vtemp_275, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, __Vtemp_274);
                    __Vtemp_276[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[4U]);
                    __Vtemp_276[1U] = 0U;
                    __Vtemp_276[2U] = 0U;
                    VL_ADD_W(3, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, __Vtemp_275, __Vtemp_276);
                    __Vtemp_278[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_base[0U];
                    __Vtemp_278[1U] = 0U;
                    __Vtemp_278[2U] = 0U;
                    __Vtemp_278[3U] = 0U;
                    __Vtemp_279[0U] = tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U];
                    __Vtemp_279[1U] = tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U];
                    __Vtemp_279[2U] = tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U];
                    __Vtemp_279[3U] = 0U;
                    VL_ADD_W(4, __Vtemp_280, __Vtemp_278, __Vtemp_279);
                    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U] 
                        = __Vtemp_280[0U];
                    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                        = __Vtemp_280[1U];
                    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U] 
                        = __Vtemp_280[2U];
                    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U] 
                        = (1U & __Vtemp_280[3U]);
                    if ((0U != ((tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                                 | tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U]) 
                                | (1U & tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U])))) {
                        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__tap_range_error = 1U;
                    } else {
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[4U] 
                            = tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U];
                    }
                }
            }
            if ((5U < (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_count))) {
                tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work 
                    = VL_DIV_III(32, (IData)(5U), vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width);
                tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work 
                    = VL_MODDIV_III(32, (IData)(5U), vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width);
                tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[5U] 
                    = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[5U] 
                    = (tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_y_work 
                       + VL_EXTENDS_QI(64,32, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work));
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[5U] 
                    = (tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_x_work 
                       + VL_EXTENDS_QI(64,32, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work));
                if ((((VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[5U]) 
                       & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[5U], (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U])))) 
                      & VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[5U])) 
                     & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[5U], (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U]))))) {
                    __Vtemp_285[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel;
                    __Vtemp_285[1U] = 0U;
                    __Vtemp_285[2U] = 0U;
                    __Vtemp_286[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U];
                    __Vtemp_286[1U] = 0U;
                    __Vtemp_286[2U] = 0U;
                    VL_MUL_W(3, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_285, __Vtemp_286);
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask 
                        = (0x00000020U | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask));
                    __Vtemp_287[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[5U]);
                    __Vtemp_287[1U] = 0U;
                    __Vtemp_287[2U] = 0U;
                    VL_ADD_W(3, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_287);
                    __Vtemp_288[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U];
                    __Vtemp_288[1U] = 0U;
                    __Vtemp_288[2U] = 0U;
                    VL_MUL_W(3, __Vtemp_289, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, __Vtemp_288);
                    __Vtemp_290[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[5U]);
                    __Vtemp_290[1U] = 0U;
                    __Vtemp_290[2U] = 0U;
                    VL_ADD_W(3, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, __Vtemp_289, __Vtemp_290);
                    __Vtemp_292[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_base[0U];
                    __Vtemp_292[1U] = 0U;
                    __Vtemp_292[2U] = 0U;
                    __Vtemp_292[3U] = 0U;
                    __Vtemp_293[0U] = tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U];
                    __Vtemp_293[1U] = tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U];
                    __Vtemp_293[2U] = tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U];
                    __Vtemp_293[3U] = 0U;
                    VL_ADD_W(4, __Vtemp_294, __Vtemp_292, __Vtemp_293);
                    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U] 
                        = __Vtemp_294[0U];
                    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                        = __Vtemp_294[1U];
                    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U] 
                        = __Vtemp_294[2U];
                    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U] 
                        = (1U & __Vtemp_294[3U]);
                    if ((0U != ((tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                                 | tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U]) 
                                | (1U & tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U])))) {
                        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__tap_range_error = 1U;
                    } else {
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[5U] 
                            = tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U];
                    }
                }
            }
            if ((6U < (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_count))) {
                tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work 
                    = VL_DIV_III(32, (IData)(6U), vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width);
                tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work 
                    = VL_MODDIV_III(32, (IData)(6U), vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width);
                tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[6U] 
                    = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[6U] 
                    = (tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_y_work 
                       + VL_EXTENDS_QI(64,32, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work));
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[6U] 
                    = (tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_x_work 
                       + VL_EXTENDS_QI(64,32, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work));
                if ((((VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[6U]) 
                       & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[6U], (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U])))) 
                      & VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[6U])) 
                     & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[6U], (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U]))))) {
                    __Vtemp_299[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel;
                    __Vtemp_299[1U] = 0U;
                    __Vtemp_299[2U] = 0U;
                    __Vtemp_300[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U];
                    __Vtemp_300[1U] = 0U;
                    __Vtemp_300[2U] = 0U;
                    VL_MUL_W(3, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_299, __Vtemp_300);
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask 
                        = (0x00000040U | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask));
                    __Vtemp_301[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[6U]);
                    __Vtemp_301[1U] = 0U;
                    __Vtemp_301[2U] = 0U;
                    VL_ADD_W(3, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_301);
                    __Vtemp_302[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U];
                    __Vtemp_302[1U] = 0U;
                    __Vtemp_302[2U] = 0U;
                    VL_MUL_W(3, __Vtemp_303, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, __Vtemp_302);
                    __Vtemp_304[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[6U]);
                    __Vtemp_304[1U] = 0U;
                    __Vtemp_304[2U] = 0U;
                    VL_ADD_W(3, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, __Vtemp_303, __Vtemp_304);
                    __Vtemp_306[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_base[0U];
                    __Vtemp_306[1U] = 0U;
                    __Vtemp_306[2U] = 0U;
                    __Vtemp_306[3U] = 0U;
                    __Vtemp_307[0U] = tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U];
                    __Vtemp_307[1U] = tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U];
                    __Vtemp_307[2U] = tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U];
                    __Vtemp_307[3U] = 0U;
                    VL_ADD_W(4, __Vtemp_308, __Vtemp_306, __Vtemp_307);
                    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U] 
                        = __Vtemp_308[0U];
                    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                        = __Vtemp_308[1U];
                    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U] 
                        = __Vtemp_308[2U];
                    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U] 
                        = (1U & __Vtemp_308[3U]);
                    if ((0U != ((tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                                 | tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U]) 
                                | (1U & tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U])))) {
                        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__tap_range_error = 1U;
                    } else {
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[6U] 
                            = tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U];
                    }
                }
            }
            if ((7U < (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_count))) {
                tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work 
                    = VL_DIV_III(32, (IData)(7U), vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width);
                tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work 
                    = VL_MODDIV_III(32, (IData)(7U), vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width);
                tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[7U] 
                    = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[7U] 
                    = (tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_y_work 
                       + VL_EXTENDS_QI(64,32, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work));
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[7U] 
                    = (tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_x_work 
                       + VL_EXTENDS_QI(64,32, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work));
                if ((((VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[7U]) 
                       & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[7U], (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U])))) 
                      & VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[7U])) 
                     & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[7U], (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U]))))) {
                    __Vtemp_313[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel;
                    __Vtemp_313[1U] = 0U;
                    __Vtemp_313[2U] = 0U;
                    __Vtemp_314[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U];
                    __Vtemp_314[1U] = 0U;
                    __Vtemp_314[2U] = 0U;
                    VL_MUL_W(3, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_313, __Vtemp_314);
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask 
                        = (0x00000080U | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask));
                    __Vtemp_315[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[7U]);
                    __Vtemp_315[1U] = 0U;
                    __Vtemp_315[2U] = 0U;
                    VL_ADD_W(3, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_315);
                    __Vtemp_316[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U];
                    __Vtemp_316[1U] = 0U;
                    __Vtemp_316[2U] = 0U;
                    VL_MUL_W(3, __Vtemp_317, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, __Vtemp_316);
                    __Vtemp_318[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[7U]);
                    __Vtemp_318[1U] = 0U;
                    __Vtemp_318[2U] = 0U;
                    VL_ADD_W(3, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, __Vtemp_317, __Vtemp_318);
                    __Vtemp_320[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_base[0U];
                    __Vtemp_320[1U] = 0U;
                    __Vtemp_320[2U] = 0U;
                    __Vtemp_320[3U] = 0U;
                    __Vtemp_321[0U] = tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U];
                    __Vtemp_321[1U] = tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U];
                    __Vtemp_321[2U] = tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U];
                    __Vtemp_321[3U] = 0U;
                    VL_ADD_W(4, __Vtemp_322, __Vtemp_320, __Vtemp_321);
                    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U] 
                        = __Vtemp_322[0U];
                    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                        = __Vtemp_322[1U];
                    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U] 
                        = __Vtemp_322[2U];
                    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U] 
                        = (1U & __Vtemp_322[3U]);
                    if ((0U != ((tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                                 | tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U]) 
                                | (1U & tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U])))) {
                        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__tap_range_error = 1U;
                    } else {
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[7U] 
                            = tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U];
                    }
                }
            }
            if ((8U < (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_count))) {
                tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work 
                    = VL_DIV_III(32, (IData)(8U), vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width);
                tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work 
                    = VL_MODDIV_III(32, (IData)(8U), vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width);
                tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[8U] 
                    = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[8U] 
                    = (tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_y_work 
                       + VL_EXTENDS_QI(64,32, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work));
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[8U] 
                    = (tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_x_work 
                       + VL_EXTENDS_QI(64,32, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work));
                if ((((VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[8U]) 
                       & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[8U], (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U])))) 
                      & VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[8U])) 
                     & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[8U], (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U]))))) {
                    __Vtemp_327[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel;
                    __Vtemp_327[1U] = 0U;
                    __Vtemp_327[2U] = 0U;
                    __Vtemp_328[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U];
                    __Vtemp_328[1U] = 0U;
                    __Vtemp_328[2U] = 0U;
                    VL_MUL_W(3, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_327, __Vtemp_328);
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask 
                        = (0x00000100U | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask));
                    __Vtemp_329[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[8U]);
                    __Vtemp_329[1U] = 0U;
                    __Vtemp_329[2U] = 0U;
                    VL_ADD_W(3, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_329);
                    __Vtemp_330[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U];
                    __Vtemp_330[1U] = 0U;
                    __Vtemp_330[2U] = 0U;
                    VL_MUL_W(3, __Vtemp_331, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, __Vtemp_330);
                    __Vtemp_332[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[8U]);
                    __Vtemp_332[1U] = 0U;
                    __Vtemp_332[2U] = 0U;
                    VL_ADD_W(3, tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, __Vtemp_331, __Vtemp_332);
                    __Vtemp_334[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_base[0U];
                    __Vtemp_334[1U] = 0U;
                    __Vtemp_334[2U] = 0U;
                    __Vtemp_334[3U] = 0U;
                    __Vtemp_335[0U] = tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U];
                    __Vtemp_335[1U] = tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U];
                    __Vtemp_335[2U] = tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U];
                    __Vtemp_335[3U] = 0U;
                    VL_ADD_W(4, __Vtemp_336, __Vtemp_334, __Vtemp_335);
                    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U] 
                        = __Vtemp_336[0U];
                    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                        = __Vtemp_336[1U];
                    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U] 
                        = __Vtemp_336[2U];
                    tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U] 
                        = (1U & __Vtemp_336[3U]);
                    if ((0U != ((tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                                 | tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U]) 
                                | (1U & tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U])))) {
                        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__tap_range_error = 1U;
                    } else {
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[8U] 
                            = tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U];
                    }
                }
            }
            if (tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__tap_range_error) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_error_code = 2U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_output_height = 0ULL;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_output_width = 0ULL;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_count = 0U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask = 0U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[0U] = 0U;
                tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[0U] = 0U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[0U] = 0ULL;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[0U] = 0ULL;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[1U] = 0U;
                tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[1U] = 0U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[1U] = 0ULL;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[1U] = 0ULL;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[2U] = 0U;
                tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[2U] = 0U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[2U] = 0ULL;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[2U] = 0ULL;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[3U] = 0U;
                tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[3U] = 0U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[3U] = 0ULL;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[3U] = 0ULL;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[4U] = 0U;
                tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[4U] = 0U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[4U] = 0ULL;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[4U] = 0ULL;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[5U] = 0U;
                tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[5U] = 0U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[5U] = 0ULL;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[5U] = 0ULL;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[6U] = 0U;
                tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[6U] = 0U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[6U] = 0ULL;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[6U] = 0ULL;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[7U] = 0U;
                tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[7U] = 0U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[7U] = 0ULL;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[7U] = 0ULL;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[8U] = 0U;
                tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[8U] = 0U;
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
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[0U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[0U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[0U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[1U] = 0U;
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[1U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[1U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[1U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[2U] = 0U;
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[2U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[2U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[2U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[3U] = 0U;
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[3U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[3U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[3U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[4U] = 0U;
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[4U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[4U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[4U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[5U] = 0U;
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[5U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[5U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[5U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[6U] = 0U;
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[6U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[6U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[6U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[7U] = 0U;
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[7U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[7U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[7U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[8U] = 0U;
        tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[8U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[8U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[8U] = 0ULL;
    }
    __VdfgRegularize_h6e95ff9d_0_5 = ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__automatic_read_responses) 
                                      & ((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_write)) 
                                         & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_valid)));
    __Vtemp_342[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__output_offset_work);
    __Vtemp_342[1U] = (IData)((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__output_offset_work 
                               >> 0x00000020U));
    __Vtemp_342[2U] = 0U;
    VL_ADD_W(3, __Vtemp_343, __Vtemp_342, __VdfgRegularize_h6e95ff9d_0_6);
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__output_address_work[0U] 
        = __Vtemp_343[0U];
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__output_address_work[1U] 
        = __Vtemp_343[1U];
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__output_address_work[2U] 
        = (1U & __Vtemp_343[2U]);
    __Vtemp_345[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_offset_work);
    __Vtemp_345[1U] = (IData)((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_offset_work 
                               >> 0x00000020U));
    __Vtemp_345[2U] = 0U;
    VL_ADD_W(3, __Vtemp_346, __Vtemp_345, __VdfgRegularize_h6e95ff9d_0_6);
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_address_work[0U] 
        = __Vtemp_346[0U];
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_address_work[1U] 
        = __Vtemp_346[1U];
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_address_work[2U] 
        = (1U & __Vtemp_346[2U]);
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__backend_memory_error_code 
        = ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__manual_mem_error_code) 
           & (- (IData)((1U & (~ (IData)(__VdfgRegularize_h6e95ff9d_0_5))))));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_ready 
        = ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__manual_mem_ready) 
           | (IData)(__VdfgRegularize_h6e95ff9d_0_5));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__memory_handshake 
        = ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_ready) 
           & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_valid));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_ready 
        = ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_valid) 
           & ((3U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state)) 
              & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_ready)));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_ready 
        = ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_valid) 
           & ((5U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state)) 
              & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_ready)));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_ready 
        = ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_valid) 
           & ((4U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state)) 
              & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_ready)));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_ready 
        = ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_valid) 
           & ((2U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state)) 
              & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_ready)));
}
