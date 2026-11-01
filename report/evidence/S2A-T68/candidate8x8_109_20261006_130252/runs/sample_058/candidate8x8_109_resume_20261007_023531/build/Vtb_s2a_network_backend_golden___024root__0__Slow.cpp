// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vtb_s2a_network_backend_golden.h for the primary calling header

#include "Vtb_s2a_network_backend_golden__pch.h"

void Vtb_s2a_network_backend_golden___024root___timing_ready(Vtb_s2a_network_backend_golden___024root* vlSelf);

VL_ATTR_COLD void Vtb_s2a_network_backend_golden___024root___eval_static(Vtb_s2a_network_backend_golden___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_network_backend_golden___024root___eval_static\n"); );
    Vtb_s2a_network_backend_golden__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    {
        // Inlined CFunc: _eval_static__TOP
        vlSelfRef.tb_s2a_network_backend_golden__DOT__clk = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__hard_reset = 1U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__backend_start = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__buffer_owner_pl = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__sample_index = 0xffffffffU;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__max_cycles = 0x00000000ffffffffULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__cycle_count = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__next_progress_cycle = 0x0000000001c9c380ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__class_wait_count = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__golden_cursor = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__stalled_previous = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__stalled_address = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__stalled_data = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__stalled_write = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__stalled_rstrb = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__stalled_wstrb = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__total_feature_write_bytes = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__total_memory_read_bytes = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__total_input_read_bytes = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__total_weight_read_bytes = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__total_feature_read_bytes = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__total_memory_write_transactions = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__total_memory_read_transactions = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__total_mismatches = 0U;
    }
    vlSelfRef.__Vtrigprevexpr___TOP__tb_s2a_network_backend_golden__DOT__clk__0 = 0U;
    Vtb_s2a_network_backend_golden___024root___timing_ready(vlSelf);
    do {
        vlSelfRef.__VactTriggeredAcc[vlSelfRef.__Vi] 
            = vlSelfRef.__VactTriggered[vlSelfRef.__Vi];
        vlSelfRef.__Vi = ((IData)(1U) + vlSelfRef.__Vi);
    } while ((0U >= vlSelfRef.__Vi));
}

VL_ATTR_COLD void Vtb_s2a_network_backend_golden___024root___eval_final(Vtb_s2a_network_backend_golden___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_network_backend_golden___024root___eval_final\n"); );
    Vtb_s2a_network_backend_golden__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
}

#ifdef VL_DEBUG
VL_ATTR_COLD void Vtb_s2a_network_backend_golden___024root___dump_triggers__stl(const VlUnpacked<QData/*63:0*/, 1> &triggers, const std::string &tag);
#endif  // VL_DEBUG
VL_ATTR_COLD bool Vtb_s2a_network_backend_golden___024root___eval_phase__stl(Vtb_s2a_network_backend_golden___024root* vlSelf);

VL_ATTR_COLD void Vtb_s2a_network_backend_golden___024root___eval_settle(Vtb_s2a_network_backend_golden___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_network_backend_golden___024root___eval_settle\n"); );
    Vtb_s2a_network_backend_golden__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    IData/*31:0*/ __VstlIterCount;
    // Body
    __VstlIterCount = 0U;
    vlSelfRef.__VstlFirstIteration = 1U;
    do {
        if (VL_UNLIKELY(((0x00002710U < __VstlIterCount)))) {
#ifdef VL_DEBUG
            Vtb_s2a_network_backend_golden___024root___dump_triggers__stl(vlSelfRef.__VstlTriggered, "stl"s);
#endif
            VL_FATAL_MT("D:\\FPGA_Competition\\sim\\tb_s2a_network_backend_golden.sv", 3, "", "DIDNOTCONVERGE: Settle region did not converge after '--converge-limit' of 10000 tries");
        }
        __VstlIterCount = ((IData)(1U) + __VstlIterCount);
        vlSelfRef.__VstlPhaseResult = Vtb_s2a_network_backend_golden___024root___eval_phase__stl(vlSelf);
        vlSelfRef.__VstlFirstIteration = 0U;
    } while (vlSelfRef.__VstlPhaseResult);
}

VL_ATTR_COLD bool Vtb_s2a_network_backend_golden___024root___trigger_anySet__stl(const VlUnpacked<QData/*63:0*/, 1> &in);

#ifdef VL_DEBUG
VL_ATTR_COLD void Vtb_s2a_network_backend_golden___024root___dump_triggers__stl(const VlUnpacked<QData/*63:0*/, 1> &triggers, const std::string &tag) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_network_backend_golden___024root___dump_triggers__stl\n"); );
    // Body
    if ((1U & (~ (IData)(Vtb_s2a_network_backend_golden___024root___trigger_anySet__stl(triggers))))) {
        VL_DBG_MSGS("         No '" + tag + "' region triggers active\n");
    }
    if ((1U & (IData)(triggers[0U]))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 0 is active: Internal 'stl' trigger - first iteration\n");
    }
}
#endif  // VL_DEBUG

VL_ATTR_COLD bool Vtb_s2a_network_backend_golden___024root___trigger_anySet__stl(const VlUnpacked<QData/*63:0*/, 1> &in) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_network_backend_golden___024root___trigger_anySet__stl\n"); );
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

extern const VlWide<10>/*319:0*/ Vtb_s2a_network_backend_golden__ConstPool__CONST_hb4617e49_0;
extern const VlUnpacked<IData/*31:0*/, 5> Vtb_s2a_network_backend_golden__ConstPool__TABLE_hc6a14c36_0;

VL_ATTR_COLD void Vtb_s2a_network_backend_golden___024root___stl_sequent__TOP__0(Vtb_s2a_network_backend_golden___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_network_backend_golden___024root___stl_sequent__TOP__0\n"); );
    Vtb_s2a_network_backend_golden__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    QData/*63:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_plane_elements;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_plane_elements = 0;
    QData/*63:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_batch_elements;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_batch_elements = 0;
    IData/*31:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__mq_index;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__mq_index = 0;
    CData/*0:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__descriptor_valid;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__descriptor_valid = 0;
    CData/*5:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__alias_layer_index;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__alias_layer_index = 0;
    CData/*0:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__conv_req_write;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__conv_req_write = 0;
    CData/*3:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__conv_req_rstrb;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__conv_req_rstrb = 0;
    CData/*3:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__conv_req_wstrb;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__conv_req_wstrb = 0;
    CData/*0:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__maxpool_req_write;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__maxpool_req_write = 0;
    IData/*31:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__maxpool_req_addr;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__maxpool_req_addr = 0;
    IData/*31:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__maxpool_req_wdata;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__maxpool_req_wdata = 0;
    CData/*3:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__maxpool_req_rstrb;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__maxpool_req_rstrb = 0;
    CData/*3:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__maxpool_req_wstrb;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__maxpool_req_wstrb = 0;
    CData/*0:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__route_req_write;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__route_req_write = 0;
    IData/*31:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__route_req_addr;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__route_req_addr = 0;
    IData/*31:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__route_req_wdata;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__route_req_wdata = 0;
    CData/*3:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__route_req_rstrb;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__route_req_rstrb = 0;
    CData/*3:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__route_req_wstrb;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__route_req_wstrb = 0;
    CData/*0:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__upsample_req_write;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__upsample_req_write = 0;
    IData/*31:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__upsample_req_addr;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__upsample_req_addr = 0;
    IData/*31:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__upsample_req_wdata;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__upsample_req_wdata = 0;
    CData/*3:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__upsample_req_rstrb;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__upsample_req_rstrb = 0;
    CData/*3:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__upsample_req_wstrb;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__upsample_req_wstrb = 0;
    IData/*31:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__selected_req_addr;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__selected_req_addr = 0;
    IData/*31:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__selected_req_wdata;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__selected_req_wdata = 0;
    VlUnpacked<IData/*31:0*/, 9> tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel;
    for (int __Vi0 = 0; __Vi0 < 9; ++__Vi0) {
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[__Vi0] = 0;
    }
    IData/*31:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__selected_input_word_address;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__selected_input_word_address = 0;
    CData/*3:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__selected_input_lane;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__selected_input_lane = 0;
    CData/*7:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__candidate_value;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__candidate_value = 0;
    CData/*7:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__current_maximum;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__current_maximum = 0;
    QData/*32:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__extent_y;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__extent_y = 0;
    QData/*32:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__extent_x;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__extent_x = 0;
    QData/*32:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_height_work;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_height_work = 0;
    QData/*32:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_width_work;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_width_work = 0;
    QData/*63:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__origin_y;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__origin_y = 0;
    QData/*63:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__origin_x;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__origin_x = 0;
    QData/*32:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_y_step;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_y_step = 0;
    QData/*32:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_x_step;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_x_step = 0;
    QData/*63:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_y_work;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_y_work = 0;
    QData/*63:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_x_work;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_x_work = 0;
    QData/*63:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work = 0;
    VlWide<3>/*95:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work;
    VL_ZERO_W(96, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work);
    VlWide<4>/*96:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work;
    VL_ZERO_W(97, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work);
    IData/*31:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work = 0;
    IData/*31:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work = 0;
    CData/*0:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__tap_range_error;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__tap_range_error = 0;
    IData/*31:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_y;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_y = 0;
    IData/*31:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_x;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_x = 0;
    QData/*63:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__output_height_work;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__output_height_work = 0;
    QData/*63:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__output_width_work;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__output_width_work = 0;
    CData/*7:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__plane_elements_work;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__plane_elements_work = 0;
    CData/*7:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__plane_index_work;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__plane_index_work = 0;
    QData/*39:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__byte_offset_work;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__byte_offset_work = 0;
    QData/*40:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__address_work;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__address_work = 0;
    IData/*31:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__selected_word_address;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__selected_word_address = 0;
    CData/*3:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__selected_read_lane;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__selected_read_lane = 0;
    CData/*0:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_argument;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_argument = 0;
    CData/*0:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_range;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_range = 0;
    QData/*63:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source0_shape_bytes;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source0_shape_bytes = 0;
    QData/*63:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_shape_bytes;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_shape_bytes = 0;
    QData/*63:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source0_plane_elements;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source0_plane_elements = 0;
    QData/*63:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_plane_elements;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_plane_elements = 0;
    QData/*63:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source0_object_end;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source0_object_end = 0;
    QData/*63:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_object_end;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_object_end = 0;
    QData/*63:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__output_channels_wide;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__output_channels_wide = 0;
    QData/*63:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__expected_group_start;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__expected_group_start = 0;
    QData/*63:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__expected_group_end;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__expected_group_end = 0;
    QData/*63:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_offset;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_offset = 0;
    QData/*63:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_address_wide;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_address_wide = 0;
    IData/*31:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source0_selected_count;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source0_selected_count = 0;
    IData/*31:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_selected_count;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_selected_count = 0;
    IData/*31:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_multiplier;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_multiplier = 0;
    IData/*31:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_base_address;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_base_address = 0;
    IData/*31:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_length_bytes;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_length_bytes = 0;
    CData/*7:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_value;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_value = 0;
    CData/*6:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_magnitude;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_magnitude = 0;
    QData/*38:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__scaled_product;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__scaled_product = 0;
    QData/*39:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__rounded_product;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__rounded_product = 0;
    SData/*8:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__rounded_magnitude;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__rounded_magnitude = 0;
    SData/*8:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__scaled_signed;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__scaled_signed = 0;
    IData/*31:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_source_index;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_source_index = 0;
    IData/*31:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_source_channel;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_source_channel = 0;
    VlWide<4>/*127:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_elements_wide;
    VL_ZERO_W(128, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_elements_wide);
    VlWide<4>/*127:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__expected_weight_bytes_wide;
    VL_ZERO_W(128, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__expected_weight_bytes_wide);
    VlWide<4>/*127:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_end_wide;
    VL_ZERO_W(128, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_end_wide);
    VlWide<4>/*127:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_end_wide;
    VL_ZERO_W(128, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_end_wide);
    VlWide<4>/*127:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_package_end_wide;
    VL_ZERO_W(128, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_package_end_wide);
    VlWide<4>/*127:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__quantized_weight_end_wide;
    VL_ZERO_W(128, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__quantized_weight_end_wide);
    QData/*63:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_numerator;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_numerator = 0;
    QData/*63:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_numerator;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_numerator = 0;
    QData/*63:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_shape_span;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_shape_span = 0;
    QData/*63:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_shape_span;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_shape_span = 0;
    QData/*63:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_shape_product;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_shape_product = 0;
    QData/*63:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_shape_product;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_shape_product = 0;
    QData/*63:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_span_plus_stride;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_span_plus_stride = 0;
    QData/*63:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_span_plus_stride;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_span_plus_stride = 0;
    VlWide<4>/*127:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_height_wide;
    VL_ZERO_W(128, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_height_wide);
    VlWide<4>/*127:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_width_wide;
    VL_ZERO_W(128, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_width_wide);
    VlWide<4>/*127:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_bytes_wide;
    VL_ZERO_W(128, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_bytes_wide);
    VlWide<4>/*127:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__full_weight_group_bytes_wide;
    VL_ZERO_W(128, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__full_weight_group_bytes_wide);
    QData/*63:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__patch_plane_bytes;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__patch_plane_bytes = 0;
    QData/*63:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_input_y;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_input_y = 0;
    QData/*63:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_input_x;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_input_x = 0;
    QData/*63:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_source_offset;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_source_offset = 0;
    IData/*31:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_area;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_area = 0;
    IData/*31:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_next_input_channel;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_next_input_channel = 0;
    IData/*31:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_next_kernel_y;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_next_kernel_y = 0;
    IData/*31:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_next_reduction_index;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_next_reduction_index = 0;
    IData/*31:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_point_y;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_point_y = 0;
    IData/*31:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_point_x;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_point_x = 0;
    IData/*31:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_input_channel;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_input_channel = 0;
    IData/*31:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_kernel_y;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_kernel_y = 0;
    IData/*31:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_kernel_x;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_kernel_x = 0;
    QData/*63:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_input_y;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_input_y = 0;
    QData/*63:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_input_x;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_input_x = 0;
    QData/*63:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_feature_index_wide;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_feature_index_wide = 0;
    IData/*31:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_index;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_index = 0;
    VlWide<3>/*79:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_parameter;
    VL_ZERO_W(80, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_parameter);
    IData/*31:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_accumulator;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_accumulator = 0;
    IData/*31:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier = 0;
    IData/*31:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift = 0;
    IData/*31:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude = 0;
    QData/*63:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product = 0;
    QData/*63:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add = 0;
    QData/*63:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude = 0;
    QData/*63:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value = 0;
    CData/*1:0*/ __Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__map_conv_activation__26__Vfuncout;
    __Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__map_conv_activation__26__Vfuncout = 0;
    CData/*1:0*/ __Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__map_conv_activation__26__descriptor_activation;
    __Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__map_conv_activation__26__descriptor_activation = 0;
    IData/*31:0*/ __VdfgRegularize_h6e95ff9d_0_3;
    __VdfgRegularize_h6e95ff9d_0_3 = 0;
    IData/*31:0*/ __VdfgRegularize_h6e95ff9d_0_9;
    __VdfgRegularize_h6e95ff9d_0_9 = 0;
    IData/*31:0*/ __VdfgRegularize_h6e95ff9d_0_12;
    __VdfgRegularize_h6e95ff9d_0_12 = 0;
    CData/*2:0*/ __VdfgRegularize_h6e95ff9d_0_13;
    __VdfgRegularize_h6e95ff9d_0_13 = 0;
    CData/*2:0*/ __VdfgRegularize_h6e95ff9d_0_14;
    __VdfgRegularize_h6e95ff9d_0_14 = 0;
    CData/*2:0*/ __VdfgRegularize_h6e95ff9d_0_15;
    __VdfgRegularize_h6e95ff9d_0_15 = 0;
    IData/*31:0*/ __VdfgRegularize_h6e95ff9d_0_18;
    __VdfgRegularize_h6e95ff9d_0_18 = 0;
    CData/*2:0*/ __VdfgRegularize_h6e95ff9d_0_19;
    __VdfgRegularize_h6e95ff9d_0_19 = 0;
    CData/*2:0*/ __VdfgRegularize_h6e95ff9d_0_20;
    __VdfgRegularize_h6e95ff9d_0_20 = 0;
    CData/*2:0*/ __VdfgRegularize_h6e95ff9d_0_26;
    __VdfgRegularize_h6e95ff9d_0_26 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_28;
    __VdfgRegularize_h6e95ff9d_0_28 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_29;
    __VdfgRegularize_h6e95ff9d_0_29 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_30;
    __VdfgRegularize_h6e95ff9d_0_30 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_31;
    __VdfgRegularize_h6e95ff9d_0_31 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_32;
    __VdfgRegularize_h6e95ff9d_0_32 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_33;
    __VdfgRegularize_h6e95ff9d_0_33 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_34;
    __VdfgRegularize_h6e95ff9d_0_34 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_35;
    __VdfgRegularize_h6e95ff9d_0_35 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_36;
    __VdfgRegularize_h6e95ff9d_0_36 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_37;
    __VdfgRegularize_h6e95ff9d_0_37 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_38;
    __VdfgRegularize_h6e95ff9d_0_38 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_39;
    __VdfgRegularize_h6e95ff9d_0_39 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_40;
    __VdfgRegularize_h6e95ff9d_0_40 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_41;
    __VdfgRegularize_h6e95ff9d_0_41 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_42;
    __VdfgRegularize_h6e95ff9d_0_42 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_43;
    __VdfgRegularize_h6e95ff9d_0_43 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_44;
    __VdfgRegularize_h6e95ff9d_0_44 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_45;
    __VdfgRegularize_h6e95ff9d_0_45 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_46;
    __VdfgRegularize_h6e95ff9d_0_46 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_47;
    __VdfgRegularize_h6e95ff9d_0_47 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_48;
    __VdfgRegularize_h6e95ff9d_0_48 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_49;
    __VdfgRegularize_h6e95ff9d_0_49 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_50;
    __VdfgRegularize_h6e95ff9d_0_50 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_51;
    __VdfgRegularize_h6e95ff9d_0_51 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_52;
    __VdfgRegularize_h6e95ff9d_0_52 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_53;
    __VdfgRegularize_h6e95ff9d_0_53 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_54;
    __VdfgRegularize_h6e95ff9d_0_54 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_55;
    __VdfgRegularize_h6e95ff9d_0_55 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_56;
    __VdfgRegularize_h6e95ff9d_0_56 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_57;
    __VdfgRegularize_h6e95ff9d_0_57 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_58;
    __VdfgRegularize_h6e95ff9d_0_58 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_59;
    __VdfgRegularize_h6e95ff9d_0_59 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_60;
    __VdfgRegularize_h6e95ff9d_0_60 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_61;
    __VdfgRegularize_h6e95ff9d_0_61 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_62;
    __VdfgRegularize_h6e95ff9d_0_62 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_63;
    __VdfgRegularize_h6e95ff9d_0_63 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_64;
    __VdfgRegularize_h6e95ff9d_0_64 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_65;
    __VdfgRegularize_h6e95ff9d_0_65 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_66;
    __VdfgRegularize_h6e95ff9d_0_66 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_67;
    __VdfgRegularize_h6e95ff9d_0_67 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_68;
    __VdfgRegularize_h6e95ff9d_0_68 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_69;
    __VdfgRegularize_h6e95ff9d_0_69 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_70;
    __VdfgRegularize_h6e95ff9d_0_70 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_71;
    __VdfgRegularize_h6e95ff9d_0_71 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_72;
    __VdfgRegularize_h6e95ff9d_0_72 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_73;
    __VdfgRegularize_h6e95ff9d_0_73 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_74;
    __VdfgRegularize_h6e95ff9d_0_74 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_75;
    __VdfgRegularize_h6e95ff9d_0_75 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_76;
    __VdfgRegularize_h6e95ff9d_0_76 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_77;
    __VdfgRegularize_h6e95ff9d_0_77 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_78;
    __VdfgRegularize_h6e95ff9d_0_78 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_79;
    __VdfgRegularize_h6e95ff9d_0_79 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_80;
    __VdfgRegularize_h6e95ff9d_0_80 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_81;
    __VdfgRegularize_h6e95ff9d_0_81 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_82;
    __VdfgRegularize_h6e95ff9d_0_82 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_83;
    __VdfgRegularize_h6e95ff9d_0_83 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_84;
    __VdfgRegularize_h6e95ff9d_0_84 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_85;
    __VdfgRegularize_h6e95ff9d_0_85 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_86;
    __VdfgRegularize_h6e95ff9d_0_86 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_87;
    __VdfgRegularize_h6e95ff9d_0_87 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_88;
    __VdfgRegularize_h6e95ff9d_0_88 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_89;
    __VdfgRegularize_h6e95ff9d_0_89 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_90;
    __VdfgRegularize_h6e95ff9d_0_90 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_91;
    __VdfgRegularize_h6e95ff9d_0_91 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_92;
    __VdfgRegularize_h6e95ff9d_0_92 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_93;
    __VdfgRegularize_h6e95ff9d_0_93 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_94;
    __VdfgRegularize_h6e95ff9d_0_94 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_95;
    __VdfgRegularize_h6e95ff9d_0_95 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_96;
    __VdfgRegularize_h6e95ff9d_0_96 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_97;
    __VdfgRegularize_h6e95ff9d_0_97 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_98;
    __VdfgRegularize_h6e95ff9d_0_98 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_99;
    __VdfgRegularize_h6e95ff9d_0_99 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_100;
    __VdfgRegularize_h6e95ff9d_0_100 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_101;
    __VdfgRegularize_h6e95ff9d_0_101 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_102;
    __VdfgRegularize_h6e95ff9d_0_102 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_103;
    __VdfgRegularize_h6e95ff9d_0_103 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_104;
    __VdfgRegularize_h6e95ff9d_0_104 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_105;
    __VdfgRegularize_h6e95ff9d_0_105 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_106;
    __VdfgRegularize_h6e95ff9d_0_106 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_107;
    __VdfgRegularize_h6e95ff9d_0_107 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_108;
    __VdfgRegularize_h6e95ff9d_0_108 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_109;
    __VdfgRegularize_h6e95ff9d_0_109 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_110;
    __VdfgRegularize_h6e95ff9d_0_110 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_111;
    __VdfgRegularize_h6e95ff9d_0_111 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_112;
    __VdfgRegularize_h6e95ff9d_0_112 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_113;
    __VdfgRegularize_h6e95ff9d_0_113 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_114;
    __VdfgRegularize_h6e95ff9d_0_114 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_115;
    __VdfgRegularize_h6e95ff9d_0_115 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_116;
    __VdfgRegularize_h6e95ff9d_0_116 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_117;
    __VdfgRegularize_h6e95ff9d_0_117 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_118;
    __VdfgRegularize_h6e95ff9d_0_118 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_119;
    __VdfgRegularize_h6e95ff9d_0_119 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_120;
    __VdfgRegularize_h6e95ff9d_0_120 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_121;
    __VdfgRegularize_h6e95ff9d_0_121 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_122;
    __VdfgRegularize_h6e95ff9d_0_122 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_123;
    __VdfgRegularize_h6e95ff9d_0_123 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_124;
    __VdfgRegularize_h6e95ff9d_0_124 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_125;
    __VdfgRegularize_h6e95ff9d_0_125 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_126;
    __VdfgRegularize_h6e95ff9d_0_126 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_127;
    __VdfgRegularize_h6e95ff9d_0_127 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_128;
    __VdfgRegularize_h6e95ff9d_0_128 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_129;
    __VdfgRegularize_h6e95ff9d_0_129 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_130;
    __VdfgRegularize_h6e95ff9d_0_130 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_131;
    __VdfgRegularize_h6e95ff9d_0_131 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_132;
    __VdfgRegularize_h6e95ff9d_0_132 = 0;
    IData/*31:0*/ __VdfgRegularize_h6e95ff9d_0_133;
    __VdfgRegularize_h6e95ff9d_0_133 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_134;
    __VdfgRegularize_h6e95ff9d_0_134 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_135;
    __VdfgRegularize_h6e95ff9d_0_135 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_136;
    __VdfgRegularize_h6e95ff9d_0_136 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_137;
    __VdfgRegularize_h6e95ff9d_0_137 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_138;
    __VdfgRegularize_h6e95ff9d_0_138 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_139;
    __VdfgRegularize_h6e95ff9d_0_139 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_140;
    __VdfgRegularize_h6e95ff9d_0_140 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_141;
    __VdfgRegularize_h6e95ff9d_0_141 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_142;
    __VdfgRegularize_h6e95ff9d_0_142 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_143;
    __VdfgRegularize_h6e95ff9d_0_143 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_144;
    __VdfgRegularize_h6e95ff9d_0_144 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_145;
    __VdfgRegularize_h6e95ff9d_0_145 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_146;
    __VdfgRegularize_h6e95ff9d_0_146 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_147;
    __VdfgRegularize_h6e95ff9d_0_147 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_148;
    __VdfgRegularize_h6e95ff9d_0_148 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_149;
    __VdfgRegularize_h6e95ff9d_0_149 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_150;
    __VdfgRegularize_h6e95ff9d_0_150 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_151;
    __VdfgRegularize_h6e95ff9d_0_151 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_152;
    __VdfgRegularize_h6e95ff9d_0_152 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_153;
    __VdfgRegularize_h6e95ff9d_0_153 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_154;
    __VdfgRegularize_h6e95ff9d_0_154 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_155;
    __VdfgRegularize_h6e95ff9d_0_155 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_156;
    __VdfgRegularize_h6e95ff9d_0_156 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_157;
    __VdfgRegularize_h6e95ff9d_0_157 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_158;
    __VdfgRegularize_h6e95ff9d_0_158 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_159;
    __VdfgRegularize_h6e95ff9d_0_159 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_160;
    __VdfgRegularize_h6e95ff9d_0_160 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_161;
    __VdfgRegularize_h6e95ff9d_0_161 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_162;
    __VdfgRegularize_h6e95ff9d_0_162 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_163;
    __VdfgRegularize_h6e95ff9d_0_163 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_164;
    __VdfgRegularize_h6e95ff9d_0_164 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_165;
    __VdfgRegularize_h6e95ff9d_0_165 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_166;
    __VdfgRegularize_h6e95ff9d_0_166 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_167;
    __VdfgRegularize_h6e95ff9d_0_167 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_168;
    __VdfgRegularize_h6e95ff9d_0_168 = 0;
    CData/*2:0*/ __VdfgRegularize_h6e95ff9d_0_177;
    __VdfgRegularize_h6e95ff9d_0_177 = 0;
    CData/*2:0*/ __VdfgRegularize_h6e95ff9d_0_178;
    __VdfgRegularize_h6e95ff9d_0_178 = 0;
    IData/*31:0*/ __VdfgRegularize_h6e95ff9d_0_182;
    __VdfgRegularize_h6e95ff9d_0_182 = 0;
    IData/*31:0*/ __VdfgRegularize_h6e95ff9d_0_183;
    __VdfgRegularize_h6e95ff9d_0_183 = 0;
    IData/*31:0*/ __VdfgRegularize_h6e95ff9d_0_184;
    __VdfgRegularize_h6e95ff9d_0_184 = 0;
    CData/*2:0*/ __VdfgRegularize_h6e95ff9d_0_185;
    __VdfgRegularize_h6e95ff9d_0_185 = 0;
    IData/*31:0*/ __VdfgRegularize_h6e95ff9d_0_186;
    __VdfgRegularize_h6e95ff9d_0_186 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_190;
    __VdfgRegularize_h6e95ff9d_0_190 = 0;
    IData/*31:0*/ __VdfgRegularize_h6e95ff9d_0_192;
    __VdfgRegularize_h6e95ff9d_0_192 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_193;
    __VdfgRegularize_h6e95ff9d_0_193 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_194;
    __VdfgRegularize_h6e95ff9d_0_194 = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_195;
    __VdfgRegularize_h6e95ff9d_0_195 = 0;
    VlWide<3>/*64:0*/ __VdfgRegularize_h6e95ff9d_0_196;
    VL_ZERO_W(65, __VdfgRegularize_h6e95ff9d_0_196);
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
    VlWide<3>/*95:0*/ __Vtemp_62;
    VlWide<3>/*95:0*/ __Vtemp_64;
    VlWide<3>/*95:0*/ __Vtemp_65;
    VlWide<3>/*95:0*/ __Vtemp_66;
    VlWide<3>/*95:0*/ __Vtemp_67;
    VlWide<3>/*95:0*/ __Vtemp_68;
    VlWide<3>/*95:0*/ __Vtemp_69;
    VlWide<3>/*95:0*/ __Vtemp_70;
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
    VlWide<4>/*127:0*/ __Vtemp_87;
    VlWide<4>/*127:0*/ __Vtemp_88;
    VlWide<4>/*127:0*/ __Vtemp_89;
    VlWide<3>/*95:0*/ __Vtemp_94;
    VlWide<3>/*95:0*/ __Vtemp_95;
    VlWide<3>/*95:0*/ __Vtemp_96;
    VlWide<4>/*127:0*/ __Vtemp_98;
    VlWide<4>/*127:0*/ __Vtemp_99;
    VlWide<4>/*127:0*/ __Vtemp_100;
    VlWide<3>/*95:0*/ __Vtemp_105;
    VlWide<3>/*95:0*/ __Vtemp_106;
    VlWide<3>/*95:0*/ __Vtemp_107;
    VlWide<4>/*127:0*/ __Vtemp_109;
    VlWide<4>/*127:0*/ __Vtemp_110;
    VlWide<4>/*127:0*/ __Vtemp_111;
    VlWide<3>/*95:0*/ __Vtemp_116;
    VlWide<3>/*95:0*/ __Vtemp_117;
    VlWide<3>/*95:0*/ __Vtemp_118;
    VlWide<4>/*127:0*/ __Vtemp_120;
    VlWide<4>/*127:0*/ __Vtemp_121;
    VlWide<4>/*127:0*/ __Vtemp_122;
    VlWide<3>/*95:0*/ __Vtemp_127;
    VlWide<3>/*95:0*/ __Vtemp_128;
    VlWide<3>/*95:0*/ __Vtemp_129;
    VlWide<4>/*127:0*/ __Vtemp_131;
    VlWide<4>/*127:0*/ __Vtemp_132;
    VlWide<4>/*127:0*/ __Vtemp_133;
    VlWide<3>/*95:0*/ __Vtemp_138;
    VlWide<3>/*95:0*/ __Vtemp_139;
    VlWide<3>/*95:0*/ __Vtemp_140;
    VlWide<4>/*127:0*/ __Vtemp_142;
    VlWide<4>/*127:0*/ __Vtemp_143;
    VlWide<4>/*127:0*/ __Vtemp_144;
    VlWide<3>/*95:0*/ __Vtemp_149;
    VlWide<3>/*95:0*/ __Vtemp_150;
    VlWide<3>/*95:0*/ __Vtemp_151;
    VlWide<4>/*127:0*/ __Vtemp_153;
    VlWide<4>/*127:0*/ __Vtemp_154;
    VlWide<4>/*127:0*/ __Vtemp_155;
    VlWide<3>/*95:0*/ __Vtemp_160;
    VlWide<3>/*95:0*/ __Vtemp_161;
    VlWide<3>/*95:0*/ __Vtemp_162;
    VlWide<4>/*127:0*/ __Vtemp_164;
    VlWide<4>/*127:0*/ __Vtemp_165;
    VlWide<4>/*127:0*/ __Vtemp_166;
    VlWide<3>/*95:0*/ __Vtemp_171;
    VlWide<3>/*95:0*/ __Vtemp_172;
    VlWide<3>/*95:0*/ __Vtemp_173;
    VlWide<4>/*127:0*/ __Vtemp_175;
    VlWide<4>/*127:0*/ __Vtemp_176;
    VlWide<4>/*127:0*/ __Vtemp_177;
    VlWide<3>/*95:0*/ __Vtemp_183;
    VlWide<3>/*95:0*/ __Vtemp_184;
    VlWide<3>/*95:0*/ __Vtemp_186;
    VlWide<3>/*95:0*/ __Vtemp_187;
    IData/*31:0*/ __Vtemp_188;
    // Body
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__mapped_response_error = 6U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__mapped_response_error = 6U;
    if ((((1U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__response_error_latched)) 
          | (2U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__response_error_latched))) 
         | (6U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__response_error_latched)))) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__mapped_response_error 
            = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__response_error_latched;
    } else if ((0U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__response_error_latched))) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__mapped_response_error = 0U;
    }
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__mapped_response_error = 6U;
    if ((((1U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__response_error_latched)) 
          | (2U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__response_error_latched))) 
         | (6U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__response_error_latched)))) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__mapped_response_error 
            = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__response_error_latched;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__mapped_response_error 
            = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__response_error_latched;
    } else if ((0U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__response_error_latched))) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__mapped_response_error = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__mapped_response_error = 0U;
    }
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__selected_byte_shift 
        = (0x00000018U & (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source_address_latched 
                          << 3U));
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__request_byte_lane 
        = (3U & (0x00030210U >> ((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__request_strobe_latched) 
                                 << 1U)));
    if ((0x25U >= (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor))) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__layer_index 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_LAYER_INDEX
            [vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor];
        __Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__map_conv_activation__26__descriptor_activation 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_ACTIVATION
            [vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor];
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_upsample_engine__stride 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_UPSAMPLE_STRIDE
            [vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor];
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__darknet_padding_parameter 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_MAXPOOL_DARKNET_PADDING
            [vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor];
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_x 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_STRIDE_W
            [vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor];
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_y 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_STRIDE_H
            [vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor];
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_KERNEL_W
            [vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor];
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_height 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_KERNEL_H
            [vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor];
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__current_op 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OP
            [vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor];
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__current_input_count 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_COUNT
            [vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor];
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_base 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_ADDRESS
            [vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor];
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_length 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_LENGTH_BYTES
            [vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor];
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_n 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_N
            [vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor];
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_c 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_C
            [vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor];
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_h 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_H
            [vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor];
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_w 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_W
            [vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor];
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__alias_layer_index 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_ALIAS_LAYER_INDEX
            [vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor];
    } else {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__layer_index = 0U;
        __Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__map_conv_activation__26__descriptor_activation = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_upsample_engine__stride = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__darknet_padding_parameter = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_x = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_y = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_height = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__current_op = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__current_input_count = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_base = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_length = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_n = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_c = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_h = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_w = 0U;
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__alias_layer_index = 0U;
    }
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__maxpool_rsp_valid 
        = ((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__response_pending) 
           & ((~ (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__hard_reset)) 
              & (1U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__response_target_latched))));
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__upsample_rsp_valid 
        = ((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__response_pending) 
           & ((~ (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__hard_reset)) 
              & (3U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__response_target_latched))));
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__route_rsp_valid 
        = ((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__response_pending) 
           & ((~ (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__hard_reset)) 
              & (2U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__response_target_latched))));
    __Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__map_conv_activation__26__Vfuncout 
        = (3U & (0xd0U >> ((IData)(__Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__map_conv_activation__26__descriptor_activation) 
                           << 1U)));
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_conv_engine__activation_mode 
        = __Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__map_conv_activation__26__Vfuncout;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_source_address_wide 
        = ((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_package_base_latched)) 
           + ((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__quantized_weight_offset_latched)) 
              + ((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_reduction_index)) 
                 + ((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_latched)) 
                    * (QData)((IData)((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base 
                                       + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_lane_index)))))));
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__window_max_value = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__window_error_code = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__current_maximum = 0x80U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__candidate_value 
        = (0x000000ffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__candidate_values_latched[0U]);
    if (VL_LTS_III(8, 0x80U, (IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__candidate_value))) {
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__current_maximum 
            = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__candidate_value;
    }
    if ((0x80U == (IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__candidate_value))) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__window_error_code = 1U;
    }
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__candidate_value 
        = (0x000000ffU & (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__candidate_values_latched[0U] 
                          >> 8U));
    if ((0x80U == (IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__candidate_value))) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__window_error_code = 1U;
    }
    if (VL_GTS_III(8, (IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__candidate_value), (IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__current_maximum))) {
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__current_maximum 
            = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__candidate_value;
    }
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__candidate_value 
        = (0x000000ffU & (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__candidate_values_latched[0U] 
                          >> 0x00000010U));
    if ((0x80U == (IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__candidate_value))) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__window_error_code = 1U;
    }
    if (VL_GTS_III(8, (IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__candidate_value), (IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__current_maximum))) {
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__current_maximum 
            = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__candidate_value;
    }
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__candidate_value 
        = (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__candidate_values_latched[0U] 
           >> 0x00000018U);
    if (VL_GTS_III(8, (IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__candidate_value), (IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__current_maximum))) {
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__current_maximum 
            = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__candidate_value;
    }
    if ((0x80U == (IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__candidate_value))) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__window_error_code = 1U;
    }
    if ((0U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__window_error_code))) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__window_max_value 
            = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__current_maximum;
    }
    vlSelfRef.__VdfgRegularize_h6e95ff9d_0_197[0U] 
        = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_width_latched;
    vlSelfRef.__VdfgRegularize_h6e95ff9d_0_197[1U] = 0U;
    vlSelfRef.__VdfgRegularize_h6e95ff9d_0_197[2U] = 0U;
    vlSelfRef.__VdfgRegularize_h6e95ff9d_0_198[0U] 
        = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_height_latched;
    vlSelfRef.__VdfgRegularize_h6e95ff9d_0_198[1U] = 0U;
    vlSelfRef.__VdfgRegularize_h6e95ff9d_0_198[2U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_byte_offset_wide 
        = ((QData)((IData)((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_point_scan_x 
                            + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_x))) 
           + ((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_latched)) 
              * ((QData)((IData)((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_point_scan_y 
                                  + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_y))) 
                 + ((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_latched)) 
                    * (QData)((IData)((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base 
                                       + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_lane_index)))))));
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__maxpool_req_wdata = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__upsample_req_wdata = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__route_req_wdata = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_index = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_parameter[0U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_parameter[1U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_parameter[2U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_bias = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_invalid = 0U;
    if (((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_lane 
          < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count) 
         & (0x00000026U > vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))) {
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_index 
            = ((((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                 [(0x0000003fU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                  : 0U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base) 
               + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_lane);
        if ((0x00000c5cU > tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_index)) {
            if ((0x0c5bU >= (0x00000fffU & tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_index))) {
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_parameter[0U] 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                    [(0x00000fffU & tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_index)][0U];
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_parameter[1U] 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                    [(0x00000fffU & tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_index)][1U];
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_parameter[2U] 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                    [(0x00000fffU & tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_index)][2U];
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_bias 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_CONV_BIAS_ACCUMULATOR_INT32
                    [(0x00000fffU & tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_index)];
            } else {
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_parameter[0U] = 0U;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_parameter[1U] = 0U;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_parameter[2U] = 0U;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_bias = 0U;
            }
            if (((((((((tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_index 
                        >= (((0x25U >= (0x0000003fU 
                                        & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                              ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                             [(0x0000003fU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                              : 0U) + ((0x25U >= (0x0000003fU 
                                                  & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                        ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                                       [(0x0000003fU 
                                         & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                        : 0U))) | (0U 
                                                   == 
                                                   ((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_parameter[2U] 
                                                     << 0x00000010U) 
                                                    | (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_parameter[1U] 
                                                       >> 0x00000010U)))) 
                      | (0U == ((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_parameter[1U] 
                                 << 0x00000018U) | 
                                (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_parameter[0U] 
                                 >> 8U)))) | (0x3fffffffU 
                                              < ((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_parameter[2U] 
                                                  << 0x00000010U) 
                                                 | (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_parameter[1U] 
                                                    >> 0x00000010U)))) 
                    | (0x3fffffffU < ((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_parameter[1U] 
                                       << 0x00000018U) 
                                      | (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_parameter[0U] 
                                         >> 8U)))) 
                   | (0x2fU < (0x000000ffU & (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_parameter[1U] 
                                              >> 8U)))) 
                  | (0x2fU < (0x000000ffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_parameter[0U]))) 
                 | ((0U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__activation_mode_latched)) 
                    & ((((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_parameter[2U] 
                          << 0x00000010U) | (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_parameter[1U] 
                                             >> 0x00000010U)) 
                        != ((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_parameter[1U] 
                             << 0x00000018U) | (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_parameter[0U] 
                                                >> 8U))) 
                       | ((0x000000ffU & (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_parameter[1U] 
                                          >> 8U)) != 
                          (0x000000ffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_parameter[0U])))))) {
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_invalid = 1U;
            }
        } else {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_invalid = 1U;
        }
    } else if ((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_lane 
                < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_invalid = 1U;
    }
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_parameter[0U] = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_parameter[1U] = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_parameter[2U] = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_accumulator = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product = 0ULL;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add = 0ULL;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude = 0ULL;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value = 0ULL;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requantized_value = 0U;
    if (((8U > vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_lane_index) 
         & (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_lane_index 
            < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count))) {
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_parameter[0U] 
            = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_mq_parameter
            [(7U & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_lane_index)][0U];
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_parameter[1U] 
            = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_mq_parameter
            [(7U & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_lane_index)][1U];
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_parameter[2U] 
            = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_mq_parameter
            [(7U & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_lane_index)][2U];
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_accumulator 
            = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator
            [(7U & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_lane_index)];
        if ((tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_accumulator 
             >> 0x1fU)) {
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier 
                = ((tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_parameter[1U] 
                    << 0x00000018U) | (tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_parameter[0U] 
                                       >> 8U));
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude 
                = ((IData)(1U) + (~ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_accumulator));
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift 
                = (0x000000ffU & tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_parameter[0U]);
        } else {
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier 
                = ((tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_parameter[2U] 
                    << 0x00000010U) | (tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_parameter[1U] 
                                       >> 0x00000010U));
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude 
                = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_accumulator;
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift 
                = (0x000000ffU & (tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_parameter[1U] 
                                  >> 8U));
        }
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product 
            = ((QData)((IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude)) 
               * (QData)((IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier)));
        if ((0U != tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift)) {
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add 
                = VL_SHIFTL_QQI(64,64,32, 1ULL, (tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift 
                                                 - (IData)(1U)));
        }
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude 
            = VL_SHIFTR_QQI(64,64,32, (tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product 
                                       + tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add), tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift);
        __Vtemp_2[0U] = (IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude);
        __Vtemp_2[1U] = (IData)((tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude 
                                 >> 0x00000020U));
        __Vtemp_2[2U] = 0U;
        VL_NEGATE_W(3, __Vtemp_3, __Vtemp_2);
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value 
            = ((tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_accumulator 
                >> 0x1fU) ? (((QData)((IData)(__Vtemp_3[1U])) 
                              << 0x00000020U) | (QData)((IData)(__Vtemp_3[0U])))
                : tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude);
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requantized_value 
            = (VL_LTS_IQQ(64, 0x000000000000007fULL, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value)
                ? 0x0000007fU : (VL_GTS_IQQ(64, 0xffffffffffffff81ULL, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value)
                                  ? 0x00000081U : (0x000000ffU 
                                                   & (IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value))));
    }
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__selected_result_error = 6U;
    vlSelfRef.__VdfgRegularize_h6e95ff9d_0_27 = ((~ (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__hard_reset)) 
                                                 & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__buffer_owner_pl));
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__selected_result_valid = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__conv_result_ready 
        = (((~ (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__hard_reset)) 
            & (2U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__state))) 
           & (0x13U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state)));
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__maxpool_result_ready 
        = (((~ (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__hard_reset)) 
            & (3U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__state))) 
           & (6U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__state)));
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__route_result_ready 
        = (((~ (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__hard_reset)) 
            & (4U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__state))) 
           & (7U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__state)));
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__upsample_result_ready 
        = (((~ (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__hard_reset)) 
            & (5U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__state))) 
           & (5U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__state)));
    __Vtemp_5[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_batch_count_latched;
    __Vtemp_5[1U] = 0U;
    __Vtemp_5[2U] = 0U;
    __Vtemp_5[3U] = 0U;
    __Vtemp_6[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_channels_latched;
    __Vtemp_6[1U] = 0U;
    __Vtemp_6[2U] = 0U;
    __Vtemp_6[3U] = 0U;
    VL_MUL_W(4, __Vtemp_7, __Vtemp_5, __Vtemp_6);
    __Vtemp_8[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_height_latched;
    __Vtemp_8[1U] = 0U;
    __Vtemp_8[2U] = 0U;
    __Vtemp_8[3U] = 0U;
    VL_MUL_W(4, __Vtemp_9, __Vtemp_7, __Vtemp_8);
    __Vtemp_10[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_width_latched;
    __Vtemp_10[1U] = 0U;
    __Vtemp_10[2U] = 0U;
    __Vtemp_10[3U] = 0U;
    VL_MUL_W(4, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_elements_wide, __Vtemp_9, __Vtemp_10);
    __Vtemp_11[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_batch_count_latched;
    __Vtemp_11[1U] = 0U;
    __Vtemp_11[2U] = 0U;
    __Vtemp_11[3U] = 0U;
    __Vtemp_12[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_channels_latched;
    __Vtemp_12[1U] = 0U;
    __Vtemp_12[2U] = 0U;
    __Vtemp_12[3U] = 0U;
    VL_MUL_W(4, __Vtemp_13, __Vtemp_11, __Vtemp_12);
    __Vtemp_14[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_latched;
    __Vtemp_14[1U] = 0U;
    __Vtemp_14[2U] = 0U;
    __Vtemp_14[3U] = 0U;
    VL_MUL_W(4, __Vtemp_15, __Vtemp_13, __Vtemp_14);
    __Vtemp_16[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_latched;
    __Vtemp_16[1U] = 0U;
    __Vtemp_16[2U] = 0U;
    __Vtemp_16[3U] = 0U;
    VL_MUL_W(4, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_elements_wide, __Vtemp_15, __Vtemp_16);
    __Vtemp_17[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_channels_latched;
    __Vtemp_17[1U] = 0U;
    __Vtemp_17[2U] = 0U;
    __Vtemp_17[3U] = 0U;
    __Vtemp_18[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_channels_latched;
    __Vtemp_18[1U] = 0U;
    __Vtemp_18[2U] = 0U;
    __Vtemp_18[3U] = 0U;
    VL_MUL_W(4, __Vtemp_19, __Vtemp_17, __Vtemp_18);
    __Vtemp_20[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_height_latched;
    __Vtemp_20[1U] = 0U;
    __Vtemp_20[2U] = 0U;
    __Vtemp_20[3U] = 0U;
    VL_MUL_W(4, __Vtemp_21, __Vtemp_19, __Vtemp_20);
    __Vtemp_22[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_width_latched;
    __Vtemp_22[1U] = 0U;
    __Vtemp_22[2U] = 0U;
    __Vtemp_22[3U] = 0U;
    VL_MUL_W(4, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__expected_weight_bytes_wide, __Vtemp_21, __Vtemp_22);
    __Vtemp_23[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_channels_latched;
    __Vtemp_23[1U] = 0U;
    __Vtemp_23[2U] = 0U;
    __Vtemp_23[3U] = 0U;
    __Vtemp_24[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_height_latched;
    __Vtemp_24[1U] = 0U;
    __Vtemp_24[2U] = 0U;
    __Vtemp_24[3U] = 0U;
    VL_MUL_W(4, __Vtemp_25, __Vtemp_23, __Vtemp_24);
    __Vtemp_26[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_width_latched;
    __Vtemp_26[1U] = 0U;
    __Vtemp_26[2U] = 0U;
    __Vtemp_26[3U] = 0U;
    VL_MUL_W(4, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_wide, __Vtemp_25, __Vtemp_26);
    __Vtemp_27[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_base_latched;
    __Vtemp_27[1U] = 0U;
    __Vtemp_27[2U] = 0U;
    __Vtemp_27[3U] = 0U;
    __Vtemp_28[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_length_latched;
    __Vtemp_28[1U] = 0U;
    __Vtemp_28[2U] = 0U;
    __Vtemp_28[3U] = 0U;
    VL_ADD_W(4, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_end_wide, __Vtemp_27, __Vtemp_28);
    __Vtemp_29[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_base_latched;
    __Vtemp_29[1U] = 0U;
    __Vtemp_29[2U] = 0U;
    __Vtemp_29[3U] = 0U;
    __Vtemp_30[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_length_latched;
    __Vtemp_30[1U] = 0U;
    __Vtemp_30[2U] = 0U;
    __Vtemp_30[3U] = 0U;
    VL_ADD_W(4, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_end_wide, __Vtemp_29, __Vtemp_30);
    __Vtemp_31[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_package_base_latched;
    __Vtemp_31[1U] = 0U;
    __Vtemp_31[2U] = 0U;
    __Vtemp_31[3U] = 0U;
    __Vtemp_32[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_package_length_latched;
    __Vtemp_32[1U] = 0U;
    __Vtemp_32[2U] = 0U;
    __Vtemp_32[3U] = 0U;
    VL_ADD_W(4, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_package_end_wide, __Vtemp_31, __Vtemp_32);
    __Vtemp_33[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__quantized_weight_offset_latched;
    __Vtemp_33[1U] = 0U;
    __Vtemp_33[2U] = 0U;
    __Vtemp_33[3U] = 0U;
    __Vtemp_34[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__quantized_weight_bytes_latched;
    __Vtemp_34[1U] = 0U;
    __Vtemp_34[2U] = 0U;
    __Vtemp_34[3U] = 0U;
    VL_ADD_W(4, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__quantized_weight_end_wide, __Vtemp_33, __Vtemp_34);
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_numerator 
        = (((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_height_latched)) 
            + (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__pad_top_latched))) 
           + (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__pad_bottom_latched)));
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_numerator 
        = (((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_width_latched)) 
            + (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__pad_left_latched))) 
           + (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__pad_right_latched)));
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_shape_span 
        = (tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_numerator 
           - (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_height_latched)));
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_shape_span 
        = (tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_numerator 
           - (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_width_latched)));
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_shape_product 
        = ((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_latched)) 
           * (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__stride_y_latched)));
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_shape_product 
        = ((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_latched)) 
           * (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__stride_x_latched)));
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_span_plus_stride 
        = (tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_shape_span 
           + (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__stride_y_latched)));
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_span_plus_stride 
        = (tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_shape_span 
           + (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__stride_x_latched)));
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_height_wide[0U] = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_height_wide[1U] = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_height_wide[2U] = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_height_wide[3U] = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_width_wide[0U] = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_width_wide[1U] = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_width_wide[2U] = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_width_wide[3U] = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_bytes_wide[0U] = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_bytes_wide[1U] = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_bytes_wide[2U] = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_bytes_wide[3U] = 0U;
    if (((0U != vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_latched) 
         & (0U != vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_latched))) {
        __Vtemp_35[0U] = (((8U > vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_latched)
                            ? vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_latched
                            : 8U) - (IData)(1U));
        __Vtemp_35[1U] = 0U;
        __Vtemp_35[2U] = 0U;
        __Vtemp_35[3U] = 0U;
        __Vtemp_36[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__stride_y_latched;
        __Vtemp_36[1U] = 0U;
        __Vtemp_36[2U] = 0U;
        __Vtemp_36[3U] = 0U;
        VL_MUL_W(4, __Vtemp_37, __Vtemp_35, __Vtemp_36);
        __Vtemp_38[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_height_latched;
        __Vtemp_38[1U] = 0U;
        __Vtemp_38[2U] = 0U;
        __Vtemp_38[3U] = 0U;
        VL_ADD_W(4, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_height_wide, __Vtemp_37, __Vtemp_38);
        __Vtemp_39[0U] = (((8U > vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_latched)
                            ? vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_latched
                            : 8U) - (IData)(1U));
        __Vtemp_39[1U] = 0U;
        __Vtemp_39[2U] = 0U;
        __Vtemp_39[3U] = 0U;
        __Vtemp_40[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__stride_x_latched;
        __Vtemp_40[1U] = 0U;
        __Vtemp_40[2U] = 0U;
        __Vtemp_40[3U] = 0U;
        VL_MUL_W(4, __Vtemp_41, __Vtemp_39, __Vtemp_40);
        __Vtemp_42[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_width_latched;
        __Vtemp_42[1U] = 0U;
        __Vtemp_42[2U] = 0U;
        __Vtemp_42[3U] = 0U;
        VL_ADD_W(4, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_width_wide, __Vtemp_41, __Vtemp_42);
        VL_MUL_W(4, __Vtemp_43, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_height_wide, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_width_wide);
        __Vtemp_44[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_channels_latched;
        __Vtemp_44[1U] = 0U;
        __Vtemp_44[2U] = 0U;
        __Vtemp_44[3U] = 0U;
        VL_MUL_W(4, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_bytes_wide, __Vtemp_43, __Vtemp_44);
    }
    __Vtemp_45[0U] = ((8U > vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_channels_latched)
                       ? vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_channels_latched
                       : 8U);
    __Vtemp_45[1U] = 0U;
    __Vtemp_45[2U] = 0U;
    __Vtemp_45[3U] = 0U;
    VL_MUL_W(4, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__full_weight_group_bytes_wide, __Vtemp_45, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_wide);
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__validation_ok = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__validation_error = 1U;
    __Vtemp_47[0U] = 0x00001200U;
    __Vtemp_47[1U] = 0U;
    __Vtemp_47[2U] = 0U;
    __Vtemp_47[3U] = 0U;
    if ((1U & ((((((((((((((((((((((~ (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__buffer_owner_pl)) 
                                   | (1U < (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__activation_mode_latched))) 
                                  | (1U != vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_batch_count_latched)) 
                                 | (1U != vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_batch_count_latched)) 
                                | (0U != vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_batch_latched)) 
                               | (0U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_channels_latched)) 
                              | (0U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_height_latched)) 
                             | (0U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_width_latched)) 
                            | (0U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_channels_latched)) 
                           | (0U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_latched)) 
                          | (0U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_latched)) 
                         | (0U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_height_latched)) 
                        | (0U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_width_latched)) 
                       | (0U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__stride_y_latched)) 
                      | (0U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__stride_x_latched)) 
                     | (1U != vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__groups_latched)) 
                    | (0U != vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__padding_latched)) 
                   | (0U == (((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_wide[0U] 
                               | vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_wide[1U]) 
                              | vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_wide[2U]) 
                             | vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_wide[3U]))) 
                  | VL_LT_W(4, __Vtemp_47, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_wide)) 
                 | (0x00000026U <= vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)) 
                | ((0x00000026U > vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched) 
                   & (0U != ((0x25U >= (0x0000003fU 
                                        & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                              ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OP
                             [(0x0000003fU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                              : 0U)))) | (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched 
                                          != vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_layer_index_latched)))) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__validation_error 
            = (((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched 
                 != vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_layer_index_latched) 
                | (0x00000026U <= vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
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
        if ((((((VL_LT_W(4, __Vtemp_48, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_elements_wide) 
                 | (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_length_latched 
                    != tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_elements_wide[0U])) 
                | VL_LT_W(4, __Vtemp_49, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_elements_wide)) 
               | (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_length_latched 
                  != vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_elements_wide[0U])) 
              | VL_LT_W(4, __Vtemp_50, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__expected_weight_bytes_wide)) 
             | (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__quantized_weight_bytes_latched 
                != tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__expected_weight_bytes_wide[0U]))) {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__validation_error = 3U;
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
            __Vtemp_54[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_package_length_latched;
            __Vtemp_54[1U] = 0U;
            __Vtemp_54[2U] = 0U;
            __Vtemp_54[3U] = 0U;
            __Vtemp_55[0U] = 0x00000c5cU;
            __Vtemp_55[1U] = 0U;
            __Vtemp_55[2U] = 0U;
            __Vtemp_55[3U] = 0U;
            __Vtemp_56[0U] = ((0x25U >= (0x0000003fU 
                                         & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                               ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                              [(0x0000003fU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                               : 0U);
            __Vtemp_56[1U] = 0U;
            __Vtemp_56[2U] = 0U;
            __Vtemp_56[3U] = 0U;
            __Vtemp_57[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_channels_latched;
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
            if (((((((((VL_LT_W(4, __Vtemp_51, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_end_wide) 
                        | VL_LT_W(4, __Vtemp_52, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_end_wide)) 
                       | VL_LT_W(4, __Vtemp_53, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_package_end_wide)) 
                      | (0U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_package_length_latched)) 
                     | VL_GT_W(4, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__quantized_weight_end_wide, __Vtemp_54)) 
                    | (((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                         ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                        [(0x0000003fU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                         : 0U) != vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_channels_latched)) 
                   | VL_LT_W(4, __Vtemp_55, __Vtemp_58)) 
                  | VL_LT_W(4, __Vtemp_59, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_bytes_wide)) 
                 | VL_LT_W(4, __Vtemp_60, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__full_weight_group_bytes_wide))) {
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__validation_error = 2U;
            } else if (((((((tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_numerator 
                             < (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_height_latched))) 
                            | (tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_numerator 
                               < (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_width_latched)))) 
                           | (tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_shape_product 
                              <= tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_shape_span)) 
                          | (tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_shape_product 
                             > tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_span_plus_stride)) 
                         | (tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_shape_product 
                            <= tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_shape_span)) 
                        | (tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_shape_product 
                           > tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_span_plus_stride))) {
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__validation_error = 1U;
            } else {
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__validation_ok = 1U;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__validation_error = 0U;
            }
        }
    }
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__query_output_channels = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__query_output_height = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__query_output_width = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__query_source_index = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__query_source_address = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__query_output_value = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__query_error_code = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_argument = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_range = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source0_shape_bytes = 0ULL;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_shape_bytes = 0ULL;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_plane_elements = 0ULL;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_object_end = 0ULL;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__expected_group_start = 0ULL;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__expected_group_end = 0ULL;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_selected_count = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_multiplier = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_base_address = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_length_bytes = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_value = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_magnitude = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__scaled_product = 0ULL;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__rounded_product = 0ULL;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__rounded_magnitude = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__scaled_signed = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_source_index = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_source_channel = 0U;
    if ((1U & ((((((((((~ ((1U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source_count_latched) 
                           | (2U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source_count_latched))) 
                       | (0U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__groups_latched)) 
                      | (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__group_id_latched 
                         >= vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__groups_latched)) 
                     | (0U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_channels_latched)) 
                    | (0U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_height_latched)) 
                   | (0U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_width_latched)) 
                  | (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_start_latched 
                     >= vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_end_latched)) 
                 | (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_end_latched 
                    > vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_channels_latched)) 
                | (0U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_multiplier_latched)) 
               | (0x80000000U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_multiplier_latched)))) {
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_argument = 1U;
    }
    if ((2U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source_count_latched)) {
        if ((((((((((0U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source1_channels_latched) 
                    | (0U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source1_height_latched)) 
                   | (0U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source1_width_latched)) 
                  | (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source1_height_latched 
                     != vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_height_latched)) 
                 | (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source1_width_latched 
                    != vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_width_latched)) 
                | (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source1_start_latched 
                   >= vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source1_end_latched)) 
               | (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source1_end_latched 
                  > vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source1_channels_latched)) 
              | (0U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source1_multiplier_latched)) 
             | (0x80000000U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source1_multiplier_latched))) {
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_argument = 1U;
        }
    }
    if (((1U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__groups_latched) 
         & ((0U != vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_start_latched) 
            | (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_end_latched 
               != vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_channels_latched)))) {
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_argument = 1U;
    } else if ((2U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__groups_latched)) {
        if ((1U & ((1U != vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source_count_latched) 
                   | vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_channels_latched))) {
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_argument = 1U;
        } else {
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__expected_group_start 
                = ((1U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__group_id_latched)
                    ? (QData)((IData)((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_channels_latched 
                                       >> 1U))) : 0ULL);
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__expected_group_end 
                = (tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__expected_group_start 
                   + (QData)((IData)((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_channels_latched 
                                      >> 1U))));
            if (((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_start_latched 
                  != (IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__expected_group_start)) 
                 | (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_end_latched 
                    != (IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__expected_group_end)))) {
                tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_argument = 1U;
            }
        }
    } else if ((2U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__groups_latched)) {
        if (((1U != vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source_count_latched) 
             | (0U != VL_MODDIV_III(32, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_channels_latched, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__groups_latched)))) {
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_argument = 1U;
        } else {
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__expected_group_start 
                = ((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__group_id_latched)) 
                   * VL_DIV_QQQ(64, (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_channels_latched)), (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__groups_latched))));
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__expected_group_end 
                = (tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__expected_group_start 
                   + VL_DIV_QQQ(64, (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_channels_latched)), (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__groups_latched))));
            if (((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_start_latched 
                  != (IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__expected_group_start)) 
                 | (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_end_latched 
                    != (IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__expected_group_end)))) {
                tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_argument = 1U;
            }
        }
    }
    if (((2U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source_count_latched) 
         & (((0U != vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source1_start_latched) 
             | (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source1_end_latched 
                != vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source1_channels_latched)) 
            | (1U != vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__groups_latched)))) {
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_argument = 1U;
    }
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source0_selected_count 
        = (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_end_latched 
           - vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_start_latched);
    if ((2U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source_count_latched)) {
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_selected_count 
            = (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source1_end_latched 
               - vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source1_start_latched);
    }
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__output_channels_wide 
        = ((QData)((IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source0_selected_count)) 
           + (QData)((IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_selected_count)));
    if ((0x00000000ffffffffULL < tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__output_channels_wide)) {
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_range = 1U;
    }
    if ((((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_y_latched 
           >= vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_height_latched) 
          | (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_x_latched 
             >= vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_width_latched)) 
         | ((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_channel_latched)) 
            >= tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__output_channels_wide))) {
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_argument = 1U;
    }
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source0_plane_elements 
        = ((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_channels_latched)) 
           * (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_height_latched)));
    if ((0x00000000ffffffffULL < tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source0_plane_elements)) {
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_range = 1U;
    } else {
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source0_shape_bytes 
            = (tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source0_plane_elements 
               * (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_width_latched)));
        if ((0x00000000ffffffffULL < tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source0_shape_bytes)) {
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_range = 1U;
        }
    }
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source0_object_end 
        = ((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_base_latched)) 
           + (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_length_latched)));
    if ((((0U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_length_latched) 
          | ((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_length_latched)) 
             < tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source0_shape_bytes)) 
         | (0x0000000100000000ULL < tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source0_object_end))) {
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_range = 1U;
    }
    if ((2U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source_count_latched)) {
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_plane_elements 
            = ((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source1_channels_latched)) 
               * (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source1_height_latched)));
        if ((0x00000000ffffffffULL < tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_plane_elements)) {
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_range = 1U;
        } else {
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_shape_bytes 
                = (tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_plane_elements 
                   * (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source1_width_latched)));
            if ((0x00000000ffffffffULL < tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_shape_bytes)) {
                tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_range = 1U;
            }
        }
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_object_end 
            = ((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source1_base_latched)) 
               + (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source1_length_latched)));
        if ((((0U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source1_length_latched) 
              | ((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source1_length_latched)) 
                 < tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_shape_bytes)) 
             | (0x0000000100000000ULL < tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_object_end))) {
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_range = 1U;
        }
    }
    if ((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_channel_latched 
         < tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source0_selected_count)) {
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_source_index = 0U;
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_source_channel 
            = (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_start_latched 
               + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_channel_latched);
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_value 
            = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_value_latched;
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_multiplier 
            = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_multiplier_latched;
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_base_address 
            = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_base_latched;
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_length_bytes 
            = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_length_latched;
    } else if ((2U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source_count_latched)) {
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_source_index = 1U;
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_source_channel 
            = (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source1_start_latched 
               + (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_channel_latched 
                  - tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source0_selected_count));
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_value 
            = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source1_value_latched;
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_multiplier 
            = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source1_multiplier_latched;
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_base_address 
            = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source1_base_latched;
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_length_bytes 
            = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source1_length_latched;
    }
    if ((0x80U == (IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_value))) {
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_argument = 1U;
    }
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_offset 
        = (((((QData)((IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_source_channel)) 
              * (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_height_latched))) 
             + (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_y_latched))) 
            * (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_width_latched))) 
           + (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_x_latched)));
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_address_wide 
        = ((QData)((IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_base_address)) 
           + tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_offset);
    if (((tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_offset 
          >= (QData)((IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_length_bytes))) 
         | (0x00000000ffffffffULL < tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_address_wide))) {
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_range = 1U;
    }
    if (tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_argument) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__query_error_code = 1U;
    } else if (tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_range) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__query_error_code = 2U;
    } else {
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_magnitude 
            = (0x0000007fU & (VL_GTS_III(8, 0U, (IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_value))
                               ? (0x000000ffU & (- (IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_value)))
                               : (IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_value)));
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__scaled_product 
            = (0x0000007fffffffffULL & ((QData)((IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_magnitude)) 
                                        * (QData)((IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_multiplier))));
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__query_output_channels 
            = (IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__output_channels_wide);
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__query_output_height 
            = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_height_latched;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__query_output_width 
            = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_width_latched;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__query_source_index 
            = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_source_index;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__query_source_address 
            = (IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_address_wide);
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__rounded_product 
            = (0x000000ffffffffffULL & (0x0000000040000000ULL 
                                        + tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__scaled_product));
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__rounded_magnitude 
            = (0x000001ffU & (IData)((tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__rounded_product 
                                      >> 0x1fU)));
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__scaled_signed 
            = (0x000001ffU & (VL_GTS_III(8, 0U, (IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_value))
                               ? (- (IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__rounded_magnitude))
                               : (IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__rounded_magnitude)));
        if (VL_LTS_III(9, 0x007fU, (IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__scaled_signed))) {
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__scaled_signed = 0x007fU;
        } else if (VL_GTS_III(9, 0x0181U, (IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__scaled_signed))) {
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__scaled_signed = 0x0181U;
        }
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__query_output_value 
            = (0x000000ffU & (IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__scaled_signed));
    }
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__conv_rsp_valid 
        = ((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__response_pending) 
           & ((~ (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__hard_reset)) 
              & (0U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__response_target_latched))));
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__maxpool_req_write = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__upsample_req_write = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__route_req_write = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__conv_req_write = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__maxpool_req_wstrb = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__upsample_req_wstrb = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__route_req_wstrb = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__conv_req_wstrb = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__maxpool_start_ready 
        = ((~ (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__hard_reset)) 
           & (0U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__state)));
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__upsample_start_ready 
        = ((~ (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__hard_reset)) 
           & (0U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__state)));
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__route_start_ready 
        = ((~ (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__hard_reset)) 
           & (0U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__state)));
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__conv_start_ready 
        = ((~ (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__hard_reset)) 
           & (0U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state)));
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__upsample_req_rstrb = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__conv_req_rstrb = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__selected_read_lane 
        = (0x0000000fU & ((IData)(1U) << (3U & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source_address_latched)));
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__route_req_rstrb = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__maxpool_req_rstrb = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__selected_input_lane = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__maxpool_req_valid = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__upsample_req_valid = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__route_req_valid = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__conv_req_valid = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__upsample_req_addr = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__selected_word_address 
        = (0xfffffffcU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source_address_latched);
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__route_req_addr = 0U;
    if ((4U > (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__read_tap_index))) {
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__selected_input_lane 
            = (0x0000000fU & ((IData)(1U) << (3U & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched
                                              [(3U 
                                                & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__read_tap_index))])));
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__maxpool_req_addr = 0U;
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__selected_input_word_address = 0U;
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__selected_input_word_address 
            = (0xfffffffcU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched
               [(3U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__read_tap_index))]);
    } else {
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__maxpool_req_addr = 0U;
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__selected_input_word_address = 0U;
    }
    if ((1U & (~ (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__hard_reset)))) {
        if ((1U != (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__state))) {
            if ((4U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__state))) {
                tb_s2a_network_backend_golden__DOT__u_backend__DOT__maxpool_req_wdata 
                    = VL_SHIFTL_III(32,32,32, (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__result_value_latched), 
                                    (0x00000018U & 
                                     (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_address_latched 
                                      << 3U)));
                tb_s2a_network_backend_golden__DOT__u_backend__DOT__maxpool_req_write = 1U;
                tb_s2a_network_backend_golden__DOT__u_backend__DOT__maxpool_req_wstrb 
                    = (0x0000000fU & ((IData)(1U) << 
                                      (3U & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_address_latched)));
            }
        }
        if ((1U != (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__state))) {
            if ((3U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__state))) {
                tb_s2a_network_backend_golden__DOT__u_backend__DOT__upsample_req_wdata 
                    = VL_SHIFTL_III(32,32,32, (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__copied_value_latched), 
                                    (0x00000018U & 
                                     (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__output_address_latched 
                                      << 3U)));
                tb_s2a_network_backend_golden__DOT__u_backend__DOT__upsample_req_write = 1U;
                tb_s2a_network_backend_golden__DOT__u_backend__DOT__upsample_req_wstrb 
                    = (0x0000000fU & ((IData)(1U) << 
                                      (3U & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__output_address_latched)));
            }
        }
        if ((2U != (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__state))) {
            if ((5U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__state))) {
                tb_s2a_network_backend_golden__DOT__u_backend__DOT__route_req_wdata 
                    = VL_SHIFTL_III(32,32,32, (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__result_value_latched), 
                                    (0x00000018U & 
                                     (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_address_latched 
                                      << 3U)));
                tb_s2a_network_backend_golden__DOT__u_backend__DOT__route_req_write = 1U;
                tb_s2a_network_backend_golden__DOT__u_backend__DOT__route_req_wstrb 
                    = (0x0000000fU & ((IData)(1U) << 
                                      (3U & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_address_latched)));
            }
        }
        if (((4U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state)) 
             || (8U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state)))) {
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__conv_req_write = 0U;
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__conv_req_rstrb 
                = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__request_strobe_latched;
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__conv_req_valid = 1U;
        } else if ((0x10U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state))) {
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__conv_req_write = 1U;
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__conv_req_valid = 1U;
        }
        if ((1U & (~ ((4U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state)) 
                      || (8U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state)))))) {
            if ((0x10U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state))) {
                tb_s2a_network_backend_golden__DOT__u_backend__DOT__conv_req_wstrb 
                    = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__request_strobe_latched;
            }
        }
        if ((1U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__state))) {
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__upsample_req_rstrb 
                = (0x0000000fU & ((IData)(1U) << (3U 
                                                  & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__source_address_latched)));
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__upsample_req_valid = 1U;
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__upsample_req_addr 
                = (0xfffffffcU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__source_address_latched);
        } else if ((3U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__state))) {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__upsample_req_valid = 1U;
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__upsample_req_addr 
                = (0xfffffffcU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__output_address_latched);
        }
        if ((2U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__state))) {
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__route_req_rstrb 
                = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__selected_read_lane;
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__route_req_valid = 1U;
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__route_req_addr 
                = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__selected_word_address;
        } else if ((5U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__state))) {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__route_req_valid = 1U;
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__route_req_addr 
                = (0xfffffffcU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_address_latched);
        }
        if ((1U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__state))) {
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__maxpool_req_rstrb 
                = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__selected_input_lane;
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__maxpool_req_valid = 1U;
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__maxpool_req_addr 
                = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__selected_input_word_address;
        } else if ((4U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__state))) {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__maxpool_req_valid = 1U;
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__maxpool_req_addr 
                = (0xfffffffcU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_address_latched);
        }
    }
    __Vtemp_62[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_x_latched;
    __Vtemp_62[1U] = 0U;
    __Vtemp_62[2U] = 0U;
    __Vtemp_64[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_y_latched;
    __Vtemp_64[1U] = 0U;
    __Vtemp_64[2U] = 0U;
    __Vtemp_65[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_channel_latched;
    __Vtemp_65[1U] = 0U;
    __Vtemp_65[2U] = 0U;
    VL_MUL_W(3, __Vtemp_66, vlSelfRef.__VdfgRegularize_h6e95ff9d_0_198, __Vtemp_65);
    VL_ADD_W(3, __Vtemp_67, __Vtemp_64, __Vtemp_66);
    __Vtemp_68[0U] = __Vtemp_67[0U];
    __Vtemp_68[1U] = __Vtemp_67[1U];
    __Vtemp_68[2U] = (1U & __Vtemp_67[2U]);
    VL_MUL_W(3, __Vtemp_69, vlSelfRef.__VdfgRegularize_h6e95ff9d_0_197, __Vtemp_68);
    VL_ADD_W(3, __Vtemp_70, __Vtemp_62, __Vtemp_69);
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_offset_work[0U] 
        = __Vtemp_70[0U];
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_offset_work[1U] 
        = __Vtemp_70[1U];
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_offset_work[2U] 
        = (1U & __Vtemp_70[2U]);
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_address_wide 
        = ((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_base_latched)) 
           + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_byte_offset_wide);
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__selected_req_wdata = 0U;
    if ((4U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__state))) {
        if ((1U & (~ ((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__state) 
                      >> 1U)))) {
            if ((1U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__state))) {
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__selected_result_error 
                    = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__result_error_latched;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__selected_result_valid 
                    = ((5U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__state)) 
                       & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__upsample_result_ready));
                tb_s2a_network_backend_golden__DOT__u_backend__DOT__selected_req_wdata 
                    = tb_s2a_network_backend_golden__DOT__u_backend__DOT__upsample_req_wdata;
            } else {
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__selected_result_error 
                    = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__result_error_latched;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__selected_result_valid 
                    = ((7U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__state)) 
                       & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__route_result_ready));
                tb_s2a_network_backend_golden__DOT__u_backend__DOT__selected_req_wdata 
                    = tb_s2a_network_backend_golden__DOT__u_backend__DOT__route_req_wdata;
            }
        }
    } else if ((2U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__state))) {
        if ((1U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__state))) {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__selected_result_error 
                = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__result_error_latched;
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__selected_result_valid 
                = ((6U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__state)) 
                   & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__maxpool_result_ready));
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__selected_req_wdata 
                = tb_s2a_network_backend_golden__DOT__u_backend__DOT__maxpool_req_wdata;
        } else {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__selected_result_error 
                = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__result_error_latched;
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__selected_result_valid 
                = ((0x13U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state)) 
                   & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__conv_result_ready));
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__selected_req_wdata 
                = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__request_wdata_latched;
        }
    }
    vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_wdata 
        = tb_s2a_network_backend_golden__DOT__u_backend__DOT__selected_req_wdata;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__patch_plane_bytes 
        = ((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__patch_height)) 
           * (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__patch_width)));
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_input_y = 0ULL;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_input_x = 0ULL;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_in_bounds = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_advance = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_source_offset = 0ULL;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_source_address_wide = 0ULL;
    if (((0ULL != tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__patch_plane_bytes) 
         & (0U != vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__patch_width))) {
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_input_y 
            = ((((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_y)) 
                 * (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__stride_y_latched))) 
                + (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_y))) 
               - (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__pad_top_latched)));
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_input_x 
            = ((((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_x)) 
                 * (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__stride_x_latched))) 
                + (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_x))) 
               - (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__pad_left_latched)));
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_in_bounds 
            = (((VL_LTES_IQQ(64, 0ULL, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_input_y) 
                 & VL_LTS_IQQ(64, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_input_y, (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_height_latched)))) 
                & VL_LTES_IQQ(64, 0ULL, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_input_x)) 
               & VL_LTS_IQQ(64, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_input_x, (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_width_latched))));
        if (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_in_bounds) {
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_source_offset 
                = (((((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_channel)) 
                      * (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_height_latched))) 
                     + tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_input_y) 
                    * (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_width_latched))) 
                   + tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_input_x);
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_source_address_wide 
                = ((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_base_latched)) 
                   + tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_source_offset);
        }
    }
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_area 
        = (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_height_latched 
           * vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_width_latched);
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_next_input_channel 
        = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_input_channel;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_next_kernel_y 
        = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_y;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_next_reduction_index 
        = ((IData)(1U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_reduction_index);
    if ((((IData)(1U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_x) 
         >= vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_width_latched)) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_next_kernel_x = 0U;
        if ((((IData)(1U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_y) 
             >= vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_height_latched)) {
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_next_kernel_y = 0U;
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_next_input_channel 
                = ((IData)(1U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_input_channel);
        } else {
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_next_kernel_y 
                = ((IData)(1U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_y);
        }
    } else {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_next_kernel_x 
            = ((IData)(1U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_x);
    }
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_point_y 
        = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_scan_y;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_point_x 
        = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_scan_x;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_input_channel 
        = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_input_channel;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_kernel_y 
        = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_y;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_kernel_x 
        = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_x;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_reduction_index 
        = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_reduction_index;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_input_y = 0ULL;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_input_x = 0ULL;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_tap_in_bounds = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_feature_index_wide = 0ULL;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_feature_index = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_enable = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_bad_argument = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_overflow = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[0U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[0U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[0U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[0U] = 0ULL;
    if ((0U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[0U] 
            = ((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[0U] 
            = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_read_byte[0U];
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[0U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[0U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[0U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[0U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[0U])));
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[0U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[0U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[0U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[0U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[0U])))));
        if (((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[0U]) 
                | (0x80U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[0U])))) {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[0U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[0U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_overflow = 1U;
        }
    }
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[1U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[1U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[1U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[1U] = 0ULL;
    if ((1U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[1U] 
            = ((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[1U] 
            = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_read_byte[1U];
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[1U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[1U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[1U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[1U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[1U])));
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[1U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[1U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[1U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[1U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[1U])))));
        if (((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[1U]) 
                | (0x80U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[1U])))) {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[1U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[1U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_overflow = 1U;
        }
    }
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[2U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[2U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[2U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[2U] = 0ULL;
    if ((2U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[2U] 
            = ((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[2U] 
            = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_read_byte[2U];
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[2U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[2U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[2U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[2U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[2U])));
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[2U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[2U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[2U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[2U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[2U])))));
        if (((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[2U]) 
                | (0x80U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[2U])))) {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[2U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[2U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_overflow = 1U;
        }
    }
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[3U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[3U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[3U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[3U] = 0ULL;
    if ((3U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[3U] 
            = ((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[3U] 
            = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_read_byte[3U];
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[3U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[3U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[3U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[3U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[3U])));
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[3U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[3U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[3U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[3U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[3U])))));
        if (((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[3U]) 
                | (0x80U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[3U])))) {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[3U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[3U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_overflow = 1U;
        }
    }
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[4U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[4U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[4U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[4U] = 0ULL;
    if ((4U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[4U] 
            = ((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[4U] 
            = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_read_byte[4U];
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[4U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[4U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[4U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[4U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[4U])));
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[4U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[4U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[4U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[4U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[4U])))));
        if (((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[4U]) 
                | (0x80U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[4U])))) {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[4U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[4U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_overflow = 1U;
        }
    }
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[5U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[5U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[5U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[5U] = 0ULL;
    if ((5U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[5U] 
            = ((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[5U] 
            = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_read_byte[5U];
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[5U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[5U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[5U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[5U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[5U])));
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[5U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[5U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[5U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[5U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[5U])))));
        if (((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[5U]) 
                | (0x80U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[5U])))) {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[5U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[5U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_overflow = 1U;
        }
    }
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[6U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[6U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[6U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[6U] = 0ULL;
    if ((6U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[6U] 
            = ((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[6U] 
            = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_read_byte[6U];
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[6U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[6U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[6U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[6U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[6U])));
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[6U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[6U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[6U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[6U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[6U])))));
        if (((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[6U]) 
                | (0x80U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[6U])))) {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[6U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[6U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_overflow = 1U;
        }
    }
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[7U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[7U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[7U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[7U] = 0ULL;
    if ((7U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[7U] 
            = ((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[7U] 
            = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_read_byte[7U];
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[7U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[7U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[7U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[7U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[7U])));
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[7U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[7U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[7U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[7U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[7U])))));
        if (((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[7U]) 
                | (0x80U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[7U])))) {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[7U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[7U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_overflow = 1U;
        }
    }
    if (((0x0bU == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state)) 
         | (0x0cU == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state)))) {
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_point_y 
            = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_scan_y;
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_point_x 
            = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_scan_x;
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_input_channel = 0U;
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_kernel_y = 0U;
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_kernel_x = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_reduction_index = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_enable = 1U;
    } else if ((0x0dU == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state))) {
        if ((((((IData)(1U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_reduction_index) 
               < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_latched) 
              & (~ (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_bad_argument))) 
             & (~ (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_overflow)))) {
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_point_y 
                = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_scan_y;
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_point_x 
                = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_scan_x;
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_input_channel 
                = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_next_input_channel;
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_kernel_y 
                = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_next_kernel_y;
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_kernel_x 
                = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_next_kernel_x;
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_reduction_index 
                = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_next_reduction_index;
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_enable = 1U;
        }
    }
    if (((0U != tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_area) 
         & (0U != vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_width))) {
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_input_y 
            = (((((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_y)) 
                  * (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__stride_y_latched))) 
                 + ((QData)((IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_point_y)) 
                    * (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__stride_y_latched)))) 
                + (QData)((IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_kernel_y))) 
               - (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__pad_top_latched)));
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_input_x 
            = (((((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_x)) 
                  * (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__stride_x_latched))) 
                 + ((QData)((IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_point_x)) 
                    * (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__stride_x_latched)))) 
                + (QData)((IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_kernel_x))) 
               - (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__pad_left_latched)));
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_tap_in_bounds 
            = (((VL_LTES_IQQ(64, 0ULL, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_input_y) 
                 & VL_LTS_IQQ(64, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_input_y, (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_height_latched)))) 
                & VL_LTES_IQQ(64, 0ULL, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_input_x)) 
               & VL_LTS_IQQ(64, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_input_x, (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_width_latched))));
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_feature_index_wide 
            = (((((QData)((IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_input_channel)) 
                  * tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__patch_plane_bytes) 
                 + ((((QData)((IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_point_y)) 
                      * (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__stride_y_latched))) 
                     + (QData)((IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_kernel_y))) 
                    * (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__patch_width)))) 
                + ((QData)((IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_point_x)) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__stride_x_latched)))) 
               + (QData)((IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_kernel_x)));
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_feature_index 
            = (IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_feature_index_wide);
    }
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mapped_response_error = 6U;
    if ((0U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__response_error_latched))) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mapped_response_error = 0U;
    } else if ((((1U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__response_error_latched)) 
                 | (2U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__response_error_latched))) 
                | (6U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__response_error_latched)))) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mapped_response_error 
            = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__response_error_latched;
    }
    if ((((3U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state)) 
          & (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_index 
             < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__patch_byte_count)) 
         & (~ (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_in_bounds)))) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_advance = 1U;
    } else if ((((5U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state)) 
                 & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__conv_rsp_valid)) 
                & (0U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mapped_response_error)))) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_advance = 1U;
    }
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_plane_elements 
        = ((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_h)) 
           * (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_w)));
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_batch_elements 
        = ((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_c)) 
           * tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_plane_elements);
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_element_count 
        = ((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_n)) 
           * tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_batch_elements);
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_channel = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_y = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_x = 0U;
    if ((((0ULL != tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_plane_elements) 
          & (0ULL != tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_batch_elements)) 
         & (0U != (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_w)))) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_channel 
            = (IData)(VL_MODDIV_QQQ(64, VL_DIV_QQQ(64, (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_element_index)), tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_plane_elements), (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_c))));
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_y 
            = (IData)(VL_MODDIV_QQQ(64, VL_DIV_QQQ(64, (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_element_index)), (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_w))), (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_h))));
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_x 
            = VL_MODDIV_III(32, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_element_index, (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_w));
    }
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_base[0U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_length[0U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_n[0U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_c[0U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_h[0U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_w[0U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_route_start[0U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_route_end[0U] = 0U;
    if ((0U < (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__current_input_count))) {
        if (((0U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor)) 
             & (~ (IData)(vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_KIND
                          [((0x25U >= (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor))
                             ? (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor)
                             : 0U)][0U])))) {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_base[0U] = 0U;
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_length[0U] = 0x0007ec00U;
        } else {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_base[0U] 
                = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_ADDRESS
                [((0x25U >= (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor))
                   ? (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor)
                   : 0U)][0U];
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_length[0U] 
                = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_LENGTH_BYTES
                [((0x25U >= (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor))
                   ? (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor)
                   : 0U)][0U];
        }
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_n[0U] 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_N
            [((0x25U >= (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor))
               ? (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor)
               : 0U)][0U];
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_c[0U] 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_C
            [((0x25U >= (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor))
               ? (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor)
               : 0U)][0U];
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_h[0U] 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_H
            [((0x25U >= (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor))
               ? (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor)
               : 0U)][0U];
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_w[0U] 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_W
            [((0x25U >= (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor))
               ? (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor)
               : 0U)][0U];
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_route_start[0U] 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_ROUTE_CHANNEL_START
            [((0x25U >= (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor))
               ? (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor)
               : 0U)][0U];
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_route_end[0U] 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_ROUTE_CHANNEL_END
            [((0x25U >= (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor))
               ? (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor)
               : 0U)][0U];
    }
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_base[1U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_length[1U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_n[1U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_c[1U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_h[1U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_w[1U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_route_start[1U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_route_end[1U] = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__mq_index 
        = (((0x25U >= (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor))
             ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
            [vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor]
             : 0U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_channel);
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__is_alias_row 
        = (4U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__current_op));
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__alias_valid = 0U;
    if (((((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__is_alias_row) 
           & (~ ((0x25U >= (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor)) 
                 && vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_MEMORY_WRITE_REQUIRED
                 [vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor]))) 
          & ((0x25U >= (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor)) 
             && vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_ALLOCATION_KIND
             [vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor])) 
         & (0x26U > (IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__alias_layer_index)))) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__alias_output_plane_elements 
            = ((QData)((IData)(((0x25U >= (IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__alias_layer_index))
                                 ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_H
                                [tb_s2a_network_backend_golden__DOT__u_backend__DOT__alias_layer_index]
                                 : 0U))) * (QData)((IData)(
                                                           ((0x25U 
                                                             >= (IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__alias_layer_index))
                                                             ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_W
                                                            [tb_s2a_network_backend_golden__DOT__u_backend__DOT__alias_layer_index]
                                                             : 0U))));
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__alias_output_element_count 
            = (((QData)((IData)(((0x25U >= (IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__alias_layer_index))
                                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_N
                                 [tb_s2a_network_backend_golden__DOT__u_backend__DOT__alias_layer_index]
                                  : 0U))) * (QData)((IData)(
                                                            ((0x25U 
                                                              >= (IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__alias_layer_index))
                                                              ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_C
                                                             [tb_s2a_network_backend_golden__DOT__u_backend__DOT__alias_layer_index]
                                                              : 0U)))) 
               * vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__alias_output_plane_elements);
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__alias_valid 
            = ((((((((((0x25U >= (IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__alias_layer_index))
                        ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_TENSOR_INDEX
                       [tb_s2a_network_backend_golden__DOT__u_backend__DOT__alias_layer_index]
                        : 0U) == ((0x25U >= (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor))
                                   ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_TENSOR_INDEX
                                  [vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor]
                                   : 0U)) & (((0x25U 
                                               >= (IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__alias_layer_index))
                                               ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_ADDRESS
                                              [tb_s2a_network_backend_golden__DOT__u_backend__DOT__alias_layer_index]
                                               : 0U) 
                                             == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_base)) 
                    & (((0x25U >= (IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__alias_layer_index))
                         ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_LENGTH_BYTES
                        [tb_s2a_network_backend_golden__DOT__u_backend__DOT__alias_layer_index]
                         : 0U) == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_length)) 
                   & (((0x25U >= (IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__alias_layer_index))
                        ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_N
                       [tb_s2a_network_backend_golden__DOT__u_backend__DOT__alias_layer_index]
                        : 0U) == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_n))) 
                  & (((0x25U >= (IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__alias_layer_index))
                       ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_C
                      [tb_s2a_network_backend_golden__DOT__u_backend__DOT__alias_layer_index]
                       : 0U) == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_c))) 
                 & (((0x25U >= (IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__alias_layer_index))
                      ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_H
                     [tb_s2a_network_backend_golden__DOT__u_backend__DOT__alias_layer_index]
                      : 0U) == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_h))) 
                & (((0x25U >= (IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__alias_layer_index))
                     ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_W
                    [tb_s2a_network_backend_golden__DOT__u_backend__DOT__alias_layer_index]
                     : 0U) == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_w))) 
               & (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__alias_output_element_count 
                  == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_element_count));
    } else {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__alias_output_plane_elements = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__alias_output_element_count = 0ULL;
    }
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__descriptor_valid = 1U;
    if ((((((((((((0x25U >= (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor))
                   ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_LAYER_INDEX
                  [vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor]
                   : 0U) != (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor)) 
                | (0U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__current_input_count))) 
               | (2U < (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__current_input_count))) 
              | (1U != (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_n))) 
             | (0U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_c))) 
            | (0U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_h))) 
           | (0U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_w))) 
          | (0U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_length)) 
         | (0ULL == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_element_count))) {
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__descriptor_valid = 0U;
    }
    if ((1U < (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__current_input_count))) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_base[1U] 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_ADDRESS
            [((0x25U >= (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor))
               ? (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor)
               : 0U)][1U];
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_length[1U] 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_LENGTH_BYTES
            [((0x25U >= (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor))
               ? (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor)
               : 0U)][1U];
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_n[1U] 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_N
            [((0x25U >= (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor))
               ? (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor)
               : 0U)][1U];
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_c[1U] 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_C
            [((0x25U >= (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor))
               ? (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor)
               : 0U)][1U];
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_h[1U] 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_H
            [((0x25U >= (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor))
               ? (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor)
               : 0U)][1U];
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_w[1U] 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_W
            [((0x25U >= (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor))
               ? (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor)
               : 0U)][1U];
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_route_start[1U] 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_ROUTE_CHANNEL_START
            [((0x25U >= (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor))
               ? (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor)
               : 0U)][1U];
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_route_end[1U] 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_ROUTE_CHANNEL_END
            [((0x25U >= (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor))
               ? (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor)
               : 0U)][1U];
    }
    if ((0U < (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__current_input_count))) {
        if ((((((1U != vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_n[0U]) 
                | (0U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_c[0U])) 
               | (0U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_h[0U])) 
              | (0U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_w[0U])) 
             | (0U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_length[0U]))) {
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__descriptor_valid = 0U;
        }
        if (((~ (IData)(vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_KIND
                        [((0x25U >= (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor))
                           ? (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor)
                           : 0U)][0U])) & (0U != (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor)))) {
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__descriptor_valid = 0U;
        }
    }
    if ((1U < (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__current_input_count))) {
        if ((((((1U != vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_n[1U]) 
                | (0U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_c[1U])) 
               | (0U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_h[1U])) 
              | (0U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_w[1U])) 
             | (0U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_length[1U]))) {
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__descriptor_valid = 0U;
        }
        if ((1U & (~ (IData)(vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_KIND
                             [((0x25U >= (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor))
                                ? (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor)
                                : 0U)][1U])))) {
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__descriptor_valid = 0U;
        }
    }
    if (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__is_alias_row) {
        if ((1U & (~ (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__alias_valid)))) {
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__descriptor_valid = 0U;
        }
    } else if ((1U & ((~ ((0x25U >= (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor)) 
                          && vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_MEMORY_WRITE_REQUIRED
                          [vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor])) 
                      | ((0x25U >= (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor)) 
                         && vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_ALLOCATION_KIND
                         [vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor])))) {
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__descriptor_valid = 0U;
    }
    if ((0U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__current_op))) {
        vlSelfRef.__Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__map_conv_activation__21__descriptor_activation 
            = ((0x25U >= (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor))
                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_ACTIVATION
               [vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor]
                : 0U);
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____VlemCall_0__map_conv_activation 
            = (3U & (0xd0U >> ((IData)(vlSelfRef.__Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__map_conv_activation__21__descriptor_activation) 
                               << 1U)));
        if (((((((1U != (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__current_input_count)) 
                 | (((0x25U >= (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor))
                      ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                     [vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor]
                      : 0U) != (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_c))) 
                | (0x00000c5cU <= tb_s2a_network_backend_golden__DOT__u_backend__DOT__mq_index)) 
               | (0x00000c5cU < (((0x25U >= (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor))
                                   ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                  [vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor]
                                   : 0U) + ((0x25U 
                                             >= (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor))
                                             ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                                            [vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor]
                                             : 0U)))) 
              | (3U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____VlemCall_0__map_conv_activation))) 
             | (((0x25U >= (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor))
                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_WEIGHT_LAYER_INDEX
                 [vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor]
                  : 0U) != ((0x25U >= (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor))
                             ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_LAYER_INDEX
                            [vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor]
                             : 0U)))) {
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__descriptor_valid = 0U;
        }
    } else if (((1U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__current_op)) 
                | (3U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__current_op)))) {
        if ((1U != (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__current_input_count))) {
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__descriptor_valid = 0U;
        }
    } else if ((2U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__current_op))) {
        if (((1U != (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__current_input_count)) 
             & (2U != (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__current_input_count)))) {
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__descriptor_valid = 0U;
        }
    } else if ((1U & (~ (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__is_alias_row)))) {
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__descriptor_valid = 0U;
    }
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__descriptor_fault 
        = (1U & (~ (IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__descriptor_valid)));
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__conv_start_valid 
        = ((((1U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__state)) 
             & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__buffer_owner_pl)) 
            & (IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__descriptor_valid)) 
           & (0U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__current_op)));
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__maxpool_start_valid 
        = ((((1U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__state)) 
             & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__buffer_owner_pl)) 
            & (IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__descriptor_valid)) 
           & (1U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__current_op)));
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__route_start_valid 
        = ((((1U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__state)) 
             & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__buffer_owner_pl)) 
            & (IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__descriptor_valid)) 
           & (2U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__current_op)));
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__upsample_start_valid 
        = ((((1U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__state)) 
             & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__buffer_owner_pl)) 
            & (IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__descriptor_valid)) 
           & (3U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__current_op)));
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__selected_start_ready 
        = ((1U & (~ ((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__current_op) 
                     >> 2U))) && ((2U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__current_op))
                                   ? ((1U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__current_op))
                                       ? (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__upsample_start_ready)
                                       : (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__route_start_ready))
                                   : ((1U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__current_op))
                                       ? (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__maxpool_start_ready)
                                       : (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__conv_start_ready))));
    vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_valid 
        = ((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__buffer_owner_pl) 
           & ((~ (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__hard_reset)) 
              & ((~ (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__response_pending)) 
                 & ((4U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__state))
                     ? ((~ ((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__state) 
                            >> 1U)) & ((1U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__state))
                                        ? (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__upsample_req_valid)
                                        : (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__route_req_valid)))
                     : (((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__state) 
                         >> 1U) & ((1U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__state))
                                    ? (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__maxpool_req_valid)
                                    : (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__conv_req_valid)))))));
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__selected_req_addr = 0U;
    if ((4U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__state))) {
        if ((1U & (~ ((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__state) 
                      >> 1U)))) {
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__selected_req_addr 
                = ((1U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__state))
                    ? tb_s2a_network_backend_golden__DOT__u_backend__DOT__upsample_req_addr
                    : tb_s2a_network_backend_golden__DOT__u_backend__DOT__route_req_addr);
        }
    } else if ((2U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__state))) {
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__selected_req_addr 
            = ((1U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__state))
                ? tb_s2a_network_backend_golden__DOT__u_backend__DOT__maxpool_req_addr
                : vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__request_address_latched);
    }
    vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr 
        = tb_s2a_network_backend_golden__DOT__u_backend__DOT__selected_req_addr;
    __VdfgRegularize_h6e95ff9d_0_196[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_base;
    __VdfgRegularize_h6e95ff9d_0_196[1U] = 0U;
    __VdfgRegularize_h6e95ff9d_0_196[2U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__operator_result_valid = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__operator_error_code = 0U;
    if (((~ (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__hard_reset)) 
         & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__buffer_owner_pl))) {
        if ((4U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__state))) {
            if ((2U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__state))) {
                vlSelfRef.tb_s2a_network_backend_golden__DOT__operator_result_valid = 1U;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__operator_error_code = 6U;
            } else {
                vlSelfRef.__Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__normalize_engine_error__22__code 
                    = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__selected_result_error;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____VlemCall_1__normalize_engine_error 
                    = ((4U & (IData)(vlSelfRef.__Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__normalize_engine_error__22__code))
                        ? (IData)(vlSelfRef.__Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__normalize_engine_error__22__code)
                        : ((2U & (IData)(vlSelfRef.__Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__normalize_engine_error__22__code))
                            ? (IData)(vlSelfRef.__Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__normalize_engine_error__22__code)
                            : ((1U & (IData)(vlSelfRef.__Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__normalize_engine_error__22__code))
                                ? (IData)(vlSelfRef.__Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__normalize_engine_error__22__code)
                                : 0U)));
                if (((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__selected_result_valid) 
                     & (0U != (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____VlemCall_1__normalize_engine_error)))) {
                    vlSelfRef.__Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__normalize_engine_error__23__code 
                        = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__selected_result_error;
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__operator_result_valid = 1U;
                    vlSelfRef.__Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__normalize_engine_error__23__Vfuncout 
                        = ((4U & (IData)(vlSelfRef.__Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__normalize_engine_error__23__code))
                            ? (IData)(vlSelfRef.__Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__normalize_engine_error__23__code)
                            : ((2U & (IData)(vlSelfRef.__Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__normalize_engine_error__23__code))
                                ? (IData)(vlSelfRef.__Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__normalize_engine_error__23__code)
                                : ((1U & (IData)(vlSelfRef.__Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__normalize_engine_error__23__code))
                                    ? (IData)(vlSelfRef.__Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__normalize_engine_error__23__code)
                                    : 0U)));
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__operator_error_code 
                        = vlSelfRef.__Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__normalize_engine_error__23__Vfuncout;
                } else if ((((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__selected_result_valid) 
                             & ((0U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__current_op)) 
                                | ((1ULL + (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_element_index))) 
                                   >= vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_element_count))) 
                            & (0x00000026U <= ((IData)(1U) 
                                               + (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor))))) {
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__operator_result_valid = 1U;
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__operator_error_code = 0U;
                }
            }
        } else if ((2U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__state))) {
            vlSelfRef.__Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__normalize_engine_error__24__code 
                = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__selected_result_error;
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____VlemCall_1__normalize_engine_error 
                = ((4U & (IData)(vlSelfRef.__Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__normalize_engine_error__24__code))
                    ? (IData)(vlSelfRef.__Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__normalize_engine_error__24__code)
                    : ((2U & (IData)(vlSelfRef.__Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__normalize_engine_error__24__code))
                        ? (IData)(vlSelfRef.__Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__normalize_engine_error__24__code)
                        : ((1U & (IData)(vlSelfRef.__Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__normalize_engine_error__24__code))
                            ? (IData)(vlSelfRef.__Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__normalize_engine_error__24__code)
                            : 0U)));
            if (((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__selected_result_valid) 
                 & (0U != (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____VlemCall_1__normalize_engine_error)))) {
                vlSelfRef.__Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__normalize_engine_error__25__code 
                    = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__selected_result_error;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__operator_result_valid = 1U;
                vlSelfRef.__Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__normalize_engine_error__25__Vfuncout 
                    = ((4U & (IData)(vlSelfRef.__Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__normalize_engine_error__25__code))
                        ? (IData)(vlSelfRef.__Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__normalize_engine_error__25__code)
                        : ((2U & (IData)(vlSelfRef.__Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__normalize_engine_error__25__code))
                            ? (IData)(vlSelfRef.__Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__normalize_engine_error__25__code)
                            : ((1U & (IData)(vlSelfRef.__Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__normalize_engine_error__25__code))
                                ? (IData)(vlSelfRef.__Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__normalize_engine_error__25__code)
                                : 0U)));
                vlSelfRef.tb_s2a_network_backend_golden__DOT__operator_error_code 
                    = vlSelfRef.__Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__normalize_engine_error__25__Vfuncout;
            } else if ((((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__selected_result_valid) 
                         & ((0U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__current_op)) 
                            | ((1ULL + (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_element_index))) 
                               >= vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_element_count))) 
                        & (0x00000026U <= ((IData)(1U) 
                                           + (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor))))) {
                vlSelfRef.tb_s2a_network_backend_golden__DOT__operator_result_valid = 1U;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__operator_error_code = 0U;
            }
        } else if ((1U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__state))) {
            if ((1U & ((((0x26U <= (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor)) 
                         | (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__descriptor_fault)) 
                        | ((~ (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__is_alias_row)) 
                           & (~ (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__selected_start_ready)))) 
                       | ((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__is_alias_row) 
                          & (~ (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__alias_valid)))))) {
                vlSelfRef.tb_s2a_network_backend_golden__DOT__operator_result_valid = 1U;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__operator_error_code = 6U;
            } else if (((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__is_alias_row) 
                        & (0x00000026U <= ((IData)(1U) 
                                           + (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor))))) {
                vlSelfRef.tb_s2a_network_backend_golden__DOT__operator_result_valid = 1U;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__operator_error_code = 0U;
            }
        }
    }
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__output_offset_work 
        = ((0x000000000000001aULL * ((0x000000000000001aULL 
                                      * (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_channel))) 
                                     + (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_y)))) 
           + (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_x)));
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_offset_work 
        = ((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_x)) 
           + (((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_y)) 
               + ((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_channel)) 
                  * (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_h)))) 
              * (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_w))));
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__output_height_work = 0ULL;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__output_width_work = 0ULL;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__plane_elements_work = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__plane_index_work = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__byte_offset_work = 0ULL;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__address_work = 0ULL;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_channel = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_y = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_x = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_address = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__query_error_code = 0U;
    if (((((((0U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_c[0U]) 
             | (0U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_h[0U])) 
            | (0U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_w[0U])) 
           | (0U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_upsample_engine__stride)) 
          | (0x000dU < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_h[0U])) 
         | (0x000dU < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_w[0U]))) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__query_error_code = 1U;
    } else {
        if ((2U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_upsample_engine__stride)) {
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__output_height_work 
                = ((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_h[0U])) 
                   << 1U);
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__output_width_work 
                = ((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_w[0U])) 
                   << 1U);
        } else {
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__output_height_work 
                = ((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_h[0U])) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_upsample_engine__stride)));
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__output_width_work 
                = ((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_w[0U])) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_upsample_engine__stride)));
        }
        if ((((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_channel 
               >= vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_c[0U]) 
              | ((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_y)) 
                 >= tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__output_height_work)) 
             | ((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_x)) 
                >= tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__output_width_work))) {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__query_error_code = 1U;
        } else {
            if ((2U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_upsample_engine__stride)) {
                tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_y 
                    = (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_y 
                       >> 1U);
                tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_x 
                    = (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_x 
                       >> 1U);
            } else {
                tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_y 
                    = VL_DIV_III(32, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_y, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_upsample_engine__stride);
                tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_x 
                    = VL_DIV_III(32, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_x, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_upsample_engine__stride);
            }
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_channel 
                = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_channel;
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__plane_elements_work 
                = (0x000000ffU & ((0x0000000fU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_h[0U]) 
                                  * (0x0000000fU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_w[0U])));
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__plane_index_work 
                = (0x000000ffU & (((0x0000000fU & tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_y) 
                                   * (0x0000000fU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_w[0U])) 
                                  + (0x0000000fU & tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_x)));
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__byte_offset_work 
                = (0x000000ffffffffffULL & (((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_channel)) 
                                             * (QData)((IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__plane_elements_work))) 
                                            + (QData)((IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__plane_index_work))));
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__address_work 
                = (0x000001ffffffffffULL & ((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_base[0U])) 
                                            + tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__byte_offset_work));
            if ((0U != (0x000001ffU & (IData)((tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__address_work 
                                               >> 0x20U))))) {
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__query_error_code = 2U;
            } else {
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_address 
                    = (IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__address_work);
            }
        }
    }
    if ((0U != (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__query_error_code))) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_channel = 0U;
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_y = 0U;
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_x = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_address = 0U;
    }
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__extent_y 
        = (0x00000001ffffffffULL & ((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_h[0U])) 
                                    + (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__darknet_padding_parameter))));
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__extent_x 
        = (0x00000001ffffffffULL & ((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_w[0U])) 
                                    + (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__darknet_padding_parameter))));
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_height_work = 0ULL;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_width_work = 0ULL;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_y_step = 0ULL;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_x_step = 0ULL;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_y_work = 0ULL;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_x_work = 0ULL;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work = 0ULL;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U] = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U] = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U] = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U] = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U] = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U] = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__tap_range_error = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_output_height = 0ULL;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_output_width = 0ULL;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_count = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_error_code = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__origin_y = 0ULL;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__origin_x = 0ULL;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_y_work[0U] = 0ULL;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_index_work[0U] = 0ULL;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[0U][0U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[0U][1U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[0U][2U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_y_work[1U] = 0ULL;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_index_work[1U] = 0ULL;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[1U][0U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[1U][1U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[1U][2U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_y_work[2U] = 0ULL;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_index_work[2U] = 0ULL;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[2U][0U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[2U][1U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[2U][2U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[0U] = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[0U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[0U] = 0ULL;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[0U] = 0ULL;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[1U] = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[1U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[1U] = 0ULL;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[1U] = 0ULL;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[2U] = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[2U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[2U] = 0ULL;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[2U] = 0ULL;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[3U] = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[3U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[3U] = 0ULL;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[3U] = 0ULL;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[4U] = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[4U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[4U] = 0ULL;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[4U] = 0ULL;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[5U] = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[5U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[5U] = 0ULL;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[5U] = 0ULL;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[6U] = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[6U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[6U] = 0ULL;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[6U] = 0ULL;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[7U] = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[7U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[7U] = 0ULL;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[7U] = 0ULL;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[8U] = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[8U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[8U] = 0ULL;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[8U] = 0ULL;
    if ((1U & ((((((~ (((2U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_height) 
                        & (2U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width)) 
                       | ((3U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_height) 
                          & (3U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width)))) 
                   | (0U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_y)) 
                  | (0U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_x)) 
                 | (0U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_c[0U])) 
                | (0U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_h[0U])) 
               | (0U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_w[0U])))) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_error_code = 1U;
    } else if (((tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__extent_y 
                 < (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_height))) 
                | (tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__extent_x 
                   < (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width))))) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_error_code = 1U;
    } else {
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_height_work 
            = (0x00000001ffffffffULL & ((2U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_y)
                                         ? (1ULL + 
                                            (0x00000000ffffffffULL 
                                             & ((tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__extent_y 
                                                 - (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_height))) 
                                                >> 1U)))
                                         : (1ULL + 
                                            VL_DIV_QQQ(33, 
                                                       (0x00000001ffffffffULL 
                                                        & (tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__extent_y 
                                                           - (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_height)))), (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_y))))));
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_width_work 
            = (0x00000001ffffffffULL & ((2U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_x)
                                         ? (1ULL + 
                                            (0x00000000ffffffffULL 
                                             & ((tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__extent_x 
                                                 - (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width))) 
                                                >> 1U)))
                                         : (1ULL + 
                                            VL_DIV_QQQ(33, 
                                                       (0x00000001ffffffffULL 
                                                        & (tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__extent_x 
                                                           - (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width)))), (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_x))))));
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_output_height 
            = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_height_work;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_output_width 
            = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_width_work;
        if ((((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_channel 
               >= vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_c[0U]) 
              | ((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_y)) 
                 >= tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_height_work)) 
             | ((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_x)) 
                >= tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_width_work))) {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_error_code = 1U;
        } else {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_count 
                = ((2U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_height)
                    ? 4U : 9U);
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__origin_y 
                = (- VL_EXTENDS_QQ(64,63, (QData)((IData)(
                                                          (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__darknet_padding_parameter 
                                                           >> 1U)))));
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__origin_x 
                = (- VL_EXTENDS_QQ(64,63, (QData)((IData)(
                                                          (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__darknet_padding_parameter 
                                                           >> 1U)))));
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_y_step 
                = (0x00000001ffffffffULL & ((2U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_y)
                                             ? ((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_y)) 
                                                << 1U)
                                             : ((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_y)) 
                                                * (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_y)))));
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_x_step 
                = (0x00000001ffffffffULL & ((2U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_x)
                                             ? ((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_x)) 
                                                << 1U)
                                             : ((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_x)) 
                                                * (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_x)))));
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_y_work 
                = (tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__origin_y 
                   + tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_y_step);
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_x_work 
                = (tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__origin_x 
                   + tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_x_step);
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work 
                = ((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_channel)) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_h[0U])));
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_y_work[0U] 
                = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_y_work;
            if ((VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_y_work[0U]) 
                 & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_y_work[0U], (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_h[0U]))))) {
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_index_work[0U] 
                    = (tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work 
                       + (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_y_work[0U])));
                __Vtemp_74[0U] = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_index_work[0U]);
                __Vtemp_74[1U] = (IData)((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_index_work[0U] 
                                          >> 0x00000020U));
                __Vtemp_74[2U] = 0U;
                __Vtemp_75[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_w[0U];
                __Vtemp_75[1U] = 0U;
                __Vtemp_75[2U] = 0U;
                VL_MUL_W(3, __Vtemp_76, __Vtemp_74, __Vtemp_75);
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[0U][0U] 
                    = __Vtemp_76[0U];
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[0U][1U] 
                    = __Vtemp_76[1U];
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[0U][2U] 
                    = __Vtemp_76[2U];
            }
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_y_work[1U] 
                = (1ULL + tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_y_work);
            if ((VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_y_work[1U]) 
                 & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_y_work[1U], (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_h[0U]))))) {
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_index_work[1U] 
                    = (tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work 
                       + (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_y_work[1U])));
                __Vtemp_77[0U] = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_index_work[1U]);
                __Vtemp_77[1U] = (IData)((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_index_work[1U] 
                                          >> 0x00000020U));
                __Vtemp_77[2U] = 0U;
                __Vtemp_78[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_w[0U];
                __Vtemp_78[1U] = 0U;
                __Vtemp_78[2U] = 0U;
                VL_MUL_W(3, __Vtemp_79, __Vtemp_77, __Vtemp_78);
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[1U][0U] 
                    = __Vtemp_79[0U];
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[1U][1U] 
                    = __Vtemp_79[1U];
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[1U][2U] 
                    = __Vtemp_79[2U];
            }
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_y_work[2U] 
                = (2ULL + tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_y_work);
            if ((VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_y_work[2U]) 
                 & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_y_work[2U], (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_h[0U]))))) {
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_index_work[2U] 
                    = (tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work 
                       + (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_y_work[2U])));
                __Vtemp_80[0U] = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_index_work[2U]);
                __Vtemp_80[1U] = (IData)((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_index_work[2U] 
                                          >> 0x00000020U));
                __Vtemp_80[2U] = 0U;
                __Vtemp_81[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_w[0U];
                __Vtemp_81[1U] = 0U;
                __Vtemp_81[2U] = 0U;
                VL_MUL_W(3, __Vtemp_82, __Vtemp_80, __Vtemp_81);
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[2U][0U] 
                    = __Vtemp_82[0U];
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[2U][1U] 
                    = __Vtemp_82[1U];
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[2U][2U] 
                    = __Vtemp_82[2U];
            }
            if ((0U < (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_count))) {
                tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work = 0U;
                tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work = 0U;
                tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[0U] 
                    = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_channel;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[0U] 
                    = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_y_work;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[0U] 
                    = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_x_work;
                if ((((VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[0U]) 
                       & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[0U], (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_h[0U])))) 
                      & VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[0U])) 
                     & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[0U], (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_w[0U]))))) {
                    if ((0U == tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work)) {
                        __Vtemp_83[0U] = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[0U]);
                        __Vtemp_83[1U] = 0U;
                        __Vtemp_83[2U] = 0U;
                        VL_ADD_W(3, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[0U], __Vtemp_83);
                    } else if ((1U == tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work)) {
                        __Vtemp_84[0U] = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[0U]);
                        __Vtemp_84[1U] = 0U;
                        __Vtemp_84[2U] = 0U;
                        VL_ADD_W(3, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[1U], __Vtemp_84);
                    } else if ((2U == tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work)) {
                        __Vtemp_85[0U] = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[0U]);
                        __Vtemp_85[1U] = 0U;
                        __Vtemp_85[2U] = 0U;
                        VL_ADD_W(3, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[2U], __Vtemp_85);
                    } else {
                        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U] = 0U;
                        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U] = 0U;
                        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U] = 0U;
                    }
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask 
                        = (1U | (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask));
                    __Vtemp_87[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_base[0U];
                    __Vtemp_87[1U] = 0U;
                    __Vtemp_87[2U] = 0U;
                    __Vtemp_87[3U] = 0U;
                    __Vtemp_88[0U] = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U];
                    __Vtemp_88[1U] = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U];
                    __Vtemp_88[2U] = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U];
                    __Vtemp_88[3U] = 0U;
                    VL_ADD_W(4, __Vtemp_89, __Vtemp_87, __Vtemp_88);
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U] 
                        = __Vtemp_89[0U];
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                        = __Vtemp_89[1U];
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U] 
                        = __Vtemp_89[2U];
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U] 
                        = (1U & __Vtemp_89[3U]);
                    if ((0U != ((tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                                 | tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U]) 
                                | (1U & tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U])))) {
                        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__tap_range_error = 1U;
                    } else {
                        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[0U] 
                            = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U];
                    }
                }
            }
            if ((1U < (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_count))) {
                tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work = 0U;
                tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work = 1U;
                tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[1U] 
                    = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_channel;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[1U] 
                    = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_y_work;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[1U] 
                    = (1ULL + tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_x_work);
                if ((((VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[1U]) 
                       & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[1U], (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_h[0U])))) 
                      & VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[1U])) 
                     & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[1U], (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_w[0U]))))) {
                    if ((0U == tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work)) {
                        __Vtemp_94[0U] = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[1U]);
                        __Vtemp_94[1U] = 0U;
                        __Vtemp_94[2U] = 0U;
                        VL_ADD_W(3, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[0U], __Vtemp_94);
                    } else if ((1U == tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work)) {
                        __Vtemp_95[0U] = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[1U]);
                        __Vtemp_95[1U] = 0U;
                        __Vtemp_95[2U] = 0U;
                        VL_ADD_W(3, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[1U], __Vtemp_95);
                    } else if ((2U == tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work)) {
                        __Vtemp_96[0U] = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[1U]);
                        __Vtemp_96[1U] = 0U;
                        __Vtemp_96[2U] = 0U;
                        VL_ADD_W(3, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[2U], __Vtemp_96);
                    } else {
                        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U] = 0U;
                        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U] = 0U;
                        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U] = 0U;
                    }
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask 
                        = (2U | (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask));
                    __Vtemp_98[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_base[0U];
                    __Vtemp_98[1U] = 0U;
                    __Vtemp_98[2U] = 0U;
                    __Vtemp_98[3U] = 0U;
                    __Vtemp_99[0U] = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U];
                    __Vtemp_99[1U] = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U];
                    __Vtemp_99[2U] = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U];
                    __Vtemp_99[3U] = 0U;
                    VL_ADD_W(4, __Vtemp_100, __Vtemp_98, __Vtemp_99);
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U] 
                        = __Vtemp_100[0U];
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                        = __Vtemp_100[1U];
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U] 
                        = __Vtemp_100[2U];
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U] 
                        = (1U & __Vtemp_100[3U]);
                    if ((0U != ((tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                                 | tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U]) 
                                | (1U & tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U])))) {
                        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__tap_range_error = 1U;
                    } else {
                        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[1U] 
                            = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U];
                    }
                }
            }
            if ((2U < (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_count))) {
                if ((2U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width)) {
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work = 1U;
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work = 0U;
                } else {
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work = 0U;
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work = 2U;
                }
                tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[2U] 
                    = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_channel;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[2U] 
                    = (tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_y_work 
                       + VL_EXTENDS_QI(64,32, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work));
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[2U] 
                    = (tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_x_work 
                       + VL_EXTENDS_QI(64,32, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work));
                if ((((VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[2U]) 
                       & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[2U], (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_h[0U])))) 
                      & VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[2U])) 
                     & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[2U], (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_w[0U]))))) {
                    if ((0U == tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work)) {
                        __Vtemp_105[0U] = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[2U]);
                        __Vtemp_105[1U] = 0U;
                        __Vtemp_105[2U] = 0U;
                        VL_ADD_W(3, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[0U], __Vtemp_105);
                    } else if ((1U == tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work)) {
                        __Vtemp_106[0U] = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[2U]);
                        __Vtemp_106[1U] = 0U;
                        __Vtemp_106[2U] = 0U;
                        VL_ADD_W(3, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[1U], __Vtemp_106);
                    } else if ((2U == tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work)) {
                        __Vtemp_107[0U] = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[2U]);
                        __Vtemp_107[1U] = 0U;
                        __Vtemp_107[2U] = 0U;
                        VL_ADD_W(3, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[2U], __Vtemp_107);
                    } else {
                        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U] = 0U;
                        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U] = 0U;
                        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U] = 0U;
                    }
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask 
                        = (4U | (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask));
                    __Vtemp_109[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_base[0U];
                    __Vtemp_109[1U] = 0U;
                    __Vtemp_109[2U] = 0U;
                    __Vtemp_109[3U] = 0U;
                    __Vtemp_110[0U] = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U];
                    __Vtemp_110[1U] = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U];
                    __Vtemp_110[2U] = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U];
                    __Vtemp_110[3U] = 0U;
                    VL_ADD_W(4, __Vtemp_111, __Vtemp_109, __Vtemp_110);
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U] 
                        = __Vtemp_111[0U];
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                        = __Vtemp_111[1U];
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U] 
                        = __Vtemp_111[2U];
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U] 
                        = (1U & __Vtemp_111[3U]);
                    if ((0U != ((tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                                 | tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U]) 
                                | (1U & tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U])))) {
                        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__tap_range_error = 1U;
                    } else {
                        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[2U] 
                            = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U];
                    }
                }
            }
            if ((3U < (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_count))) {
                if ((2U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width)) {
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work = 1U;
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work = 1U;
                } else {
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work = 1U;
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work = 0U;
                }
                tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[3U] 
                    = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_channel;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[3U] 
                    = (tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_y_work 
                       + VL_EXTENDS_QI(64,32, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work));
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[3U] 
                    = (tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_x_work 
                       + VL_EXTENDS_QI(64,32, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work));
                if ((((VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[3U]) 
                       & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[3U], (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_h[0U])))) 
                      & VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[3U])) 
                     & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[3U], (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_w[0U]))))) {
                    if ((0U == tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work)) {
                        __Vtemp_116[0U] = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[3U]);
                        __Vtemp_116[1U] = 0U;
                        __Vtemp_116[2U] = 0U;
                        VL_ADD_W(3, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[0U], __Vtemp_116);
                    } else if ((1U == tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work)) {
                        __Vtemp_117[0U] = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[3U]);
                        __Vtemp_117[1U] = 0U;
                        __Vtemp_117[2U] = 0U;
                        VL_ADD_W(3, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[1U], __Vtemp_117);
                    } else if ((2U == tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work)) {
                        __Vtemp_118[0U] = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[3U]);
                        __Vtemp_118[1U] = 0U;
                        __Vtemp_118[2U] = 0U;
                        VL_ADD_W(3, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[2U], __Vtemp_118);
                    } else {
                        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U] = 0U;
                        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U] = 0U;
                        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U] = 0U;
                    }
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask 
                        = (8U | (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask));
                    __Vtemp_120[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_base[0U];
                    __Vtemp_120[1U] = 0U;
                    __Vtemp_120[2U] = 0U;
                    __Vtemp_120[3U] = 0U;
                    __Vtemp_121[0U] = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U];
                    __Vtemp_121[1U] = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U];
                    __Vtemp_121[2U] = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U];
                    __Vtemp_121[3U] = 0U;
                    VL_ADD_W(4, __Vtemp_122, __Vtemp_120, __Vtemp_121);
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U] 
                        = __Vtemp_122[0U];
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                        = __Vtemp_122[1U];
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U] 
                        = __Vtemp_122[2U];
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U] 
                        = (1U & __Vtemp_122[3U]);
                    if ((0U != ((tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                                 | tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U]) 
                                | (1U & tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U])))) {
                        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__tap_range_error = 1U;
                    } else {
                        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[3U] 
                            = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U];
                    }
                }
            }
            if ((4U < (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_count))) {
                if ((2U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width)) {
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work = 0U;
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work = 0U;
                } else {
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work = 1U;
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work = 1U;
                }
                tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[4U] 
                    = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_channel;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[4U] 
                    = (tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_y_work 
                       + VL_EXTENDS_QI(64,32, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work));
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[4U] 
                    = (tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_x_work 
                       + VL_EXTENDS_QI(64,32, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work));
                if ((((VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[4U]) 
                       & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[4U], (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_h[0U])))) 
                      & VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[4U])) 
                     & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[4U], (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_w[0U]))))) {
                    if ((0U == tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work)) {
                        __Vtemp_127[0U] = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[4U]);
                        __Vtemp_127[1U] = 0U;
                        __Vtemp_127[2U] = 0U;
                        VL_ADD_W(3, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[0U], __Vtemp_127);
                    } else if ((1U == tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work)) {
                        __Vtemp_128[0U] = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[4U]);
                        __Vtemp_128[1U] = 0U;
                        __Vtemp_128[2U] = 0U;
                        VL_ADD_W(3, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[1U], __Vtemp_128);
                    } else if ((2U == tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work)) {
                        __Vtemp_129[0U] = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[4U]);
                        __Vtemp_129[1U] = 0U;
                        __Vtemp_129[2U] = 0U;
                        VL_ADD_W(3, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[2U], __Vtemp_129);
                    } else {
                        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U] = 0U;
                        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U] = 0U;
                        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U] = 0U;
                    }
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask 
                        = (0x00000010U | (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask));
                    __Vtemp_131[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_base[0U];
                    __Vtemp_131[1U] = 0U;
                    __Vtemp_131[2U] = 0U;
                    __Vtemp_131[3U] = 0U;
                    __Vtemp_132[0U] = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U];
                    __Vtemp_132[1U] = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U];
                    __Vtemp_132[2U] = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U];
                    __Vtemp_132[3U] = 0U;
                    VL_ADD_W(4, __Vtemp_133, __Vtemp_131, __Vtemp_132);
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U] 
                        = __Vtemp_133[0U];
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                        = __Vtemp_133[1U];
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U] 
                        = __Vtemp_133[2U];
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U] 
                        = (1U & __Vtemp_133[3U]);
                    if ((0U != ((tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                                 | tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U]) 
                                | (1U & tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U])))) {
                        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__tap_range_error = 1U;
                    } else {
                        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[4U] 
                            = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U];
                    }
                }
            }
            if ((5U < (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_count))) {
                if ((2U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width)) {
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work = 0U;
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work = 0U;
                } else {
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work = 1U;
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work = 2U;
                }
                tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[5U] 
                    = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_channel;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[5U] 
                    = (tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_y_work 
                       + VL_EXTENDS_QI(64,32, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work));
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[5U] 
                    = (tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_x_work 
                       + VL_EXTENDS_QI(64,32, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work));
                if ((((VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[5U]) 
                       & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[5U], (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_h[0U])))) 
                      & VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[5U])) 
                     & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[5U], (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_w[0U]))))) {
                    if ((0U == tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work)) {
                        __Vtemp_138[0U] = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[5U]);
                        __Vtemp_138[1U] = 0U;
                        __Vtemp_138[2U] = 0U;
                        VL_ADD_W(3, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[0U], __Vtemp_138);
                    } else if ((1U == tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work)) {
                        __Vtemp_139[0U] = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[5U]);
                        __Vtemp_139[1U] = 0U;
                        __Vtemp_139[2U] = 0U;
                        VL_ADD_W(3, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[1U], __Vtemp_139);
                    } else if ((2U == tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work)) {
                        __Vtemp_140[0U] = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[5U]);
                        __Vtemp_140[1U] = 0U;
                        __Vtemp_140[2U] = 0U;
                        VL_ADD_W(3, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[2U], __Vtemp_140);
                    } else {
                        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U] = 0U;
                        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U] = 0U;
                        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U] = 0U;
                    }
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask 
                        = (0x00000020U | (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask));
                    __Vtemp_142[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_base[0U];
                    __Vtemp_142[1U] = 0U;
                    __Vtemp_142[2U] = 0U;
                    __Vtemp_142[3U] = 0U;
                    __Vtemp_143[0U] = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U];
                    __Vtemp_143[1U] = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U];
                    __Vtemp_143[2U] = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U];
                    __Vtemp_143[3U] = 0U;
                    VL_ADD_W(4, __Vtemp_144, __Vtemp_142, __Vtemp_143);
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U] 
                        = __Vtemp_144[0U];
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                        = __Vtemp_144[1U];
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U] 
                        = __Vtemp_144[2U];
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U] 
                        = (1U & __Vtemp_144[3U]);
                    if ((0U != ((tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                                 | tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U]) 
                                | (1U & tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U])))) {
                        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__tap_range_error = 1U;
                    } else {
                        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[5U] 
                            = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U];
                    }
                }
            }
            if ((6U < (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_count))) {
                tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work 
                    = ((2U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width)
                        ? 0U : 2U);
                tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work = 0U;
                tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[6U] 
                    = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_channel;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[6U] 
                    = (tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_y_work 
                       + VL_EXTENDS_QI(64,32, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work));
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[6U] 
                    = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_x_work;
                if ((((VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[6U]) 
                       & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[6U], (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_h[0U])))) 
                      & VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[6U])) 
                     & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[6U], (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_w[0U]))))) {
                    if ((0U == tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work)) {
                        __Vtemp_149[0U] = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[6U]);
                        __Vtemp_149[1U] = 0U;
                        __Vtemp_149[2U] = 0U;
                        VL_ADD_W(3, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[0U], __Vtemp_149);
                    } else if ((1U == tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work)) {
                        __Vtemp_150[0U] = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[6U]);
                        __Vtemp_150[1U] = 0U;
                        __Vtemp_150[2U] = 0U;
                        VL_ADD_W(3, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[1U], __Vtemp_150);
                    } else if ((2U == tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work)) {
                        __Vtemp_151[0U] = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[6U]);
                        __Vtemp_151[1U] = 0U;
                        __Vtemp_151[2U] = 0U;
                        VL_ADD_W(3, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[2U], __Vtemp_151);
                    } else {
                        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U] = 0U;
                        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U] = 0U;
                        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U] = 0U;
                    }
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask 
                        = (0x00000040U | (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask));
                    __Vtemp_153[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_base[0U];
                    __Vtemp_153[1U] = 0U;
                    __Vtemp_153[2U] = 0U;
                    __Vtemp_153[3U] = 0U;
                    __Vtemp_154[0U] = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U];
                    __Vtemp_154[1U] = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U];
                    __Vtemp_154[2U] = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U];
                    __Vtemp_154[3U] = 0U;
                    VL_ADD_W(4, __Vtemp_155, __Vtemp_153, __Vtemp_154);
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U] 
                        = __Vtemp_155[0U];
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                        = __Vtemp_155[1U];
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U] 
                        = __Vtemp_155[2U];
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U] 
                        = (1U & __Vtemp_155[3U]);
                    if ((0U != ((tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                                 | tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U]) 
                                | (1U & tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U])))) {
                        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__tap_range_error = 1U;
                    } else {
                        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[6U] 
                            = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U];
                    }
                }
            }
            if ((7U < (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_count))) {
                if ((2U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width)) {
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work = 0U;
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work = 0U;
                } else {
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work = 2U;
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work = 1U;
                }
                tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[7U] 
                    = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_channel;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[7U] 
                    = (tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_y_work 
                       + VL_EXTENDS_QI(64,32, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work));
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[7U] 
                    = (tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_x_work 
                       + VL_EXTENDS_QI(64,32, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work));
                if ((((VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[7U]) 
                       & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[7U], (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_h[0U])))) 
                      & VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[7U])) 
                     & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[7U], (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_w[0U]))))) {
                    if ((0U == tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work)) {
                        __Vtemp_160[0U] = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[7U]);
                        __Vtemp_160[1U] = 0U;
                        __Vtemp_160[2U] = 0U;
                        VL_ADD_W(3, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[0U], __Vtemp_160);
                    } else if ((1U == tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work)) {
                        __Vtemp_161[0U] = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[7U]);
                        __Vtemp_161[1U] = 0U;
                        __Vtemp_161[2U] = 0U;
                        VL_ADD_W(3, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[1U], __Vtemp_161);
                    } else if ((2U == tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work)) {
                        __Vtemp_162[0U] = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[7U]);
                        __Vtemp_162[1U] = 0U;
                        __Vtemp_162[2U] = 0U;
                        VL_ADD_W(3, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[2U], __Vtemp_162);
                    } else {
                        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U] = 0U;
                        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U] = 0U;
                        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U] = 0U;
                    }
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask 
                        = (0x00000080U | (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask));
                    __Vtemp_164[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_base[0U];
                    __Vtemp_164[1U] = 0U;
                    __Vtemp_164[2U] = 0U;
                    __Vtemp_164[3U] = 0U;
                    __Vtemp_165[0U] = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U];
                    __Vtemp_165[1U] = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U];
                    __Vtemp_165[2U] = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U];
                    __Vtemp_165[3U] = 0U;
                    VL_ADD_W(4, __Vtemp_166, __Vtemp_164, __Vtemp_165);
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U] 
                        = __Vtemp_166[0U];
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                        = __Vtemp_166[1U];
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U] 
                        = __Vtemp_166[2U];
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U] 
                        = (1U & __Vtemp_166[3U]);
                    if ((0U != ((tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                                 | tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U]) 
                                | (1U & tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U])))) {
                        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__tap_range_error = 1U;
                    } else {
                        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[7U] 
                            = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U];
                    }
                }
            }
            if ((8U < (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_count))) {
                if ((2U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width)) {
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work = 0U;
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work = 0U;
                } else {
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work = 2U;
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work = 2U;
                }
                tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[8U] 
                    = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_channel;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[8U] 
                    = (tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_y_work 
                       + VL_EXTENDS_QI(64,32, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work));
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[8U] 
                    = (tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_x_work 
                       + VL_EXTENDS_QI(64,32, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work));
                if ((((VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[8U]) 
                       & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[8U], (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_h[0U])))) 
                      & VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[8U])) 
                     & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[8U], (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_w[0U]))))) {
                    if ((0U == tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work)) {
                        __Vtemp_171[0U] = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[8U]);
                        __Vtemp_171[1U] = 0U;
                        __Vtemp_171[2U] = 0U;
                        VL_ADD_W(3, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[0U], __Vtemp_171);
                    } else if ((1U == tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work)) {
                        __Vtemp_172[0U] = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[8U]);
                        __Vtemp_172[1U] = 0U;
                        __Vtemp_172[2U] = 0U;
                        VL_ADD_W(3, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[1U], __Vtemp_172);
                    } else if ((2U == tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work)) {
                        __Vtemp_173[0U] = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[8U]);
                        __Vtemp_173[1U] = 0U;
                        __Vtemp_173[2U] = 0U;
                        VL_ADD_W(3, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[2U], __Vtemp_173);
                    } else {
                        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U] = 0U;
                        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U] = 0U;
                        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U] = 0U;
                    }
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask 
                        = (0x00000100U | (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask));
                    __Vtemp_175[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_base[0U];
                    __Vtemp_175[1U] = 0U;
                    __Vtemp_175[2U] = 0U;
                    __Vtemp_175[3U] = 0U;
                    __Vtemp_176[0U] = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U];
                    __Vtemp_176[1U] = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U];
                    __Vtemp_176[2U] = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U];
                    __Vtemp_176[3U] = 0U;
                    VL_ADD_W(4, __Vtemp_177, __Vtemp_175, __Vtemp_176);
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U] 
                        = __Vtemp_177[0U];
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                        = __Vtemp_177[1U];
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U] 
                        = __Vtemp_177[2U];
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U] 
                        = (1U & __Vtemp_177[3U]);
                    if ((0U != ((tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                                 | tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U]) 
                                | (1U & tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U])))) {
                        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__tap_range_error = 1U;
                    } else {
                        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[8U] 
                            = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U];
                    }
                }
            }
            if (tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__tap_range_error) {
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_error_code = 2U;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_output_height = 0ULL;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_output_width = 0ULL;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_count = 0U;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask = 0U;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[0U] = 0U;
                tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[0U] = 0U;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[0U] = 0ULL;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[0U] = 0ULL;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[1U] = 0U;
                tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[1U] = 0U;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[1U] = 0ULL;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[1U] = 0ULL;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[2U] = 0U;
                tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[2U] = 0U;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[2U] = 0ULL;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[2U] = 0ULL;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[3U] = 0U;
                tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[3U] = 0U;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[3U] = 0ULL;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[3U] = 0ULL;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[4U] = 0U;
                tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[4U] = 0U;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[4U] = 0ULL;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[4U] = 0ULL;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[5U] = 0U;
                tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[5U] = 0U;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[5U] = 0ULL;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[5U] = 0ULL;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[6U] = 0U;
                tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[6U] = 0U;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[6U] = 0ULL;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[6U] = 0ULL;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[7U] = 0U;
                tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[7U] = 0U;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[7U] = 0ULL;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[7U] = 0ULL;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[8U] = 0U;
                tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[8U] = 0U;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[8U] = 0ULL;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[8U] = 0ULL;
            }
        }
    }
    if ((1U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_error_code))) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_output_height = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_output_width = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_count = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[0U] = 0U;
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[0U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[0U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[0U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[1U] = 0U;
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[1U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[1U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[1U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[2U] = 0U;
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[2U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[2U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[2U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[3U] = 0U;
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[3U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[3U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[3U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[4U] = 0U;
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[4U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[4U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[4U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[5U] = 0U;
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[5U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[5U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[5U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[6U] = 0U;
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[6U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[6U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[6U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[7U] = 0U;
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[7U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[7U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[7U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[8U] = 0U;
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[8U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[8U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[8U] = 0ULL;
    }
    vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_write 
        = (((4U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__state))
             ? ((~ ((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__state) 
                    >> 1U)) & ((1U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__state))
                                ? (IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__upsample_req_write)
                                : (IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__route_req_write)))
             : (((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__state) 
                 >> 1U) & ((1U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__state))
                            ? (IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__maxpool_req_write)
                            : (IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__conv_req_write)))) 
           & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_valid));
    vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_wstrb 
        = (((4U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__state))
             ? (((1U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__state))
                  ? (IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__upsample_req_wstrb)
                  : (IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__route_req_wstrb)) 
                & (- (IData)((1U & (~ ((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__state) 
                                       >> 1U)))))) : 
            (((1U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__state))
               ? (IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__maxpool_req_wstrb)
               : (IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__conv_req_wstrb)) 
             & (- (IData)((1U & ((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__state) 
                                 >> 1U)))))) & (- (IData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_valid))));
    vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_rstrb 
        = (((4U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__state))
             ? (((1U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__state))
                  ? (IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__upsample_req_rstrb)
                  : (IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__route_req_rstrb)) 
                & (- (IData)((1U & (~ ((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__state) 
                                       >> 1U)))))) : 
            (((1U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__state))
               ? (IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__maxpool_req_rstrb)
               : (IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__conv_req_rstrb)) 
             & (- (IData)((1U & ((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__state) 
                                 >> 1U)))))) & (- (IData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_valid))));
    vlSelfRef.__VdfgRegularize_h6e95ff9d_0_187 = ((0x00adadb7U 
                                                   >= 
                                                   (0x00ffffffU 
                                                    & ((IData)(3U) 
                                                       + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr))) 
                                                  & (0U 
                                                     != vlSelfRef.tb_s2a_network_backend_golden__DOT__feature_byte_valid
                                                     [
                                                     (0x00ffffffU 
                                                      & ((IData)(3U) 
                                                         + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr))]));
    vlSelfRef.__VdfgRegularize_h6e95ff9d_0_188 = ((0x00adadb7U 
                                                   >= 
                                                   (0x00ffffffU 
                                                    & ((IData)(2U) 
                                                       + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr))) 
                                                  & (0U 
                                                     != vlSelfRef.tb_s2a_network_backend_golden__DOT__feature_byte_valid
                                                     [
                                                     (0x00ffffffU 
                                                      & ((IData)(2U) 
                                                         + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr))]));
    vlSelfRef.__VdfgRegularize_h6e95ff9d_0_189 = ((0x00adadb7U 
                                                   >= 
                                                   (0x00ffffffU 
                                                    & ((IData)(1U) 
                                                       + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr))) 
                                                  & (0U 
                                                     != vlSelfRef.tb_s2a_network_backend_golden__DOT__feature_byte_valid
                                                     [
                                                     (0x00ffffffU 
                                                      & ((IData)(1U) 
                                                         + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr))]));
    __VdfgRegularize_h6e95ff9d_0_190 = ((0x00adadb7U 
                                         >= (0x00ffffffU 
                                             & vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0U != vlSelfRef.tb_s2a_network_backend_golden__DOT__feature_byte_valid
                                           [(0x00ffffffU 
                                             & vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)]));
    __VdfgRegularize_h6e95ff9d_0_134 = ((0x01152000U 
                                         <= ((IData)(3U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x011fb000U 
                                           > ((IData)(3U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_135 = ((0x011fb000U 
                                         <= ((IData)(3U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x012a4000U 
                                           > ((IData)(3U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_136 = ((0x012a4000U 
                                         <= ((IData)(3U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x012f8800U 
                                           > ((IData)(3U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_137 = ((0x012f8800U 
                                         <= ((IData)(3U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x0134d000U 
                                           > ((IData)(3U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_138 = ((0x0134d000U 
                                         <= ((IData)(3U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x013a1800U 
                                           > ((IData)(3U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_139 = ((0x013a1800U 
                                         <= ((IData)(3U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x0144a800U 
                                           > ((IData)(3U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_140 = ((0x0144a800U 
                                         <= ((IData)(3U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x014f3800U 
                                           > ((IData)(3U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_141 = ((0x014f3800U 
                                         <= ((IData)(3U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x01645800U 
                                           > ((IData)(3U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_142 = ((0x01645800U 
                                         <= ((IData)(3U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x0169a000U 
                                           > ((IData)(3U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_143 = ((0x0169a000U 
                                         <= ((IData)(3U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x016ee800U 
                                           > ((IData)(3U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_144 = ((0x016ee800U 
                                         <= ((IData)(3U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x01718c00U 
                                           > ((IData)(3U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_145 = ((0x01718c00U 
                                         <= ((IData)(3U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x01743000U 
                                           > ((IData)(3U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_146 = ((0x01743000U 
                                         <= ((IData)(3U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x0176d400U 
                                           > ((IData)(3U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_147 = ((0x0176d400U 
                                         <= ((IData)(3U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x017c1c00U 
                                           > ((IData)(3U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_148 = ((0x017c1c00U 
                                         <= ((IData)(3U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x01816400U 
                                           > ((IData)(3U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_149 = ((0x01816400U 
                                         <= ((IData)(3U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x018bf400U 
                                           > ((IData)(3U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_150 = ((0x018bf400U 
                                         <= ((IData)(3U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x018e9800U 
                                           > ((IData)(3U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_151 = ((0x018e9800U 
                                         <= ((IData)(3U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x01913c00U 
                                           > ((IData)(3U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_152 = ((0x01913c00U 
                                         <= ((IData)(3U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x01928e00U 
                                           > ((IData)(3U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_153 = ((0x01928e00U 
                                         <= ((IData)(3U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x0193e000U 
                                           > ((IData)(3U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_154 = ((0x0193e000U 
                                         <= ((IData)(3U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x01953200U 
                                           > ((IData)(3U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_155 = ((0x01953200U 
                                         <= ((IData)(3U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x0197d600U 
                                           > ((IData)(3U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_156 = ((0x0197d600U 
                                         <= ((IData)(3U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x019a7a00U 
                                           > ((IData)(3U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_157 = ((0x019a7a00U 
                                         <= ((IData)(3U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x019fc200U 
                                           > ((IData)(3U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_158 = ((0x019fc200U 
                                         <= ((IData)(3U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x01a11400U 
                                           > ((IData)(3U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_159 = ((0x01a11400U 
                                         <= ((IData)(3U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x01a26600U 
                                           > ((IData)(3U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_160 = ((0x01a26600U 
                                         <= ((IData)(3U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x01a30f00U 
                                           > ((IData)(3U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_161 = ((0x01a30f00U 
                                         <= ((IData)(3U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x01a46100U 
                                           > ((IData)(3U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_162 = ((0x01a46100U 
                                         <= ((IData)(3U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x01a474ceU 
                                           > ((IData)(3U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_163 = ((0x01a47500U 
                                         <= ((IData)(3U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x01a51e00U 
                                           > ((IData)(3U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_164 = ((0x01a51e00U 
                                         <= ((IData)(3U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x01a57280U 
                                           > ((IData)(3U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_165 = ((0x01a57280U 
                                         <= ((IData)(3U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x01a6c480U 
                                           > ((IData)(3U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_166 = ((0x01a6c480U 
                                         <= ((IData)(3U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x01aaba80U 
                                           > ((IData)(3U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_167 = ((0x01aaba80U 
                                         <= ((IData)(3U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x01ad5e80U 
                                           > ((IData)(3U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_168 = ((0x01ad5e80U 
                                         <= ((IData)(3U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x01adadb8U 
                                           > ((IData)(3U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_182 = (- (IData)((1U 
                                                   & (~ 
                                                      ((0x01000000U 
                                                        <= 
                                                        ((IData)(3U) 
                                                         + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                                       & (0x01152000U 
                                                          > 
                                                          ((IData)(3U) 
                                                           + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)))))));
    __VdfgRegularize_h6e95ff9d_0_98 = ((0x01152000U 
                                        <= ((IData)(2U) 
                                            + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                       & (0x011fb000U 
                                          > ((IData)(2U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_99 = ((0x011fb000U 
                                        <= ((IData)(2U) 
                                            + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                       & (0x012a4000U 
                                          > ((IData)(2U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_100 = ((0x012a4000U 
                                         <= ((IData)(2U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x012f8800U 
                                           > ((IData)(2U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_101 = ((0x012f8800U 
                                         <= ((IData)(2U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x0134d000U 
                                           > ((IData)(2U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_102 = ((0x0134d000U 
                                         <= ((IData)(2U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x013a1800U 
                                           > ((IData)(2U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_103 = ((0x013a1800U 
                                         <= ((IData)(2U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x0144a800U 
                                           > ((IData)(2U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_104 = ((0x0144a800U 
                                         <= ((IData)(2U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x014f3800U 
                                           > ((IData)(2U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_105 = ((0x014f3800U 
                                         <= ((IData)(2U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x01645800U 
                                           > ((IData)(2U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_106 = ((0x01645800U 
                                         <= ((IData)(2U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x0169a000U 
                                           > ((IData)(2U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_107 = ((0x0169a000U 
                                         <= ((IData)(2U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x016ee800U 
                                           > ((IData)(2U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_108 = ((0x016ee800U 
                                         <= ((IData)(2U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x01718c00U 
                                           > ((IData)(2U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_109 = ((0x01718c00U 
                                         <= ((IData)(2U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x01743000U 
                                           > ((IData)(2U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_110 = ((0x01743000U 
                                         <= ((IData)(2U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x0176d400U 
                                           > ((IData)(2U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_111 = ((0x0176d400U 
                                         <= ((IData)(2U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x017c1c00U 
                                           > ((IData)(2U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_112 = ((0x017c1c00U 
                                         <= ((IData)(2U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x01816400U 
                                           > ((IData)(2U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_113 = ((0x01816400U 
                                         <= ((IData)(2U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x018bf400U 
                                           > ((IData)(2U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_114 = ((0x018bf400U 
                                         <= ((IData)(2U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x018e9800U 
                                           > ((IData)(2U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_115 = ((0x018e9800U 
                                         <= ((IData)(2U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x01913c00U 
                                           > ((IData)(2U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_116 = ((0x01913c00U 
                                         <= ((IData)(2U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x01928e00U 
                                           > ((IData)(2U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_117 = ((0x01928e00U 
                                         <= ((IData)(2U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x0193e000U 
                                           > ((IData)(2U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_118 = ((0x0193e000U 
                                         <= ((IData)(2U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x01953200U 
                                           > ((IData)(2U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_119 = ((0x01953200U 
                                         <= ((IData)(2U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x0197d600U 
                                           > ((IData)(2U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_120 = ((0x0197d600U 
                                         <= ((IData)(2U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x019a7a00U 
                                           > ((IData)(2U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_121 = ((0x019a7a00U 
                                         <= ((IData)(2U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x019fc200U 
                                           > ((IData)(2U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_122 = ((0x019fc200U 
                                         <= ((IData)(2U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x01a11400U 
                                           > ((IData)(2U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_123 = ((0x01a11400U 
                                         <= ((IData)(2U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x01a26600U 
                                           > ((IData)(2U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_124 = ((0x01a26600U 
                                         <= ((IData)(2U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x01a30f00U 
                                           > ((IData)(2U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_125 = ((0x01a30f00U 
                                         <= ((IData)(2U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x01a46100U 
                                           > ((IData)(2U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_126 = ((0x01a46100U 
                                         <= ((IData)(2U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x01a474ceU 
                                           > ((IData)(2U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_127 = ((0x01a47500U 
                                         <= ((IData)(2U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x01a51e00U 
                                           > ((IData)(2U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_128 = ((0x01a51e00U 
                                         <= ((IData)(2U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x01a57280U 
                                           > ((IData)(2U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_129 = ((0x01a57280U 
                                         <= ((IData)(2U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x01a6c480U 
                                           > ((IData)(2U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_130 = ((0x01a6c480U 
                                         <= ((IData)(2U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x01aaba80U 
                                           > ((IData)(2U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_131 = ((0x01aaba80U 
                                         <= ((IData)(2U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x01ad5e80U 
                                           > ((IData)(2U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_132 = ((0x01ad5e80U 
                                         <= ((IData)(2U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                        & (0x01adadb8U 
                                           > ((IData)(2U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_183 = (- (IData)((1U 
                                                   & (~ 
                                                      ((0x01000000U 
                                                        <= 
                                                        ((IData)(2U) 
                                                         + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                                       & (0x01152000U 
                                                          > 
                                                          ((IData)(2U) 
                                                           + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)))))));
    __VdfgRegularize_h6e95ff9d_0_63 = ((0x01152000U 
                                        <= ((IData)(1U) 
                                            + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                       & (0x011fb000U 
                                          > ((IData)(1U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_64 = ((0x011fb000U 
                                        <= ((IData)(1U) 
                                            + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                       & (0x012a4000U 
                                          > ((IData)(1U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_65 = ((0x012a4000U 
                                        <= ((IData)(1U) 
                                            + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                       & (0x012f8800U 
                                          > ((IData)(1U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_66 = ((0x012f8800U 
                                        <= ((IData)(1U) 
                                            + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                       & (0x0134d000U 
                                          > ((IData)(1U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_67 = ((0x0134d000U 
                                        <= ((IData)(1U) 
                                            + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                       & (0x013a1800U 
                                          > ((IData)(1U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_68 = ((0x013a1800U 
                                        <= ((IData)(1U) 
                                            + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                       & (0x0144a800U 
                                          > ((IData)(1U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_69 = ((0x0144a800U 
                                        <= ((IData)(1U) 
                                            + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                       & (0x014f3800U 
                                          > ((IData)(1U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_70 = ((0x014f3800U 
                                        <= ((IData)(1U) 
                                            + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                       & (0x01645800U 
                                          > ((IData)(1U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_71 = ((0x01645800U 
                                        <= ((IData)(1U) 
                                            + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                       & (0x0169a000U 
                                          > ((IData)(1U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_72 = ((0x0169a000U 
                                        <= ((IData)(1U) 
                                            + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                       & (0x016ee800U 
                                          > ((IData)(1U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_73 = ((0x016ee800U 
                                        <= ((IData)(1U) 
                                            + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                       & (0x01718c00U 
                                          > ((IData)(1U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_74 = ((0x01718c00U 
                                        <= ((IData)(1U) 
                                            + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                       & (0x01743000U 
                                          > ((IData)(1U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_75 = ((0x01743000U 
                                        <= ((IData)(1U) 
                                            + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                       & (0x0176d400U 
                                          > ((IData)(1U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_76 = ((0x0176d400U 
                                        <= ((IData)(1U) 
                                            + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                       & (0x017c1c00U 
                                          > ((IData)(1U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_77 = ((0x017c1c00U 
                                        <= ((IData)(1U) 
                                            + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                       & (0x01816400U 
                                          > ((IData)(1U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_78 = ((0x01816400U 
                                        <= ((IData)(1U) 
                                            + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                       & (0x018bf400U 
                                          > ((IData)(1U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_79 = ((0x018bf400U 
                                        <= ((IData)(1U) 
                                            + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                       & (0x018e9800U 
                                          > ((IData)(1U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_80 = ((0x018e9800U 
                                        <= ((IData)(1U) 
                                            + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                       & (0x01913c00U 
                                          > ((IData)(1U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_81 = ((0x01913c00U 
                                        <= ((IData)(1U) 
                                            + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                       & (0x01928e00U 
                                          > ((IData)(1U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_82 = ((0x01928e00U 
                                        <= ((IData)(1U) 
                                            + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                       & (0x0193e000U 
                                          > ((IData)(1U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_83 = ((0x0193e000U 
                                        <= ((IData)(1U) 
                                            + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                       & (0x01953200U 
                                          > ((IData)(1U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_84 = ((0x01953200U 
                                        <= ((IData)(1U) 
                                            + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                       & (0x0197d600U 
                                          > ((IData)(1U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_85 = ((0x0197d600U 
                                        <= ((IData)(1U) 
                                            + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                       & (0x019a7a00U 
                                          > ((IData)(1U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_86 = ((0x019a7a00U 
                                        <= ((IData)(1U) 
                                            + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                       & (0x019fc200U 
                                          > ((IData)(1U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_87 = ((0x019fc200U 
                                        <= ((IData)(1U) 
                                            + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                       & (0x01a11400U 
                                          > ((IData)(1U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_88 = ((0x01a11400U 
                                        <= ((IData)(1U) 
                                            + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                       & (0x01a26600U 
                                          > ((IData)(1U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_89 = ((0x01a26600U 
                                        <= ((IData)(1U) 
                                            + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                       & (0x01a30f00U 
                                          > ((IData)(1U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_90 = ((0x01a30f00U 
                                        <= ((IData)(1U) 
                                            + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                       & (0x01a46100U 
                                          > ((IData)(1U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_91 = ((0x01a46100U 
                                        <= ((IData)(1U) 
                                            + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                       & (0x01a474ceU 
                                          > ((IData)(1U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_92 = ((0x01a47500U 
                                        <= ((IData)(1U) 
                                            + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                       & (0x01a51e00U 
                                          > ((IData)(1U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_93 = ((0x01a51e00U 
                                        <= ((IData)(1U) 
                                            + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                       & (0x01a57280U 
                                          > ((IData)(1U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_94 = ((0x01a57280U 
                                        <= ((IData)(1U) 
                                            + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                       & (0x01a6c480U 
                                          > ((IData)(1U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_95 = ((0x01a6c480U 
                                        <= ((IData)(1U) 
                                            + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                       & (0x01aaba80U 
                                          > ((IData)(1U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_96 = ((0x01aaba80U 
                                        <= ((IData)(1U) 
                                            + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                       & (0x01ad5e80U 
                                          > ((IData)(1U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_97 = ((0x01ad5e80U 
                                        <= ((IData)(1U) 
                                            + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                       & (0x01adadb8U 
                                          > ((IData)(1U) 
                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)));
    __VdfgRegularize_h6e95ff9d_0_184 = (- (IData)((1U 
                                                   & (~ 
                                                      ((0x01000000U 
                                                        <= 
                                                        ((IData)(1U) 
                                                         + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                                       & (0x01152000U 
                                                          > 
                                                          ((IData)(1U) 
                                                           + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)))))));
    __VdfgRegularize_h6e95ff9d_0_28 = ((0x01152000U 
                                        <= vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr) 
                                       & (0x011fb000U 
                                          > vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr));
    __VdfgRegularize_h6e95ff9d_0_29 = ((0x011fb000U 
                                        <= vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr) 
                                       & (0x012a4000U 
                                          > vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr));
    __VdfgRegularize_h6e95ff9d_0_30 = ((0x012a4000U 
                                        <= vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr) 
                                       & (0x012f8800U 
                                          > vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr));
    __VdfgRegularize_h6e95ff9d_0_31 = ((0x012f8800U 
                                        <= vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr) 
                                       & (0x0134d000U 
                                          > vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr));
    __VdfgRegularize_h6e95ff9d_0_32 = ((0x0134d000U 
                                        <= vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr) 
                                       & (0x013a1800U 
                                          > vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr));
    __VdfgRegularize_h6e95ff9d_0_33 = ((0x013a1800U 
                                        <= vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr) 
                                       & (0x0144a800U 
                                          > vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr));
    __VdfgRegularize_h6e95ff9d_0_34 = ((0x0144a800U 
                                        <= vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr) 
                                       & (0x014f3800U 
                                          > vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr));
    __VdfgRegularize_h6e95ff9d_0_35 = ((0x014f3800U 
                                        <= vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr) 
                                       & (0x01645800U 
                                          > vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr));
    __VdfgRegularize_h6e95ff9d_0_36 = ((0x01645800U 
                                        <= vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr) 
                                       & (0x0169a000U 
                                          > vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr));
    __VdfgRegularize_h6e95ff9d_0_37 = ((0x0169a000U 
                                        <= vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr) 
                                       & (0x016ee800U 
                                          > vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr));
    __VdfgRegularize_h6e95ff9d_0_38 = ((0x016ee800U 
                                        <= vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr) 
                                       & (0x01718c00U 
                                          > vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr));
    __VdfgRegularize_h6e95ff9d_0_39 = ((0x01718c00U 
                                        <= vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr) 
                                       & (0x01743000U 
                                          > vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr));
    __VdfgRegularize_h6e95ff9d_0_40 = ((0x01743000U 
                                        <= vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr) 
                                       & (0x0176d400U 
                                          > vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr));
    __VdfgRegularize_h6e95ff9d_0_41 = ((0x0176d400U 
                                        <= vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr) 
                                       & (0x017c1c00U 
                                          > vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr));
    __VdfgRegularize_h6e95ff9d_0_42 = ((0x017c1c00U 
                                        <= vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr) 
                                       & (0x01816400U 
                                          > vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr));
    __VdfgRegularize_h6e95ff9d_0_43 = ((0x01816400U 
                                        <= vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr) 
                                       & (0x018bf400U 
                                          > vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr));
    __VdfgRegularize_h6e95ff9d_0_44 = ((0x018bf400U 
                                        <= vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr) 
                                       & (0x018e9800U 
                                          > vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr));
    __VdfgRegularize_h6e95ff9d_0_45 = ((0x018e9800U 
                                        <= vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr) 
                                       & (0x01913c00U 
                                          > vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr));
    __VdfgRegularize_h6e95ff9d_0_46 = ((0x01913c00U 
                                        <= vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr) 
                                       & (0x01928e00U 
                                          > vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr));
    __VdfgRegularize_h6e95ff9d_0_47 = ((0x01928e00U 
                                        <= vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr) 
                                       & (0x0193e000U 
                                          > vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr));
    __VdfgRegularize_h6e95ff9d_0_48 = ((0x0193e000U 
                                        <= vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr) 
                                       & (0x01953200U 
                                          > vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr));
    __VdfgRegularize_h6e95ff9d_0_49 = ((0x01953200U 
                                        <= vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr) 
                                       & (0x0197d600U 
                                          > vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr));
    __VdfgRegularize_h6e95ff9d_0_50 = ((0x0197d600U 
                                        <= vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr) 
                                       & (0x019a7a00U 
                                          > vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr));
    __VdfgRegularize_h6e95ff9d_0_51 = ((0x019a7a00U 
                                        <= vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr) 
                                       & (0x019fc200U 
                                          > vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr));
    __VdfgRegularize_h6e95ff9d_0_52 = ((0x019fc200U 
                                        <= vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr) 
                                       & (0x01a11400U 
                                          > vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr));
    __VdfgRegularize_h6e95ff9d_0_53 = ((0x01a11400U 
                                        <= vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr) 
                                       & (0x01a26600U 
                                          > vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr));
    __VdfgRegularize_h6e95ff9d_0_54 = ((0x01a26600U 
                                        <= vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr) 
                                       & (0x01a30f00U 
                                          > vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr));
    __VdfgRegularize_h6e95ff9d_0_55 = ((0x01a30f00U 
                                        <= vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr) 
                                       & (0x01a46100U 
                                          > vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr));
    __VdfgRegularize_h6e95ff9d_0_56 = ((0x01a46100U 
                                        <= vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr) 
                                       & (0x01a474ceU 
                                          > vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr));
    __VdfgRegularize_h6e95ff9d_0_57 = ((0x01a47500U 
                                        <= vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr) 
                                       & (0x01a51e00U 
                                          > vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr));
    __VdfgRegularize_h6e95ff9d_0_58 = ((0x01a51e00U 
                                        <= vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr) 
                                       & (0x01a57280U 
                                          > vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr));
    __VdfgRegularize_h6e95ff9d_0_59 = ((0x01a57280U 
                                        <= vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr) 
                                       & (0x01a6c480U 
                                          > vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr));
    __VdfgRegularize_h6e95ff9d_0_60 = ((0x01a6c480U 
                                        <= vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr) 
                                       & (0x01aaba80U 
                                          > vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr));
    __VdfgRegularize_h6e95ff9d_0_61 = ((0x01aaba80U 
                                        <= vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr) 
                                       & (0x01ad5e80U 
                                          > vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr));
    __VdfgRegularize_h6e95ff9d_0_62 = ((0x01ad5e80U 
                                        <= vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr) 
                                       & (0x01adadb8U 
                                          > vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr));
    __VdfgRegularize_h6e95ff9d_0_186 = (- (IData)((1U 
                                                   & (~ 
                                                      ((0x01000000U 
                                                        <= vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr) 
                                                       & (0x01152000U 
                                                          > vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr))))));
    __Vtemp_183[0U] = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__output_offset_work);
    __Vtemp_183[1U] = (IData)((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__output_offset_work 
                               >> 0x00000020U));
    __Vtemp_183[2U] = 0U;
    VL_ADD_W(3, __Vtemp_184, __Vtemp_183, __VdfgRegularize_h6e95ff9d_0_196);
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__output_address_work[0U] 
        = __Vtemp_184[0U];
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__output_address_work[1U] 
        = __Vtemp_184[1U];
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__output_address_work[2U] 
        = (1U & __Vtemp_184[2U]);
    __Vtemp_186[0U] = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_offset_work);
    __Vtemp_186[1U] = (IData)((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_offset_work 
                               >> 0x00000020U));
    __Vtemp_186[2U] = 0U;
    VL_ADD_W(3, __Vtemp_187, __Vtemp_186, __VdfgRegularize_h6e95ff9d_0_196);
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_address_work[0U] 
        = __Vtemp_187[0U];
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_address_work[1U] 
        = __Vtemp_187[1U];
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_address_work[2U] 
        = (1U & __Vtemp_187[2U]);
    __VdfgRegularize_h6e95ff9d_0_194 = (IData)((2U 
                                                == 
                                                (3U 
                                                 & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_rstrb))));
    vlSelfRef.__VdfgRegularize_h6e95ff9d_0_17 = (((
                                                   (0x00100000U 
                                                    <= 
                                                    ((IData)(3U) 
                                                     + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                                   & (0x006a12fcU 
                                                      > 
                                                      ((IData)(3U) 
                                                       + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)))
                                                   ? 1U
                                                   : 
                                                  ((IData)(__VdfgRegularize_h6e95ff9d_0_168)
                                                    ? 0x00000026U
                                                    : 
                                                   ((IData)(__VdfgRegularize_h6e95ff9d_0_167)
                                                     ? 0x00000025U
                                                     : 
                                                    ((IData)(__VdfgRegularize_h6e95ff9d_0_166)
                                                      ? 0x00000024U
                                                      : 
                                                     ((IData)(__VdfgRegularize_h6e95ff9d_0_165)
                                                       ? 0x00000023U
                                                       : 
                                                      ((IData)(__VdfgRegularize_h6e95ff9d_0_164)
                                                        ? 0x00000022U
                                                        : 
                                                       ((IData)(__VdfgRegularize_h6e95ff9d_0_163)
                                                         ? 0x00000021U
                                                         : 
                                                        ((IData)(__VdfgRegularize_h6e95ff9d_0_162)
                                                          ? 0x0000001fU
                                                          : 
                                                         ((IData)(__VdfgRegularize_h6e95ff9d_0_161)
                                                           ? 0x0000001eU
                                                           : 
                                                          ((IData)(__VdfgRegularize_h6e95ff9d_0_160)
                                                            ? 0x0000001dU
                                                            : 
                                                           ((IData)(__VdfgRegularize_h6e95ff9d_0_159)
                                                             ? 0x0000001cU
                                                             : 
                                                            ((IData)(__VdfgRegularize_h6e95ff9d_0_158)
                                                              ? 0x0000001bU
                                                              : 
                                                             ((IData)(__VdfgRegularize_h6e95ff9d_0_157)
                                                               ? 0x0000001aU
                                                               : 
                                                              ((IData)(__VdfgRegularize_h6e95ff9d_0_156)
                                                                ? 0x00000019U
                                                                : 
                                                               ((IData)(__VdfgRegularize_h6e95ff9d_0_155)
                                                                 ? 0x00000018U
                                                                 : 
                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_154)
                                                                  ? 0x00000017U
                                                                  : 
                                                                 ((IData)(__VdfgRegularize_h6e95ff9d_0_153)
                                                                   ? 0x00000016U
                                                                   : 
                                                                  ((IData)(__VdfgRegularize_h6e95ff9d_0_152)
                                                                    ? 0x00000015U
                                                                    : 
                                                                   ((IData)(__VdfgRegularize_h6e95ff9d_0_151)
                                                                     ? 0x00000014U
                                                                     : 
                                                                    ((IData)(__VdfgRegularize_h6e95ff9d_0_150)
                                                                      ? 0x00000013U
                                                                      : 
                                                                     ((IData)(__VdfgRegularize_h6e95ff9d_0_149)
                                                                       ? 0x00000012U
                                                                       : 
                                                                      ((IData)(__VdfgRegularize_h6e95ff9d_0_148)
                                                                        ? 0x00000011U
                                                                        : 
                                                                       ((IData)(__VdfgRegularize_h6e95ff9d_0_147)
                                                                         ? 0x00000010U
                                                                         : 
                                                                        ((IData)(__VdfgRegularize_h6e95ff9d_0_146)
                                                                          ? 0x0000000fU
                                                                          : 
                                                                         ((IData)(__VdfgRegularize_h6e95ff9d_0_145)
                                                                           ? 0x0000000eU
                                                                           : 
                                                                          ((IData)(__VdfgRegularize_h6e95ff9d_0_144)
                                                                            ? 0x0000000dU
                                                                            : 
                                                                           ((IData)(__VdfgRegularize_h6e95ff9d_0_143)
                                                                             ? 0x0000000cU
                                                                             : 
                                                                            ((IData)(__VdfgRegularize_h6e95ff9d_0_142)
                                                                              ? 0x0000000bU
                                                                              : 
                                                                             ((IData)(__VdfgRegularize_h6e95ff9d_0_141)
                                                                               ? 0x0000000aU
                                                                               : 
                                                                              ((IData)(__VdfgRegularize_h6e95ff9d_0_140)
                                                                                ? 9U
                                                                                : 
                                                                               ((IData)(__VdfgRegularize_h6e95ff9d_0_139)
                                                                                 ? 8U
                                                                                 : 
                                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_138)
                                                                                 ? 7U
                                                                                 : 
                                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_137)
                                                                                 ? 6U
                                                                                 : 
                                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_136)
                                                                                 ? 5U
                                                                                 : 
                                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_135)
                                                                                 ? 4U
                                                                                 : 
                                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_134)
                                                                                 ? 3U
                                                                                 : 
                                                                                (2U 
                                                                                | __VdfgRegularize_h6e95ff9d_0_182))))))))))))))))))))))))))))))))))))) 
                                                 & (- (IData)(
                                                              (0x0007ec00U 
                                                               <= 
                                                               ((IData)(3U) 
                                                                + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)))));
    vlSelfRef.__VdfgRegularize_h6e95ff9d_0_10 = (((
                                                   (0x00100000U 
                                                    <= 
                                                    ((IData)(2U) 
                                                     + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                                   & (0x006a12fcU 
                                                      > 
                                                      ((IData)(2U) 
                                                       + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)))
                                                   ? 1U
                                                   : 
                                                  ((IData)(__VdfgRegularize_h6e95ff9d_0_132)
                                                    ? 0x00000026U
                                                    : 
                                                   ((IData)(__VdfgRegularize_h6e95ff9d_0_131)
                                                     ? 0x00000025U
                                                     : 
                                                    ((IData)(__VdfgRegularize_h6e95ff9d_0_130)
                                                      ? 0x00000024U
                                                      : 
                                                     ((IData)(__VdfgRegularize_h6e95ff9d_0_129)
                                                       ? 0x00000023U
                                                       : 
                                                      ((IData)(__VdfgRegularize_h6e95ff9d_0_128)
                                                        ? 0x00000022U
                                                        : 
                                                       ((IData)(__VdfgRegularize_h6e95ff9d_0_127)
                                                         ? 0x00000021U
                                                         : 
                                                        ((IData)(__VdfgRegularize_h6e95ff9d_0_126)
                                                          ? 0x0000001fU
                                                          : 
                                                         ((IData)(__VdfgRegularize_h6e95ff9d_0_125)
                                                           ? 0x0000001eU
                                                           : 
                                                          ((IData)(__VdfgRegularize_h6e95ff9d_0_124)
                                                            ? 0x0000001dU
                                                            : 
                                                           ((IData)(__VdfgRegularize_h6e95ff9d_0_123)
                                                             ? 0x0000001cU
                                                             : 
                                                            ((IData)(__VdfgRegularize_h6e95ff9d_0_122)
                                                              ? 0x0000001bU
                                                              : 
                                                             ((IData)(__VdfgRegularize_h6e95ff9d_0_121)
                                                               ? 0x0000001aU
                                                               : 
                                                              ((IData)(__VdfgRegularize_h6e95ff9d_0_120)
                                                                ? 0x00000019U
                                                                : 
                                                               ((IData)(__VdfgRegularize_h6e95ff9d_0_119)
                                                                 ? 0x00000018U
                                                                 : 
                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_118)
                                                                  ? 0x00000017U
                                                                  : 
                                                                 ((IData)(__VdfgRegularize_h6e95ff9d_0_117)
                                                                   ? 0x00000016U
                                                                   : 
                                                                  ((IData)(__VdfgRegularize_h6e95ff9d_0_116)
                                                                    ? 0x00000015U
                                                                    : 
                                                                   ((IData)(__VdfgRegularize_h6e95ff9d_0_115)
                                                                     ? 0x00000014U
                                                                     : 
                                                                    ((IData)(__VdfgRegularize_h6e95ff9d_0_114)
                                                                      ? 0x00000013U
                                                                      : 
                                                                     ((IData)(__VdfgRegularize_h6e95ff9d_0_113)
                                                                       ? 0x00000012U
                                                                       : 
                                                                      ((IData)(__VdfgRegularize_h6e95ff9d_0_112)
                                                                        ? 0x00000011U
                                                                        : 
                                                                       ((IData)(__VdfgRegularize_h6e95ff9d_0_111)
                                                                         ? 0x00000010U
                                                                         : 
                                                                        ((IData)(__VdfgRegularize_h6e95ff9d_0_110)
                                                                          ? 0x0000000fU
                                                                          : 
                                                                         ((IData)(__VdfgRegularize_h6e95ff9d_0_109)
                                                                           ? 0x0000000eU
                                                                           : 
                                                                          ((IData)(__VdfgRegularize_h6e95ff9d_0_108)
                                                                            ? 0x0000000dU
                                                                            : 
                                                                           ((IData)(__VdfgRegularize_h6e95ff9d_0_107)
                                                                             ? 0x0000000cU
                                                                             : 
                                                                            ((IData)(__VdfgRegularize_h6e95ff9d_0_106)
                                                                              ? 0x0000000bU
                                                                              : 
                                                                             ((IData)(__VdfgRegularize_h6e95ff9d_0_105)
                                                                               ? 0x0000000aU
                                                                               : 
                                                                              ((IData)(__VdfgRegularize_h6e95ff9d_0_104)
                                                                                ? 9U
                                                                                : 
                                                                               ((IData)(__VdfgRegularize_h6e95ff9d_0_103)
                                                                                 ? 8U
                                                                                 : 
                                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_102)
                                                                                 ? 7U
                                                                                 : 
                                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_101)
                                                                                 ? 6U
                                                                                 : 
                                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_100)
                                                                                 ? 5U
                                                                                 : 
                                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_99)
                                                                                 ? 4U
                                                                                 : 
                                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_98)
                                                                                 ? 3U
                                                                                 : 
                                                                                (2U 
                                                                                | __VdfgRegularize_h6e95ff9d_0_183))))))))))))))))))))))))))))))))))))) 
                                                 & (- (IData)(
                                                              (0x0007ec00U 
                                                               <= 
                                                               ((IData)(2U) 
                                                                + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)))));
    vlSelfRef.__VdfgRegularize_h6e95ff9d_0_11 = (((
                                                   (0x00100000U 
                                                    <= 
                                                    ((IData)(1U) 
                                                     + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                                   & (0x006a12fcU 
                                                      > 
                                                      ((IData)(1U) 
                                                       + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)))
                                                   ? 1U
                                                   : 
                                                  ((IData)(__VdfgRegularize_h6e95ff9d_0_97)
                                                    ? 0x00000026U
                                                    : 
                                                   ((IData)(__VdfgRegularize_h6e95ff9d_0_96)
                                                     ? 0x00000025U
                                                     : 
                                                    ((IData)(__VdfgRegularize_h6e95ff9d_0_95)
                                                      ? 0x00000024U
                                                      : 
                                                     ((IData)(__VdfgRegularize_h6e95ff9d_0_94)
                                                       ? 0x00000023U
                                                       : 
                                                      ((IData)(__VdfgRegularize_h6e95ff9d_0_93)
                                                        ? 0x00000022U
                                                        : 
                                                       ((IData)(__VdfgRegularize_h6e95ff9d_0_92)
                                                         ? 0x00000021U
                                                         : 
                                                        ((IData)(__VdfgRegularize_h6e95ff9d_0_91)
                                                          ? 0x0000001fU
                                                          : 
                                                         ((IData)(__VdfgRegularize_h6e95ff9d_0_90)
                                                           ? 0x0000001eU
                                                           : 
                                                          ((IData)(__VdfgRegularize_h6e95ff9d_0_89)
                                                            ? 0x0000001dU
                                                            : 
                                                           ((IData)(__VdfgRegularize_h6e95ff9d_0_88)
                                                             ? 0x0000001cU
                                                             : 
                                                            ((IData)(__VdfgRegularize_h6e95ff9d_0_87)
                                                              ? 0x0000001bU
                                                              : 
                                                             ((IData)(__VdfgRegularize_h6e95ff9d_0_86)
                                                               ? 0x0000001aU
                                                               : 
                                                              ((IData)(__VdfgRegularize_h6e95ff9d_0_85)
                                                                ? 0x00000019U
                                                                : 
                                                               ((IData)(__VdfgRegularize_h6e95ff9d_0_84)
                                                                 ? 0x00000018U
                                                                 : 
                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_83)
                                                                  ? 0x00000017U
                                                                  : 
                                                                 ((IData)(__VdfgRegularize_h6e95ff9d_0_82)
                                                                   ? 0x00000016U
                                                                   : 
                                                                  ((IData)(__VdfgRegularize_h6e95ff9d_0_81)
                                                                    ? 0x00000015U
                                                                    : 
                                                                   ((IData)(__VdfgRegularize_h6e95ff9d_0_80)
                                                                     ? 0x00000014U
                                                                     : 
                                                                    ((IData)(__VdfgRegularize_h6e95ff9d_0_79)
                                                                      ? 0x00000013U
                                                                      : 
                                                                     ((IData)(__VdfgRegularize_h6e95ff9d_0_78)
                                                                       ? 0x00000012U
                                                                       : 
                                                                      ((IData)(__VdfgRegularize_h6e95ff9d_0_77)
                                                                        ? 0x00000011U
                                                                        : 
                                                                       ((IData)(__VdfgRegularize_h6e95ff9d_0_76)
                                                                         ? 0x00000010U
                                                                         : 
                                                                        ((IData)(__VdfgRegularize_h6e95ff9d_0_75)
                                                                          ? 0x0000000fU
                                                                          : 
                                                                         ((IData)(__VdfgRegularize_h6e95ff9d_0_74)
                                                                           ? 0x0000000eU
                                                                           : 
                                                                          ((IData)(__VdfgRegularize_h6e95ff9d_0_73)
                                                                            ? 0x0000000dU
                                                                            : 
                                                                           ((IData)(__VdfgRegularize_h6e95ff9d_0_72)
                                                                             ? 0x0000000cU
                                                                             : 
                                                                            ((IData)(__VdfgRegularize_h6e95ff9d_0_71)
                                                                              ? 0x0000000bU
                                                                              : 
                                                                             ((IData)(__VdfgRegularize_h6e95ff9d_0_70)
                                                                               ? 0x0000000aU
                                                                               : 
                                                                              ((IData)(__VdfgRegularize_h6e95ff9d_0_69)
                                                                                ? 9U
                                                                                : 
                                                                               ((IData)(__VdfgRegularize_h6e95ff9d_0_68)
                                                                                 ? 8U
                                                                                 : 
                                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_67)
                                                                                 ? 7U
                                                                                 : 
                                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_66)
                                                                                 ? 6U
                                                                                 : 
                                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_65)
                                                                                 ? 5U
                                                                                 : 
                                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_64)
                                                                                 ? 4U
                                                                                 : 
                                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_63)
                                                                                 ? 3U
                                                                                 : 
                                                                                (2U 
                                                                                | __VdfgRegularize_h6e95ff9d_0_184))))))))))))))))))))))))))))))))))))) 
                                                 & (- (IData)(
                                                              (0x0007ec00U 
                                                               <= 
                                                               ((IData)(1U) 
                                                                + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)))));
    __VdfgRegularize_h6e95ff9d_0_185 = (2U & (- (IData)(
                                                        ((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_wstrb) 
                                                         & VL_GTS_III(32, 0U, 
                                                                      ((IData)(__VdfgRegularize_h6e95ff9d_0_62)
                                                                        ? 0x00000024U
                                                                        : 
                                                                       ((IData)(__VdfgRegularize_h6e95ff9d_0_61)
                                                                         ? 0x00000023U
                                                                         : 
                                                                        ((IData)(__VdfgRegularize_h6e95ff9d_0_60)
                                                                          ? 0x00000022U
                                                                          : 
                                                                         ((IData)(__VdfgRegularize_h6e95ff9d_0_59)
                                                                           ? 0x00000021U
                                                                           : 
                                                                          ((IData)(__VdfgRegularize_h6e95ff9d_0_58)
                                                                            ? 0x00000020U
                                                                            : 
                                                                           ((IData)(__VdfgRegularize_h6e95ff9d_0_57)
                                                                             ? 0x0000001fU
                                                                             : 
                                                                            ((IData)(__VdfgRegularize_h6e95ff9d_0_56)
                                                                              ? 0x0000001dU
                                                                              : 
                                                                             ((IData)(__VdfgRegularize_h6e95ff9d_0_55)
                                                                               ? 0x0000001cU
                                                                               : 
                                                                              ((IData)(__VdfgRegularize_h6e95ff9d_0_54)
                                                                                ? 0x0000001bU
                                                                                : 
                                                                               ((IData)(__VdfgRegularize_h6e95ff9d_0_53)
                                                                                 ? 0x0000001aU
                                                                                 : 
                                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_52)
                                                                                 ? 0x00000019U
                                                                                 : 
                                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_51)
                                                                                 ? 0x00000018U
                                                                                 : 
                                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_50)
                                                                                 ? 0x00000017U
                                                                                 : 
                                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_49)
                                                                                 ? 0x00000016U
                                                                                 : 
                                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_48)
                                                                                 ? 0x00000015U
                                                                                 : 
                                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_47)
                                                                                 ? 0x00000014U
                                                                                 : 
                                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_46)
                                                                                 ? 0x00000013U
                                                                                 : 
                                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_45)
                                                                                 ? 0x00000012U
                                                                                 : 
                                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_44)
                                                                                 ? 0x00000011U
                                                                                 : 
                                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_43)
                                                                                 ? 0x00000010U
                                                                                 : 
                                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_42)
                                                                                 ? 0x0000000fU
                                                                                 : 
                                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_41)
                                                                                 ? 0x0000000eU
                                                                                 : 
                                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_40)
                                                                                 ? 0x0000000dU
                                                                                 : 
                                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_39)
                                                                                 ? 0x0000000cU
                                                                                 : 
                                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_38)
                                                                                 ? 0x0000000bU
                                                                                 : 
                                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_37)
                                                                                 ? 0x0000000aU
                                                                                 : 
                                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_36)
                                                                                 ? 9U
                                                                                 : 
                                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_35)
                                                                                 ? 8U
                                                                                 : 
                                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_34)
                                                                                 ? 7U
                                                                                 : 
                                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_33)
                                                                                 ? 6U
                                                                                 : 
                                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_32)
                                                                                 ? 5U
                                                                                 : 
                                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_31)
                                                                                 ? 4U
                                                                                 : 
                                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_30)
                                                                                 ? 3U
                                                                                 : 
                                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_29)
                                                                                 ? 2U
                                                                                 : 
                                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_28)
                                                                                 ? 1U
                                                                                 : __VdfgRegularize_h6e95ff9d_0_186))))))))))))))))))))))))))))))))))))))));
    __VdfgRegularize_h6e95ff9d_0_18 = ((((0x00100000U 
                                          <= vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr) 
                                         & (0x006a12fcU 
                                            > vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr))
                                         ? 1U : ((IData)(__VdfgRegularize_h6e95ff9d_0_62)
                                                  ? 0x00000026U
                                                  : 
                                                 ((IData)(__VdfgRegularize_h6e95ff9d_0_61)
                                                   ? 0x00000025U
                                                   : 
                                                  ((IData)(__VdfgRegularize_h6e95ff9d_0_60)
                                                    ? 0x00000024U
                                                    : 
                                                   ((IData)(__VdfgRegularize_h6e95ff9d_0_59)
                                                     ? 0x00000023U
                                                     : 
                                                    ((IData)(__VdfgRegularize_h6e95ff9d_0_58)
                                                      ? 0x00000022U
                                                      : 
                                                     ((IData)(__VdfgRegularize_h6e95ff9d_0_57)
                                                       ? 0x00000021U
                                                       : 
                                                      ((IData)(__VdfgRegularize_h6e95ff9d_0_56)
                                                        ? 0x0000001fU
                                                        : 
                                                       ((IData)(__VdfgRegularize_h6e95ff9d_0_55)
                                                         ? 0x0000001eU
                                                         : 
                                                        ((IData)(__VdfgRegularize_h6e95ff9d_0_54)
                                                          ? 0x0000001dU
                                                          : 
                                                         ((IData)(__VdfgRegularize_h6e95ff9d_0_53)
                                                           ? 0x0000001cU
                                                           : 
                                                          ((IData)(__VdfgRegularize_h6e95ff9d_0_52)
                                                            ? 0x0000001bU
                                                            : 
                                                           ((IData)(__VdfgRegularize_h6e95ff9d_0_51)
                                                             ? 0x0000001aU
                                                             : 
                                                            ((IData)(__VdfgRegularize_h6e95ff9d_0_50)
                                                              ? 0x00000019U
                                                              : 
                                                             ((IData)(__VdfgRegularize_h6e95ff9d_0_49)
                                                               ? 0x00000018U
                                                               : 
                                                              ((IData)(__VdfgRegularize_h6e95ff9d_0_48)
                                                                ? 0x00000017U
                                                                : 
                                                               ((IData)(__VdfgRegularize_h6e95ff9d_0_47)
                                                                 ? 0x00000016U
                                                                 : 
                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_46)
                                                                  ? 0x00000015U
                                                                  : 
                                                                 ((IData)(__VdfgRegularize_h6e95ff9d_0_45)
                                                                   ? 0x00000014U
                                                                   : 
                                                                  ((IData)(__VdfgRegularize_h6e95ff9d_0_44)
                                                                    ? 0x00000013U
                                                                    : 
                                                                   ((IData)(__VdfgRegularize_h6e95ff9d_0_43)
                                                                     ? 0x00000012U
                                                                     : 
                                                                    ((IData)(__VdfgRegularize_h6e95ff9d_0_42)
                                                                      ? 0x00000011U
                                                                      : 
                                                                     ((IData)(__VdfgRegularize_h6e95ff9d_0_41)
                                                                       ? 0x00000010U
                                                                       : 
                                                                      ((IData)(__VdfgRegularize_h6e95ff9d_0_40)
                                                                        ? 0x0000000fU
                                                                        : 
                                                                       ((IData)(__VdfgRegularize_h6e95ff9d_0_39)
                                                                         ? 0x0000000eU
                                                                         : 
                                                                        ((IData)(__VdfgRegularize_h6e95ff9d_0_38)
                                                                          ? 0x0000000dU
                                                                          : 
                                                                         ((IData)(__VdfgRegularize_h6e95ff9d_0_37)
                                                                           ? 0x0000000cU
                                                                           : 
                                                                          ((IData)(__VdfgRegularize_h6e95ff9d_0_36)
                                                                            ? 0x0000000bU
                                                                            : 
                                                                           ((IData)(__VdfgRegularize_h6e95ff9d_0_35)
                                                                             ? 0x0000000aU
                                                                             : 
                                                                            ((IData)(__VdfgRegularize_h6e95ff9d_0_34)
                                                                              ? 9U
                                                                              : 
                                                                             ((IData)(__VdfgRegularize_h6e95ff9d_0_33)
                                                                               ? 8U
                                                                               : 
                                                                              ((IData)(__VdfgRegularize_h6e95ff9d_0_32)
                                                                                ? 7U
                                                                                : 
                                                                               ((IData)(__VdfgRegularize_h6e95ff9d_0_31)
                                                                                 ? 6U
                                                                                 : 
                                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_30)
                                                                                 ? 5U
                                                                                 : 
                                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_29)
                                                                                 ? 4U
                                                                                 : 
                                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_28)
                                                                                 ? 3U
                                                                                 : 
                                                                                (2U 
                                                                                | __VdfgRegularize_h6e95ff9d_0_186))))))))))))))))))))))))))))))))))))) 
                                       & (- (IData)(
                                                    (0x0007ec00U 
                                                     <= vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr))));
    __VdfgRegularize_h6e95ff9d_0_195 = (1U & ((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_rstrb) 
                                              | (IData)(__VdfgRegularize_h6e95ff9d_0_194)));
    __VdfgRegularize_h6e95ff9d_0_177 = ((2U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_wstrb))
                                         ? (VL_GTS_III(32, 0U, 
                                                       ((IData)(__VdfgRegularize_h6e95ff9d_0_97)
                                                         ? 0x00000024U
                                                         : 
                                                        ((IData)(__VdfgRegularize_h6e95ff9d_0_96)
                                                          ? 0x00000023U
                                                          : 
                                                         ((IData)(__VdfgRegularize_h6e95ff9d_0_95)
                                                           ? 0x00000022U
                                                           : 
                                                          ((IData)(__VdfgRegularize_h6e95ff9d_0_94)
                                                            ? 0x00000021U
                                                            : 
                                                           ((IData)(__VdfgRegularize_h6e95ff9d_0_93)
                                                             ? 0x00000020U
                                                             : 
                                                            ((IData)(__VdfgRegularize_h6e95ff9d_0_92)
                                                              ? 0x0000001fU
                                                              : 
                                                             ((IData)(__VdfgRegularize_h6e95ff9d_0_91)
                                                               ? 0x0000001dU
                                                               : 
                                                              ((IData)(__VdfgRegularize_h6e95ff9d_0_90)
                                                                ? 0x0000001cU
                                                                : 
                                                               ((IData)(__VdfgRegularize_h6e95ff9d_0_89)
                                                                 ? 0x0000001bU
                                                                 : 
                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_88)
                                                                  ? 0x0000001aU
                                                                  : 
                                                                 ((IData)(__VdfgRegularize_h6e95ff9d_0_87)
                                                                   ? 0x00000019U
                                                                   : 
                                                                  ((IData)(__VdfgRegularize_h6e95ff9d_0_86)
                                                                    ? 0x00000018U
                                                                    : 
                                                                   ((IData)(__VdfgRegularize_h6e95ff9d_0_85)
                                                                     ? 0x00000017U
                                                                     : 
                                                                    ((IData)(__VdfgRegularize_h6e95ff9d_0_84)
                                                                      ? 0x00000016U
                                                                      : 
                                                                     ((IData)(__VdfgRegularize_h6e95ff9d_0_83)
                                                                       ? 0x00000015U
                                                                       : 
                                                                      ((IData)(__VdfgRegularize_h6e95ff9d_0_82)
                                                                        ? 0x00000014U
                                                                        : 
                                                                       ((IData)(__VdfgRegularize_h6e95ff9d_0_81)
                                                                         ? 0x00000013U
                                                                         : 
                                                                        ((IData)(__VdfgRegularize_h6e95ff9d_0_80)
                                                                          ? 0x00000012U
                                                                          : 
                                                                         ((IData)(__VdfgRegularize_h6e95ff9d_0_79)
                                                                           ? 0x00000011U
                                                                           : 
                                                                          ((IData)(__VdfgRegularize_h6e95ff9d_0_78)
                                                                            ? 0x00000010U
                                                                            : 
                                                                           ((IData)(__VdfgRegularize_h6e95ff9d_0_77)
                                                                             ? 0x0000000fU
                                                                             : 
                                                                            ((IData)(__VdfgRegularize_h6e95ff9d_0_76)
                                                                              ? 0x0000000eU
                                                                              : 
                                                                             ((IData)(__VdfgRegularize_h6e95ff9d_0_75)
                                                                               ? 0x0000000dU
                                                                               : 
                                                                              ((IData)(__VdfgRegularize_h6e95ff9d_0_74)
                                                                                ? 0x0000000cU
                                                                                : 
                                                                               ((IData)(__VdfgRegularize_h6e95ff9d_0_73)
                                                                                 ? 0x0000000bU
                                                                                 : 
                                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_72)
                                                                                 ? 0x0000000aU
                                                                                 : 
                                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_71)
                                                                                 ? 9U
                                                                                 : 
                                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_70)
                                                                                 ? 8U
                                                                                 : 
                                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_69)
                                                                                 ? 7U
                                                                                 : 
                                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_68)
                                                                                 ? 6U
                                                                                 : 
                                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_67)
                                                                                 ? 5U
                                                                                 : 
                                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_66)
                                                                                 ? 4U
                                                                                 : 
                                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_65)
                                                                                 ? 3U
                                                                                 : 
                                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_64)
                                                                                 ? 2U
                                                                                 : 
                                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_63)
                                                                                 ? 1U
                                                                                 : __VdfgRegularize_h6e95ff9d_0_184))))))))))))))))))))))))))))))))))))
                                             ? 2U : (IData)(__VdfgRegularize_h6e95ff9d_0_185))
                                         : (IData)(__VdfgRegularize_h6e95ff9d_0_185));
    vlSelfRef.__VdfgRegularize_h6e95ff9d_0_16 = (((0U 
                                                   == __VdfgRegularize_h6e95ff9d_0_18)
                                                   ? 
                                                  (vlSelfRef.tb_s2a_network_backend_golden__DOT__input_bytes
                                                   [
                                                   (0x0007ffffU 
                                                    & vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)] 
                                                   & (- (IData)(
                                                                (0x0007ebffU 
                                                                 >= 
                                                                 (0x0007ffffU 
                                                                  & vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)))))
                                                   : 
                                                  ((1U 
                                                    == __VdfgRegularize_h6e95ff9d_0_18)
                                                    ? 
                                                   (vlSelfRef.tb_s2a_network_backend_golden__DOT__weight_bytes
                                                    [
                                                    (0x007fffffU 
                                                     & (vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr 
                                                        - (IData)(0x00100000U)))] 
                                                    & (- (IData)(
                                                                 (0x005a12fbU 
                                                                  >= 
                                                                  (0x007fffffU 
                                                                   & (vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr 
                                                                      - (IData)(0x00100000U)))))))
                                                    : 
                                                   (vlSelfRef.tb_s2a_network_backend_golden__DOT__feature_bytes
                                                    [
                                                    (0x00ffffffU 
                                                     & vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)] 
                                                    & (- (IData)((IData)(__VdfgRegularize_h6e95ff9d_0_190)))))) 
                                                 & (- (IData)(
                                                              (1U 
                                                               & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_rstrb)))));
    __VdfgRegularize_h6e95ff9d_0_26 = (2U & ((- (IData)(
                                                        VL_GTS_III(32, 0U, __VdfgRegularize_h6e95ff9d_0_18))) 
                                             & (- (IData)(
                                                          (1U 
                                                           & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_rstrb))))));
    __VdfgRegularize_h6e95ff9d_0_12 = (__VdfgRegularize_h6e95ff9d_0_18 
                                       | ((- (IData)(
                                                     (1U 
                                                      & (~ (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_rstrb))))) 
                                          | (- (IData)(
                                                       VL_GTS_III(32, 0U, __VdfgRegularize_h6e95ff9d_0_18)))));
    __VdfgRegularize_h6e95ff9d_0_193 = (1U & ((~ (IData)(__VdfgRegularize_h6e95ff9d_0_195)) 
                                              & ((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_rstrb) 
                                                 >> 2U)));
    __VdfgRegularize_h6e95ff9d_0_178 = ((4U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_wstrb))
                                         ? (VL_GTS_III(32, 0U, 
                                                       ((IData)(__VdfgRegularize_h6e95ff9d_0_132)
                                                         ? 0x00000024U
                                                         : 
                                                        ((IData)(__VdfgRegularize_h6e95ff9d_0_131)
                                                          ? 0x00000023U
                                                          : 
                                                         ((IData)(__VdfgRegularize_h6e95ff9d_0_130)
                                                           ? 0x00000022U
                                                           : 
                                                          ((IData)(__VdfgRegularize_h6e95ff9d_0_129)
                                                            ? 0x00000021U
                                                            : 
                                                           ((IData)(__VdfgRegularize_h6e95ff9d_0_128)
                                                             ? 0x00000020U
                                                             : 
                                                            ((IData)(__VdfgRegularize_h6e95ff9d_0_127)
                                                              ? 0x0000001fU
                                                              : 
                                                             ((IData)(__VdfgRegularize_h6e95ff9d_0_126)
                                                               ? 0x0000001dU
                                                               : 
                                                              ((IData)(__VdfgRegularize_h6e95ff9d_0_125)
                                                                ? 0x0000001cU
                                                                : 
                                                               ((IData)(__VdfgRegularize_h6e95ff9d_0_124)
                                                                 ? 0x0000001bU
                                                                 : 
                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_123)
                                                                  ? 0x0000001aU
                                                                  : 
                                                                 ((IData)(__VdfgRegularize_h6e95ff9d_0_122)
                                                                   ? 0x00000019U
                                                                   : 
                                                                  ((IData)(__VdfgRegularize_h6e95ff9d_0_121)
                                                                    ? 0x00000018U
                                                                    : 
                                                                   ((IData)(__VdfgRegularize_h6e95ff9d_0_120)
                                                                     ? 0x00000017U
                                                                     : 
                                                                    ((IData)(__VdfgRegularize_h6e95ff9d_0_119)
                                                                      ? 0x00000016U
                                                                      : 
                                                                     ((IData)(__VdfgRegularize_h6e95ff9d_0_118)
                                                                       ? 0x00000015U
                                                                       : 
                                                                      ((IData)(__VdfgRegularize_h6e95ff9d_0_117)
                                                                        ? 0x00000014U
                                                                        : 
                                                                       ((IData)(__VdfgRegularize_h6e95ff9d_0_116)
                                                                         ? 0x00000013U
                                                                         : 
                                                                        ((IData)(__VdfgRegularize_h6e95ff9d_0_115)
                                                                          ? 0x00000012U
                                                                          : 
                                                                         ((IData)(__VdfgRegularize_h6e95ff9d_0_114)
                                                                           ? 0x00000011U
                                                                           : 
                                                                          ((IData)(__VdfgRegularize_h6e95ff9d_0_113)
                                                                            ? 0x00000010U
                                                                            : 
                                                                           ((IData)(__VdfgRegularize_h6e95ff9d_0_112)
                                                                             ? 0x0000000fU
                                                                             : 
                                                                            ((IData)(__VdfgRegularize_h6e95ff9d_0_111)
                                                                              ? 0x0000000eU
                                                                              : 
                                                                             ((IData)(__VdfgRegularize_h6e95ff9d_0_110)
                                                                               ? 0x0000000dU
                                                                               : 
                                                                              ((IData)(__VdfgRegularize_h6e95ff9d_0_109)
                                                                                ? 0x0000000cU
                                                                                : 
                                                                               ((IData)(__VdfgRegularize_h6e95ff9d_0_108)
                                                                                 ? 0x0000000bU
                                                                                 : 
                                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_107)
                                                                                 ? 0x0000000aU
                                                                                 : 
                                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_106)
                                                                                 ? 9U
                                                                                 : 
                                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_105)
                                                                                 ? 8U
                                                                                 : 
                                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_104)
                                                                                 ? 7U
                                                                                 : 
                                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_103)
                                                                                 ? 6U
                                                                                 : 
                                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_102)
                                                                                 ? 5U
                                                                                 : 
                                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_101)
                                                                                 ? 4U
                                                                                 : 
                                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_100)
                                                                                 ? 3U
                                                                                 : 
                                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_99)
                                                                                 ? 2U
                                                                                 : 
                                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_98)
                                                                                 ? 1U
                                                                                 : __VdfgRegularize_h6e95ff9d_0_183))))))))))))))))))))))))))))))))))))
                                             ? 2U : (IData)(__VdfgRegularize_h6e95ff9d_0_177))
                                         : (IData)(__VdfgRegularize_h6e95ff9d_0_177));
    __VdfgRegularize_h6e95ff9d_0_3 = (vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr 
                                      + ((IData)((((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_rstrb) 
                                                   >> 3U) 
                                                  & (~ 
                                                     ((IData)(__VdfgRegularize_h6e95ff9d_0_193) 
                                                      | (IData)(__VdfgRegularize_h6e95ff9d_0_195)))))
                                          ? 3U : ((IData)(__VdfgRegularize_h6e95ff9d_0_193)
                                                   ? 2U
                                                   : 
                                                  (1U 
                                                   & (- (IData)((IData)(__VdfgRegularize_h6e95ff9d_0_194)))))));
    if ((2U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_rstrb))) {
        if (VL_GTS_III(32, 0U, vlSelfRef.__VdfgRegularize_h6e95ff9d_0_11)) {
            __VdfgRegularize_h6e95ff9d_0_19 = 2U;
            __VdfgRegularize_h6e95ff9d_0_9 = __VdfgRegularize_h6e95ff9d_0_12;
        } else if (VL_GTS_III(32, 0U, __VdfgRegularize_h6e95ff9d_0_12)) {
            __VdfgRegularize_h6e95ff9d_0_19 = __VdfgRegularize_h6e95ff9d_0_26;
            __VdfgRegularize_h6e95ff9d_0_9 = vlSelfRef.__VdfgRegularize_h6e95ff9d_0_11;
        } else {
            __VdfgRegularize_h6e95ff9d_0_19 = ((vlSelfRef.__VdfgRegularize_h6e95ff9d_0_11 
                                                == __VdfgRegularize_h6e95ff9d_0_12)
                                                ? (IData)(__VdfgRegularize_h6e95ff9d_0_26)
                                                : 2U);
            __VdfgRegularize_h6e95ff9d_0_9 = __VdfgRegularize_h6e95ff9d_0_12;
        }
    } else {
        __VdfgRegularize_h6e95ff9d_0_19 = __VdfgRegularize_h6e95ff9d_0_26;
        __VdfgRegularize_h6e95ff9d_0_9 = __VdfgRegularize_h6e95ff9d_0_12;
    }
    __VdfgRegularize_h6e95ff9d_0_192 = ((((0x00100000U 
                                           <= __VdfgRegularize_h6e95ff9d_0_3) 
                                          & (0x006a12fcU 
                                             > __VdfgRegularize_h6e95ff9d_0_3))
                                          ? 1U : ((
                                                   (0x01ad5e80U 
                                                    <= __VdfgRegularize_h6e95ff9d_0_3) 
                                                   & (0x01adadb8U 
                                                      > __VdfgRegularize_h6e95ff9d_0_3))
                                                   ? 0x00000026U
                                                   : 
                                                  (((0x01aaba80U 
                                                     <= __VdfgRegularize_h6e95ff9d_0_3) 
                                                    & (0x01ad5e80U 
                                                       > __VdfgRegularize_h6e95ff9d_0_3))
                                                    ? 0x00000025U
                                                    : 
                                                   (((0x01a6c480U 
                                                      <= __VdfgRegularize_h6e95ff9d_0_3) 
                                                     & (0x01aaba80U 
                                                        > __VdfgRegularize_h6e95ff9d_0_3))
                                                     ? 0x00000024U
                                                     : 
                                                    (((0x01a57280U 
                                                       <= __VdfgRegularize_h6e95ff9d_0_3) 
                                                      & (0x01a6c480U 
                                                         > __VdfgRegularize_h6e95ff9d_0_3))
                                                      ? 0x00000023U
                                                      : 
                                                     (((0x01a51e00U 
                                                        <= __VdfgRegularize_h6e95ff9d_0_3) 
                                                       & (0x01a57280U 
                                                          > __VdfgRegularize_h6e95ff9d_0_3))
                                                       ? 0x00000022U
                                                       : 
                                                      (((0x01a47500U 
                                                         <= __VdfgRegularize_h6e95ff9d_0_3) 
                                                        & (0x01a51e00U 
                                                           > __VdfgRegularize_h6e95ff9d_0_3))
                                                        ? 0x00000021U
                                                        : 
                                                       (((0x01a46100U 
                                                          <= __VdfgRegularize_h6e95ff9d_0_3) 
                                                         & (0x01a474ceU 
                                                            > __VdfgRegularize_h6e95ff9d_0_3))
                                                         ? 0x0000001fU
                                                         : 
                                                        (((0x01a30f00U 
                                                           <= __VdfgRegularize_h6e95ff9d_0_3) 
                                                          & (0x01a46100U 
                                                             > __VdfgRegularize_h6e95ff9d_0_3))
                                                          ? 0x0000001eU
                                                          : 
                                                         (((0x01a26600U 
                                                            <= __VdfgRegularize_h6e95ff9d_0_3) 
                                                           & (0x01a30f00U 
                                                              > __VdfgRegularize_h6e95ff9d_0_3))
                                                           ? 0x0000001dU
                                                           : 
                                                          (((0x01a11400U 
                                                             <= __VdfgRegularize_h6e95ff9d_0_3) 
                                                            & (0x01a26600U 
                                                               > __VdfgRegularize_h6e95ff9d_0_3))
                                                            ? 0x0000001cU
                                                            : 
                                                           (((0x019fc200U 
                                                              <= __VdfgRegularize_h6e95ff9d_0_3) 
                                                             & (0x01a11400U 
                                                                > __VdfgRegularize_h6e95ff9d_0_3))
                                                             ? 0x0000001bU
                                                             : 
                                                            (((0x019a7a00U 
                                                               <= __VdfgRegularize_h6e95ff9d_0_3) 
                                                              & (0x019fc200U 
                                                                 > __VdfgRegularize_h6e95ff9d_0_3))
                                                              ? 0x0000001aU
                                                              : 
                                                             (((0x0197d600U 
                                                                <= __VdfgRegularize_h6e95ff9d_0_3) 
                                                               & (0x019a7a00U 
                                                                  > __VdfgRegularize_h6e95ff9d_0_3))
                                                               ? 0x00000019U
                                                               : 
                                                              (((0x01953200U 
                                                                 <= __VdfgRegularize_h6e95ff9d_0_3) 
                                                                & (0x0197d600U 
                                                                   > __VdfgRegularize_h6e95ff9d_0_3))
                                                                ? 0x00000018U
                                                                : 
                                                               (((0x0193e000U 
                                                                  <= __VdfgRegularize_h6e95ff9d_0_3) 
                                                                 & (0x01953200U 
                                                                    > __VdfgRegularize_h6e95ff9d_0_3))
                                                                 ? 0x00000017U
                                                                 : 
                                                                (((0x01928e00U 
                                                                   <= __VdfgRegularize_h6e95ff9d_0_3) 
                                                                  & (0x0193e000U 
                                                                     > __VdfgRegularize_h6e95ff9d_0_3))
                                                                  ? 0x00000016U
                                                                  : 
                                                                 (((0x01913c00U 
                                                                    <= __VdfgRegularize_h6e95ff9d_0_3) 
                                                                   & (0x01928e00U 
                                                                      > __VdfgRegularize_h6e95ff9d_0_3))
                                                                   ? 0x00000015U
                                                                   : 
                                                                  (((0x018e9800U 
                                                                     <= __VdfgRegularize_h6e95ff9d_0_3) 
                                                                    & (0x01913c00U 
                                                                       > __VdfgRegularize_h6e95ff9d_0_3))
                                                                    ? 0x00000014U
                                                                    : 
                                                                   (((0x018bf400U 
                                                                      <= __VdfgRegularize_h6e95ff9d_0_3) 
                                                                     & (0x018e9800U 
                                                                        > __VdfgRegularize_h6e95ff9d_0_3))
                                                                     ? 0x00000013U
                                                                     : 
                                                                    (((0x01816400U 
                                                                       <= __VdfgRegularize_h6e95ff9d_0_3) 
                                                                      & (0x018bf400U 
                                                                         > __VdfgRegularize_h6e95ff9d_0_3))
                                                                      ? 0x00000012U
                                                                      : 
                                                                     (((0x017c1c00U 
                                                                        <= __VdfgRegularize_h6e95ff9d_0_3) 
                                                                       & (0x01816400U 
                                                                          > __VdfgRegularize_h6e95ff9d_0_3))
                                                                       ? 0x00000011U
                                                                       : 
                                                                      (((0x0176d400U 
                                                                         <= __VdfgRegularize_h6e95ff9d_0_3) 
                                                                        & (0x017c1c00U 
                                                                           > __VdfgRegularize_h6e95ff9d_0_3))
                                                                        ? 0x00000010U
                                                                        : 
                                                                       (((0x01743000U 
                                                                          <= __VdfgRegularize_h6e95ff9d_0_3) 
                                                                         & (0x0176d400U 
                                                                            > __VdfgRegularize_h6e95ff9d_0_3))
                                                                         ? 0x0000000fU
                                                                         : 
                                                                        (((0x01718c00U 
                                                                           <= __VdfgRegularize_h6e95ff9d_0_3) 
                                                                          & (0x01743000U 
                                                                             > __VdfgRegularize_h6e95ff9d_0_3))
                                                                          ? 0x0000000eU
                                                                          : 
                                                                         (((0x016ee800U 
                                                                            <= __VdfgRegularize_h6e95ff9d_0_3) 
                                                                           & (0x01718c00U 
                                                                              > __VdfgRegularize_h6e95ff9d_0_3))
                                                                           ? 0x0000000dU
                                                                           : 
                                                                          (((0x0169a000U 
                                                                             <= __VdfgRegularize_h6e95ff9d_0_3) 
                                                                            & (0x016ee800U 
                                                                               > __VdfgRegularize_h6e95ff9d_0_3))
                                                                            ? 0x0000000cU
                                                                            : 
                                                                           (((0x01645800U 
                                                                              <= __VdfgRegularize_h6e95ff9d_0_3) 
                                                                             & (0x0169a000U 
                                                                                > __VdfgRegularize_h6e95ff9d_0_3))
                                                                             ? 0x0000000bU
                                                                             : 
                                                                            (((0x014f3800U 
                                                                               <= __VdfgRegularize_h6e95ff9d_0_3) 
                                                                              & (0x01645800U 
                                                                                > __VdfgRegularize_h6e95ff9d_0_3))
                                                                              ? 0x0000000aU
                                                                              : 
                                                                             (((0x0144a800U 
                                                                                <= __VdfgRegularize_h6e95ff9d_0_3) 
                                                                               & (0x014f3800U 
                                                                                > __VdfgRegularize_h6e95ff9d_0_3))
                                                                               ? 9U
                                                                               : 
                                                                              (((0x013a1800U 
                                                                                <= __VdfgRegularize_h6e95ff9d_0_3) 
                                                                                & (0x0144a800U 
                                                                                > __VdfgRegularize_h6e95ff9d_0_3))
                                                                                ? 8U
                                                                                : 
                                                                               (((0x0134d000U 
                                                                                <= __VdfgRegularize_h6e95ff9d_0_3) 
                                                                                & (0x013a1800U 
                                                                                > __VdfgRegularize_h6e95ff9d_0_3))
                                                                                 ? 7U
                                                                                 : 
                                                                                (((0x012f8800U 
                                                                                <= __VdfgRegularize_h6e95ff9d_0_3) 
                                                                                & (0x0134d000U 
                                                                                > __VdfgRegularize_h6e95ff9d_0_3))
                                                                                 ? 6U
                                                                                 : 
                                                                                (((0x012a4000U 
                                                                                <= __VdfgRegularize_h6e95ff9d_0_3) 
                                                                                & (0x012f8800U 
                                                                                > __VdfgRegularize_h6e95ff9d_0_3))
                                                                                 ? 5U
                                                                                 : 
                                                                                (((0x011fb000U 
                                                                                <= __VdfgRegularize_h6e95ff9d_0_3) 
                                                                                & (0x012a4000U 
                                                                                > __VdfgRegularize_h6e95ff9d_0_3))
                                                                                 ? 4U
                                                                                 : 
                                                                                (((0x01152000U 
                                                                                <= __VdfgRegularize_h6e95ff9d_0_3) 
                                                                                & (0x011fb000U 
                                                                                > __VdfgRegularize_h6e95ff9d_0_3))
                                                                                 ? 3U
                                                                                 : 
                                                                                (2U 
                                                                                | (- (IData)(
                                                                                (1U 
                                                                                & (~ 
                                                                                ((0x01000000U 
                                                                                <= __VdfgRegularize_h6e95ff9d_0_3) 
                                                                                & (0x01152000U 
                                                                                > __VdfgRegularize_h6e95ff9d_0_3))))))))))))))))))))))))))))))))))))))))))) 
                                        & (- (IData)(
                                                     (0x0007ec00U 
                                                      <= __VdfgRegularize_h6e95ff9d_0_3))));
    if ((4U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_rstrb))) {
        if (VL_GTS_III(32, 0U, vlSelfRef.__VdfgRegularize_h6e95ff9d_0_10)) {
            __VdfgRegularize_h6e95ff9d_0_133 = __VdfgRegularize_h6e95ff9d_0_9;
            __VdfgRegularize_h6e95ff9d_0_20 = 2U;
        } else if (VL_GTS_III(32, 0U, __VdfgRegularize_h6e95ff9d_0_9)) {
            __VdfgRegularize_h6e95ff9d_0_133 = vlSelfRef.__VdfgRegularize_h6e95ff9d_0_10;
            __VdfgRegularize_h6e95ff9d_0_20 = __VdfgRegularize_h6e95ff9d_0_19;
        } else {
            __VdfgRegularize_h6e95ff9d_0_133 = __VdfgRegularize_h6e95ff9d_0_9;
            __VdfgRegularize_h6e95ff9d_0_20 = ((__VdfgRegularize_h6e95ff9d_0_9 
                                                == vlSelfRef.__VdfgRegularize_h6e95ff9d_0_10)
                                                ? (IData)(__VdfgRegularize_h6e95ff9d_0_19)
                                                : 2U);
        }
    } else {
        __VdfgRegularize_h6e95ff9d_0_133 = __VdfgRegularize_h6e95ff9d_0_9;
        __VdfgRegularize_h6e95ff9d_0_20 = __VdfgRegularize_h6e95ff9d_0_19;
    }
    vlSelfRef.__VdfgRegularize_h6e95ff9d_0_6 = ((0U 
                                                 != 
                                                 (3U 
                                                  & vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr))
                                                 ? 2U
                                                 : 
                                                ((0U 
                                                  == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_rstrb))
                                                  ? 1U
                                                  : 
                                                 ((8U 
                                                   & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_rstrb))
                                                   ? 
                                                  (VL_GTS_III(32, 0U, vlSelfRef.__VdfgRegularize_h6e95ff9d_0_17)
                                                    ? 2U
                                                    : 
                                                   (VL_GTS_III(32, 0U, __VdfgRegularize_h6e95ff9d_0_133)
                                                     ? (IData)(__VdfgRegularize_h6e95ff9d_0_20)
                                                     : 
                                                    ((__VdfgRegularize_h6e95ff9d_0_133 
                                                      == vlSelfRef.__VdfgRegularize_h6e95ff9d_0_17)
                                                      ? (IData)(__VdfgRegularize_h6e95ff9d_0_20)
                                                      : 2U)))
                                                   : (IData)(__VdfgRegularize_h6e95ff9d_0_20))));
    __Vtemp_188 = VL_MATCHMASKED_I(32, VL_MODDIVS_III(32, vlSelfRef.tb_s2a_network_backend_golden__DOT__class_transfer_index
                                                      [
                                                      (3U 
                                                       & ((((1U 
                                                             == __VdfgRegularize_h6e95ff9d_0_192)
                                                             ? 1U
                                                             : 2U) 
                                                           & (- (IData)(
                                                                        (0U 
                                                                         != __VdfgRegularize_h6e95ff9d_0_192)))) 
                                                          | (- (IData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_write)))))], (IData)(5U)), Vtb_s2a_network_backend_golden__ConstPool__CONST_hb4617e49_0);
    vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_ready 
        = ((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_valid)
            ? (VL_GTES_III(32, vlSelfRef.tb_s2a_network_backend_golden__DOT__class_wait_count, Vtb_s2a_network_backend_golden__ConstPool__TABLE_hc6a14c36_0
                           [__Vtemp_188]) & (IData)(vlSelfRef.__VdfgRegularize_h6e95ff9d_0_27))
            : (IData)(vlSelfRef.__VdfgRegularize_h6e95ff9d_0_27));
    __VdfgRegularize_h6e95ff9d_0_13 = ((1U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_rstrb))
                                        ? ((0U == __VdfgRegularize_h6e95ff9d_0_18)
                                            ? (IData)(vlSelfRef.__VdfgRegularize_h6e95ff9d_0_6)
                                            : ((1U 
                                                == __VdfgRegularize_h6e95ff9d_0_18)
                                                ? (IData)(vlSelfRef.__VdfgRegularize_h6e95ff9d_0_6)
                                                : ((IData)(__VdfgRegularize_h6e95ff9d_0_190)
                                                    ? (IData)(vlSelfRef.__VdfgRegularize_h6e95ff9d_0_6)
                                                    : 6U)))
                                        : (IData)(vlSelfRef.__VdfgRegularize_h6e95ff9d_0_6));
    __VdfgRegularize_h6e95ff9d_0_14 = ((2U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_rstrb))
                                        ? ((0U == vlSelfRef.__VdfgRegularize_h6e95ff9d_0_11)
                                            ? (IData)(__VdfgRegularize_h6e95ff9d_0_13)
                                            : ((1U 
                                                == vlSelfRef.__VdfgRegularize_h6e95ff9d_0_11)
                                                ? (IData)(__VdfgRegularize_h6e95ff9d_0_13)
                                                : ((IData)(vlSelfRef.__VdfgRegularize_h6e95ff9d_0_189)
                                                    ? (IData)(__VdfgRegularize_h6e95ff9d_0_13)
                                                    : 6U)))
                                        : (IData)(__VdfgRegularize_h6e95ff9d_0_13));
    __VdfgRegularize_h6e95ff9d_0_15 = ((4U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_rstrb))
                                        ? ((0U == vlSelfRef.__VdfgRegularize_h6e95ff9d_0_10)
                                            ? (IData)(__VdfgRegularize_h6e95ff9d_0_14)
                                            : ((1U 
                                                == vlSelfRef.__VdfgRegularize_h6e95ff9d_0_10)
                                                ? (IData)(__VdfgRegularize_h6e95ff9d_0_14)
                                                : ((IData)(vlSelfRef.__VdfgRegularize_h6e95ff9d_0_188)
                                                    ? (IData)(__VdfgRegularize_h6e95ff9d_0_14)
                                                    : 6U)))
                                        : (IData)(__VdfgRegularize_h6e95ff9d_0_14));
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__maxpool_req_ready 
        = ((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_valid) 
           & ((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_ready) 
              & (3U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__state))));
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__upsample_req_ready 
        = ((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_valid) 
           & ((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_ready) 
              & (5U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__state))));
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__route_req_ready 
        = ((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_valid) 
           & ((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_ready) 
              & (4U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__state))));
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__conv_req_ready 
        = ((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_valid) 
           & ((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_ready) 
              & (2U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__state))));
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__memory_handshake 
        = ((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_ready) 
           & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_valid));
    vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_error_code 
        = (((0U != (3U & vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr))
             ? 2U : ((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_write)
                      ? (((0U != (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_rstrb)) 
                          | (0U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_wstrb)))
                          ? 1U : ((8U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_wstrb))
                                   ? (VL_GTS_III(32, 0U, 
                                                 ((IData)(__VdfgRegularize_h6e95ff9d_0_168)
                                                   ? 0x00000024U
                                                   : 
                                                  ((IData)(__VdfgRegularize_h6e95ff9d_0_167)
                                                    ? 0x00000023U
                                                    : 
                                                   ((IData)(__VdfgRegularize_h6e95ff9d_0_166)
                                                     ? 0x00000022U
                                                     : 
                                                    ((IData)(__VdfgRegularize_h6e95ff9d_0_165)
                                                      ? 0x00000021U
                                                      : 
                                                     ((IData)(__VdfgRegularize_h6e95ff9d_0_164)
                                                       ? 0x00000020U
                                                       : 
                                                      ((IData)(__VdfgRegularize_h6e95ff9d_0_163)
                                                        ? 0x0000001fU
                                                        : 
                                                       ((IData)(__VdfgRegularize_h6e95ff9d_0_162)
                                                         ? 0x0000001dU
                                                         : 
                                                        ((IData)(__VdfgRegularize_h6e95ff9d_0_161)
                                                          ? 0x0000001cU
                                                          : 
                                                         ((IData)(__VdfgRegularize_h6e95ff9d_0_160)
                                                           ? 0x0000001bU
                                                           : 
                                                          ((IData)(__VdfgRegularize_h6e95ff9d_0_159)
                                                            ? 0x0000001aU
                                                            : 
                                                           ((IData)(__VdfgRegularize_h6e95ff9d_0_158)
                                                             ? 0x00000019U
                                                             : 
                                                            ((IData)(__VdfgRegularize_h6e95ff9d_0_157)
                                                              ? 0x00000018U
                                                              : 
                                                             ((IData)(__VdfgRegularize_h6e95ff9d_0_156)
                                                               ? 0x00000017U
                                                               : 
                                                              ((IData)(__VdfgRegularize_h6e95ff9d_0_155)
                                                                ? 0x00000016U
                                                                : 
                                                               ((IData)(__VdfgRegularize_h6e95ff9d_0_154)
                                                                 ? 0x00000015U
                                                                 : 
                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_153)
                                                                  ? 0x00000014U
                                                                  : 
                                                                 ((IData)(__VdfgRegularize_h6e95ff9d_0_152)
                                                                   ? 0x00000013U
                                                                   : 
                                                                  ((IData)(__VdfgRegularize_h6e95ff9d_0_151)
                                                                    ? 0x00000012U
                                                                    : 
                                                                   ((IData)(__VdfgRegularize_h6e95ff9d_0_150)
                                                                     ? 0x00000011U
                                                                     : 
                                                                    ((IData)(__VdfgRegularize_h6e95ff9d_0_149)
                                                                      ? 0x00000010U
                                                                      : 
                                                                     ((IData)(__VdfgRegularize_h6e95ff9d_0_148)
                                                                       ? 0x0000000fU
                                                                       : 
                                                                      ((IData)(__VdfgRegularize_h6e95ff9d_0_147)
                                                                        ? 0x0000000eU
                                                                        : 
                                                                       ((IData)(__VdfgRegularize_h6e95ff9d_0_146)
                                                                         ? 0x0000000dU
                                                                         : 
                                                                        ((IData)(__VdfgRegularize_h6e95ff9d_0_145)
                                                                          ? 0x0000000cU
                                                                          : 
                                                                         ((IData)(__VdfgRegularize_h6e95ff9d_0_144)
                                                                           ? 0x0000000bU
                                                                           : 
                                                                          ((IData)(__VdfgRegularize_h6e95ff9d_0_143)
                                                                            ? 0x0000000aU
                                                                            : 
                                                                           ((IData)(__VdfgRegularize_h6e95ff9d_0_142)
                                                                             ? 9U
                                                                             : 
                                                                            ((IData)(__VdfgRegularize_h6e95ff9d_0_141)
                                                                              ? 8U
                                                                              : 
                                                                             ((IData)(__VdfgRegularize_h6e95ff9d_0_140)
                                                                               ? 7U
                                                                               : 
                                                                              ((IData)(__VdfgRegularize_h6e95ff9d_0_139)
                                                                                ? 6U
                                                                                : 
                                                                               ((IData)(__VdfgRegularize_h6e95ff9d_0_138)
                                                                                 ? 5U
                                                                                 : 
                                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_137)
                                                                                 ? 4U
                                                                                 : 
                                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_136)
                                                                                 ? 3U
                                                                                 : 
                                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_135)
                                                                                 ? 2U
                                                                                 : 
                                                                                ((IData)(__VdfgRegularize_h6e95ff9d_0_134)
                                                                                 ? 1U
                                                                                 : __VdfgRegularize_h6e95ff9d_0_182))))))))))))))))))))))))))))))))))))
                                       ? 2U : (IData)(__VdfgRegularize_h6e95ff9d_0_178))
                                   : (IData)(__VdfgRegularize_h6e95ff9d_0_178)))
                      : ((0U != (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_wstrb))
                          ? 1U : ((0U == (IData)(vlSelfRef.__VdfgRegularize_h6e95ff9d_0_6))
                                   ? ((8U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_rstrb))
                                       ? ((0U == vlSelfRef.__VdfgRegularize_h6e95ff9d_0_17)
                                           ? (IData)(__VdfgRegularize_h6e95ff9d_0_15)
                                           : ((1U == vlSelfRef.__VdfgRegularize_h6e95ff9d_0_17)
                                               ? (IData)(__VdfgRegularize_h6e95ff9d_0_15)
                                               : ((IData)(vlSelfRef.__VdfgRegularize_h6e95ff9d_0_187)
                                                   ? (IData)(__VdfgRegularize_h6e95ff9d_0_15)
                                                   : 6U)))
                                       : (IData)(__VdfgRegularize_h6e95ff9d_0_15))
                                   : (IData)(vlSelfRef.__VdfgRegularize_h6e95ff9d_0_6))))) 
           & (- (IData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_valid))));
    vlSelfRef.tb_s2a_network_backend_golden__DOT__backend_memory_error_valid 
        = ((0U != (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_error_code)) 
           & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__memory_handshake));
}

VL_ATTR_COLD bool Vtb_s2a_network_backend_golden___024root___eval_phase__stl(Vtb_s2a_network_backend_golden___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_network_backend_golden___024root___eval_phase__stl\n"); );
    Vtb_s2a_network_backend_golden__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
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
        Vtb_s2a_network_backend_golden___024root___dump_triggers__stl(vlSelfRef.__VstlTriggered, "stl"s);
    }
#endif
    __VstlExecute = Vtb_s2a_network_backend_golden___024root___trigger_anySet__stl(vlSelfRef.__VstlTriggered);
    if (__VstlExecute) {
        {
            // Inlined CFunc: _eval_stl
            if ((1ULL & vlSelfRef.__VstlTriggered[0U])) {
                Vtb_s2a_network_backend_golden___024root___stl_sequent__TOP__0(vlSelf);
            }
        }
    }
    return (__VstlExecute);
}

bool Vtb_s2a_network_backend_golden___024root___trigger_anySet__act(const VlUnpacked<QData/*63:0*/, 1> &in);

#ifdef VL_DEBUG
VL_ATTR_COLD void Vtb_s2a_network_backend_golden___024root___dump_triggers__act(const VlUnpacked<QData/*63:0*/, 1> &triggers, const std::string &tag) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_network_backend_golden___024root___dump_triggers__act\n"); );
    // Body
    if ((1U & (~ (IData)(Vtb_s2a_network_backend_golden___024root___trigger_anySet__act(triggers))))) {
        VL_DBG_MSGS("         No '" + tag + "' region triggers active\n");
    }
    if ((1U & (IData)(triggers[0U]))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 0 is active: @(posedge tb_s2a_network_backend_golden.clk)\n");
    }
    if ((1U & (IData)((triggers[0U] >> 1U)))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 1 is active: @(negedge tb_s2a_network_backend_golden.clk)\n");
    }
    if ((1U & (IData)((triggers[0U] >> 2U)))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 2 is active: @([true] __VdlySched.awaitingCurrentTime())\n");
    }
}
#endif  // VL_DEBUG

VL_ATTR_COLD void Vtb_s2a_network_backend_golden___024root___ctor_var_reset(Vtb_s2a_network_backend_golden___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_network_backend_golden___024root___ctor_var_reset\n"); );
    Vtb_s2a_network_backend_golden__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    const uint64_t __VscopeHash = VL_MURMUR64_HASH(vlSelf->vlNamep);
    vlSelf->tb_s2a_network_backend_golden__DOT__mem_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 16100198414199411505ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__mem_write = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 6060134145391135197ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__mem_addr = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16029929573564882918ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__mem_wdata = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5962384585297802984ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__mem_rstrb = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 8527913995776095472ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__mem_wstrb = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 11171712500590747815ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__mem_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 16563846886932375195ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__mem_error_code = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 12878808059683324775ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__backend_memory_error_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 2037680343439438567ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__operator_result_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 16635222668099193927ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__operator_error_code = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 10201403422971403072ull);
    for (int __Vi0 = 0; __Vi0 < 519168; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__input_bytes[__Vi0] = 0;
    }
    for (int __Vi0 = 0; __Vi0 < 5903100; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__weight_bytes[__Vi0] = 0;
    }
    for (int __Vi0 = 0; __Vi0 < 11382200; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__feature_bytes[__Vi0] = 0;
    }
    for (int __Vi0 = 0; __Vi0 < 11382200; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__feature_byte_valid[__Vi0] = 0;
    }
    for (int __Vi0 = 0; __Vi0 < 11382150; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__expected_bytes[__Vi0] = 0;
    }
    for (int __Vi0 = 0; __Vi0 < 11382150; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__golden_byte_seen[__Vi0] = 0;
    }
    for (int __Vi0 = 0; __Vi0 < 38; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__golden_offset[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13911160734636342069ull);
    }
    for (int __Vi0 = 0; __Vi0 < 38; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__layer_write_count[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9726416475376545262ull);
    }
    for (int __Vi0 = 0; __Vi0 < 4; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__class_transfer_index[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 18340525652362302265ull);
    }
    for (int __Vi0 = 0; __Vi0 < 4; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__class_accepted_count[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15783076053982401452ull);
    }
    for (int __Vi0 = 0; __Vi0 < 4; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__class_selected_byte_count[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6858452777197071273ull);
    }
    vlSelf->tb_s2a_network_backend_golden__DOT__seq_owner = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9716120092829110394ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__seq_lane_owner = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2892132426058136527ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__seq_tensor_owner = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1432493383051430856ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__seq_transfer_class = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3477927022936153516ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__seq_golden_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8085887563466377429ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__verify_golden_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6516981951979910298ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__seq_feature_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 350559394991436580ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__input_bytes_this_transfer = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13908228073133168689ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__weight_bytes_this_transfer = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16952875417178419670ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__feature_bytes_this_transfer = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7418497957104589291ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__active_byte_count = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14860157155531172163ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__seq_lane_address = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10493551382415953498ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__state = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 2492193751728825027ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor = VL_SCOPED_RAND_RESET_I(6, __VscopeHash, 17420666702124239898ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_element_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12096703921370241124ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__response_pending = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 1991455680971125495ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__response_data_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9497935804535901287ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__response_error_latched = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 5347441095233030452ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__response_target_latched = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 17504115061574583495ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__current_op = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 1591820691374530562ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__current_input_count = VL_SCOPED_RAND_RESET_I(2, __VscopeHash, 4863867026171007089ull);
    for (int __Vi0 = 0; __Vi0 < 2; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_base[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11583133688056706677ull);
    }
    for (int __Vi0 = 0; __Vi0 < 2; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_length[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17310377544734334926ull);
    }
    for (int __Vi0 = 0; __Vi0 < 2; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_n[__Vi0] = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 4061181006501278662ull);
    }
    for (int __Vi0 = 0; __Vi0 < 2; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_c[__Vi0] = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 17119256223616776852ull);
    }
    for (int __Vi0 = 0; __Vi0 < 2; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_h[__Vi0] = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 2197192170791944193ull);
    }
    for (int __Vi0 = 0; __Vi0 < 2; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_w[__Vi0] = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 2737246143691316772ull);
    }
    for (int __Vi0 = 0; __Vi0 < 2; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_route_start[__Vi0] = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 16582630554902601414ull);
    }
    for (int __Vi0 = 0; __Vi0 < 2; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_route_end[__Vi0] = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 10956509261504322330ull);
    }
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_base = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 18254028070609691537ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_length = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4345845828091207697ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_n = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 13583765199652611028ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_c = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 7850388407913146998ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_h = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 4580269939905128119ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_w = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 1640106556434191314ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_element_count = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 13631403628916271676ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_channel = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9702308038307349880ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16724763010875344379ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15985174848948839361ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__alias_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 6072798412044919672ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__descriptor_fault = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 7097293191361464144ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__is_alias_row = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 18404459764623195580ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__alias_output_plane_elements = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 9813448087869424865ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__alias_output_element_count = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 18185388332617621647ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__conv_start_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 13231756471655936357ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__conv_start_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 4139463117361222169ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__maxpool_start_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 15071636668945572278ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__maxpool_start_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 4964172398404816026ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__route_start_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 3979571493063525574ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__route_start_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 13426582368030634005ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__upsample_start_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 4980207224640018163ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__upsample_start_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 13734317633714565355ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__conv_req_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 10604350682805699145ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__conv_req_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 7517994611627325824ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__maxpool_req_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 7277058378475747366ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__maxpool_req_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 18116798807422360825ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__route_req_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 10220641947343473131ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__route_req_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 12066841422901605071ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__upsample_req_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 1959745044612670603ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__upsample_req_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 8524116269610869678ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__conv_rsp_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 15467357143000797252ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__maxpool_rsp_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 17422248750690608842ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__route_rsp_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 313788663838042538ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__upsample_rsp_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 2242192424970303678ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__conv_result_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 10923047928912799696ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__maxpool_result_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 8731860478692925408ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__route_result_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 7634376353104578359ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__upsample_result_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 17882247220484225577ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__selected_result_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 2846070594720318276ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__selected_result_error = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 12769091853700423681ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__memory_handshake = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 47440525016962293ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__selected_start_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 15404692880337326379ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_conv_engine__activation_mode = 0;
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__darknet_padding_parameter = 0;
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_x = 0;
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_y = 0;
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width = 0;
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_height = 0;
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__layer_index = 0;
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_upsample_engine__stride = 0;
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__state = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 15711450754013964364ull);
    for (int __Vi0 = 0; __Vi0 < 4; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16480287378563875258ull);
    }
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_address_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15669110682939342810ull);
    VL_SCOPED_RAND_RESET_W(72, vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__candidate_values_latched, __VscopeHash, 10682540766135488902ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__read_tap_index = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 9565862273580026186ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__result_value_latched = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 8130862385066934453ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__result_error_latched = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 13028704436324204074ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_output_height = VL_SCOPED_RAND_RESET_Q(33, __VscopeHash, 6207937959582245916ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_output_width = VL_SCOPED_RAND_RESET_Q(33, __VscopeHash, 11803085728363717969ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_count = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 937406210897688303ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask = VL_SCOPED_RAND_RESET_I(9, __VscopeHash, 1017201663009446187ull);
    for (int __Vi0 = 0; __Vi0 < 9; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17385810500789780455ull);
    }
    for (int __Vi0 = 0; __Vi0 < 9; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[__Vi0] = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 8413087352107830726ull);
    }
    for (int __Vi0 = 0; __Vi0 < 9; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[__Vi0] = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 15822575308521172987ull);
    }
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_error_code = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 6873419061442842124ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_offset_work = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 7260769200988525191ull);
    VL_SCOPED_RAND_RESET_W(65, vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_address_work, __VscopeHash, 1385617825726183136ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__mapped_response_error = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 6114712815747579331ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__window_max_value = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 12221924636031550449ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__window_error_code = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 14841632341367197857ull);
    for (int __Vi0 = 0; __Vi0 < 3; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_y_work[__Vi0] = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 4471326638207442755ull);
    }
    for (int __Vi0 = 0; __Vi0 < 3; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_index_work[__Vi0] = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 1090904278071269029ull);
    }
    for (int __Vi0 = 0; __Vi0 < 3; ++__Vi0) {
        VL_SCOPED_RAND_RESET_W(96, vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[__Vi0], __VscopeHash, 11297149186351597096ull);
    }
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__state = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 15278691175163198796ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__source_address_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14982792451914373759ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__output_address_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13169231948368907130ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__copied_value_latched = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 2754046961278013421ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__result_error_latched = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 12100594204200887699ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_channel = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10949850590258829802ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_address = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2156026763584506499ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__query_error_code = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 18138159687542809716ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__output_offset_work = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 12152982438550622826ull);
    VL_SCOPED_RAND_RESET_W(65, vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__output_address_work, __VscopeHash, 13977157297585003532ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__mapped_response_error = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 15921142441585566205ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__state = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 10960733162566130458ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source_count_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3704626770822146483ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__groups_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11436960485483156170ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__group_id_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8645638888517794064ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_channel_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3756170359873865987ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_y_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13710668988592392195ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_x_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13014093185492558516ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_base_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9284350128772370679ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_length_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5227834261568788618ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_channels_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16371815011618711359ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_height_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11860468815881262070ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_width_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12193256959509197007ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_start_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9044282031618656733ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_end_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17869257475247520727ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_multiplier_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5369193014760278531ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_value_latched = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 1161354193894751313ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source1_base_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 18044806300045043657ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source1_length_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11061458939987428281ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source1_channels_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11184647453932152764ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source1_height_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13655996196554057746ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source1_width_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4177788514463799895ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source1_start_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7818659560466194741ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source1_end_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7669372535539626944ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source1_multiplier_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10895154635841802626ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source1_value_latched = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 4536625694533601681ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_base_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 18002122548107686793ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_length_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15526298147540000736ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_channels_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3602948644557889390ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_height_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14237965026397981453ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_width_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2409676593217158519ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source_index_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9299694979576740105ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source_address_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 326725007391245305ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_address_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17972889933358287204ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__result_value_latched = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 1759100202155574907ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__result_error_latched = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 4286612736245719892ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__query_output_channels = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15394276623840365904ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__query_output_height = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12344051783052965693ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__query_output_width = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1411335286936844141ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__query_source_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6493057979531734097ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__query_source_address = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1012405736171004717ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__query_output_value = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 12913208674636401710ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__query_error_code = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 8708921188372310410ull);
    VL_SCOPED_RAND_RESET_W(65, vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_offset_work, __VscopeHash, 12595054863746896465ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__selected_byte_shift = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10627133812051168302ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__mapped_response_error = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 16438688589215447139ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state = VL_SCOPED_RAND_RESET_I(5, __VscopeHash, 14889565692329679276ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 384519945138116481ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_layer_index_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14657049037673641881ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_base_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10704069281828787240ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_length_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13780506050271528370ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_batch_count_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13165090760765627938ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_channels_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5114964483136933419ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_height_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17445182560078606275ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_width_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2649588431379203834ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_base_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14339810591499655225ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_length_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4437938483133683215ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_batch_count_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8261035290592733372ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_channels_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7714954163296474013ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1157356448097519670ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17173616447100372093ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_height_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9539721255718126180ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_width_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8307257829921206713ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__stride_y_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13630915682945312257ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__stride_x_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14978269015641538940ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__pad_left_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13402125134773734845ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__pad_right_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13525185344565348426ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__pad_top_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10503596982968943019ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__pad_bottom_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4643837325142558876ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__groups_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2346013889220210976ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__padding_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13254191643024330176ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_package_base_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10912111345912827242ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_package_length_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11518254366475057864ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__quantized_weight_offset_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6676982226102893582ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__quantized_weight_bytes_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8923522241876325424ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_batch_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5730472103591234735ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__activation_mode_latched = VL_SCOPED_RAND_RESET_I(2, __VscopeHash, 3145541650314554696ull);
    for (int __Vi0 = 0; __Vi0 < 51200; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_patch[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 11772419232826911430ull);
    }
    for (int __Vi0 = 0; __Vi0 < 512; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 3783417804081936696ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10851504567823666468ull);
    }
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_read_data = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 3283139966510849542ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_read_in_bounds = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 9109945485756970207ull);
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_read_byte[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 17977505376494339521ull);
    }
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13785158159033326904ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11155634649802818365ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9230575091863492786ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 18335499671991303439ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_height = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9485981058852616498ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_width = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12248323764194740139ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__patch_height = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 620832222126860659ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__patch_width = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9195955769567491479ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__patch_byte_count = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17362209645211617757ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_point_count = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9079551801147448462ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16630439370798564457ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7036940250762448533ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_lane_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2368253565793786435ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_reduction_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6957996991670076667ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 964498301884896963ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_scan_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 826139130045396559ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_scan_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2880415776599253987ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_reduction_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11757898023172129907ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_lane_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6360553972122796673ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_point_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17270592992530230010ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__request_address_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4446836773863578973ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__request_strobe_latched = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 16739636532576847380ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__request_wdata_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10586576825949133186ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__result_error_latched = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 10472253414111345643ull);
    VL_SCOPED_RAND_RESET_W(128, vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_elements_wide, __VscopeHash, 995237875522032997ull);
    VL_SCOPED_RAND_RESET_W(128, vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_wide, __VscopeHash, 15738579736219483832ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__validation_ok = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 14136151798595773670ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__validation_error = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 5016123832773439380ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_channel = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11072839287547931290ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2574343523563090471ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6190655803560544703ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_advance = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 15635389571154707137ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_in_bounds = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 16681306662221878741ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_source_address_wide = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 15595760530934477248ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_source_address_wide = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 15358913247823562188ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_input_channel = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9411881620785336441ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11107913821117915981ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2636621122330654230ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_next_kernel_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6033149404038288111ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_reduction_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14112425856250151243ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_tap_in_bounds = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 17078047432295025106ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_feature_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4850930956393373952ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_enable = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 5697139804263310059ull);
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 12908737793722345181ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 6014493900350247089ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[__Vi0] = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 9469685211791069632ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[__Vi0] = VL_SCOPED_RAND_RESET_Q(33, __VscopeHash, 10096495855394012867ull);
    }
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_bad_argument = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 1066713769358585484ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_overflow = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 12721438541776263274ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_lane = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2235889855539790327ull);
    VL_SCOPED_RAND_RESET_W(80, vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_parameter, __VscopeHash, 17098082190879896636ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_bias = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16050348095914175818ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_invalid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 10026152011562819962ull);
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        VL_SCOPED_RAND_RESET_W(80, vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_mq_parameter[__Vi0], __VscopeHash, 14648875925423686861ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_bias[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 140291592418346177ull);
    }
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_lane_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16386156341886374770ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requantized_value = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 15707716089727146040ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_point_scan_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2024317327695590387ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_point_scan_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5360619385881856665ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_byte_offset_wide = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 2631951127939833172ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_address_wide = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 14134493819334236850ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mapped_response_error = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 2619824505446794685ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__request_byte_lane = VL_SCOPED_RAND_RESET_I(2, __VscopeHash, 14192600385340166417ull);
    for (int __Vi0 = 0; __Vi0 < 4608; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 5906475569289162169ull);
    }
    for (int __Vi0 = 0; __Vi0 < 4608; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 14508785542876280747ull);
    }
    for (int __Vi0 = 0; __Vi0 < 4608; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 7286593653358260509ull);
    }
    for (int __Vi0 = 0; __Vi0 < 4608; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 944283541865504707ull);
    }
    for (int __Vi0 = 0; __Vi0 < 4608; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 13252434671478998359ull);
    }
    for (int __Vi0 = 0; __Vi0 < 4608; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 10153472578301468453ull);
    }
    for (int __Vi0 = 0; __Vi0 < 4608; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 8605697210911825742ull);
    }
    for (int __Vi0 = 0; __Vi0 < 4608; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 18393903067423535210ull);
    }
    vlSelf->__Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__map_conv_activation__21__descriptor_activation = 0;
    vlSelf->__Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__normalize_engine_error__22__code = 0;
    vlSelf->__Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__normalize_engine_error__23__Vfuncout = 0;
    vlSelf->__Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__normalize_engine_error__23__code = 0;
    vlSelf->__Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__normalize_engine_error__24__code = 0;
    vlSelf->__Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__normalize_engine_error__25__Vfuncout = 0;
    vlSelf->__Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__normalize_engine_error__25__code = 0;
    vlSelf->__VdfgRegularize_h6e95ff9d_0_6 = 0;
    vlSelf->__VdfgRegularize_h6e95ff9d_0_10 = 0;
    vlSelf->__VdfgRegularize_h6e95ff9d_0_11 = 0;
    vlSelf->__VdfgRegularize_h6e95ff9d_0_16 = 0;
    vlSelf->__VdfgRegularize_h6e95ff9d_0_17 = 0;
    vlSelf->__VdfgRegularize_h6e95ff9d_0_27 = 0;
    vlSelf->__VdfgRegularize_h6e95ff9d_0_187 = 0;
    vlSelf->__VdfgRegularize_h6e95ff9d_0_188 = 0;
    vlSelf->__VdfgRegularize_h6e95ff9d_0_189 = 0;
    VL_ZERO_RESET_W(65, vlSelf->__VdfgRegularize_h6e95ff9d_0_197);
    VL_ZERO_RESET_W(65, vlSelf->__VdfgRegularize_h6e95ff9d_0_198);
    for (int __Vi0 = 0; __Vi0 < 1; ++__Vi0) {
        vlSelf->__VstlTriggered[__Vi0] = 0;
    }
    for (int __Vi0 = 0; __Vi0 < 1; ++__Vi0) {
        vlSelf->__VactTriggered[__Vi0] = 0;
    }
    for (int __Vi0 = 0; __Vi0 < 1; ++__Vi0) {
        vlSelf->__VactTriggeredAcc[__Vi0] = 0;
    }
    vlSelf->__Vtrigprevexpr___TOP__tb_s2a_network_backend_golden__DOT__clk__0 = 0;
    for (int __Vi0 = 0; __Vi0 < 1; ++__Vi0) {
        vlSelf->__VnbaTriggered[__Vi0] = 0;
    }
    vlSelf->__Vi = 0;
}
