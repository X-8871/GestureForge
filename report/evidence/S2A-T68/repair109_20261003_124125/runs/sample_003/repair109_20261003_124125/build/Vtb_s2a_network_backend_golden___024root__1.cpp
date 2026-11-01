// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vtb_s2a_network_backend_golden.h for the primary calling header

#include "Vtb_s2a_network_backend_golden__pch.h"

void Vtb_s2a_network_backend_golden___024root___nba_sequent__TOP__0(Vtb_s2a_network_backend_golden___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_network_backend_golden___024root___nba_sequent__TOP__0\n"); );
    Vtb_s2a_network_backend_golden__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    CData/*7:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__candidate_value;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__candidate_value = 0;
    CData/*7:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__current_maximum;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__current_maximum = 0;
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
    CData/*7:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_magnitude;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_magnitude = 0;
    QData/*63:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__scaled_product;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__scaled_product = 0;
    QData/*63:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__rounded_magnitude;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__rounded_magnitude = 0;
    QData/*63:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__scaled_signed;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__scaled_signed = 0;
    IData/*31:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_source_index;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_source_index = 0;
    IData/*31:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_source_channel;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_source_channel = 0;
    QData/*63:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__patch_plane_bytes;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__patch_plane_bytes = 0;
    IData/*31:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_channel;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_channel = 0;
    IData/*31:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_rem;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_rem = 0;
    IData/*31:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_y;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_y = 0;
    IData/*31:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_x;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_x = 0;
    QData/*63:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_input_y;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_input_y = 0;
    QData/*63:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_input_x;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_input_x = 0;
    QData/*63:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_source_offset;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_source_offset = 0;
    IData/*31:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_area;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_area = 0;
    IData/*31:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_input_channel;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_input_channel = 0;
    IData/*31:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_y;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_y = 0;
    IData/*31:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_x;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_x = 0;
    IData/*31:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_y;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_y = 0;
    IData/*31:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_x;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_x = 0;
    QData/*63:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_input_y;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_input_y = 0;
    QData/*63:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_input_x;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_input_x = 0;
    CData/*0:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_tap_in_bounds;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_tap_in_bounds = 0;
    QData/*63:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index_wide;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index_wide = 0;
    IData/*31:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index = 0;
    IData/*31:0*/ __Vtask_tb_s2a_network_backend_golden__DOT__emit_progress__15__progress_marker_file_id;
    __Vtask_tb_s2a_network_backend_golden__DOT__emit_progress__15__progress_marker_file_id = 0;
    CData/*3:0*/ __Vfunc_tb_s2a_network_backend_golden__DOT__is_onehot4__16__value;
    __Vfunc_tb_s2a_network_backend_golden__DOT__is_onehot4__16__value = 0;
    IData/*31:0*/ __Vfunc_tb_s2a_network_backend_golden__DOT__classify_transfer__17__Vfuncout;
    __Vfunc_tb_s2a_network_backend_golden__DOT__classify_transfer__17__Vfuncout = 0;
    CData/*0:0*/ __Vfunc_tb_s2a_network_backend_golden__DOT__classify_transfer__17__write_request;
    __Vfunc_tb_s2a_network_backend_golden__DOT__classify_transfer__17__write_request = 0;
    IData/*31:0*/ __Vfunc_tb_s2a_network_backend_golden__DOT__classify_transfer__17__address;
    __Vfunc_tb_s2a_network_backend_golden__DOT__classify_transfer__17__address = 0;
    CData/*3:0*/ __Vfunc_tb_s2a_network_backend_golden__DOT__classify_transfer__17__read_strobe;
    __Vfunc_tb_s2a_network_backend_golden__DOT__classify_transfer__17__read_strobe = 0;
    IData/*31:0*/ __Vfunc_tb_s2a_network_backend_golden__DOT__classify_transfer__17__selected_lane;
    __Vfunc_tb_s2a_network_backend_golden__DOT__classify_transfer__17__selected_lane = 0;
    IData/*31:0*/ __Vfunc_tb_s2a_network_backend_golden__DOT__classify_transfer__17__lane_owner;
    __Vfunc_tb_s2a_network_backend_golden__DOT__classify_transfer__17__lane_owner = 0;
    IData/*31:0*/ __Vfunc_tb_s2a_network_backend_golden__DOT__classify_transfer__17__found_lane;
    __Vfunc_tb_s2a_network_backend_golden__DOT__classify_transfer__17__found_lane = 0;
    IData/*31:0*/ __Vfunc_tb_s2a_network_backend_golden__DOT__classify_transfer__17__selected_address;
    __Vfunc_tb_s2a_network_backend_golden__DOT__classify_transfer__17__selected_address = 0;
    IData/*31:0*/ __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__Vfuncout;
    __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__Vfuncout = 0;
    IData/*31:0*/ __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address;
    __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address = 0;
    IData/*31:0*/ __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout;
    __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0;
    IData/*31:0*/ __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address;
    __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address = 0;
    IData/*31:0*/ __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout;
    __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0;
    IData/*31:0*/ __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address;
    __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address = 0;
    CData/*1:0*/ __Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__map_conv_activation__26__Vfuncout;
    __Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__map_conv_activation__26__Vfuncout = 0;
    CData/*1:0*/ __Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__map_conv_activation__26__descriptor_activation;
    __Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__map_conv_activation__26__descriptor_activation = 0;
    CData/*2:0*/ __Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__normalize_engine_error__27__code;
    __Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__normalize_engine_error__27__code = 0;
    CData/*2:0*/ __Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__normalize_engine_error__28__code;
    __Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__normalize_engine_error__28__code = 0;
    QData/*63:0*/ __Vdly__tb_s2a_network_backend_golden__DOT__cycle_count;
    __Vdly__tb_s2a_network_backend_golden__DOT__cycle_count = 0;
    QData/*63:0*/ __Vdly__tb_s2a_network_backend_golden__DOT__next_progress_cycle;
    __Vdly__tb_s2a_network_backend_golden__DOT__next_progress_cycle = 0;
    IData/*31:0*/ __Vdly__tb_s2a_network_backend_golden__DOT__class_wait_count;
    __Vdly__tb_s2a_network_backend_golden__DOT__class_wait_count = 0;
    CData/*0:0*/ __Vdly__tb_s2a_network_backend_golden__DOT__stalled_previous;
    __Vdly__tb_s2a_network_backend_golden__DOT__stalled_previous = 0;
    IData/*31:0*/ __Vdly__tb_s2a_network_backend_golden__DOT__stalled_address;
    __Vdly__tb_s2a_network_backend_golden__DOT__stalled_address = 0;
    IData/*31:0*/ __Vdly__tb_s2a_network_backend_golden__DOT__stalled_data;
    __Vdly__tb_s2a_network_backend_golden__DOT__stalled_data = 0;
    CData/*0:0*/ __Vdly__tb_s2a_network_backend_golden__DOT__stalled_write;
    __Vdly__tb_s2a_network_backend_golden__DOT__stalled_write = 0;
    CData/*3:0*/ __Vdly__tb_s2a_network_backend_golden__DOT__stalled_rstrb;
    __Vdly__tb_s2a_network_backend_golden__DOT__stalled_rstrb = 0;
    CData/*3:0*/ __Vdly__tb_s2a_network_backend_golden__DOT__stalled_wstrb;
    __Vdly__tb_s2a_network_backend_golden__DOT__stalled_wstrb = 0;
    CData/*0:0*/ __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__response_pending;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__response_pending = 0;
    CData/*2:0*/ __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__state;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__state = 0;
    CData/*5:0*/ __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor = 0;
    IData/*31:0*/ __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_element_index;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_element_index = 0;
    CData/*3:0*/ __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__state;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__state = 0;
    CData/*2:0*/ __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__read_tap_index;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__read_tap_index = 0;
    CData/*2:0*/ __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__state;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__state = 0;
    IData/*31:0*/ __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__source_address_latched;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__source_address_latched = 0;
    CData/*3:0*/ __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__state;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__state = 0;
    IData/*31:0*/ __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_base_latched;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_base_latched = 0;
    IData/*31:0*/ __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_length_latched;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_length_latched = 0;
    IData/*31:0*/ __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_channels_latched;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_channels_latched = 0;
    IData/*31:0*/ __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_height_latched;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_height_latched = 0;
    IData/*31:0*/ __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_width_latched;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_width_latched = 0;
    IData/*31:0*/ __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source_index_latched;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source_index_latched = 0;
    CData/*4:0*/ __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state = 0;
    IData/*31:0*/ __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched = 0;
    IData/*31:0*/ __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_channels_latched;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_channels_latched = 0;
    IData/*31:0*/ __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_channels_latched;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_channels_latched = 0;
    IData/*31:0*/ __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_latched;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_latched = 0;
    IData/*31:0*/ __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_latched;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_latched = 0;
    IData/*31:0*/ __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_height_latched;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_height_latched = 0;
    IData/*31:0*/ __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_width_latched;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_width_latched = 0;
    IData/*31:0*/ __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__stride_y_latched;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__stride_y_latched = 0;
    IData/*31:0*/ __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__stride_x_latched;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__stride_x_latched = 0;
    IData/*31:0*/ __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_latched;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_latched = 0;
    IData/*31:0*/ __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base = 0;
    IData/*31:0*/ __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_y;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_y = 0;
    IData/*31:0*/ __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_x;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_x = 0;
    IData/*31:0*/ __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_height;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_height = 0;
    IData/*31:0*/ __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_width;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_width = 0;
    IData/*31:0*/ __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__patch_byte_count;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__patch_byte_count = 0;
    IData/*31:0*/ __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_point_count;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_point_count = 0;
    IData/*31:0*/ __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count = 0;
    IData/*31:0*/ __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_index;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_index = 0;
    IData/*31:0*/ __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_lane_index;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_lane_index = 0;
    IData/*31:0*/ __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_reduction_index;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_reduction_index = 0;
    IData/*31:0*/ __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_index;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_index = 0;
    IData/*31:0*/ __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_reduction_index;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_reduction_index = 0;
    IData/*31:0*/ __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_lane_index;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_lane_index = 0;
    IData/*31:0*/ __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_point_index;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_point_index = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_network_backend_golden__DOT__class_transfer_index__v0;
    __VdlyVal__tb_s2a_network_backend_golden__DOT__class_transfer_index__v0 = 0;
    CData/*1:0*/ __VdlyDim0__tb_s2a_network_backend_golden__DOT__class_transfer_index__v0;
    __VdlyDim0__tb_s2a_network_backend_golden__DOT__class_transfer_index__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_network_backend_golden__DOT__class_transfer_index__v0;
    __VdlySet__tb_s2a_network_backend_golden__DOT__class_transfer_index__v0 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_network_backend_golden__DOT__class_accepted_count__v0;
    __VdlyVal__tb_s2a_network_backend_golden__DOT__class_accepted_count__v0 = 0;
    CData/*1:0*/ __VdlyDim0__tb_s2a_network_backend_golden__DOT__class_accepted_count__v0;
    __VdlyDim0__tb_s2a_network_backend_golden__DOT__class_accepted_count__v0 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_network_backend_golden__DOT__feature_bytes__v0;
    __VdlyVal__tb_s2a_network_backend_golden__DOT__feature_bytes__v0 = 0;
    IData/*23:0*/ __VdlyDim0__tb_s2a_network_backend_golden__DOT__feature_bytes__v0;
    __VdlyDim0__tb_s2a_network_backend_golden__DOT__feature_bytes__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_network_backend_golden__DOT__feature_bytes__v0;
    __VdlySet__tb_s2a_network_backend_golden__DOT__feature_bytes__v0 = 0;
    IData/*23:0*/ __VdlyDim0__tb_s2a_network_backend_golden__DOT__feature_byte_valid__v0;
    __VdlyDim0__tb_s2a_network_backend_golden__DOT__feature_byte_valid__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_network_backend_golden__DOT__feature_byte_valid__v0;
    __VdlySet__tb_s2a_network_backend_golden__DOT__feature_byte_valid__v0 = 0;
    IData/*23:0*/ __VdlyDim0__tb_s2a_network_backend_golden__DOT__golden_byte_seen__v0;
    __VdlyDim0__tb_s2a_network_backend_golden__DOT__golden_byte_seen__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_network_backend_golden__DOT__golden_byte_seen__v0;
    __VdlySet__tb_s2a_network_backend_golden__DOT__golden_byte_seen__v0 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_network_backend_golden__DOT__feature_bytes__v1;
    __VdlyVal__tb_s2a_network_backend_golden__DOT__feature_bytes__v1 = 0;
    IData/*23:0*/ __VdlyDim0__tb_s2a_network_backend_golden__DOT__feature_bytes__v1;
    __VdlyDim0__tb_s2a_network_backend_golden__DOT__feature_bytes__v1 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_network_backend_golden__DOT__feature_bytes__v1;
    __VdlySet__tb_s2a_network_backend_golden__DOT__feature_bytes__v1 = 0;
    IData/*23:0*/ __VdlyDim0__tb_s2a_network_backend_golden__DOT__feature_byte_valid__v1;
    __VdlyDim0__tb_s2a_network_backend_golden__DOT__feature_byte_valid__v1 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_network_backend_golden__DOT__feature_byte_valid__v1;
    __VdlySet__tb_s2a_network_backend_golden__DOT__feature_byte_valid__v1 = 0;
    IData/*23:0*/ __VdlyDim0__tb_s2a_network_backend_golden__DOT__golden_byte_seen__v1;
    __VdlyDim0__tb_s2a_network_backend_golden__DOT__golden_byte_seen__v1 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_network_backend_golden__DOT__golden_byte_seen__v1;
    __VdlySet__tb_s2a_network_backend_golden__DOT__golden_byte_seen__v1 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_network_backend_golden__DOT__feature_bytes__v2;
    __VdlyVal__tb_s2a_network_backend_golden__DOT__feature_bytes__v2 = 0;
    IData/*23:0*/ __VdlyDim0__tb_s2a_network_backend_golden__DOT__feature_bytes__v2;
    __VdlyDim0__tb_s2a_network_backend_golden__DOT__feature_bytes__v2 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_network_backend_golden__DOT__feature_bytes__v2;
    __VdlySet__tb_s2a_network_backend_golden__DOT__feature_bytes__v2 = 0;
    IData/*23:0*/ __VdlyDim0__tb_s2a_network_backend_golden__DOT__feature_byte_valid__v2;
    __VdlyDim0__tb_s2a_network_backend_golden__DOT__feature_byte_valid__v2 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_network_backend_golden__DOT__feature_byte_valid__v2;
    __VdlySet__tb_s2a_network_backend_golden__DOT__feature_byte_valid__v2 = 0;
    IData/*23:0*/ __VdlyDim0__tb_s2a_network_backend_golden__DOT__golden_byte_seen__v2;
    __VdlyDim0__tb_s2a_network_backend_golden__DOT__golden_byte_seen__v2 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_network_backend_golden__DOT__golden_byte_seen__v2;
    __VdlySet__tb_s2a_network_backend_golden__DOT__golden_byte_seen__v2 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_network_backend_golden__DOT__feature_bytes__v3;
    __VdlyVal__tb_s2a_network_backend_golden__DOT__feature_bytes__v3 = 0;
    IData/*23:0*/ __VdlyDim0__tb_s2a_network_backend_golden__DOT__feature_bytes__v3;
    __VdlyDim0__tb_s2a_network_backend_golden__DOT__feature_bytes__v3 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_network_backend_golden__DOT__feature_bytes__v3;
    __VdlySet__tb_s2a_network_backend_golden__DOT__feature_bytes__v3 = 0;
    IData/*23:0*/ __VdlyDim0__tb_s2a_network_backend_golden__DOT__feature_byte_valid__v3;
    __VdlyDim0__tb_s2a_network_backend_golden__DOT__feature_byte_valid__v3 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_network_backend_golden__DOT__feature_byte_valid__v3;
    __VdlySet__tb_s2a_network_backend_golden__DOT__feature_byte_valid__v3 = 0;
    IData/*23:0*/ __VdlyDim0__tb_s2a_network_backend_golden__DOT__golden_byte_seen__v3;
    __VdlyDim0__tb_s2a_network_backend_golden__DOT__golden_byte_seen__v3 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_network_backend_golden__DOT__golden_byte_seen__v3;
    __VdlySet__tb_s2a_network_backend_golden__DOT__golden_byte_seen__v3 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_network_backend_golden__DOT__layer_write_count__v0;
    __VdlyVal__tb_s2a_network_backend_golden__DOT__layer_write_count__v0 = 0;
    CData/*5:0*/ __VdlyDim0__tb_s2a_network_backend_golden__DOT__layer_write_count__v0;
    __VdlyDim0__tb_s2a_network_backend_golden__DOT__layer_write_count__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_network_backend_golden__DOT__layer_write_count__v0;
    __VdlySet__tb_s2a_network_backend_golden__DOT__layer_write_count__v0 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_network_backend_golden__DOT__class_selected_byte_count__v0;
    __VdlyVal__tb_s2a_network_backend_golden__DOT__class_selected_byte_count__v0 = 0;
    CData/*1:0*/ __VdlyDim0__tb_s2a_network_backend_golden__DOT__class_selected_byte_count__v0;
    __VdlyDim0__tb_s2a_network_backend_golden__DOT__class_selected_byte_count__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_network_backend_golden__DOT__class_selected_byte_count__v0;
    __VdlySet__tb_s2a_network_backend_golden__DOT__class_selected_byte_count__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched__v0;
    __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched__v1;
    __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched__v1 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched__v4;
    __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched__v4 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched__v5;
    __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched__v5 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched__v8;
    __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched__v8 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched__v8;
    __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched__v8 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched__v9;
    __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched__v9 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched__v9;
    __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched__v9 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched__v10;
    __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched__v10 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched__v11;
    __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched__v11 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v0;
    __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v0 = 0;
    SData/*8:0*/ __VdlyDim0__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v0;
    __VdlyDim0__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v0;
    __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v0 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v1;
    __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v1 = 0;
    SData/*8:0*/ __VdlyDim0__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v1;
    __VdlyDim0__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v1 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v1;
    __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v1 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v2;
    __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v2 = 0;
    SData/*8:0*/ __VdlyDim0__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v2;
    __VdlyDim0__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v2 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v2;
    __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v2 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v3;
    __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v3 = 0;
    SData/*8:0*/ __VdlyDim0__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v3;
    __VdlyDim0__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v3 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v3;
    __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v3 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v4;
    __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v4 = 0;
    SData/*8:0*/ __VdlyDim0__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v4;
    __VdlyDim0__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v4 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v4;
    __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v4 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v5;
    __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v5 = 0;
    SData/*8:0*/ __VdlyDim0__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v5;
    __VdlyDim0__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v5 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v5;
    __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v5 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v6;
    __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v6 = 0;
    SData/*8:0*/ __VdlyDim0__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v6;
    __VdlyDim0__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v6 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v6;
    __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v6 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v7;
    __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v7 = 0;
    SData/*8:0*/ __VdlyDim0__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v7;
    __VdlyDim0__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v7 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v7;
    __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v7 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v0;
    __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v0;
    __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v0 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v1;
    __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v1 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v1;
    __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v1 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v2;
    __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v2 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v2;
    __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v2 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v3;
    __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v3 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v3;
    __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v3 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v4;
    __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v4 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v4;
    __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v4 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v5;
    __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v5 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v5;
    __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v5 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v6;
    __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v6 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v6;
    __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v6 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v7;
    __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v7 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v7;
    __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v7 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v8;
    __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v8 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v8;
    __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v8 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v9;
    __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v9 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v9;
    __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v9 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v10;
    __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v10 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v11;
    __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v11 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v12;
    __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v12 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v13;
    __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v13 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v14;
    __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v14 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v15;
    __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v15 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v16;
    __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v16 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v16;
    __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v16 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v17;
    __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v17 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v17;
    __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v17 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v18;
    __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v18 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v19;
    __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v19 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v20;
    __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v20 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v21;
    __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v21 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v22;
    __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v22 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v23;
    __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v23 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_group__v0;
    __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_group__v0 = 0;
    SData/*15:0*/ __VdlyDim0__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_group__v0;
    __VdlyDim0__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_group__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_group__v0;
    __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_group__v0 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_patch__v0;
    __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_patch__v0 = 0;
    SData/*15:0*/ __VdlyDim0__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_patch__v0;
    __VdlyDim0__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_patch__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_patch__v0;
    __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_patch__v0 = 0;
    SData/*15:0*/ __VdlyDim0__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_patch__v1;
    __VdlyDim0__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_patch__v1 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_patch__v1;
    __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_patch__v1 = 0;
    VlWide<4>/*127:0*/ __Vtemp_1;
    VlWide<3>/*95:0*/ __Vtemp_4;
    VlWide<3>/*95:0*/ __Vtemp_5;
    VlWide<3>/*95:0*/ __Vtemp_6;
    VlWide<3>/*95:0*/ __Vtemp_7;
    VlWide<3>/*95:0*/ __Vtemp_8;
    VlWide<3>/*95:0*/ __Vtemp_9;
    VlWide<3>/*95:0*/ __Vtemp_10;
    VlWide<3>/*95:0*/ __Vtemp_12;
    VlWide<3>/*95:0*/ __Vtemp_13;
    VlWide<3>/*95:0*/ __Vtemp_14;
    VlWide<3>/*95:0*/ __Vtemp_15;
    VlWide<3>/*95:0*/ __Vtemp_16;
    VlWide<3>/*95:0*/ __Vtemp_17;
    VlWide<3>/*95:0*/ __Vtemp_18;
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
    VlWide<3>/*95:0*/ __Vtemp_32;
    VlWide<3>/*95:0*/ __Vtemp_33;
    VlWide<3>/*95:0*/ __Vtemp_35;
    VlWide<3>/*95:0*/ __Vtemp_36;
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
    VlWide<3>/*95:0*/ __Vtemp_50;
    VlWide<3>/*95:0*/ __Vtemp_51;
    VlWide<3>/*95:0*/ __Vtemp_53;
    VlWide<3>/*95:0*/ __Vtemp_54;
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
    VlWide<3>/*95:0*/ __Vtemp_68;
    VlWide<3>/*95:0*/ __Vtemp_69;
    VlWide<3>/*95:0*/ __Vtemp_71;
    VlWide<3>/*95:0*/ __Vtemp_72;
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
    VlWide<3>/*95:0*/ __Vtemp_86;
    VlWide<3>/*95:0*/ __Vtemp_87;
    VlWide<3>/*95:0*/ __Vtemp_89;
    VlWide<3>/*95:0*/ __Vtemp_90;
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
    VlWide<3>/*95:0*/ __Vtemp_104;
    VlWide<3>/*95:0*/ __Vtemp_105;
    VlWide<3>/*95:0*/ __Vtemp_107;
    VlWide<3>/*95:0*/ __Vtemp_108;
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
    VlWide<3>/*95:0*/ __Vtemp_122;
    VlWide<3>/*95:0*/ __Vtemp_123;
    VlWide<3>/*95:0*/ __Vtemp_125;
    VlWide<3>/*95:0*/ __Vtemp_126;
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
    VlWide<3>/*95:0*/ __Vtemp_140;
    VlWide<3>/*95:0*/ __Vtemp_141;
    VlWide<3>/*95:0*/ __Vtemp_143;
    VlWide<3>/*95:0*/ __Vtemp_144;
    VlWide<3>/*95:0*/ __Vtemp_145;
    VlWide<3>/*95:0*/ __Vtemp_146;
    VlWide<3>/*95:0*/ __Vtemp_147;
    VlWide<3>/*95:0*/ __Vtemp_148;
    VlWide<3>/*95:0*/ __Vtemp_149;
    VlWide<3>/*95:0*/ __Vtemp_150;
    VlWide<3>/*95:0*/ __Vtemp_151;
    VlWide<3>/*95:0*/ __Vtemp_152;
    VlWide<3>/*95:0*/ __Vtemp_153;
    VlWide<3>/*95:0*/ __Vtemp_154;
    VlWide<3>/*95:0*/ __Vtemp_155;
    VlWide<3>/*95:0*/ __Vtemp_156;
    VlWide<3>/*95:0*/ __Vtemp_158;
    VlWide<3>/*95:0*/ __Vtemp_159;
    VlWide<3>/*95:0*/ __Vtemp_162;
    VlWide<3>/*95:0*/ __Vtemp_164;
    VlWide<3>/*95:0*/ __Vtemp_165;
    VlWide<3>/*95:0*/ __Vtemp_166;
    VlWide<3>/*95:0*/ __Vtemp_167;
    VlWide<3>/*95:0*/ __Vtemp_168;
    VlWide<3>/*95:0*/ __Vtemp_169;
    VlWide<3>/*95:0*/ __Vtemp_170;
    // Body
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__response_pending 
        = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__response_pending;
    __Vdly__tb_s2a_network_backend_golden__DOT__cycle_count 
        = vlSelfRef.tb_s2a_network_backend_golden__DOT__cycle_count;
    __Vdly__tb_s2a_network_backend_golden__DOT__next_progress_cycle 
        = vlSelfRef.tb_s2a_network_backend_golden__DOT__next_progress_cycle;
    __Vdly__tb_s2a_network_backend_golden__DOT__stalled_previous 
        = vlSelfRef.tb_s2a_network_backend_golden__DOT__stalled_previous;
    __Vdly__tb_s2a_network_backend_golden__DOT__stalled_address 
        = vlSelfRef.tb_s2a_network_backend_golden__DOT__stalled_address;
    __Vdly__tb_s2a_network_backend_golden__DOT__stalled_data 
        = vlSelfRef.tb_s2a_network_backend_golden__DOT__stalled_data;
    __Vdly__tb_s2a_network_backend_golden__DOT__stalled_write 
        = vlSelfRef.tb_s2a_network_backend_golden__DOT__stalled_write;
    __Vdly__tb_s2a_network_backend_golden__DOT__stalled_rstrb 
        = vlSelfRef.tb_s2a_network_backend_golden__DOT__stalled_rstrb;
    __Vdly__tb_s2a_network_backend_golden__DOT__stalled_wstrb 
        = vlSelfRef.tb_s2a_network_backend_golden__DOT__stalled_wstrb;
    __VdlySet__tb_s2a_network_backend_golden__DOT__layer_write_count__v0 = 0U;
    __VdlySet__tb_s2a_network_backend_golden__DOT__class_selected_byte_count__v0 = 0U;
    __VdlySet__tb_s2a_network_backend_golden__DOT__golden_byte_seen__v0 = 0U;
    __VdlySet__tb_s2a_network_backend_golden__DOT__golden_byte_seen__v1 = 0U;
    __VdlySet__tb_s2a_network_backend_golden__DOT__golden_byte_seen__v2 = 0U;
    __VdlySet__tb_s2a_network_backend_golden__DOT__golden_byte_seen__v3 = 0U;
    __VdlySet__tb_s2a_network_backend_golden__DOT__feature_bytes__v0 = 0U;
    __VdlySet__tb_s2a_network_backend_golden__DOT__feature_bytes__v1 = 0U;
    __VdlySet__tb_s2a_network_backend_golden__DOT__feature_bytes__v2 = 0U;
    __VdlySet__tb_s2a_network_backend_golden__DOT__feature_bytes__v3 = 0U;
    __Vdly__tb_s2a_network_backend_golden__DOT__class_wait_count 
        = vlSelfRef.tb_s2a_network_backend_golden__DOT__class_wait_count;
    __VdlySet__tb_s2a_network_backend_golden__DOT__class_transfer_index__v0 = 0U;
    __VdlySet__tb_s2a_network_backend_golden__DOT__feature_byte_valid__v0 = 0U;
    __VdlySet__tb_s2a_network_backend_golden__DOT__feature_byte_valid__v1 = 0U;
    __VdlySet__tb_s2a_network_backend_golden__DOT__feature_byte_valid__v2 = 0U;
    __VdlySet__tb_s2a_network_backend_golden__DOT__feature_byte_valid__v3 = 0U;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_element_index 
        = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_element_index;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor 
        = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_height 
        = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_height;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__patch_byte_count 
        = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__patch_byte_count;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_point_count 
        = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_point_count;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_lane_index 
        = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_lane_index;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_reduction_index 
        = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_reduction_index;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_lane_index 
        = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_lane_index;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_point_index 
        = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_point_index;
    __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v0 = 0U;
    __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v1 = 0U;
    __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v2 = 0U;
    __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v3 = 0U;
    __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v4 = 0U;
    __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v5 = 0U;
    __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v6 = 0U;
    __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v7 = 0U;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base 
        = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_channels_latched 
        = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_channels_latched;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_channels_latched 
        = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_channels_latched;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_index 
        = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_index;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_index 
        = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_index;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_reduction_index 
        = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_reduction_index;
    __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_group__v0 = 0U;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_latched 
        = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_latched;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_latched 
        = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_latched;
    __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_patch__v0 = 0U;
    __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_patch__v1 = 0U;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_latched 
        = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_latched;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_y 
        = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_y;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_x 
        = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_x;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_width 
        = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_width;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched 
        = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count 
        = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count;
    __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v0 = 0U;
    __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v1 = 0U;
    __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v2 = 0U;
    __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v3 = 0U;
    __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v4 = 0U;
    __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v5 = 0U;
    __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v6 = 0U;
    __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v7 = 0U;
    __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v8 = 0U;
    __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v9 = 0U;
    __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v16 = 0U;
    __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v17 = 0U;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_height_latched 
        = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_height_latched;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_width_latched 
        = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_width_latched;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__stride_y_latched 
        = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__stride_y_latched;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__stride_x_latched 
        = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__stride_x_latched;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state 
        = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__state 
        = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__state;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_base_latched 
        = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_base_latched;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_length_latched 
        = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_length_latched;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_channels_latched 
        = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_channels_latched;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source_index_latched 
        = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source_index_latched;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_height_latched 
        = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_height_latched;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_width_latched 
        = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_width_latched;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__state 
        = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__state;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__source_address_latched 
        = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__source_address_latched;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__state 
        = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__state;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__read_tap_index 
        = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__read_tap_index;
    __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched__v0 = 0U;
    __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched__v1 = 0U;
    __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched__v4 = 0U;
    __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched__v5 = 0U;
    __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched__v8 = 0U;
    __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched__v9 = 0U;
    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__state 
        = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__state;
    if (vlSelfRef.tb_s2a_network_backend_golden__DOT__hard_reset) {
        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__response_pending = 0U;
    } else {
        if (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__response_pending) {
            __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__response_pending = 0U;
        }
        if (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__memory_handshake) {
            __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__response_pending = 1U;
        }
    }
    if (vlSelfRef.tb_s2a_network_backend_golden__DOT__hard_reset) {
        __Vdly__tb_s2a_network_backend_golden__DOT__cycle_count = 0ULL;
        __Vdly__tb_s2a_network_backend_golden__DOT__next_progress_cycle = 0x0000000001c9c380ULL;
        __Vdly__tb_s2a_network_backend_golden__DOT__class_wait_count = 0U;
        __Vdly__tb_s2a_network_backend_golden__DOT__stalled_previous = 0U;
        __Vdly__tb_s2a_network_backend_golden__DOT__stalled_address = 0U;
        __Vdly__tb_s2a_network_backend_golden__DOT__stalled_data = 0U;
        __Vdly__tb_s2a_network_backend_golden__DOT__stalled_write = 0U;
        __Vdly__tb_s2a_network_backend_golden__DOT__stalled_rstrb = 0U;
        __Vdly__tb_s2a_network_backend_golden__DOT__stalled_wstrb = 0U;
    } else {
        __Vdly__tb_s2a_network_backend_golden__DOT__cycle_count 
            = (1ULL + vlSelfRef.tb_s2a_network_backend_golden__DOT__cycle_count);
        if (VL_UNLIKELY(((vlSelfRef.tb_s2a_network_backend_golden__DOT__cycle_count 
                          >= vlSelfRef.tb_s2a_network_backend_golden__DOT__next_progress_cycle)))) {
            __Vdly__tb_s2a_network_backend_golden__DOT__next_progress_cycle 
                = (0x0000000001c9c380ULL + vlSelfRef.tb_s2a_network_backend_golden__DOT__next_progress_cycle);
            __Vtask_tb_s2a_network_backend_golden__DOT__emit_progress__15__progress_marker_file_id 
                = VL_FOPEN_NN(vlSelfRef.tb_s2a_network_backend_golden__DOT__progress_file_path
                              , "a"s);
            ;
            if (VL_UNLIKELY(((0U == __Vtask_tb_s2a_network_backend_golden__DOT__emit_progress__15__progress_marker_file_id)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_network_backend_golden.sv:245: Assertion failed in %m: T68 \346\227\240\346\263\225\350\277\275\345\212\240 progress marker\357\274\232%s\n",4, 'M',vlSymsp->name(),"tb_s2a_network_backend_golden.emit_progress", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000)
                             , 'S',&(vlSelfRef.tb_s2a_network_backend_golden__DOT__progress_file_path));
                VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_network_backend_golden.sv", 245, "", false);
            }
            VL_FWRITEF_NX(__Vtask_tb_s2a_network_backend_golden__DOT__emit_progress__15__progress_marker_file_id,"S2A_PROGRESS sample=%0d layer=%0d cycle=%0d output=%0d conv_tile_y=%0d conv_tile_x=%0d conv_group=%0d conv_point=%0d conv_reduction=%0d conv_feature_scan=%0d conv_weight_reduction=%0d conv_output_lane=%0d conv_output_point=%0d pool_tap=%0d feature_write_bytes=%0d read_transactions=%0d write_transactions=%0d phase=running\n",17
                          , '~',32,vlSelfRef.tb_s2a_network_backend_golden__DOT__sample_index
                          , '#',6,(IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor)
                          , '#',64,vlSelfRef.tb_s2a_network_backend_golden__DOT__cycle_count
                          , '#',32,vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_element_index
                          , '#',32,vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_y
                          , '#',32,vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_x
                          , '#',32,vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base
                          , '#',32,vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_index
                          , '#',32,vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_reduction_index
                          , '#',32,vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_index
                          , '#',32,vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_reduction_index
                          , '#',32,vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_lane_index
                          , '#',32,vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_point_index
                          , '#',3,(IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__read_tap_index)
                          , '~',32,vlSelfRef.tb_s2a_network_backend_golden__DOT__total_feature_write_bytes
                          , '~',32,vlSelfRef.tb_s2a_network_backend_golden__DOT__total_memory_read_transactions
                          , '~',32,vlSelfRef.tb_s2a_network_backend_golden__DOT__total_memory_write_transactions);
            VL_FFLUSH_I(__Vtask_tb_s2a_network_backend_golden__DOT__emit_progress__15__progress_marker_file_id);
            VL_FCLOSE_I(__Vtask_tb_s2a_network_backend_golden__DOT__emit_progress__15__progress_marker_file_id); VL_WRITEF_NX("S2A_PROGRESS sample=%0d layer=%0d cycle=%0d output=%0d conv_tile_y=%0d conv_tile_x=%0d conv_group=%0d conv_point=%0d conv_reduction=%0d conv_feature_scan=%0d conv_weight_reduction=%0d conv_output_lane=%0d conv_output_point=%0d pool_tap=%0d feature_write_bytes=%0d read_transactions=%0d write_transactions=%0d phase=running\n",17
                                                                                , '~',32,vlSelfRef.tb_s2a_network_backend_golden__DOT__sample_index
                                                                                , '#',6,(IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor)
                                                                                , '#',64,vlSelfRef.tb_s2a_network_backend_golden__DOT__cycle_count
                                                                                , '#',32,vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_element_index
                                                                                , '#',32,vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_y
                                                                                , '#',32,vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_x
                                                                                , '#',32,vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base
                                                                                , '#',32,vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_index
                                                                                , '#',32,vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_reduction_index
                                                                                , '#',32,vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_index
                                                                                , '#',32,vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_reduction_index
                                                                                , '#',32,vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_lane_index
                                                                                , '#',32,vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_point_index
                                                                                , '#',3,(IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__read_tap_index)
                                                                                , '~',32,vlSelfRef.tb_s2a_network_backend_golden__DOT__total_feature_write_bytes
                                                                                , '~',32,vlSelfRef.tb_s2a_network_backend_golden__DOT__total_memory_read_transactions
                                                                                , '~',32,vlSelfRef.tb_s2a_network_backend_golden__DOT__total_memory_write_transactions);
            VL_FFLUSH_MT();}
        __Vfunc_tb_s2a_network_backend_golden__DOT__is_onehot4__16__value 
            = vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_rstrb;
        vlSelfRef.tb_s2a_network_backend_golden__DOT____VlemCall_10__is_onehot4 
            = (1U & (0x0116U >> (IData)(__Vfunc_tb_s2a_network_backend_golden__DOT__is_onehot4__16__value)));
        if (VL_UNLIKELY(((((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_valid) 
                           & (~ (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_write))) 
                          & (~ (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT____VlemCall_10__is_onehot4)))))) {
            VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_network_backend_golden.sv:578: Assertion failed in %m: T68 \345\220\216\347\253\257\350\257\273\350\257\267\346\261\202\345\277\205\351\241\273\346\257\217\346\254\241\345\217\252\351\200\211\344\270\200\344\270\252 byte lane\357\274\232addr=%08h rstrb=%b\n",5, 'M',vlSymsp->name(),"tb_s2a_network_backend_golden", 'T',-9
                         , '#',64,VL_TIME_UNITED_Q(1000)
                         , '#',32,vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr
                         , '#',4,(IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_rstrb));
            VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_network_backend_golden.sv", 578, "", false);
        }
        if (VL_UNLIKELY(((((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_valid) 
                           & (~ (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_write))) 
                          & (0U != (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_error_code)))))) {
            VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_network_backend_golden.sv:582: Assertion failed in %m: T68 \345\220\216\347\253\257\350\257\273\350\257\267\346\261\202\347\232\204\351\200\211\344\270\255\345\255\227\350\212\202\350\266\212\350\277\207 tensor/object \350\276\271\347\225\214\346\210\226\351\235\236\346\263\225\357\274\232addr=%08h rstrb=%b code=%0d\n",6, 'M',vlSymsp->name(),"tb_s2a_network_backend_golden", 'T',-9
                         , '#',64,VL_TIME_UNITED_Q(1000)
                         , '#',32,vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr
                         , '#',4,(IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_rstrb)
                         , '#',3,vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_error_code);
            VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_network_backend_golden.sv", 582, "", false);
        }
        if (VL_UNLIKELY((((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__stalled_previous) 
                          & ((((((~ (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_valid)) 
                                 | (vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr 
                                    != vlSelfRef.tb_s2a_network_backend_golden__DOT__stalled_address)) 
                                | ((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_write) 
                                   != (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__stalled_write))) 
                               | (vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_wdata 
                                  != vlSelfRef.tb_s2a_network_backend_golden__DOT__stalled_data)) 
                              | ((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_rstrb) 
                                 != (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__stalled_rstrb))) 
                             | ((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_wstrb) 
                                != (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__stalled_wstrb))))))) {
            VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_network_backend_golden.sv:588: Assertion failed in %m: T68 request signals changed while stalled\n",3, 'M',vlSymsp->name(),"tb_s2a_network_backend_golden", 'T',-9
                         , '#',64,VL_TIME_UNITED_Q(1000));
            VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_network_backend_golden.sv", 588, "", false);
        }
        if (VL_UNLIKELY((((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__backend_memory_error_valid) 
                          | (0U != (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_error_code)))))) {
            VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_network_backend_golden.sv:603: Assertion failed in %m: T68 backend memory error\357\274\232valid=%0d code=%0d\n",5, 'M',vlSymsp->name(),"tb_s2a_network_backend_golden", 'T',-9
                         , '#',64,VL_TIME_UNITED_Q(1000)
                         , '#',1,(IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__backend_memory_error_valid)
                         , '#',3,vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_error_code);
            VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_network_backend_golden.sv", 603, "", false);
        }
        if (((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_valid) 
             & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_ready))) {
            if (VL_UNLIKELY(((0U != (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_error_code))))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_network_backend_golden.sv:608: Assertion failed in %m: T68 memory model error\357\274\232code=%0d addr=%08h write=%0d\n",6, 'M',vlSymsp->name(),"tb_s2a_network_backend_golden", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000)
                             , '#',3,(IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_error_code)
                             , '#',32,vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr
                             , '#',1,(IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_write));
                VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_network_backend_golden.sv", 608, "", false);
            }
            __Vfunc_tb_s2a_network_backend_golden__DOT__classify_transfer__17__read_strobe 
                = vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_rstrb;
            __Vfunc_tb_s2a_network_backend_golden__DOT__classify_transfer__17__address 
                = vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr;
            __Vfunc_tb_s2a_network_backend_golden__DOT__classify_transfer__17__write_request 
                = vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_write;
            __Vfunc_tb_s2a_network_backend_golden__DOT__classify_transfer__17__selected_lane = 0;
            __Vfunc_tb_s2a_network_backend_golden__DOT__classify_transfer__17__lane_owner = 0;
            __Vfunc_tb_s2a_network_backend_golden__DOT__classify_transfer__17__found_lane = 0;
            __Vfunc_tb_s2a_network_backend_golden__DOT__classify_transfer__17__selected_address = 0;
            if (__Vfunc_tb_s2a_network_backend_golden__DOT__classify_transfer__17__write_request) {
                __Vfunc_tb_s2a_network_backend_golden__DOT__classify_transfer__17__Vfuncout = 3U;
            } else {
                __Vfunc_tb_s2a_network_backend_golden__DOT__classify_transfer__17__selected_lane = 0U;
                __Vfunc_tb_s2a_network_backend_golden__DOT__classify_transfer__17__found_lane = 0U;
                if ((1U & (IData)(__Vfunc_tb_s2a_network_backend_golden__DOT__classify_transfer__17__read_strobe))) {
                    __Vfunc_tb_s2a_network_backend_golden__DOT__classify_transfer__17__selected_lane = 0U;
                    __Vfunc_tb_s2a_network_backend_golden__DOT__classify_transfer__17__found_lane = 1U;
                }
                if ((1U & (((IData)(__Vfunc_tb_s2a_network_backend_golden__DOT__classify_transfer__17__read_strobe) 
                            >> 1U) & (~ (0U != __Vfunc_tb_s2a_network_backend_golden__DOT__classify_transfer__17__found_lane))))) {
                    __Vfunc_tb_s2a_network_backend_golden__DOT__classify_transfer__17__selected_lane = 1U;
                    __Vfunc_tb_s2a_network_backend_golden__DOT__classify_transfer__17__found_lane = 1U;
                }
                if ((1U & (((IData)(__Vfunc_tb_s2a_network_backend_golden__DOT__classify_transfer__17__read_strobe) 
                            >> 2U) & (~ (0U != __Vfunc_tb_s2a_network_backend_golden__DOT__classify_transfer__17__found_lane))))) {
                    __Vfunc_tb_s2a_network_backend_golden__DOT__classify_transfer__17__selected_lane = 2U;
                    __Vfunc_tb_s2a_network_backend_golden__DOT__classify_transfer__17__found_lane = 1U;
                }
                if ((IData)((((IData)(__Vfunc_tb_s2a_network_backend_golden__DOT__classify_transfer__17__read_strobe) 
                              >> 3U) & (~ (0U != __Vfunc_tb_s2a_network_backend_golden__DOT__classify_transfer__17__found_lane))))) {
                    __Vfunc_tb_s2a_network_backend_golden__DOT__classify_transfer__17__selected_lane = 3U;
                    __Vfunc_tb_s2a_network_backend_golden__DOT__classify_transfer__17__found_lane = 1U;
                }
                __Vfunc_tb_s2a_network_backend_golden__DOT__classify_transfer__17__selected_address 
                    = (__Vfunc_tb_s2a_network_backend_golden__DOT__classify_transfer__17__address 
                       + __Vfunc_tb_s2a_network_backend_golden__DOT__classify_transfer__17__selected_lane);
                __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address 
                    = __Vfunc_tb_s2a_network_backend_golden__DOT__classify_transfer__17__selected_address;
                __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__Vfuncout = 0xffffffffU;
                if ((0x0007ec00U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address)) {
                    __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__Vfuncout = 0U;
                } else if (((0x00100000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address) 
                            & (0x006a12fcU > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address))) {
                    __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__Vfuncout = 1U;
                } else {
                    if (((0x01000000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address) 
                         & (0x01152000U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__Vfuncout = 2U;
                    }
                    if (((0x01152000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address) 
                         & (0x011fb000U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__Vfuncout = 3U;
                    }
                    if (((0x011fb000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address) 
                         & (0x012a4000U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__Vfuncout = 4U;
                    }
                    if (((0x012a4000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address) 
                         & (0x012f8800U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__Vfuncout = 5U;
                    }
                    if (((0x012f8800U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address) 
                         & (0x0134d000U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__Vfuncout = 6U;
                    }
                    if (((0x0134d000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address) 
                         & (0x013a1800U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__Vfuncout = 7U;
                    }
                    if (((0x013a1800U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address) 
                         & (0x0144a800U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__Vfuncout = 8U;
                    }
                    if (((0x0144a800U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address) 
                         & (0x014f3800U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__Vfuncout = 9U;
                    }
                    if (((0x014f3800U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address) 
                         & (0x01645800U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__Vfuncout = 0x0000000aU;
                    }
                    if (((0x01645800U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address) 
                         & (0x0169a000U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__Vfuncout = 0x0000000bU;
                    }
                    if (((0x0169a000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address) 
                         & (0x016ee800U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__Vfuncout = 0x0000000cU;
                    }
                    if (((0x016ee800U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address) 
                         & (0x01718c00U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__Vfuncout = 0x0000000dU;
                    }
                    if (((0x01718c00U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address) 
                         & (0x01743000U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__Vfuncout = 0x0000000eU;
                    }
                    if (((0x01743000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address) 
                         & (0x0176d400U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__Vfuncout = 0x0000000fU;
                    }
                    if (((0x0176d400U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address) 
                         & (0x017c1c00U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__Vfuncout = 0x00000010U;
                    }
                    if (((0x017c1c00U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address) 
                         & (0x01816400U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__Vfuncout = 0x00000011U;
                    }
                    if (((0x01816400U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address) 
                         & (0x018bf400U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__Vfuncout = 0x00000012U;
                    }
                    if (((0x018bf400U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address) 
                         & (0x018e9800U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__Vfuncout = 0x00000013U;
                    }
                    if (((0x018e9800U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address) 
                         & (0x01913c00U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__Vfuncout = 0x00000014U;
                    }
                    if (((0x01913c00U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address) 
                         & (0x01928e00U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__Vfuncout = 0x00000015U;
                    }
                    if (((0x01928e00U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address) 
                         & (0x0193e000U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__Vfuncout = 0x00000016U;
                    }
                    if (((0x0193e000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address) 
                         & (0x01953200U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__Vfuncout = 0x00000017U;
                    }
                    if (((0x01953200U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address) 
                         & (0x0197d600U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__Vfuncout = 0x00000018U;
                    }
                    if (((0x0197d600U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address) 
                         & (0x019a7a00U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__Vfuncout = 0x00000019U;
                    }
                    if (((0x019a7a00U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address) 
                         & (0x019fc200U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__Vfuncout = 0x0000001aU;
                    }
                    if (((0x019fc200U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address) 
                         & (0x01a11400U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__Vfuncout = 0x0000001bU;
                    }
                    if (((0x01a11400U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address) 
                         & (0x01a26600U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__Vfuncout = 0x0000001cU;
                    }
                    if (((0x01a26600U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address) 
                         & (0x01a30f00U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__Vfuncout = 0x0000001dU;
                    }
                    if (((0x01a30f00U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address) 
                         & (0x01a46100U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__Vfuncout = 0x0000001eU;
                    }
                    if (((0x01a46100U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address) 
                         & (0x01a474ceU > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__Vfuncout = 0x0000001fU;
                    }
                    if (((0x01a47500U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address) 
                         & (0x01a51e00U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__Vfuncout = 0x00000021U;
                    }
                    if (((0x01a51e00U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address) 
                         & (0x01a57280U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__Vfuncout = 0x00000022U;
                    }
                    if (((0x01a57280U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address) 
                         & (0x01a6c480U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__Vfuncout = 0x00000023U;
                    }
                    if (((0x01a6c480U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address) 
                         & (0x01aaba80U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__Vfuncout = 0x00000024U;
                    }
                    if (((0x01aaba80U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address) 
                         & (0x01ad5e80U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__Vfuncout = 0x00000025U;
                    }
                    if (((0x01ad5e80U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address) 
                         & (0x01adadb8U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__Vfuncout = 0x00000026U;
                    }
                }
                __Vfunc_tb_s2a_network_backend_golden__DOT__classify_transfer__17__lane_owner 
                    = __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__18__Vfuncout;
                __Vfunc_tb_s2a_network_backend_golden__DOT__classify_transfer__17__Vfuncout 
                    = ((0U == __Vfunc_tb_s2a_network_backend_golden__DOT__classify_transfer__17__lane_owner)
                        ? 0U : ((1U == __Vfunc_tb_s2a_network_backend_golden__DOT__classify_transfer__17__lane_owner)
                                 ? 1U : 2U));
            }
            vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_transfer_class 
                = __Vfunc_tb_s2a_network_backend_golden__DOT__classify_transfer__17__Vfuncout;
            __VdlyVal__tb_s2a_network_backend_golden__DOT__class_transfer_index__v0 
                = ((IData)(1U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__class_transfer_index
                   [(3U & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_transfer_class)]);
            __VdlyDim0__tb_s2a_network_backend_golden__DOT__class_transfer_index__v0 
                = (3U & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_transfer_class);
            __VdlySet__tb_s2a_network_backend_golden__DOT__class_transfer_index__v0 = 1U;
            __VdlyVal__tb_s2a_network_backend_golden__DOT__class_accepted_count__v0 
                = ((IData)(1U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__class_accepted_count
                   [(3U & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_transfer_class)]);
            __VdlyDim0__tb_s2a_network_backend_golden__DOT__class_accepted_count__v0 
                = (3U & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_transfer_class);
            vlSelfRef.tb_s2a_network_backend_golden__DOT__active_byte_count = 0U;
            if (vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_write) {
                vlSelfRef.tb_s2a_network_backend_golden__DOT__total_memory_write_transactions 
                    = ((IData)(1U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__total_memory_write_transactions);
                vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_owner = 0xffffffffU;
                if ((1U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_wstrb))) {
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__active_byte_count 
                        = ((IData)(1U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__active_byte_count);
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_address 
                        = vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr;
                    __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address 
                        = vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_address;
                    __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0xffffffffU;
                    if (((0x01000000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01152000U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0U;
                    }
                    if (((0x01152000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x011fb000U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 1U;
                    }
                    if (((0x011fb000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x012a4000U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 2U;
                    }
                    if (((0x012a4000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x012f8800U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 3U;
                    }
                    if (((0x012f8800U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x0134d000U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 4U;
                    }
                    if (((0x0134d000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x013a1800U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 5U;
                    }
                    if (((0x013a1800U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x0144a800U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 6U;
                    }
                    if (((0x0144a800U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x014f3800U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 7U;
                    }
                    if (((0x014f3800U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01645800U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 8U;
                    }
                    if (((0x01645800U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x0169a000U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 9U;
                    }
                    if (((0x0169a000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x016ee800U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x0000000aU;
                    }
                    if (((0x016ee800U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01718c00U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x0000000bU;
                    }
                    if (((0x01718c00U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01743000U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x0000000cU;
                    }
                    if (((0x01743000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x0176d400U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x0000000dU;
                    }
                    if (((0x0176d400U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x017c1c00U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x0000000eU;
                    }
                    if (((0x017c1c00U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01816400U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x0000000fU;
                    }
                    if (((0x01816400U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x018bf400U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x00000010U;
                    }
                    if (((0x018bf400U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x018e9800U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x00000011U;
                    }
                    if (((0x018e9800U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01913c00U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x00000012U;
                    }
                    if (((0x01913c00U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01928e00U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x00000013U;
                    }
                    if (((0x01928e00U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x0193e000U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x00000014U;
                    }
                    if (((0x0193e000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01953200U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x00000015U;
                    }
                    if (((0x01953200U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x0197d600U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x00000016U;
                    }
                    if (((0x0197d600U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x019a7a00U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x00000017U;
                    }
                    if (((0x019a7a00U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x019fc200U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x00000018U;
                    }
                    if (((0x019fc200U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01a11400U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x00000019U;
                    }
                    if (((0x01a11400U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01a26600U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x0000001aU;
                    }
                    if (((0x01a26600U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01a30f00U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x0000001bU;
                    }
                    if (((0x01a30f00U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01a46100U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x0000001cU;
                    }
                    if (((0x01a46100U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01a474ceU > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x0000001dU;
                    }
                    if (((0x01a47500U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01a51e00U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x0000001fU;
                    }
                    if (((0x01a51e00U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01a57280U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x00000020U;
                    }
                    if (((0x01a57280U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01a6c480U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x00000021U;
                    }
                    if (((0x01a6c480U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01aaba80U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x00000022U;
                    }
                    if (((0x01aaba80U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01ad5e80U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x00000023U;
                    }
                    if (((0x01ad5e80U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01adadb8U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x00000024U;
                    }
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_owner 
                        = __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout;
                    if (VL_UNLIKELY((VL_GTS_III(32, 0U, vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_owner)))) {
                        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_network_backend_golden.sv:623: Assertion failed in %m: T68 feature write \350\220\275\345\234\250\351\235\236 owned output \345\234\260\345\235\200\357\274\232%08h\n",4, 'M',vlSymsp->name(),"tb_s2a_network_backend_golden", 'T',-9
                                     , '#',64,VL_TIME_UNITED_Q(1000)
                                     , '#',32,vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_address);
                        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_network_backend_golden.sv", 623, "", false);
                    }
                    if (VL_UNLIKELY(((VL_LTES_III(32, 0U, vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_owner) 
                                      & (vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_owner 
                                         != vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_owner))))) {
                        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_network_backend_golden.sv:626: Assertion failed in %m: T68 \345\215\225\344\270\252 word write \350\267\250\350\266\212\344\270\244\344\270\252 tensor\357\274\232addr=%08h\n",4, 'M',vlSymsp->name(),"tb_s2a_network_backend_golden", 'T',-9
                                     , '#',64,VL_TIME_UNITED_Q(1000)
                                     , '#',32,vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_address);
                        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_network_backend_golden.sv", 626, "", false);
                    }
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_owner 
                        = vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_owner;
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_feature_index 
                        = (vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_address 
                           - (IData)(0x01000000U));
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_golden_index 
                        = (((0x25U >= (0x0000003fU 
                                       & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_owner))
                             ? vlSelfRef.tb_s2a_network_backend_golden__DOT__golden_offset
                            [(0x0000003fU & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_owner)]
                             : 0U) + (vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_address 
                                      - ((0x25U >= 
                                          (0x0000003fU 
                                           & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_owner))
                                          ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_ADDRESS
                                         [(0x0000003fU 
                                           & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_owner)]
                                          : 0U)));
                    if (VL_UNLIKELY(((0U != ((0x00adad85U 
                                              >= (0x00ffffffU 
                                                  & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_golden_index))
                                              ? vlSelfRef.tb_s2a_network_backend_golden__DOT__golden_byte_seen
                                             [(0x00ffffffU 
                                               & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_golden_index)]
                                              : 0U))))) {
                        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_network_backend_golden.sv:633: Assertion failed in %m: T68 feature byte \350\242\253\351\207\215\345\244\215\345\206\231\345\205\245\357\274\232layer=%0d offset=%0d\n",5, 'M',vlSymsp->name(),"tb_s2a_network_backend_golden", 'T',-9
                                     , '#',64,VL_TIME_UNITED_Q(1000)
                                     , '~',32,vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_owner
                                     , '#',32,(vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_address 
                                               - ((0x25U 
                                                   >= 
                                                   (0x0000003fU 
                                                    & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_owner))
                                                   ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_ADDRESS
                                                  [
                                                  (0x0000003fU 
                                                   & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_owner)]
                                                   : 0U)));
                        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_network_backend_golden.sv", 633, "", false);
                    }
                    if (VL_UNLIKELY((((0x000000ffU 
                                       & vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_wdata) 
                                      != ((0x00adad85U 
                                           >= (0x00ffffffU 
                                               & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_golden_index))
                                           ? vlSelfRef.tb_s2a_network_backend_golden__DOT__expected_bytes
                                          [(0x00ffffffU 
                                            & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_golden_index)]
                                           : 0U))))) {
                        vlSelfRef.tb_s2a_network_backend_golden__DOT__total_mismatches 
                            = ((IData)(1U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__total_mismatches);
                        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_network_backend_golden.sv:638: Assertion failed in %m: T68 golden mismatch\357\274\232layer=%0d offset=%0d addr=%08h got=%02h expected=%02h\n",8, 'M',vlSymsp->name(),"tb_s2a_network_backend_golden", 'T',-9
                                     , '#',64,VL_TIME_UNITED_Q(1000)
                                     , '~',32,vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_owner
                                     , '#',32,(vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_address 
                                               - ((0x25U 
                                                   >= 
                                                   (0x0000003fU 
                                                    & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_owner))
                                                   ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_ADDRESS
                                                  [
                                                  (0x0000003fU 
                                                   & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_owner)]
                                                   : 0U))
                                     , '#',32,vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_address
                                     , '#',8,(0x000000ffU 
                                              & vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_wdata)
                                     , '#',8,((0x00adad85U 
                                               >= (0x00ffffffU 
                                                   & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_golden_index))
                                               ? vlSelfRef.tb_s2a_network_backend_golden__DOT__expected_bytes
                                              [(0x00ffffffU 
                                                & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_golden_index)]
                                               : 0U));
                        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_network_backend_golden.sv", 638, "", false);
                    }
                    if ((0x00adadb7U >= (0x00ffffffU 
                                         & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_feature_index))) {
                        __VdlyVal__tb_s2a_network_backend_golden__DOT__feature_bytes__v0 
                            = (0x000000ffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_wdata);
                        __VdlyDim0__tb_s2a_network_backend_golden__DOT__feature_bytes__v0 
                            = (0x00ffffffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_feature_index);
                        __VdlySet__tb_s2a_network_backend_golden__DOT__feature_bytes__v0 = 1U;
                        __VdlyDim0__tb_s2a_network_backend_golden__DOT__feature_byte_valid__v0 
                            = (0x00ffffffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_feature_index);
                        __VdlySet__tb_s2a_network_backend_golden__DOT__feature_byte_valid__v0 = 1U;
                    }
                    if ((0x00adad85U >= (0x00ffffffU 
                                         & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_golden_index))) {
                        __VdlyDim0__tb_s2a_network_backend_golden__DOT__golden_byte_seen__v0 
                            = (0x00ffffffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_golden_index);
                        __VdlySet__tb_s2a_network_backend_golden__DOT__golden_byte_seen__v0 = 1U;
                    }
                }
                if ((2U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_wstrb))) {
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__active_byte_count 
                        = ((IData)(1U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__active_byte_count);
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_address 
                        = ((IData)(1U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr);
                    __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address 
                        = vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_address;
                    __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0xffffffffU;
                    if (((0x01000000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01152000U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0U;
                    }
                    if (((0x01152000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x011fb000U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 1U;
                    }
                    if (((0x011fb000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x012a4000U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 2U;
                    }
                    if (((0x012a4000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x012f8800U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 3U;
                    }
                    if (((0x012f8800U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x0134d000U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 4U;
                    }
                    if (((0x0134d000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x013a1800U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 5U;
                    }
                    if (((0x013a1800U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x0144a800U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 6U;
                    }
                    if (((0x0144a800U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x014f3800U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 7U;
                    }
                    if (((0x014f3800U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01645800U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 8U;
                    }
                    if (((0x01645800U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x0169a000U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 9U;
                    }
                    if (((0x0169a000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x016ee800U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x0000000aU;
                    }
                    if (((0x016ee800U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01718c00U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x0000000bU;
                    }
                    if (((0x01718c00U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01743000U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x0000000cU;
                    }
                    if (((0x01743000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x0176d400U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x0000000dU;
                    }
                    if (((0x0176d400U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x017c1c00U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x0000000eU;
                    }
                    if (((0x017c1c00U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01816400U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x0000000fU;
                    }
                    if (((0x01816400U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x018bf400U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x00000010U;
                    }
                    if (((0x018bf400U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x018e9800U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x00000011U;
                    }
                    if (((0x018e9800U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01913c00U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x00000012U;
                    }
                    if (((0x01913c00U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01928e00U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x00000013U;
                    }
                    if (((0x01928e00U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x0193e000U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x00000014U;
                    }
                    if (((0x0193e000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01953200U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x00000015U;
                    }
                    if (((0x01953200U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x0197d600U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x00000016U;
                    }
                    if (((0x0197d600U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x019a7a00U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x00000017U;
                    }
                    if (((0x019a7a00U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x019fc200U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x00000018U;
                    }
                    if (((0x019fc200U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01a11400U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x00000019U;
                    }
                    if (((0x01a11400U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01a26600U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x0000001aU;
                    }
                    if (((0x01a26600U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01a30f00U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x0000001bU;
                    }
                    if (((0x01a30f00U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01a46100U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x0000001cU;
                    }
                    if (((0x01a46100U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01a474ceU > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x0000001dU;
                    }
                    if (((0x01a47500U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01a51e00U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x0000001fU;
                    }
                    if (((0x01a51e00U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01a57280U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x00000020U;
                    }
                    if (((0x01a57280U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01a6c480U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x00000021U;
                    }
                    if (((0x01a6c480U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01aaba80U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x00000022U;
                    }
                    if (((0x01aaba80U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01ad5e80U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x00000023U;
                    }
                    if (((0x01ad5e80U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01adadb8U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x00000024U;
                    }
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_owner 
                        = __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout;
                    if (VL_UNLIKELY((VL_GTS_III(32, 0U, vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_owner)))) {
                        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_network_backend_golden.sv:623: Assertion failed in %m: T68 feature write \350\220\275\345\234\250\351\235\236 owned output \345\234\260\345\235\200\357\274\232%08h\n",4, 'M',vlSymsp->name(),"tb_s2a_network_backend_golden", 'T',-9
                                     , '#',64,VL_TIME_UNITED_Q(1000)
                                     , '#',32,vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_address);
                        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_network_backend_golden.sv", 623, "", false);
                    }
                    if (VL_UNLIKELY(((VL_LTES_III(32, 0U, vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_owner) 
                                      & (vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_owner 
                                         != vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_owner))))) {
                        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_network_backend_golden.sv:626: Assertion failed in %m: T68 \345\215\225\344\270\252 word write \350\267\250\350\266\212\344\270\244\344\270\252 tensor\357\274\232addr=%08h\n",4, 'M',vlSymsp->name(),"tb_s2a_network_backend_golden", 'T',-9
                                     , '#',64,VL_TIME_UNITED_Q(1000)
                                     , '#',32,vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_address);
                        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_network_backend_golden.sv", 626, "", false);
                    }
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_owner 
                        = vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_owner;
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_feature_index 
                        = (vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_address 
                           - (IData)(0x01000000U));
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_golden_index 
                        = (((0x25U >= (0x0000003fU 
                                       & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_owner))
                             ? vlSelfRef.tb_s2a_network_backend_golden__DOT__golden_offset
                            [(0x0000003fU & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_owner)]
                             : 0U) + (vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_address 
                                      - ((0x25U >= 
                                          (0x0000003fU 
                                           & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_owner))
                                          ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_ADDRESS
                                         [(0x0000003fU 
                                           & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_owner)]
                                          : 0U)));
                    if (VL_UNLIKELY(((0U != ((0x00adad85U 
                                              >= (0x00ffffffU 
                                                  & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_golden_index))
                                              ? vlSelfRef.tb_s2a_network_backend_golden__DOT__golden_byte_seen
                                             [(0x00ffffffU 
                                               & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_golden_index)]
                                              : 0U))))) {
                        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_network_backend_golden.sv:633: Assertion failed in %m: T68 feature byte \350\242\253\351\207\215\345\244\215\345\206\231\345\205\245\357\274\232layer=%0d offset=%0d\n",5, 'M',vlSymsp->name(),"tb_s2a_network_backend_golden", 'T',-9
                                     , '#',64,VL_TIME_UNITED_Q(1000)
                                     , '~',32,vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_owner
                                     , '#',32,(vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_address 
                                               - ((0x25U 
                                                   >= 
                                                   (0x0000003fU 
                                                    & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_owner))
                                                   ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_ADDRESS
                                                  [
                                                  (0x0000003fU 
                                                   & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_owner)]
                                                   : 0U)));
                        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_network_backend_golden.sv", 633, "", false);
                    }
                    if (VL_UNLIKELY((((0x000000ffU 
                                       & (vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_wdata 
                                          >> 8U)) != 
                                      ((0x00adad85U 
                                        >= (0x00ffffffU 
                                            & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_golden_index))
                                        ? vlSelfRef.tb_s2a_network_backend_golden__DOT__expected_bytes
                                       [(0x00ffffffU 
                                         & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_golden_index)]
                                        : 0U))))) {
                        vlSelfRef.tb_s2a_network_backend_golden__DOT__total_mismatches 
                            = ((IData)(1U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__total_mismatches);
                        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_network_backend_golden.sv:638: Assertion failed in %m: T68 golden mismatch\357\274\232layer=%0d offset=%0d addr=%08h got=%02h expected=%02h\n",8, 'M',vlSymsp->name(),"tb_s2a_network_backend_golden", 'T',-9
                                     , '#',64,VL_TIME_UNITED_Q(1000)
                                     , '~',32,vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_owner
                                     , '#',32,(vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_address 
                                               - ((0x25U 
                                                   >= 
                                                   (0x0000003fU 
                                                    & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_owner))
                                                   ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_ADDRESS
                                                  [
                                                  (0x0000003fU 
                                                   & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_owner)]
                                                   : 0U))
                                     , '#',32,vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_address
                                     , '#',8,(0x000000ffU 
                                              & (vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_wdata 
                                                 >> 8U))
                                     , '#',8,((0x00adad85U 
                                               >= (0x00ffffffU 
                                                   & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_golden_index))
                                               ? vlSelfRef.tb_s2a_network_backend_golden__DOT__expected_bytes
                                              [(0x00ffffffU 
                                                & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_golden_index)]
                                               : 0U));
                        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_network_backend_golden.sv", 638, "", false);
                    }
                    if ((0x00adadb7U >= (0x00ffffffU 
                                         & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_feature_index))) {
                        __VdlyVal__tb_s2a_network_backend_golden__DOT__feature_bytes__v1 
                            = (0x000000ffU & (vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_wdata 
                                              >> 8U));
                        __VdlyDim0__tb_s2a_network_backend_golden__DOT__feature_bytes__v1 
                            = (0x00ffffffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_feature_index);
                        __VdlySet__tb_s2a_network_backend_golden__DOT__feature_bytes__v1 = 1U;
                        __VdlyDim0__tb_s2a_network_backend_golden__DOT__feature_byte_valid__v1 
                            = (0x00ffffffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_feature_index);
                        __VdlySet__tb_s2a_network_backend_golden__DOT__feature_byte_valid__v1 = 1U;
                    }
                    if ((0x00adad85U >= (0x00ffffffU 
                                         & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_golden_index))) {
                        __VdlyDim0__tb_s2a_network_backend_golden__DOT__golden_byte_seen__v1 
                            = (0x00ffffffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_golden_index);
                        __VdlySet__tb_s2a_network_backend_golden__DOT__golden_byte_seen__v1 = 1U;
                    }
                }
                if ((4U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_wstrb))) {
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__active_byte_count 
                        = ((IData)(1U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__active_byte_count);
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_address 
                        = ((IData)(2U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr);
                    __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address 
                        = vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_address;
                    __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0xffffffffU;
                    if (((0x01000000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01152000U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0U;
                    }
                    if (((0x01152000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x011fb000U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 1U;
                    }
                    if (((0x011fb000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x012a4000U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 2U;
                    }
                    if (((0x012a4000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x012f8800U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 3U;
                    }
                    if (((0x012f8800U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x0134d000U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 4U;
                    }
                    if (((0x0134d000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x013a1800U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 5U;
                    }
                    if (((0x013a1800U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x0144a800U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 6U;
                    }
                    if (((0x0144a800U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x014f3800U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 7U;
                    }
                    if (((0x014f3800U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01645800U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 8U;
                    }
                    if (((0x01645800U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x0169a000U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 9U;
                    }
                    if (((0x0169a000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x016ee800U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x0000000aU;
                    }
                    if (((0x016ee800U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01718c00U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x0000000bU;
                    }
                    if (((0x01718c00U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01743000U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x0000000cU;
                    }
                    if (((0x01743000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x0176d400U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x0000000dU;
                    }
                    if (((0x0176d400U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x017c1c00U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x0000000eU;
                    }
                    if (((0x017c1c00U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01816400U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x0000000fU;
                    }
                    if (((0x01816400U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x018bf400U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x00000010U;
                    }
                    if (((0x018bf400U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x018e9800U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x00000011U;
                    }
                    if (((0x018e9800U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01913c00U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x00000012U;
                    }
                    if (((0x01913c00U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01928e00U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x00000013U;
                    }
                    if (((0x01928e00U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x0193e000U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x00000014U;
                    }
                    if (((0x0193e000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01953200U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x00000015U;
                    }
                    if (((0x01953200U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x0197d600U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x00000016U;
                    }
                    if (((0x0197d600U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x019a7a00U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x00000017U;
                    }
                    if (((0x019a7a00U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x019fc200U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x00000018U;
                    }
                    if (((0x019fc200U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01a11400U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x00000019U;
                    }
                    if (((0x01a11400U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01a26600U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x0000001aU;
                    }
                    if (((0x01a26600U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01a30f00U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x0000001bU;
                    }
                    if (((0x01a30f00U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01a46100U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x0000001cU;
                    }
                    if (((0x01a46100U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01a474ceU > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x0000001dU;
                    }
                    if (((0x01a47500U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01a51e00U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x0000001fU;
                    }
                    if (((0x01a51e00U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01a57280U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x00000020U;
                    }
                    if (((0x01a57280U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01a6c480U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x00000021U;
                    }
                    if (((0x01a6c480U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01aaba80U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x00000022U;
                    }
                    if (((0x01aaba80U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01ad5e80U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x00000023U;
                    }
                    if (((0x01ad5e80U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01adadb8U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x00000024U;
                    }
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_owner 
                        = __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout;
                    if (VL_UNLIKELY((VL_GTS_III(32, 0U, vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_owner)))) {
                        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_network_backend_golden.sv:623: Assertion failed in %m: T68 feature write \350\220\275\345\234\250\351\235\236 owned output \345\234\260\345\235\200\357\274\232%08h\n",4, 'M',vlSymsp->name(),"tb_s2a_network_backend_golden", 'T',-9
                                     , '#',64,VL_TIME_UNITED_Q(1000)
                                     , '#',32,vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_address);
                        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_network_backend_golden.sv", 623, "", false);
                    }
                    if (VL_UNLIKELY(((VL_LTES_III(32, 0U, vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_owner) 
                                      & (vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_owner 
                                         != vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_owner))))) {
                        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_network_backend_golden.sv:626: Assertion failed in %m: T68 \345\215\225\344\270\252 word write \350\267\250\350\266\212\344\270\244\344\270\252 tensor\357\274\232addr=%08h\n",4, 'M',vlSymsp->name(),"tb_s2a_network_backend_golden", 'T',-9
                                     , '#',64,VL_TIME_UNITED_Q(1000)
                                     , '#',32,vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_address);
                        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_network_backend_golden.sv", 626, "", false);
                    }
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_owner 
                        = vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_owner;
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_feature_index 
                        = (vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_address 
                           - (IData)(0x01000000U));
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_golden_index 
                        = (((0x25U >= (0x0000003fU 
                                       & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_owner))
                             ? vlSelfRef.tb_s2a_network_backend_golden__DOT__golden_offset
                            [(0x0000003fU & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_owner)]
                             : 0U) + (vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_address 
                                      - ((0x25U >= 
                                          (0x0000003fU 
                                           & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_owner))
                                          ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_ADDRESS
                                         [(0x0000003fU 
                                           & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_owner)]
                                          : 0U)));
                    if (VL_UNLIKELY(((0U != ((0x00adad85U 
                                              >= (0x00ffffffU 
                                                  & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_golden_index))
                                              ? vlSelfRef.tb_s2a_network_backend_golden__DOT__golden_byte_seen
                                             [(0x00ffffffU 
                                               & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_golden_index)]
                                              : 0U))))) {
                        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_network_backend_golden.sv:633: Assertion failed in %m: T68 feature byte \350\242\253\351\207\215\345\244\215\345\206\231\345\205\245\357\274\232layer=%0d offset=%0d\n",5, 'M',vlSymsp->name(),"tb_s2a_network_backend_golden", 'T',-9
                                     , '#',64,VL_TIME_UNITED_Q(1000)
                                     , '~',32,vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_owner
                                     , '#',32,(vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_address 
                                               - ((0x25U 
                                                   >= 
                                                   (0x0000003fU 
                                                    & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_owner))
                                                   ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_ADDRESS
                                                  [
                                                  (0x0000003fU 
                                                   & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_owner)]
                                                   : 0U)));
                        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_network_backend_golden.sv", 633, "", false);
                    }
                    if (VL_UNLIKELY((((0x000000ffU 
                                       & (vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_wdata 
                                          >> 0x10U)) 
                                      != ((0x00adad85U 
                                           >= (0x00ffffffU 
                                               & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_golden_index))
                                           ? vlSelfRef.tb_s2a_network_backend_golden__DOT__expected_bytes
                                          [(0x00ffffffU 
                                            & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_golden_index)]
                                           : 0U))))) {
                        vlSelfRef.tb_s2a_network_backend_golden__DOT__total_mismatches 
                            = ((IData)(1U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__total_mismatches);
                        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_network_backend_golden.sv:638: Assertion failed in %m: T68 golden mismatch\357\274\232layer=%0d offset=%0d addr=%08h got=%02h expected=%02h\n",8, 'M',vlSymsp->name(),"tb_s2a_network_backend_golden", 'T',-9
                                     , '#',64,VL_TIME_UNITED_Q(1000)
                                     , '~',32,vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_owner
                                     , '#',32,(vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_address 
                                               - ((0x25U 
                                                   >= 
                                                   (0x0000003fU 
                                                    & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_owner))
                                                   ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_ADDRESS
                                                  [
                                                  (0x0000003fU 
                                                   & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_owner)]
                                                   : 0U))
                                     , '#',32,vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_address
                                     , '#',8,(0x000000ffU 
                                              & (vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_wdata 
                                                 >> 0x10U))
                                     , '#',8,((0x00adad85U 
                                               >= (0x00ffffffU 
                                                   & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_golden_index))
                                               ? vlSelfRef.tb_s2a_network_backend_golden__DOT__expected_bytes
                                              [(0x00ffffffU 
                                                & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_golden_index)]
                                               : 0U));
                        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_network_backend_golden.sv", 638, "", false);
                    }
                    if ((0x00adadb7U >= (0x00ffffffU 
                                         & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_feature_index))) {
                        __VdlyVal__tb_s2a_network_backend_golden__DOT__feature_bytes__v2 
                            = (0x000000ffU & (vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_wdata 
                                              >> 0x10U));
                        __VdlyDim0__tb_s2a_network_backend_golden__DOT__feature_bytes__v2 
                            = (0x00ffffffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_feature_index);
                        __VdlySet__tb_s2a_network_backend_golden__DOT__feature_bytes__v2 = 1U;
                        __VdlyDim0__tb_s2a_network_backend_golden__DOT__feature_byte_valid__v2 
                            = (0x00ffffffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_feature_index);
                        __VdlySet__tb_s2a_network_backend_golden__DOT__feature_byte_valid__v2 = 1U;
                    }
                    if ((0x00adad85U >= (0x00ffffffU 
                                         & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_golden_index))) {
                        __VdlyDim0__tb_s2a_network_backend_golden__DOT__golden_byte_seen__v2 
                            = (0x00ffffffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_golden_index);
                        __VdlySet__tb_s2a_network_backend_golden__DOT__golden_byte_seen__v2 = 1U;
                    }
                }
                if ((8U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_wstrb))) {
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__active_byte_count 
                        = ((IData)(1U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__active_byte_count);
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_address 
                        = ((IData)(3U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr);
                    __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address 
                        = vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_address;
                    __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0xffffffffU;
                    if (((0x01000000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01152000U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0U;
                    }
                    if (((0x01152000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x011fb000U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 1U;
                    }
                    if (((0x011fb000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x012a4000U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 2U;
                    }
                    if (((0x012a4000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x012f8800U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 3U;
                    }
                    if (((0x012f8800U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x0134d000U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 4U;
                    }
                    if (((0x0134d000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x013a1800U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 5U;
                    }
                    if (((0x013a1800U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x0144a800U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 6U;
                    }
                    if (((0x0144a800U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x014f3800U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 7U;
                    }
                    if (((0x014f3800U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01645800U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 8U;
                    }
                    if (((0x01645800U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x0169a000U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 9U;
                    }
                    if (((0x0169a000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x016ee800U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x0000000aU;
                    }
                    if (((0x016ee800U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01718c00U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x0000000bU;
                    }
                    if (((0x01718c00U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01743000U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x0000000cU;
                    }
                    if (((0x01743000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x0176d400U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x0000000dU;
                    }
                    if (((0x0176d400U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x017c1c00U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x0000000eU;
                    }
                    if (((0x017c1c00U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01816400U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x0000000fU;
                    }
                    if (((0x01816400U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x018bf400U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x00000010U;
                    }
                    if (((0x018bf400U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x018e9800U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x00000011U;
                    }
                    if (((0x018e9800U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01913c00U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x00000012U;
                    }
                    if (((0x01913c00U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01928e00U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x00000013U;
                    }
                    if (((0x01928e00U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x0193e000U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x00000014U;
                    }
                    if (((0x0193e000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01953200U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x00000015U;
                    }
                    if (((0x01953200U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x0197d600U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x00000016U;
                    }
                    if (((0x0197d600U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x019a7a00U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x00000017U;
                    }
                    if (((0x019a7a00U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x019fc200U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x00000018U;
                    }
                    if (((0x019fc200U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01a11400U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x00000019U;
                    }
                    if (((0x01a11400U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01a26600U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x0000001aU;
                    }
                    if (((0x01a26600U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01a30f00U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x0000001bU;
                    }
                    if (((0x01a30f00U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01a46100U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x0000001cU;
                    }
                    if (((0x01a46100U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01a474ceU > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x0000001dU;
                    }
                    if (((0x01a47500U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01a51e00U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x0000001fU;
                    }
                    if (((0x01a51e00U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01a57280U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x00000020U;
                    }
                    if (((0x01a57280U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01a6c480U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x00000021U;
                    }
                    if (((0x01a6c480U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01aaba80U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x00000022U;
                    }
                    if (((0x01aaba80U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01ad5e80U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x00000023U;
                    }
                    if (((0x01ad5e80U <= __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address) 
                         & (0x01adadb8U > __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout = 0x00000024U;
                    }
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_owner 
                        = __Vfunc_tb_s2a_network_backend_golden__DOT__owned_output_layer__19__Vfuncout;
                    if (VL_UNLIKELY((VL_GTS_III(32, 0U, vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_owner)))) {
                        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_network_backend_golden.sv:623: Assertion failed in %m: T68 feature write \350\220\275\345\234\250\351\235\236 owned output \345\234\260\345\235\200\357\274\232%08h\n",4, 'M',vlSymsp->name(),"tb_s2a_network_backend_golden", 'T',-9
                                     , '#',64,VL_TIME_UNITED_Q(1000)
                                     , '#',32,vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_address);
                        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_network_backend_golden.sv", 623, "", false);
                    }
                    if (VL_UNLIKELY(((VL_LTES_III(32, 0U, vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_owner) 
                                      & (vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_owner 
                                         != vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_owner))))) {
                        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_network_backend_golden.sv:626: Assertion failed in %m: T68 \345\215\225\344\270\252 word write \350\267\250\350\266\212\344\270\244\344\270\252 tensor\357\274\232addr=%08h\n",4, 'M',vlSymsp->name(),"tb_s2a_network_backend_golden", 'T',-9
                                     , '#',64,VL_TIME_UNITED_Q(1000)
                                     , '#',32,vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_address);
                        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_network_backend_golden.sv", 626, "", false);
                    }
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_owner 
                        = vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_owner;
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_feature_index 
                        = (vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_address 
                           - (IData)(0x01000000U));
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_golden_index 
                        = (((0x25U >= (0x0000003fU 
                                       & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_owner))
                             ? vlSelfRef.tb_s2a_network_backend_golden__DOT__golden_offset
                            [(0x0000003fU & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_owner)]
                             : 0U) + (vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_address 
                                      - ((0x25U >= 
                                          (0x0000003fU 
                                           & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_owner))
                                          ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_ADDRESS
                                         [(0x0000003fU 
                                           & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_owner)]
                                          : 0U)));
                    if (VL_UNLIKELY(((0U != ((0x00adad85U 
                                              >= (0x00ffffffU 
                                                  & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_golden_index))
                                              ? vlSelfRef.tb_s2a_network_backend_golden__DOT__golden_byte_seen
                                             [(0x00ffffffU 
                                               & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_golden_index)]
                                              : 0U))))) {
                        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_network_backend_golden.sv:633: Assertion failed in %m: T68 feature byte \350\242\253\351\207\215\345\244\215\345\206\231\345\205\245\357\274\232layer=%0d offset=%0d\n",5, 'M',vlSymsp->name(),"tb_s2a_network_backend_golden", 'T',-9
                                     , '#',64,VL_TIME_UNITED_Q(1000)
                                     , '~',32,vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_owner
                                     , '#',32,(vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_address 
                                               - ((0x25U 
                                                   >= 
                                                   (0x0000003fU 
                                                    & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_owner))
                                                   ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_ADDRESS
                                                  [
                                                  (0x0000003fU 
                                                   & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_owner)]
                                                   : 0U)));
                        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_network_backend_golden.sv", 633, "", false);
                    }
                    if (VL_UNLIKELY((((vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_wdata 
                                       >> 0x18U) != 
                                      ((0x00adad85U 
                                        >= (0x00ffffffU 
                                            & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_golden_index))
                                        ? vlSelfRef.tb_s2a_network_backend_golden__DOT__expected_bytes
                                       [(0x00ffffffU 
                                         & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_golden_index)]
                                        : 0U))))) {
                        vlSelfRef.tb_s2a_network_backend_golden__DOT__total_mismatches 
                            = ((IData)(1U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__total_mismatches);
                        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_network_backend_golden.sv:638: Assertion failed in %m: T68 golden mismatch\357\274\232layer=%0d offset=%0d addr=%08h got=%02h expected=%02h\n",8, 'M',vlSymsp->name(),"tb_s2a_network_backend_golden", 'T',-9
                                     , '#',64,VL_TIME_UNITED_Q(1000)
                                     , '~',32,vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_owner
                                     , '#',32,(vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_address 
                                               - ((0x25U 
                                                   >= 
                                                   (0x0000003fU 
                                                    & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_owner))
                                                   ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_ADDRESS
                                                  [
                                                  (0x0000003fU 
                                                   & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_owner)]
                                                   : 0U))
                                     , '#',32,vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_address
                                     , '#',8,(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_wdata 
                                              >> 0x18U)
                                     , '#',8,((0x00adad85U 
                                               >= (0x00ffffffU 
                                                   & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_golden_index))
                                               ? vlSelfRef.tb_s2a_network_backend_golden__DOT__expected_bytes
                                              [(0x00ffffffU 
                                                & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_golden_index)]
                                               : 0U));
                        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_network_backend_golden.sv", 638, "", false);
                    }
                    if ((0x00adadb7U >= (0x00ffffffU 
                                         & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_feature_index))) {
                        __VdlyVal__tb_s2a_network_backend_golden__DOT__feature_bytes__v3 
                            = (vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_wdata 
                               >> 0x18U);
                        __VdlyDim0__tb_s2a_network_backend_golden__DOT__feature_bytes__v3 
                            = (0x00ffffffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_feature_index);
                        __VdlySet__tb_s2a_network_backend_golden__DOT__feature_bytes__v3 = 1U;
                        __VdlyDim0__tb_s2a_network_backend_golden__DOT__feature_byte_valid__v3 
                            = (0x00ffffffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_feature_index);
                        __VdlySet__tb_s2a_network_backend_golden__DOT__feature_byte_valid__v3 = 1U;
                    }
                    if ((0x00adad85U >= (0x00ffffffU 
                                         & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_golden_index))) {
                        __VdlyDim0__tb_s2a_network_backend_golden__DOT__golden_byte_seen__v3 
                            = (0x00ffffffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_golden_index);
                        __VdlySet__tb_s2a_network_backend_golden__DOT__golden_byte_seen__v3 = 1U;
                    }
                }
                if (VL_LTES_III(32, 0U, vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_owner)) {
                    if ((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_owner))) {
                        __VdlyVal__tb_s2a_network_backend_golden__DOT__layer_write_count__v0 
                            = (((0x25U >= (0x0000003fU 
                                           & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_owner))
                                 ? vlSelfRef.tb_s2a_network_backend_golden__DOT__layer_write_count
                                [(0x0000003fU & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_owner)]
                                 : 0U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__active_byte_count);
                        __VdlyDim0__tb_s2a_network_backend_golden__DOT__layer_write_count__v0 
                            = (0x0000003fU & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_owner);
                        __VdlySet__tb_s2a_network_backend_golden__DOT__layer_write_count__v0 = 1U;
                    }
                }
                vlSelfRef.tb_s2a_network_backend_golden__DOT__total_feature_write_bytes 
                    = (vlSelfRef.tb_s2a_network_backend_golden__DOT__total_feature_write_bytes 
                       + vlSelfRef.tb_s2a_network_backend_golden__DOT__active_byte_count);
            } else {
                vlSelfRef.tb_s2a_network_backend_golden__DOT__total_memory_read_transactions 
                    = ((IData)(1U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__total_memory_read_transactions);
                vlSelfRef.tb_s2a_network_backend_golden__DOT__input_bytes_this_transfer = 0U;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__weight_bytes_this_transfer = 0U;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__feature_bytes_this_transfer = 0U;
                if ((1U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_rstrb))) {
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_address 
                        = vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr;
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__active_byte_count 
                        = ((IData)(1U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__active_byte_count);
                    __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address 
                        = vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_address;
                    __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0xffffffffU;
                    if ((0x0007ec00U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address)) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0U;
                    } else if (((0x00100000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                                & (0x006a12fcU > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 1U;
                    } else {
                        if (((0x01000000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01152000U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 2U;
                        }
                        if (((0x01152000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x011fb000U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 3U;
                        }
                        if (((0x011fb000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x012a4000U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 4U;
                        }
                        if (((0x012a4000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x012f8800U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 5U;
                        }
                        if (((0x012f8800U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x0134d000U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 6U;
                        }
                        if (((0x0134d000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x013a1800U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 7U;
                        }
                        if (((0x013a1800U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x0144a800U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 8U;
                        }
                        if (((0x0144a800U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x014f3800U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 9U;
                        }
                        if (((0x014f3800U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01645800U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x0000000aU;
                        }
                        if (((0x01645800U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x0169a000U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x0000000bU;
                        }
                        if (((0x0169a000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x016ee800U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x0000000cU;
                        }
                        if (((0x016ee800U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01718c00U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x0000000dU;
                        }
                        if (((0x01718c00U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01743000U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x0000000eU;
                        }
                        if (((0x01743000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x0176d400U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x0000000fU;
                        }
                        if (((0x0176d400U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x017c1c00U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x00000010U;
                        }
                        if (((0x017c1c00U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01816400U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x00000011U;
                        }
                        if (((0x01816400U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x018bf400U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x00000012U;
                        }
                        if (((0x018bf400U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x018e9800U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x00000013U;
                        }
                        if (((0x018e9800U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01913c00U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x00000014U;
                        }
                        if (((0x01913c00U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01928e00U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x00000015U;
                        }
                        if (((0x01928e00U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x0193e000U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x00000016U;
                        }
                        if (((0x0193e000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01953200U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x00000017U;
                        }
                        if (((0x01953200U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x0197d600U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x00000018U;
                        }
                        if (((0x0197d600U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x019a7a00U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x00000019U;
                        }
                        if (((0x019a7a00U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x019fc200U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x0000001aU;
                        }
                        if (((0x019fc200U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01a11400U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x0000001bU;
                        }
                        if (((0x01a11400U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01a26600U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x0000001cU;
                        }
                        if (((0x01a26600U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01a30f00U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x0000001dU;
                        }
                        if (((0x01a30f00U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01a46100U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x0000001eU;
                        }
                        if (((0x01a46100U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01a474ceU > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x0000001fU;
                        }
                        if (((0x01a47500U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01a51e00U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x00000021U;
                        }
                        if (((0x01a51e00U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01a57280U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x00000022U;
                        }
                        if (((0x01a57280U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01a6c480U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x00000023U;
                        }
                        if (((0x01a6c480U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01aaba80U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x00000024U;
                        }
                        if (((0x01aaba80U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01ad5e80U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x00000025U;
                        }
                        if (((0x01ad5e80U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01adadb8U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x00000026U;
                        }
                    }
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_tensor_owner 
                        = __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout;
                    if ((0U == vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_tensor_owner)) {
                        vlSelfRef.tb_s2a_network_backend_golden__DOT__input_bytes_this_transfer 
                            = ((IData)(1U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__input_bytes_this_transfer);
                    } else if ((1U == vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_tensor_owner)) {
                        vlSelfRef.tb_s2a_network_backend_golden__DOT__weight_bytes_this_transfer 
                            = ((IData)(1U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__weight_bytes_this_transfer);
                    } else if (VL_LIKELY((VL_LTES_III(32, 2U, vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_tensor_owner)))) {
                        vlSelfRef.tb_s2a_network_backend_golden__DOT__feature_bytes_this_transfer 
                            = ((IData)(1U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__feature_bytes_this_transfer);
                        vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_feature_index 
                            = (vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_address 
                               - (IData)(0x01000000U));
                        if (VL_UNLIKELY(((1U & (~ (0U 
                                                   != 
                                                   ((0x00adadb7U 
                                                     >= 
                                                     (0x00ffffffU 
                                                      & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_feature_index))
                                                     ? vlSelfRef.tb_s2a_network_backend_golden__DOT__feature_byte_valid
                                                    [
                                                    (0x00ffffffU 
                                                     & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_feature_index)]
                                                     : 0U))))))) {
                            VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_network_backend_golden.sv:671: Assertion failed in %m: T68 feature read \346\234\252\345\210\235\345\247\213\345\214\226\357\274\232%08h\n",4, 'M',vlSymsp->name(),"tb_s2a_network_backend_golden", 'T',-9
                                         , '#',64,VL_TIME_UNITED_Q(1000)
                                         , '#',32,vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_address);
                            VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_network_backend_golden.sv", 671, "", false);
                        }
                    } else {
                        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_network_backend_golden.sv:674: Assertion failed in %m: T68 \346\216\245\345\217\227\344\272\206\346\262\241\346\234\211\345\220\210\346\263\225 tensor owner \347\232\204 read lane\357\274\232%08h\n",4, 'M',vlSymsp->name(),"tb_s2a_network_backend_golden", 'T',-9
                                     , '#',64,VL_TIME_UNITED_Q(1000)
                                     , '#',32,vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_address);
                        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_network_backend_golden.sv", 674, "", false);
                    }
                }
                if ((2U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_rstrb))) {
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_address 
                        = ((IData)(1U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr);
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__active_byte_count 
                        = ((IData)(1U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__active_byte_count);
                    __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address 
                        = vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_address;
                    __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0xffffffffU;
                    if ((0x0007ec00U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address)) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0U;
                    } else if (((0x00100000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                                & (0x006a12fcU > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 1U;
                    } else {
                        if (((0x01000000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01152000U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 2U;
                        }
                        if (((0x01152000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x011fb000U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 3U;
                        }
                        if (((0x011fb000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x012a4000U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 4U;
                        }
                        if (((0x012a4000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x012f8800U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 5U;
                        }
                        if (((0x012f8800U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x0134d000U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 6U;
                        }
                        if (((0x0134d000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x013a1800U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 7U;
                        }
                        if (((0x013a1800U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x0144a800U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 8U;
                        }
                        if (((0x0144a800U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x014f3800U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 9U;
                        }
                        if (((0x014f3800U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01645800U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x0000000aU;
                        }
                        if (((0x01645800U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x0169a000U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x0000000bU;
                        }
                        if (((0x0169a000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x016ee800U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x0000000cU;
                        }
                        if (((0x016ee800U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01718c00U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x0000000dU;
                        }
                        if (((0x01718c00U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01743000U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x0000000eU;
                        }
                        if (((0x01743000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x0176d400U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x0000000fU;
                        }
                        if (((0x0176d400U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x017c1c00U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x00000010U;
                        }
                        if (((0x017c1c00U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01816400U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x00000011U;
                        }
                        if (((0x01816400U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x018bf400U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x00000012U;
                        }
                        if (((0x018bf400U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x018e9800U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x00000013U;
                        }
                        if (((0x018e9800U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01913c00U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x00000014U;
                        }
                        if (((0x01913c00U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01928e00U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x00000015U;
                        }
                        if (((0x01928e00U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x0193e000U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x00000016U;
                        }
                        if (((0x0193e000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01953200U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x00000017U;
                        }
                        if (((0x01953200U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x0197d600U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x00000018U;
                        }
                        if (((0x0197d600U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x019a7a00U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x00000019U;
                        }
                        if (((0x019a7a00U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x019fc200U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x0000001aU;
                        }
                        if (((0x019fc200U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01a11400U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x0000001bU;
                        }
                        if (((0x01a11400U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01a26600U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x0000001cU;
                        }
                        if (((0x01a26600U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01a30f00U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x0000001dU;
                        }
                        if (((0x01a30f00U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01a46100U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x0000001eU;
                        }
                        if (((0x01a46100U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01a474ceU > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x0000001fU;
                        }
                        if (((0x01a47500U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01a51e00U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x00000021U;
                        }
                        if (((0x01a51e00U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01a57280U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x00000022U;
                        }
                        if (((0x01a57280U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01a6c480U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x00000023U;
                        }
                        if (((0x01a6c480U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01aaba80U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x00000024U;
                        }
                        if (((0x01aaba80U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01ad5e80U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x00000025U;
                        }
                        if (((0x01ad5e80U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01adadb8U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x00000026U;
                        }
                    }
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_tensor_owner 
                        = __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout;
                    if ((0U == vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_tensor_owner)) {
                        vlSelfRef.tb_s2a_network_backend_golden__DOT__input_bytes_this_transfer 
                            = ((IData)(1U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__input_bytes_this_transfer);
                    } else if ((1U == vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_tensor_owner)) {
                        vlSelfRef.tb_s2a_network_backend_golden__DOT__weight_bytes_this_transfer 
                            = ((IData)(1U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__weight_bytes_this_transfer);
                    } else if (VL_LIKELY((VL_LTES_III(32, 2U, vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_tensor_owner)))) {
                        vlSelfRef.tb_s2a_network_backend_golden__DOT__feature_bytes_this_transfer 
                            = ((IData)(1U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__feature_bytes_this_transfer);
                        vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_feature_index 
                            = (vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_address 
                               - (IData)(0x01000000U));
                        if (VL_UNLIKELY(((1U & (~ (0U 
                                                   != 
                                                   ((0x00adadb7U 
                                                     >= 
                                                     (0x00ffffffU 
                                                      & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_feature_index))
                                                     ? vlSelfRef.tb_s2a_network_backend_golden__DOT__feature_byte_valid
                                                    [
                                                    (0x00ffffffU 
                                                     & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_feature_index)]
                                                     : 0U))))))) {
                            VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_network_backend_golden.sv:671: Assertion failed in %m: T68 feature read \346\234\252\345\210\235\345\247\213\345\214\226\357\274\232%08h\n",4, 'M',vlSymsp->name(),"tb_s2a_network_backend_golden", 'T',-9
                                         , '#',64,VL_TIME_UNITED_Q(1000)
                                         , '#',32,vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_address);
                            VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_network_backend_golden.sv", 671, "", false);
                        }
                    } else {
                        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_network_backend_golden.sv:674: Assertion failed in %m: T68 \346\216\245\345\217\227\344\272\206\346\262\241\346\234\211\345\220\210\346\263\225 tensor owner \347\232\204 read lane\357\274\232%08h\n",4, 'M',vlSymsp->name(),"tb_s2a_network_backend_golden", 'T',-9
                                     , '#',64,VL_TIME_UNITED_Q(1000)
                                     , '#',32,vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_address);
                        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_network_backend_golden.sv", 674, "", false);
                    }
                }
                if ((4U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_rstrb))) {
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_address 
                        = ((IData)(2U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr);
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__active_byte_count 
                        = ((IData)(1U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__active_byte_count);
                    __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address 
                        = vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_address;
                    __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0xffffffffU;
                    if ((0x0007ec00U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address)) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0U;
                    } else if (((0x00100000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                                & (0x006a12fcU > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 1U;
                    } else {
                        if (((0x01000000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01152000U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 2U;
                        }
                        if (((0x01152000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x011fb000U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 3U;
                        }
                        if (((0x011fb000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x012a4000U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 4U;
                        }
                        if (((0x012a4000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x012f8800U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 5U;
                        }
                        if (((0x012f8800U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x0134d000U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 6U;
                        }
                        if (((0x0134d000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x013a1800U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 7U;
                        }
                        if (((0x013a1800U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x0144a800U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 8U;
                        }
                        if (((0x0144a800U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x014f3800U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 9U;
                        }
                        if (((0x014f3800U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01645800U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x0000000aU;
                        }
                        if (((0x01645800U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x0169a000U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x0000000bU;
                        }
                        if (((0x0169a000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x016ee800U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x0000000cU;
                        }
                        if (((0x016ee800U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01718c00U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x0000000dU;
                        }
                        if (((0x01718c00U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01743000U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x0000000eU;
                        }
                        if (((0x01743000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x0176d400U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x0000000fU;
                        }
                        if (((0x0176d400U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x017c1c00U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x00000010U;
                        }
                        if (((0x017c1c00U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01816400U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x00000011U;
                        }
                        if (((0x01816400U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x018bf400U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x00000012U;
                        }
                        if (((0x018bf400U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x018e9800U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x00000013U;
                        }
                        if (((0x018e9800U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01913c00U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x00000014U;
                        }
                        if (((0x01913c00U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01928e00U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x00000015U;
                        }
                        if (((0x01928e00U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x0193e000U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x00000016U;
                        }
                        if (((0x0193e000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01953200U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x00000017U;
                        }
                        if (((0x01953200U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x0197d600U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x00000018U;
                        }
                        if (((0x0197d600U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x019a7a00U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x00000019U;
                        }
                        if (((0x019a7a00U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x019fc200U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x0000001aU;
                        }
                        if (((0x019fc200U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01a11400U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x0000001bU;
                        }
                        if (((0x01a11400U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01a26600U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x0000001cU;
                        }
                        if (((0x01a26600U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01a30f00U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x0000001dU;
                        }
                        if (((0x01a30f00U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01a46100U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x0000001eU;
                        }
                        if (((0x01a46100U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01a474ceU > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x0000001fU;
                        }
                        if (((0x01a47500U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01a51e00U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x00000021U;
                        }
                        if (((0x01a51e00U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01a57280U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x00000022U;
                        }
                        if (((0x01a57280U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01a6c480U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x00000023U;
                        }
                        if (((0x01a6c480U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01aaba80U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x00000024U;
                        }
                        if (((0x01aaba80U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01ad5e80U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x00000025U;
                        }
                        if (((0x01ad5e80U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01adadb8U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x00000026U;
                        }
                    }
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_tensor_owner 
                        = __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout;
                    if ((0U == vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_tensor_owner)) {
                        vlSelfRef.tb_s2a_network_backend_golden__DOT__input_bytes_this_transfer 
                            = ((IData)(1U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__input_bytes_this_transfer);
                    } else if ((1U == vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_tensor_owner)) {
                        vlSelfRef.tb_s2a_network_backend_golden__DOT__weight_bytes_this_transfer 
                            = ((IData)(1U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__weight_bytes_this_transfer);
                    } else if (VL_LIKELY((VL_LTES_III(32, 2U, vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_tensor_owner)))) {
                        vlSelfRef.tb_s2a_network_backend_golden__DOT__feature_bytes_this_transfer 
                            = ((IData)(1U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__feature_bytes_this_transfer);
                        vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_feature_index 
                            = (vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_address 
                               - (IData)(0x01000000U));
                        if (VL_UNLIKELY(((1U & (~ (0U 
                                                   != 
                                                   ((0x00adadb7U 
                                                     >= 
                                                     (0x00ffffffU 
                                                      & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_feature_index))
                                                     ? vlSelfRef.tb_s2a_network_backend_golden__DOT__feature_byte_valid
                                                    [
                                                    (0x00ffffffU 
                                                     & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_feature_index)]
                                                     : 0U))))))) {
                            VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_network_backend_golden.sv:671: Assertion failed in %m: T68 feature read \346\234\252\345\210\235\345\247\213\345\214\226\357\274\232%08h\n",4, 'M',vlSymsp->name(),"tb_s2a_network_backend_golden", 'T',-9
                                         , '#',64,VL_TIME_UNITED_Q(1000)
                                         , '#',32,vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_address);
                            VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_network_backend_golden.sv", 671, "", false);
                        }
                    } else {
                        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_network_backend_golden.sv:674: Assertion failed in %m: T68 \346\216\245\345\217\227\344\272\206\346\262\241\346\234\211\345\220\210\346\263\225 tensor owner \347\232\204 read lane\357\274\232%08h\n",4, 'M',vlSymsp->name(),"tb_s2a_network_backend_golden", 'T',-9
                                     , '#',64,VL_TIME_UNITED_Q(1000)
                                     , '#',32,vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_address);
                        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_network_backend_golden.sv", 674, "", false);
                    }
                }
                if ((8U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_rstrb))) {
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_address 
                        = ((IData)(3U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr);
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__active_byte_count 
                        = ((IData)(1U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__active_byte_count);
                    __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address 
                        = vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_address;
                    __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0xffffffffU;
                    if ((0x0007ec00U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address)) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0U;
                    } else if (((0x00100000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                                & (0x006a12fcU > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                        __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 1U;
                    } else {
                        if (((0x01000000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01152000U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 2U;
                        }
                        if (((0x01152000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x011fb000U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 3U;
                        }
                        if (((0x011fb000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x012a4000U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 4U;
                        }
                        if (((0x012a4000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x012f8800U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 5U;
                        }
                        if (((0x012f8800U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x0134d000U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 6U;
                        }
                        if (((0x0134d000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x013a1800U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 7U;
                        }
                        if (((0x013a1800U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x0144a800U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 8U;
                        }
                        if (((0x0144a800U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x014f3800U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 9U;
                        }
                        if (((0x014f3800U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01645800U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x0000000aU;
                        }
                        if (((0x01645800U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x0169a000U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x0000000bU;
                        }
                        if (((0x0169a000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x016ee800U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x0000000cU;
                        }
                        if (((0x016ee800U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01718c00U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x0000000dU;
                        }
                        if (((0x01718c00U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01743000U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x0000000eU;
                        }
                        if (((0x01743000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x0176d400U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x0000000fU;
                        }
                        if (((0x0176d400U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x017c1c00U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x00000010U;
                        }
                        if (((0x017c1c00U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01816400U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x00000011U;
                        }
                        if (((0x01816400U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x018bf400U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x00000012U;
                        }
                        if (((0x018bf400U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x018e9800U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x00000013U;
                        }
                        if (((0x018e9800U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01913c00U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x00000014U;
                        }
                        if (((0x01913c00U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01928e00U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x00000015U;
                        }
                        if (((0x01928e00U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x0193e000U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x00000016U;
                        }
                        if (((0x0193e000U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01953200U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x00000017U;
                        }
                        if (((0x01953200U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x0197d600U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x00000018U;
                        }
                        if (((0x0197d600U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x019a7a00U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x00000019U;
                        }
                        if (((0x019a7a00U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x019fc200U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x0000001aU;
                        }
                        if (((0x019fc200U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01a11400U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x0000001bU;
                        }
                        if (((0x01a11400U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01a26600U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x0000001cU;
                        }
                        if (((0x01a26600U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01a30f00U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x0000001dU;
                        }
                        if (((0x01a30f00U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01a46100U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x0000001eU;
                        }
                        if (((0x01a46100U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01a474ceU > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x0000001fU;
                        }
                        if (((0x01a47500U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01a51e00U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x00000021U;
                        }
                        if (((0x01a51e00U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01a57280U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x00000022U;
                        }
                        if (((0x01a57280U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01a6c480U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x00000023U;
                        }
                        if (((0x01a6c480U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01aaba80U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x00000024U;
                        }
                        if (((0x01aaba80U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01ad5e80U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x00000025U;
                        }
                        if (((0x01ad5e80U <= __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address) 
                             & (0x01adadb8U > __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__address))) {
                            __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout = 0x00000026U;
                        }
                    }
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_tensor_owner 
                        = __Vfunc_tb_s2a_network_backend_golden__DOT__memory_tensor_owner__20__Vfuncout;
                    if ((0U == vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_tensor_owner)) {
                        vlSelfRef.tb_s2a_network_backend_golden__DOT__input_bytes_this_transfer 
                            = ((IData)(1U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__input_bytes_this_transfer);
                    } else if ((1U == vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_tensor_owner)) {
                        vlSelfRef.tb_s2a_network_backend_golden__DOT__weight_bytes_this_transfer 
                            = ((IData)(1U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__weight_bytes_this_transfer);
                    } else if (VL_LIKELY((VL_LTES_III(32, 2U, vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_tensor_owner)))) {
                        vlSelfRef.tb_s2a_network_backend_golden__DOT__feature_bytes_this_transfer 
                            = ((IData)(1U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__feature_bytes_this_transfer);
                        vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_feature_index 
                            = (vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_address 
                               - (IData)(0x01000000U));
                        if (VL_UNLIKELY(((1U & (~ (0U 
                                                   != 
                                                   ((0x00adadb7U 
                                                     >= 
                                                     (0x00ffffffU 
                                                      & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_feature_index))
                                                     ? vlSelfRef.tb_s2a_network_backend_golden__DOT__feature_byte_valid
                                                    [
                                                    (0x00ffffffU 
                                                     & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_feature_index)]
                                                     : 0U))))))) {
                            VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_network_backend_golden.sv:671: Assertion failed in %m: T68 feature read \346\234\252\345\210\235\345\247\213\345\214\226\357\274\232%08h\n",4, 'M',vlSymsp->name(),"tb_s2a_network_backend_golden", 'T',-9
                                         , '#',64,VL_TIME_UNITED_Q(1000)
                                         , '#',32,vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_address);
                            VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_network_backend_golden.sv", 671, "", false);
                        }
                    } else {
                        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_network_backend_golden.sv:674: Assertion failed in %m: T68 \346\216\245\345\217\227\344\272\206\346\262\241\346\234\211\345\220\210\346\263\225 tensor owner \347\232\204 read lane\357\274\232%08h\n",4, 'M',vlSymsp->name(),"tb_s2a_network_backend_golden", 'T',-9
                                     , '#',64,VL_TIME_UNITED_Q(1000)
                                     , '#',32,vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_lane_address);
                        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_network_backend_golden.sv", 674, "", false);
                    }
                }
                vlSelfRef.tb_s2a_network_backend_golden__DOT__total_input_read_bytes 
                    = (vlSelfRef.tb_s2a_network_backend_golden__DOT__total_input_read_bytes 
                       + vlSelfRef.tb_s2a_network_backend_golden__DOT__input_bytes_this_transfer);
                vlSelfRef.tb_s2a_network_backend_golden__DOT__total_weight_read_bytes 
                    = (vlSelfRef.tb_s2a_network_backend_golden__DOT__total_weight_read_bytes 
                       + vlSelfRef.tb_s2a_network_backend_golden__DOT__weight_bytes_this_transfer);
                vlSelfRef.tb_s2a_network_backend_golden__DOT__total_feature_read_bytes 
                    = (vlSelfRef.tb_s2a_network_backend_golden__DOT__total_feature_read_bytes 
                       + vlSelfRef.tb_s2a_network_backend_golden__DOT__feature_bytes_this_transfer);
                vlSelfRef.tb_s2a_network_backend_golden__DOT__total_memory_read_bytes 
                    = (vlSelfRef.tb_s2a_network_backend_golden__DOT__total_memory_read_bytes 
                       + vlSelfRef.tb_s2a_network_backend_golden__DOT__active_byte_count);
            }
            __VdlyVal__tb_s2a_network_backend_golden__DOT__class_selected_byte_count__v0 
                = (vlSelfRef.tb_s2a_network_backend_golden__DOT__class_selected_byte_count
                   [(3U & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_transfer_class)] 
                   + vlSelfRef.tb_s2a_network_backend_golden__DOT__active_byte_count);
            __VdlyDim0__tb_s2a_network_backend_golden__DOT__class_selected_byte_count__v0 
                = (3U & vlSelfRef.tb_s2a_network_backend_golden__DOT__seq_transfer_class);
            __VdlySet__tb_s2a_network_backend_golden__DOT__class_selected_byte_count__v0 = 1U;
        }
        if (((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_valid) 
             & (~ (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_ready)))) {
            __Vdly__tb_s2a_network_backend_golden__DOT__stalled_previous = 1U;
            __Vdly__tb_s2a_network_backend_golden__DOT__class_wait_count 
                = ((IData)(1U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__class_wait_count);
            __Vdly__tb_s2a_network_backend_golden__DOT__stalled_address 
                = vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr;
            __Vdly__tb_s2a_network_backend_golden__DOT__stalled_data 
                = vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_wdata;
            __Vdly__tb_s2a_network_backend_golden__DOT__stalled_write 
                = vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_write;
            __Vdly__tb_s2a_network_backend_golden__DOT__stalled_rstrb 
                = vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_rstrb;
            __Vdly__tb_s2a_network_backend_golden__DOT__stalled_wstrb 
                = vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_wstrb;
        } else {
            __Vdly__tb_s2a_network_backend_golden__DOT__stalled_previous = 0U;
            if ((1U & ((~ (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_valid)) 
                       | ((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_valid) 
                          & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_ready))))) {
                __Vdly__tb_s2a_network_backend_golden__DOT__class_wait_count = 0U;
            }
        }
    }
    if (vlSelfRef.tb_s2a_network_backend_golden__DOT__hard_reset) {
        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__state = 0U;
        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor = 0U;
        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_element_index = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__response_error_latched = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__response_target_latched = 0U;
        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state = 0U;
        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_layer_index_latched = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_base_latched = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_length_latched = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_batch_count_latched = 0U;
        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_channels_latched = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_height_latched = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_width_latched = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_base_latched = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_length_latched = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_batch_count_latched = 0U;
        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_channels_latched = 0U;
        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_latched = 0U;
        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_latched = 0U;
        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_height_latched = 0U;
        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_width_latched = 0U;
        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__stride_y_latched = 0U;
        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__stride_x_latched = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__pad_left_latched = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__pad_right_latched = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__pad_top_latched = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__pad_bottom_latched = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__groups_latched = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__padding_latched = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_package_base_latched = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_package_length_latched = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__quantized_weight_offset_latched = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__quantized_weight_bytes_latched = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_batch_latched = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__activation_mode_latched = 0U;
        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_latched = 0U;
        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base = 0U;
        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_y = 0U;
        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_x = 0U;
        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_height = 0U;
        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_width = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__patch_height = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__patch_width = 0U;
        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__patch_byte_count = 0U;
        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_point_count = 0U;
        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count = 0U;
        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_index = 0U;
        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_lane_index = 0U;
        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_reduction_index = 0U;
        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_index = 0U;
        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_reduction_index = 0U;
        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_lane_index = 0U;
        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_point_index = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__request_address_latched = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__request_strobe_latched = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__request_wdata_latched = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__result_error_latched = 0U;
        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__state = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source_count_latched = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__groups_latched = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__group_id_latched = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_channel_latched = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_y_latched = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_x_latched = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_base_latched = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_length_latched = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_channels_latched = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_height_latched = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_width_latched = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_start_latched = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_end_latched = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_multiplier_latched = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_value_latched = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source1_base_latched = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source1_length_latched = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source1_channels_latched = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source1_height_latched = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source1_width_latched = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source1_start_latched = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source1_end_latched = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source1_multiplier_latched = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source1_value_latched = 0U;
        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_base_latched = 0U;
        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_length_latched = 0U;
        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_channels_latched = 0U;
        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_height_latched = 0U;
        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_width_latched = 0U;
        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source_index_latched = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source_address_latched = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_address_latched = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__result_value_latched = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__result_error_latched = 0U;
        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__state = 0U;
        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__source_address_latched = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__output_address_latched = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__copied_value_latched = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__result_error_latched = 0U;
        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__state = 0U;
        __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched__v0 = 1U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_address_latched = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__candidate_values_latched[0U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__candidate_values_latched[1U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__candidate_values_latched[2U] = 0U;
        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__read_tap_index = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__result_value_latched = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__result_error_latched = 0U;
        __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched__v1 = 1U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__response_data_latched = 0U;
    } else {
        if ((4U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__state))) {
            if ((2U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__state))) {
                __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__state = 0U;
            } else if (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__selected_result_valid) {
                __Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__normalize_engine_error__27__code 
                    = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__selected_result_error;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____VlemCall_2__normalize_engine_error 
                    = ((4U & (IData)(__Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__normalize_engine_error__27__code))
                        ? (IData)(__Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__normalize_engine_error__27__code)
                        : ((2U & (IData)(__Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__normalize_engine_error__27__code))
                            ? (IData)(__Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__normalize_engine_error__27__code)
                            : ((1U & (IData)(__Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__normalize_engine_error__27__code))
                                ? (IData)(__Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__normalize_engine_error__27__code)
                                : 0U)));
                if ((0U != (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____VlemCall_2__normalize_engine_error))) {
                    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__state = 0U;
                } else if (((0U != (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__current_op)) 
                            & ((1ULL + (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_element_index))) 
                               < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_element_count))) {
                    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_element_index 
                        = ((IData)(1U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_element_index);
                    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__state = 1U;
                } else if ((0x00000026U <= ((IData)(1U) 
                                            + (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor)))) {
                    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__state = 0U;
                } else {
                    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor 
                        = (0x0000003fU & ((IData)(1U) 
                                          + (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor)));
                    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_element_index = 0U;
                    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__state = 1U;
                }
            }
        } else if ((2U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__state))) {
            if (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__selected_result_valid) {
                __Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__normalize_engine_error__28__code 
                    = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__selected_result_error;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____VlemCall_2__normalize_engine_error 
                    = ((4U & (IData)(__Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__normalize_engine_error__28__code))
                        ? (IData)(__Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__normalize_engine_error__28__code)
                        : ((2U & (IData)(__Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__normalize_engine_error__28__code))
                            ? (IData)(__Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__normalize_engine_error__28__code)
                            : ((1U & (IData)(__Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__normalize_engine_error__28__code))
                                ? (IData)(__Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__normalize_engine_error__28__code)
                                : 0U)));
                if ((0U != (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____VlemCall_2__normalize_engine_error))) {
                    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__state = 0U;
                } else if (((0U != (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__current_op)) 
                            & ((1ULL + (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_element_index))) 
                               < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_element_count))) {
                    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_element_index 
                        = ((IData)(1U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_element_index);
                    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__state = 1U;
                } else if ((0x00000026U <= ((IData)(1U) 
                                            + (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor)))) {
                    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__state = 0U;
                } else {
                    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor 
                        = (0x0000003fU & ((IData)(1U) 
                                          + (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor)));
                    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_element_index = 0U;
                    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__state = 1U;
                }
            }
        } else if ((1U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__state))) {
            if (vlSelfRef.tb_s2a_network_backend_golden__DOT__buffer_owner_pl) {
                if (((0x26U <= (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor)) 
                     | (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__descriptor_fault))) {
                    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__state = 0U;
                } else if (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__is_alias_row) {
                    if (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__alias_valid) {
                        if ((0x00000026U <= ((IData)(1U) 
                                             + (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor)))) {
                            __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__state = 0U;
                        } else {
                            __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor 
                                = (0x0000003fU & ((IData)(1U) 
                                                  + (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor)));
                            __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_element_index = 0U;
                        }
                    } else {
                        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__state = 0U;
                    }
                } else {
                    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__state 
                        = ((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__selected_start_ready)
                            ? (7U & (0x00000b1aU >> 
                                     ((IData)(3U) * (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__current_op))))
                            : 0U);
                }
            }
        } else if (((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__backend_start) 
                    & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__buffer_owner_pl))) {
            __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor = 0U;
            __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_element_index = 0U;
            __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__state = 1U;
        }
        if ((0x00000010U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state))) {
            if ((8U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state))) {
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__result_error_latched = 6U;
                __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state = 0x12U;
            } else if ((4U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state))) {
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__result_error_latched = 6U;
                __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state = 0x12U;
            } else if ((2U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state))) {
                if ((1U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state))) {
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__result_error_latched = 6U;
                    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state = 0x12U;
                } else if (((0x12U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state)) 
                            & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__conv_result_ready))) {
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__result_error_latched = 0U;
                    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state = 0U;
                }
            } else if ((1U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state))) {
                if ((((IData)(8U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base) 
                     < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_channels_latched)) {
                    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base 
                        = ((IData)(8U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base);
                    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state = 6U;
                } else if (((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_x 
                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_width) 
                            < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_latched)) {
                    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_x 
                        = ((IData)(8U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_x);
                    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base = 0U;
                    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state = 2U;
                } else if (((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_y 
                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_height) 
                            < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_latched)) {
                    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_y 
                        = ((IData)(8U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_y);
                    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base = 0U;
                    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_x = 0U;
                    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state = 2U;
                } else {
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__result_error_latched = 0U;
                    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state = 0x12U;
                }
            } else if (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__conv_rsp_valid) {
                if ((0U != (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mapped_response_error))) {
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__result_error_latched 
                        = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mapped_response_error;
                    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state = 0x12U;
                } else {
                    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_point_index 
                        = ((IData)(1U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_point_index);
                    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state = 0x0eU;
                }
            }
        } else if ((8U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state))) {
            if ((4U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state))) {
                if ((2U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state))) {
                    if ((1U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state))) {
                        if (((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__conv_req_valid) 
                             & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__conv_req_ready))) {
                            __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state = 0x10U;
                        }
                    } else if ((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_lane_index 
                                >= vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
                        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state = 0x11U;
                    } else if ((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_point_index 
                                >= vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_point_count)) {
                        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_lane_index 
                            = ((IData)(1U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_lane_index);
                        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_point_index = 0U;
                    } else {
                        __Vtemp_1[0U] = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_byte_offset_wide);
                        __Vtemp_1[1U] = (IData)((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_byte_offset_wide 
                                                 >> 0x00000020U));
                        __Vtemp_1[2U] = 0U;
                        __Vtemp_1[3U] = 0U;
                        if (((0x00000000ffffffffULL 
                              < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_address_wide) 
                             | VL_GTE_W(4, __Vtemp_1, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_elements_wide))) {
                            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__result_error_latched = 2U;
                            __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state = 0x12U;
                        } else {
                            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__request_address_latched 
                                = ((IData)((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_address_wide 
                                            >> 2U)) 
                                   << 2U);
                            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__request_strobe_latched 
                                = (0x0000000fU & ((IData)(1U) 
                                                  << 
                                                  (3U 
                                                   & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_address_wide))));
                            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__request_wdata_latched 
                                = VL_SHIFTL_III(32,32,32, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block
                                                [(0x000001ffU 
                                                  & ((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_lane_index 
                                                      << 6U) 
                                                     + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_point_index))], 
                                                (0x00000018U 
                                                 & ((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_address_wide) 
                                                    << 3U)));
                            __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state = 0x0fU;
                        }
                    }
                } else if ((1U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state))) {
                    if ((0U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
                        __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v0 
                            = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requantized_value[0U];
                        __VdlyDim0__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v0 
                            = (0x000001ffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_index);
                        __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v0 = 1U;
                    }
                    if ((1U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
                        __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v1 
                            = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requantized_value[1U];
                        __VdlyDim0__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v1 
                            = (0x000001ffU & ((IData)(0x0040U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_index));
                        __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v1 = 1U;
                    }
                    if ((2U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
                        __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v2 
                            = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requantized_value[2U];
                        __VdlyDim0__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v2 
                            = (0x000001ffU & ((IData)(0x0080U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_index));
                        __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v2 = 1U;
                    }
                    if ((3U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
                        __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v3 
                            = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requantized_value[3U];
                        __VdlyDim0__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v3 
                            = (0x000001ffU & ((IData)(0x00c0U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_index));
                        __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v3 = 1U;
                    }
                    if ((4U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
                        __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v4 
                            = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requantized_value[4U];
                        __VdlyDim0__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v4 
                            = (0x000001ffU & ((IData)(0x0100U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_index));
                        __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v4 = 1U;
                    }
                    if ((5U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
                        __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v5 
                            = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requantized_value[5U];
                        __VdlyDim0__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v5 
                            = (0x000001ffU & ((IData)(0x0140U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_index));
                        __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v5 = 1U;
                    }
                    if ((6U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
                        __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v6 
                            = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requantized_value[6U];
                        __VdlyDim0__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v6 
                            = (0x000001ffU & ((IData)(0x0180U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_index));
                        __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v6 = 1U;
                    }
                    if ((7U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
                        __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v7 
                            = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requantized_value[7U];
                        __VdlyDim0__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v7 
                            = (0x000001ffU & ((IData)(0x01c0U) 
                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_index));
                        __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v7 = 1U;
                    }
                    if ((((IData)(1U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_index) 
                         >= vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_point_count)) {
                        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_lane_index = 0U;
                        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_point_index = 0U;
                        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state = 0x0eU;
                    } else {
                        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_index 
                            = ((IData)(1U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_index);
                        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_reduction_index = 0U;
                        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state = 0x0bU;
                    }
                } else if (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_bad_argument) {
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__result_error_latched = 1U;
                    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state = 0x12U;
                } else if (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_overflow) {
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__result_error_latched = 7U;
                    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state = 0x12U;
                } else {
                    if ((0U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
                        __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v0 
                            = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[0U]);
                        __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v0 = 1U;
                    }
                    if ((((IData)(1U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_reduction_index) 
                         >= vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_latched)) {
                        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state = 0x0dU;
                    } else {
                        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_reduction_index 
                            = ((IData)(1U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_reduction_index);
                    }
                    if ((1U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
                        __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v1 
                            = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[1U]);
                        __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v1 = 1U;
                    }
                    if ((2U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
                        __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v2 
                            = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[2U]);
                        __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v2 = 1U;
                    }
                    if ((3U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
                        __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v3 
                            = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[3U]);
                        __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v3 = 1U;
                    }
                    if ((4U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
                        __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v4 
                            = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[4U]);
                        __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v4 = 1U;
                    }
                    if ((5U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
                        __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v5 
                            = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[5U]);
                        __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v5 = 1U;
                    }
                    if ((6U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
                        __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v6 
                            = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[6U]);
                        __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v6 = 1U;
                    }
                    if ((7U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
                        __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v7 
                            = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[7U]);
                        __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v7 = 1U;
                    }
                }
            } else if ((2U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state))) {
                if ((1U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state))) {
                    if (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_group_invalid) {
                        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__result_error_latched = 1U;
                        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state = 0x12U;
                    } else {
                        __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v8 
                            = ((0U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)
                                ? ((0x0c5bU >= (0x00000fffU 
                                                & (((0x25U 
                                                     >= 
                                                     (0x0000003fU 
                                                      & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                                     ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                                    [
                                                    (0x0000003fU 
                                                     & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                                     : 0U) 
                                                   + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base)))
                                    ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_CONV_BIAS_ACCUMULATOR_INT32
                                   [(0x00000fffU & 
                                     (((0x25U >= (0x0000003fU 
                                                  & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                        ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                       [(0x0000003fU 
                                         & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                        : 0U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base))]
                                    : 0U) : 0U);
                        __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v8 = 1U;
                        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_reduction_index = 0U;
                        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state = 0x0cU;
                        __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v9 
                            = ((1U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)
                                ? ((0x0c5bU >= (0x00000fffU 
                                                & ((IData)(1U) 
                                                   + 
                                                   (((0x25U 
                                                      >= 
                                                      (0x0000003fU 
                                                       & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                                      ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                                     [
                                                     (0x0000003fU 
                                                      & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                                      : 0U) 
                                                    + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base))))
                                    ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_CONV_BIAS_ACCUMULATOR_INT32
                                   [(0x00000fffU & 
                                     ((IData)(1U) + 
                                      (((0x25U >= (0x0000003fU 
                                                   & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                         ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                        [(0x0000003fU 
                                          & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                         : 0U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base)))]
                                    : 0U) : 0U);
                        __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v9 = 1U;
                        __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v10 
                            = ((2U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)
                                ? ((0x0c5bU >= (0x00000fffU 
                                                & ((IData)(2U) 
                                                   + 
                                                   (((0x25U 
                                                      >= 
                                                      (0x0000003fU 
                                                       & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                                      ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                                     [
                                                     (0x0000003fU 
                                                      & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                                      : 0U) 
                                                    + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base))))
                                    ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_CONV_BIAS_ACCUMULATOR_INT32
                                   [(0x00000fffU & 
                                     ((IData)(2U) + 
                                      (((0x25U >= (0x0000003fU 
                                                   & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                         ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                        [(0x0000003fU 
                                          & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                         : 0U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base)))]
                                    : 0U) : 0U);
                        __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v11 
                            = ((3U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)
                                ? ((0x0c5bU >= (0x00000fffU 
                                                & ((IData)(3U) 
                                                   + 
                                                   (((0x25U 
                                                      >= 
                                                      (0x0000003fU 
                                                       & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                                      ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                                     [
                                                     (0x0000003fU 
                                                      & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                                      : 0U) 
                                                    + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base))))
                                    ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_CONV_BIAS_ACCUMULATOR_INT32
                                   [(0x00000fffU & 
                                     ((IData)(3U) + 
                                      (((0x25U >= (0x0000003fU 
                                                   & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                         ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                        [(0x0000003fU 
                                          & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                         : 0U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base)))]
                                    : 0U) : 0U);
                        __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v12 
                            = ((4U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)
                                ? ((0x0c5bU >= (0x00000fffU 
                                                & ((IData)(4U) 
                                                   + 
                                                   (((0x25U 
                                                      >= 
                                                      (0x0000003fU 
                                                       & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                                      ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                                     [
                                                     (0x0000003fU 
                                                      & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                                      : 0U) 
                                                    + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base))))
                                    ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_CONV_BIAS_ACCUMULATOR_INT32
                                   [(0x00000fffU & 
                                     ((IData)(4U) + 
                                      (((0x25U >= (0x0000003fU 
                                                   & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                         ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                        [(0x0000003fU 
                                          & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                         : 0U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base)))]
                                    : 0U) : 0U);
                        __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v13 
                            = ((5U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)
                                ? ((0x0c5bU >= (0x00000fffU 
                                                & ((IData)(5U) 
                                                   + 
                                                   (((0x25U 
                                                      >= 
                                                      (0x0000003fU 
                                                       & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                                      ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                                     [
                                                     (0x0000003fU 
                                                      & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                                      : 0U) 
                                                    + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base))))
                                    ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_CONV_BIAS_ACCUMULATOR_INT32
                                   [(0x00000fffU & 
                                     ((IData)(5U) + 
                                      (((0x25U >= (0x0000003fU 
                                                   & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                         ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                        [(0x0000003fU 
                                          & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                         : 0U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base)))]
                                    : 0U) : 0U);
                        __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v14 
                            = ((6U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)
                                ? ((0x0c5bU >= (0x00000fffU 
                                                & ((IData)(6U) 
                                                   + 
                                                   (((0x25U 
                                                      >= 
                                                      (0x0000003fU 
                                                       & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                                      ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                                     [
                                                     (0x0000003fU 
                                                      & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                                      : 0U) 
                                                    + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base))))
                                    ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_CONV_BIAS_ACCUMULATOR_INT32
                                   [(0x00000fffU & 
                                     ((IData)(6U) + 
                                      (((0x25U >= (0x0000003fU 
                                                   & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                         ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                        [(0x0000003fU 
                                          & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                         : 0U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base)))]
                                    : 0U) : 0U);
                        __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v15 
                            = ((7U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)
                                ? ((0x0c5bU >= (0x00000fffU 
                                                & ((IData)(7U) 
                                                   + 
                                                   (((0x25U 
                                                      >= 
                                                      (0x0000003fU 
                                                       & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                                      ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                                     [
                                                     (0x0000003fU 
                                                      & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                                      : 0U) 
                                                    + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base))))
                                    ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_CONV_BIAS_ACCUMULATOR_INT32
                                   [(0x00000fffU & 
                                     ((IData)(7U) + 
                                      (((0x25U >= (0x0000003fU 
                                                   & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                         ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                        [(0x0000003fU 
                                          & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                         : 0U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base)))]
                                    : 0U) : 0U);
                    }
                } else if (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_group_invalid) {
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__result_error_latched = 1U;
                    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state = 0x12U;
                } else {
                    __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v16 
                        = ((0U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)
                            ? ((0x0c5bU >= (0x00000fffU 
                                            & (((0x25U 
                                                 >= 
                                                 (0x0000003fU 
                                                  & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                                 ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                                [(0x0000003fU 
                                                  & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                                 : 0U) 
                                               + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base)))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_CONV_BIAS_ACCUMULATOR_INT32
                               [(0x00000fffU & (((0x25U 
                                                  >= 
                                                  (0x0000003fU 
                                                   & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                                 [(0x0000003fU 
                                                   & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                                  : 0U) 
                                                + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base))]
                                : 0U) : 0U);
                    __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v16 = 1U;
                    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_index = 0U;
                    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_reduction_index = 0U;
                    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state = 0x0cU;
                    __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v17 
                        = ((1U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)
                            ? ((0x0c5bU >= (0x00000fffU 
                                            & ((IData)(1U) 
                                               + ((
                                                   (0x25U 
                                                    >= 
                                                    (0x0000003fU 
                                                     & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                                    ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                                   [
                                                   (0x0000003fU 
                                                    & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                                    : 0U) 
                                                  + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base))))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_CONV_BIAS_ACCUMULATOR_INT32
                               [(0x00000fffU & ((IData)(1U) 
                                                + (
                                                   ((0x25U 
                                                     >= 
                                                     (0x0000003fU 
                                                      & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                                     ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                                    [
                                                    (0x0000003fU 
                                                     & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                                     : 0U) 
                                                   + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base)))]
                                : 0U) : 0U);
                    __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v17 = 1U;
                    __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v18 
                        = ((2U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)
                            ? ((0x0c5bU >= (0x00000fffU 
                                            & ((IData)(2U) 
                                               + ((
                                                   (0x25U 
                                                    >= 
                                                    (0x0000003fU 
                                                     & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                                    ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                                   [
                                                   (0x0000003fU 
                                                    & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                                    : 0U) 
                                                  + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base))))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_CONV_BIAS_ACCUMULATOR_INT32
                               [(0x00000fffU & ((IData)(2U) 
                                                + (
                                                   ((0x25U 
                                                     >= 
                                                     (0x0000003fU 
                                                      & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                                     ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                                    [
                                                    (0x0000003fU 
                                                     & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                                     : 0U) 
                                                   + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base)))]
                                : 0U) : 0U);
                    __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v19 
                        = ((3U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)
                            ? ((0x0c5bU >= (0x00000fffU 
                                            & ((IData)(3U) 
                                               + ((
                                                   (0x25U 
                                                    >= 
                                                    (0x0000003fU 
                                                     & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                                    ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                                   [
                                                   (0x0000003fU 
                                                    & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                                    : 0U) 
                                                  + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base))))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_CONV_BIAS_ACCUMULATOR_INT32
                               [(0x00000fffU & ((IData)(3U) 
                                                + (
                                                   ((0x25U 
                                                     >= 
                                                     (0x0000003fU 
                                                      & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                                     ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                                    [
                                                    (0x0000003fU 
                                                     & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                                     : 0U) 
                                                   + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base)))]
                                : 0U) : 0U);
                    __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v20 
                        = ((4U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)
                            ? ((0x0c5bU >= (0x00000fffU 
                                            & ((IData)(4U) 
                                               + ((
                                                   (0x25U 
                                                    >= 
                                                    (0x0000003fU 
                                                     & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                                    ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                                   [
                                                   (0x0000003fU 
                                                    & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                                    : 0U) 
                                                  + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base))))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_CONV_BIAS_ACCUMULATOR_INT32
                               [(0x00000fffU & ((IData)(4U) 
                                                + (
                                                   ((0x25U 
                                                     >= 
                                                     (0x0000003fU 
                                                      & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                                     ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                                    [
                                                    (0x0000003fU 
                                                     & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                                     : 0U) 
                                                   + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base)))]
                                : 0U) : 0U);
                    __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v21 
                        = ((5U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)
                            ? ((0x0c5bU >= (0x00000fffU 
                                            & ((IData)(5U) 
                                               + ((
                                                   (0x25U 
                                                    >= 
                                                    (0x0000003fU 
                                                     & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                                    ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                                   [
                                                   (0x0000003fU 
                                                    & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                                    : 0U) 
                                                  + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base))))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_CONV_BIAS_ACCUMULATOR_INT32
                               [(0x00000fffU & ((IData)(5U) 
                                                + (
                                                   ((0x25U 
                                                     >= 
                                                     (0x0000003fU 
                                                      & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                                     ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                                    [
                                                    (0x0000003fU 
                                                     & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                                     : 0U) 
                                                   + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base)))]
                                : 0U) : 0U);
                    __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v22 
                        = ((6U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)
                            ? ((0x0c5bU >= (0x00000fffU 
                                            & ((IData)(6U) 
                                               + ((
                                                   (0x25U 
                                                    >= 
                                                    (0x0000003fU 
                                                     & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                                    ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                                   [
                                                   (0x0000003fU 
                                                    & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                                    : 0U) 
                                                  + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base))))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_CONV_BIAS_ACCUMULATOR_INT32
                               [(0x00000fffU & ((IData)(6U) 
                                                + (
                                                   ((0x25U 
                                                     >= 
                                                     (0x0000003fU 
                                                      & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                                     ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                                    [
                                                    (0x0000003fU 
                                                     & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                                     : 0U) 
                                                   + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base)))]
                                : 0U) : 0U);
                    __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v23 
                        = ((7U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)
                            ? ((0x0c5bU >= (0x00000fffU 
                                            & ((IData)(7U) 
                                               + ((
                                                   (0x25U 
                                                    >= 
                                                    (0x0000003fU 
                                                     & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                                    ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                                   [
                                                   (0x0000003fU 
                                                    & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                                    : 0U) 
                                                  + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base))))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_CONV_BIAS_ACCUMULATOR_INT32
                               [(0x00000fffU & ((IData)(7U) 
                                                + (
                                                   ((0x25U 
                                                     >= 
                                                     (0x0000003fU 
                                                      & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                                     ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                                    [
                                                    (0x0000003fU 
                                                     & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                                     : 0U) 
                                                   + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base)))]
                                : 0U) : 0U);
                }
            } else if ((1U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state))) {
                if (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__conv_rsp_valid) {
                    if ((0U != (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mapped_response_error))) {
                        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__result_error_latched 
                            = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mapped_response_error;
                        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state = 0x12U;
                    } else {
                        if ((0x8fffU >= (0x0000ffffU 
                                         & ((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_lane_index 
                                             * vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_latched) 
                                            + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_reduction_index)))) {
                            __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_group__v0 
                                = (0x000000ffU & VL_SHIFTR_III(8,32,32, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__response_data_latched, 
                                                               ((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__request_byte_lane) 
                                                                << 3U)));
                            __VdlyDim0__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_group__v0 
                                = (0x0000ffffU & ((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_lane_index 
                                                   * vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_latched) 
                                                  + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_reduction_index));
                            __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_group__v0 = 1U;
                        }
                        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state = 7U;
                        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_reduction_index 
                            = ((IData)(1U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_reduction_index);
                    }
                }
            } else if (((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__conv_req_valid) 
                        & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__conv_req_ready))) {
                __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state = 9U;
            }
        } else if ((4U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state))) {
            if ((2U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state))) {
                if ((1U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state))) {
                    if ((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_lane_index 
                         >= vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
                        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state = 0x0aU;
                    } else if ((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_reduction_index 
                                >= vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_latched)) {
                        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_lane_index 
                            = ((IData)(1U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_lane_index);
                        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_reduction_index = 0U;
                    } else if ((0x00000000ffffffffULL 
                                < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_source_address_wide)) {
                        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__result_error_latched = 2U;
                        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state = 0x12U;
                    } else {
                        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__request_address_latched 
                            = ((IData)((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_source_address_wide 
                                        >> 2U)) << 2U);
                        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__request_strobe_latched 
                            = (0x0000000fU & ((IData)(1U) 
                                              << (3U 
                                                  & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_source_address_wide))));
                        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__request_wdata_latched = 0U;
                        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state = 8U;
                    }
                } else if ((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base 
                            >= vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_channels_latched)) {
                    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state = 0x11U;
                } else {
                    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count 
                        = ((8U <= (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_channels_latched 
                                   - vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base))
                            ? 8U : (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_channels_latched 
                                    - vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base));
                    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_lane_index = 0U;
                    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_reduction_index = 0U;
                    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state = 7U;
                }
            } else if ((1U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state))) {
                if (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__conv_rsp_valid) {
                    if ((0U != (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mapped_response_error))) {
                        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__result_error_latched 
                            = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mapped_response_error;
                        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state = 0x12U;
                    } else {
                        if ((0xc7ffU >= (0x0000ffffU 
                                         & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_index))) {
                            __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_patch__v0 
                                = (0x000000ffU & VL_SHIFTR_III(8,32,32, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__response_data_latched, 
                                                               ((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__request_byte_lane) 
                                                                << 3U)));
                            __VdlyDim0__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_patch__v0 
                                = (0x0000ffffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_index);
                            __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_patch__v0 = 1U;
                        }
                        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state = 3U;
                        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_index 
                            = ((IData)(1U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_index);
                    }
                }
            } else if (((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__conv_req_valid) 
                        & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__conv_req_ready))) {
                __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state = 5U;
            }
        } else if ((2U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state))) {
            if ((1U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state))) {
                if ((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_index 
                     >= vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__patch_byte_count)) {
                    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base = 0U;
                    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state = 6U;
                } else if (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_in_bounds) {
                    if ((0x00000000ffffffffULL < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_source_address_wide)) {
                        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__result_error_latched = 2U;
                        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state = 0x12U;
                    } else {
                        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__request_address_latched 
                            = ((IData)((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_source_address_wide 
                                        >> 2U)) << 2U);
                        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__request_strobe_latched 
                            = (0x0000000fU & ((IData)(1U) 
                                              << (3U 
                                                  & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_source_address_wide))));
                        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__request_wdata_latched = 0U;
                        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state = 4U;
                    }
                } else {
                    if ((0xc7ffU >= (0x0000ffffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_index))) {
                        __VdlyDim0__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_patch__v1 
                            = (0x0000ffffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_index);
                        __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_patch__v1 = 1U;
                    }
                    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_index 
                        = ((IData)(1U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_index);
                }
            } else {
                __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_height 
                    = ((8U <= (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_latched 
                               - vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_y))
                        ? 8U : (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_latched 
                                - vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_y));
                __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_index = 0U;
                __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state = 3U;
                __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_width 
                    = ((8U <= (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_latched 
                               - vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_x))
                        ? 8U : (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_latched 
                                - vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_x));
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__patch_height 
                    = (((((8U <= (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_latched 
                                  - vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_y))
                           ? 8U : (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_latched 
                                   - vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_y)) 
                         - (IData)(1U)) * vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__stride_y_latched) 
                       + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_height_latched);
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__patch_width 
                    = (((((8U <= (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_latched 
                                  - vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_x))
                           ? 8U : (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_latched 
                                   - vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_x)) 
                         - (IData)(1U)) * vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__stride_x_latched) 
                       + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_width_latched);
                __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__patch_byte_count 
                    = (((((((8U <= (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_latched 
                                    - vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_y))
                             ? 8U : (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_latched 
                                     - vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_y)) 
                           - (IData)(1U)) * vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__stride_y_latched) 
                         + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_height_latched) 
                        * (((((8U <= (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_latched 
                                      - vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_x))
                               ? 8U : (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_latched 
                                       - vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_x)) 
                             - (IData)(1U)) * vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__stride_x_latched) 
                           + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_width_latched)) 
                       * vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_channels_latched);
                __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_point_count 
                    = (((8U <= (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_latched 
                                - vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_y))
                         ? 8U : (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_latched 
                                 - vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_y)) 
                       * ((8U <= (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_latched 
                                  - vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_x))
                           ? 8U : (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_latched 
                                   - vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_x)));
            }
        } else if ((1U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state))) {
            if (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__validation_ok) {
                __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_latched 
                    = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_wide[0U];
                __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state = 2U;
            } else {
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__result_error_latched 
                    = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__validation_error;
                __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state = 0x12U;
            }
        } else if (((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__conv_start_valid) 
                    & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__conv_start_ready))) {
            if ((0x25U >= (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor))) {
                __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_LAYER_INDEX
                    [vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor];
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_layer_index_latched 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_WEIGHT_LAYER_INDEX
                    [vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor];
                __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_height_latched 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_KERNEL_H
                    [vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor];
                __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_width_latched 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_KERNEL_W
                    [vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor];
                __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__stride_y_latched 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_STRIDE_H
                    [vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor];
                __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__stride_x_latched 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_STRIDE_W
                    [vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor];
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__pad_left_latched 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_PADDING_LEFT
                    [vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor];
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__pad_right_latched 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_PADDING_RIGHT
                    [vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor];
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__pad_top_latched 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_PADDING_TOP
                    [vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor];
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__pad_bottom_latched 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_PADDING_BOTTOM
                    [vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor];
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__groups_latched 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_GROUP_COUNT
                    [vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor];
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__quantized_weight_offset_latched 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_GF8_WEIGHT_OFFSET
                    [vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor];
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__quantized_weight_bytes_latched 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_GF8_WEIGHT_BYTES
                    [vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor];
            } else {
                __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched = 0U;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_layer_index_latched = 0U;
                __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_height_latched = 0U;
                __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_width_latched = 0U;
                __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__stride_y_latched = 0U;
                __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__stride_x_latched = 0U;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__pad_left_latched = 0U;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__pad_right_latched = 0U;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__pad_top_latched = 0U;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__pad_bottom_latched = 0U;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__groups_latched = 0U;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__quantized_weight_offset_latched = 0U;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__quantized_weight_bytes_latched = 0U;
            }
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_base_latched 
                = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_base[0U];
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_length_latched 
                = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_length[0U];
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_batch_count_latched 
                = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_n[0U];
            __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_channels_latched 
                = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_c[0U];
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_height_latched 
                = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_h[0U];
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_width_latched 
                = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_w[0U];
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_base_latched 
                = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_base;
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_length_latched 
                = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_length;
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_batch_count_latched 
                = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_n;
            __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_channels_latched 
                = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_c;
            __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_latched 
                = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_h;
            __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_latched 
                = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_w;
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__padding_latched 
                = (((- (IData)((1U & (((0x25U >= (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor))
                                        ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_PADDING_VALUE_INT8
                                       [vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor]
                                        : 0U) >> 7U)))) 
                    << 8U) | ((0x25U >= (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor))
                               ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_PADDING_VALUE_INT8
                              [vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor]
                               : 0U));
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_package_base_latched = 0x00100000U;
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_package_length_latched = 0x005a12fcU;
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_batch_latched = 0U;
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__activation_mode_latched 
                = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_conv_engine__activation_mode;
            __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_latched = 0U;
            __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base = 0U;
            __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_y = 0U;
            __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_x = 0U;
            __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_index = 0U;
            __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_lane_index = 0U;
            __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_reduction_index = 0U;
            __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_index = 0U;
            __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_reduction_index = 0U;
            __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_lane_index = 0U;
            __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_point_index = 0U;
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__result_error_latched = 0U;
            __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state = 1U;
        }
        if ((8U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__state))) {
            __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__state = 0U;
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__result_value_latched = 0U;
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__result_error_latched = 6U;
        } else if ((4U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__state))) {
            if ((2U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__state))) {
                if ((1U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__state))) {
                    if (((7U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__state)) 
                         & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__route_result_ready))) {
                        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__state = 0U;
                        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__result_error_latched = 0U;
                    }
                } else if (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__route_rsp_valid) {
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__result_error_latched 
                        = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__mapped_response_error;
                    if ((0U != (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__mapped_response_error))) {
                        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__result_value_latched = 0U;
                    }
                    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__state = 7U;
                }
            } else if ((1U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__state))) {
                if (((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__route_req_valid) 
                     & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__route_req_ready))) {
                    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__state = 6U;
                }
            } else if ((0U != (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__query_error_code))) {
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__result_value_latched = 0U;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__result_error_latched 
                    = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__query_error_code;
                __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__state = 7U;
            } else {
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__result_value_latched 
                    = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__query_output_value;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__result_error_latched = 0U;
                __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__state = 5U;
            }
        } else if ((2U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__state))) {
            if ((1U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__state))) {
                if (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__route_rsp_valid) {
                    if ((0U != (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__mapped_response_error))) {
                        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__result_value_latched = 0U;
                        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__result_error_latched 
                            = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__mapped_response_error;
                        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__state = 7U;
                    } else if ((0U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source_index_latched)) {
                        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_value_latched 
                            = (0x000000ffU & VL_SHIFTR_III(8,32,32, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__response_data_latched, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__selected_byte_shift));
                        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__state = 4U;
                    } else if ((1U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source_index_latched)) {
                        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source1_value_latched 
                            = (0x000000ffU & VL_SHIFTR_III(8,32,32, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__response_data_latched, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__selected_byte_shift));
                        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__state = 4U;
                    } else {
                        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__result_value_latched = 0U;
                        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__result_error_latched = 6U;
                        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__state = 7U;
                    }
                }
            } else if (((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__route_req_valid) 
                        & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__route_req_ready))) {
                __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__state = 3U;
            }
        } else if ((1U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__state))) {
            __Vtemp_4[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_channels_latched;
            __Vtemp_4[1U] = 0U;
            __Vtemp_4[2U] = 0U;
            VL_MUL_W(3, __Vtemp_5, __Vtemp_4, vlSelfRef.__VdfgRegularize_h6e95ff9d_0_197);
            __Vtemp_6[0U] = __Vtemp_5[0U];
            __Vtemp_6[1U] = __Vtemp_5[1U];
            __Vtemp_6[2U] = (1U & __Vtemp_5[2U]);
            VL_MUL_W(3, __Vtemp_7, vlSelfRef.__VdfgRegularize_h6e95ff9d_0_198, __Vtemp_6);
            __Vtemp_8[0U] = __Vtemp_7[0U];
            __Vtemp_8[1U] = __Vtemp_7[1U];
            __Vtemp_8[2U] = (1U & __Vtemp_7[2U]);
            __Vtemp_9[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_length_latched;
            __Vtemp_9[1U] = 0U;
            __Vtemp_9[2U] = 0U;
            if ((((((((((0U != (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__query_error_code)) 
                        | (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__query_output_channels 
                           != vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_channels_latched)) 
                       | (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__query_output_height 
                          != vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_height_latched)) 
                      | (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__query_output_width 
                         != vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_width_latched)) 
                     | (0U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_channels_latched)) 
                    | (0U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_height_latched)) 
                   | (0U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_width_latched)) 
                  | (0U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_length_latched)) 
                 | VL_GT_W(3, __Vtemp_8, __Vtemp_9))) {
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__result_error_latched 
                    = ((2U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__query_error_code))
                        ? 2U : ((1U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__query_error_code))
                                 ? 1U : 3U));
                __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__state = 7U;
            } else {
                __Vtemp_10[0U] = 0U;
                __Vtemp_10[1U] = 1U;
                __Vtemp_10[2U] = 0U;
                __Vtemp_12[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_length_latched;
                __Vtemp_12[1U] = 0U;
                __Vtemp_12[2U] = 0U;
                __Vtemp_13[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_base_latched;
                __Vtemp_13[1U] = 0U;
                __Vtemp_13[2U] = 0U;
                VL_ADD_W(3, __Vtemp_14, __Vtemp_12, __Vtemp_13);
                __Vtemp_15[0U] = __Vtemp_14[0U];
                __Vtemp_15[1U] = __Vtemp_14[1U];
                __Vtemp_15[2U] = (1U & __Vtemp_14[2U]);
                if (VL_LT_W(3, __Vtemp_10, __Vtemp_15)) {
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__result_error_latched = 2U;
                    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__state = 7U;
                } else {
                    __Vtemp_16[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_length_latched;
                    __Vtemp_16[1U] = 0U;
                    __Vtemp_16[2U] = 0U;
                    if ((VL_GTE_W(3, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_offset_work, __Vtemp_16) 
                         | ((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_base_latched 
                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_offset_work[0U]) 
                            < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_base_latched))) {
                        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__result_error_latched = 2U;
                        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__state = 7U;
                    } else {
                        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source_index_latched 
                            = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__query_source_index;
                        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source_address_latched 
                            = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__query_source_address;
                        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_address_latched 
                            = (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_base_latched 
                               + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_offset_work[0U]);
                        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__state = 2U;
                    }
                }
            }
        } else if (((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__route_start_valid) 
                    & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__route_start_ready))) {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source_count_latched 
                = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__current_input_count;
            if ((0x25U >= (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor))) {
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__groups_latched 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_GROUP_COUNT
                    [vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor];
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__group_id_latched 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_ROUTE_GROUP_ID
                    [vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor];
            } else {
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__groups_latched = 0U;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__group_id_latched = 0U;
            }
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_channel_latched 
                = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_channel;
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_y_latched 
                = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_y;
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_x_latched 
                = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_x;
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_base_latched 
                = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_base[0U];
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_length_latched 
                = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_length[0U];
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_channels_latched 
                = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_c[0U];
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_height_latched 
                = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_h[0U];
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_width_latched 
                = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_w[0U];
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_start_latched 
                = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_route_start[0U];
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_end_latched 
                = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_route_end[0U];
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_multiplier_latched 
                = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_ROUTE_SOURCE_MULTIPLIER_Q31
                [((0x25U >= (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor))
                   ? (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor)
                   : 0U)][0U];
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_value_latched = 0U;
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source1_base_latched 
                = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_base[1U];
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source1_length_latched 
                = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_length[1U];
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source1_channels_latched 
                = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_c[1U];
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source1_height_latched 
                = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_h[1U];
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source1_width_latched 
                = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_w[1U];
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source1_start_latched 
                = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_route_start[1U];
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source1_end_latched 
                = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_route_end[1U];
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source1_multiplier_latched 
                = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_ROUTE_SOURCE_MULTIPLIER_Q31
                [((0x25U >= (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor))
                   ? (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor)
                   : 0U)][1U];
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source1_value_latched = 0U;
            __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_base_latched 
                = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_base;
            __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_length_latched 
                = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_length;
            __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_channels_latched 
                = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_c;
            __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_height_latched 
                = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_h;
            __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_width_latched 
                = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_w;
            __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source_index_latched = 0U;
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source_address_latched = 0U;
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_address_latched = 0U;
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__result_value_latched = 0U;
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__result_error_latched = 0U;
            __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__state = 1U;
        }
        if ((4U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__state))) {
            if ((2U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__state))) {
                __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__state = 0U;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__copied_value_latched = 0U;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__result_error_latched = 6U;
            } else if ((1U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__state))) {
                if (((5U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__state)) 
                     & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__upsample_result_ready))) {
                    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__state = 0U;
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__result_error_latched = 0U;
                }
            } else if (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__upsample_rsp_valid) {
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__result_error_latched 
                    = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__mapped_response_error;
                if ((0U != (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__mapped_response_error))) {
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__copied_value_latched = 0U;
                }
                __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__state = 5U;
            }
        } else if ((2U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__state))) {
            if ((1U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__state))) {
                if (((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__upsample_req_valid) 
                     & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__upsample_req_ready))) {
                    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__state = 4U;
                }
            } else if (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__upsample_rsp_valid) {
                if ((0U != (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__mapped_response_error))) {
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__copied_value_latched = 0U;
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__result_error_latched 
                        = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__mapped_response_error;
                    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__state = 5U;
                } else {
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__copied_value_latched 
                        = (0x000000ffU & VL_SHIFTR_III(8,32,32, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__response_data_latched, 
                                                       (0x00000018U 
                                                        & (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__source_address_latched 
                                                           << 3U))));
                    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__state = 3U;
                }
            }
        } else if ((1U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__state))) {
            if (((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__upsample_req_valid) 
                 & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__upsample_req_ready))) {
                __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__state = 2U;
            }
        } else if (((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__upsample_start_valid) 
                    & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__upsample_start_ready))) {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__copied_value_latched = 0U;
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__result_error_latched = 0U;
            __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__source_address_latched = 0U;
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__output_address_latched = 0U;
            if ((((((((0x0080U != vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_c[0U]) 
                      | (0x000dU != vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_h[0U])) 
                     | (0x000dU != vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_w[0U])) 
                    | (2U != vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_upsample_engine__stride)) 
                   | (0x00000080U <= vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_channel)) 
                  | (0x0000001aU <= vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_y)) 
                 | (0x0000001aU <= vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_x))) {
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__result_error_latched = 1U;
                __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__state = 5U;
            } else if (((0x00005480U != vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_length[0U]) 
                        | (0x00015200U != vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_length))) {
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__result_error_latched = 3U;
                __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__state = 5U;
            } else if (((0x01a51e00U != vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_base[0U]) 
                        | (0x01a57280U != vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_base))) {
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__result_error_latched = 2U;
                __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__state = 5U;
            } else if (((((((0U != (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__query_error_code)) 
                            | (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_channel 
                               != vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_channel)) 
                           | (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_address 
                              < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_base[0U])) 
                          | ((0x00000001ffffffffULL 
                              & ((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_address)) 
                                 - (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_base[0U])))) 
                             >= (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_length[0U])))) 
                         | (0ULL != (0x00000001ffffffffULL 
                                     & (((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__output_address_work[2U])) 
                                         << 0x00000020U) 
                                        | (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__output_address_work[1U])))))) 
                        | (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__output_offset_work 
                           >= (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_length))))) {
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__result_error_latched 
                    = ((2U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__query_error_code))
                        ? 2U : 1U);
                __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__state = 5U;
            } else {
                __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__source_address_latched 
                    = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_address;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__output_address_latched 
                    = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__output_address_work[0U];
                __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__state = 1U;
            }
        }
        if ((8U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__state))) {
            __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__state = 6U;
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__result_value_latched = 0U;
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__result_error_latched = 6U;
        } else if ((4U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__state))) {
            if ((2U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__state))) {
                if ((1U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__state))) {
                    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__state = 6U;
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__result_value_latched = 0U;
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__result_error_latched = 6U;
                } else if (((6U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__state)) 
                            & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__maxpool_result_ready))) {
                    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__state = 0U;
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__result_error_latched = 0U;
                }
            } else if ((1U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__state))) {
                if (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__maxpool_rsp_valid) {
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__result_error_latched 
                        = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__mapped_response_error;
                    if ((0U != (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__mapped_response_error))) {
                        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__result_value_latched = 0U;
                    }
                    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__state = 6U;
                }
            } else if (((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__maxpool_req_valid) 
                        & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__maxpool_req_ready))) {
                __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__state = 5U;
            }
        } else if ((2U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__state))) {
            if ((1U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__state))) {
                if ((0U != (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__window_error_code))) {
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__result_value_latched = 0U;
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__result_error_latched 
                        = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__window_error_code;
                    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__state = 6U;
                } else {
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__result_value_latched 
                        = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__window_max_value;
                    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__state = 4U;
                }
            } else if (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__maxpool_rsp_valid) {
                if ((0U != (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__mapped_response_error))) {
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__candidate_values_latched[0U] = 0U;
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__candidate_values_latched[1U] = 0U;
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__candidate_values_latched[2U] = 0U;
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__result_value_latched = 0U;
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__result_error_latched 
                        = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__mapped_response_error;
                    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__state = 6U;
                } else {
                    if ((0x47U >= (0x0000007fU & ((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__read_tap_index) 
                                                  << 3U)))) {
                        VL_ASSIGNSEL_WI(72, 8, (0x0000007fU 
                                                & ((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__read_tap_index) 
                                                   << 3U)), vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__candidate_values_latched, 
                                        (0x000000ffU 
                                         & VL_SHIFTR_III(8,32,32, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__response_data_latched, 
                                                         (0x00000018U 
                                                          & ((- (IData)(
                                                                        (4U 
                                                                         > (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__read_tap_index)))) 
                                                             & (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched
                                                                [
                                                                (3U 
                                                                 & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__read_tap_index))] 
                                                                << 3U))))));
                    }
                    if ((3U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__read_tap_index))) {
                        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__state = 3U;
                    } else {
                        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__read_tap_index 
                            = (7U & ((IData)(1U) + (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__read_tap_index)));
                        __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__state = 1U;
                    }
                }
            }
        } else if ((1U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__state))) {
            if (((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__maxpool_req_valid) 
                 & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__maxpool_req_ready))) {
                __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__state = 2U;
            }
        } else if (((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__maxpool_start_valid) 
                    & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__maxpool_start_ready))) {
            __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched__v4 = 1U;
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__candidate_values_latched[0U] = 0U;
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__candidate_values_latched[1U] = 0U;
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__candidate_values_latched[2U] = 0U;
            __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__read_tap_index = 0U;
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__result_value_latched = 0U;
            __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched__v5 = 1U;
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_address_latched = 0U;
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__result_error_latched = 0U;
            if (((9U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__layer_index)
                  ? ((2U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_height) 
                     & ((2U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width) 
                        & ((2U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_y) 
                           & ((2U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_x) 
                              & ((1U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__darknet_padding_parameter) 
                                 & ((0x0080U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_c[0U]) 
                                    & ((0x0068U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_h[0U]) 
                                       & ((0x0068U 
                                           == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_w[0U]) 
                                          & ((0x0080U 
                                              == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_c)) 
                                             & ((0x0034U 
                                                 == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_h)) 
                                                & (0x0034U 
                                                   == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_w))))))))))))
                  : ((0x00000011U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__layer_index)
                      ? ((2U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_height) 
                         & ((2U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width) 
                            & ((2U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_y) 
                               & ((2U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_x) 
                                  & ((1U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__darknet_padding_parameter) 
                                     & ((0x0100U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_c[0U]) 
                                        & ((0x0034U 
                                            == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_h[0U]) 
                                           & ((0x0034U 
                                               == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_w[0U]) 
                                              & ((0x0100U 
                                                  == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_c)) 
                                                 & ((0x001aU 
                                                     == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_h)) 
                                                    & (0x001aU 
                                                       == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_w))))))))))))
                      : ((2U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_height) 
                         & ((2U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width) 
                            & ((2U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_y) 
                               & ((2U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_x) 
                                  & ((1U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__darknet_padding_parameter) 
                                     & ((0x00000019U 
                                         == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__layer_index) 
                                        & ((0x0200U 
                                            == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_c[0U]) 
                                           & ((0x001aU 
                                               == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_h[0U]) 
                                              & ((0x001aU 
                                                  == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_w[0U]) 
                                                 & ((0x0200U 
                                                     == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_c)) 
                                                    & ((0x000dU 
                                                        == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_h)) 
                                                       & (0x000dU 
                                                          == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_w)))))))))))))))) {
                if (((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_length[0U] 
                      != ((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_c[0U] 
                           * vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_h[0U]) 
                          * vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_w[0U])) 
                     | (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_length 
                        != (((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_c) 
                             * (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_h)) 
                            * (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_w))))) {
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__result_error_latched = 3U;
                    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__state = 6U;
                } else if (((((9U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__layer_index) 
                              & ((((0x014f3800U != vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_base[0U]) 
                                   | (0x01645800U != vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_base)) 
                                  | (0x00152000U != vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_length[0U])) 
                                 | (0x00054800U != vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_length))) 
                             | ((0x00000011U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__layer_index) 
                                & ((((0x01816400U != vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_base[0U]) 
                                     | (0x018bf400U 
                                        != vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_base)) 
                                    | (0x000a9000U 
                                       != vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_length[0U])) 
                                   | (0x0002a400U != vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_length)))) 
                            | ((0x00000019U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__layer_index) 
                               & ((((0x019a7a00U != vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_base[0U]) 
                                    | (0x019fc200U 
                                       != vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_base)) 
                                   | (0x00054800U != vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_length[0U])) 
                                  | (0x00015200U != vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_length))))) {
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__result_error_latched 
                        = (((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_length[0U] 
                             != ((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_c[0U] 
                                  * vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_h[0U]) 
                                 * vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_w[0U])) 
                            | (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_length 
                               != (((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_c) 
                                    * (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_h)) 
                                   * (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_w))))
                            ? 3U : 2U);
                    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__state = 6U;
                } else if ((1U & (((((((0U != (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_error_code)) 
                                       | (~ ((0U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_error_code)) 
                                             & ((4U 
                                                 == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_count)) 
                                                & ((0x0fU 
                                                    == 
                                                    (0x0000000fU 
                                                     & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask))) 
                                                   & ((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_output_height 
                                                       == (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_h))) 
                                                      & (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_output_width 
                                                         == (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_w))))))))) 
                                      | (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_channel 
                                         >= (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_c))) 
                                     | (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_y 
                                        >= (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_h))) 
                                    | (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_x 
                                       >= (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_w))) 
                                   | (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_offset_work 
                                      >= (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_length)))) 
                                  | (0ULL != (0x00000001ffffffffULL 
                                              & (((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_address_work[2U])) 
                                                  << 0x00000020U) 
                                                 | (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_address_work[1U])))))))) {
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__result_error_latched 
                        = (((2U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_error_code)) 
                            | (0ULL != (0x00000001ffffffffULL 
                                        & (((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_address_work[2U])) 
                                            << 0x00000020U) 
                                           | (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_address_work[1U]))))))
                            ? 2U : 1U);
                    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__state = 6U;
                } else {
                    __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched__v8 
                        = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[0U];
                    __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched__v8 = 1U;
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_address_latched 
                        = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_address_work[0U];
                    __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__state = 1U;
                    __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched__v9 
                        = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[1U];
                    __VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched__v9 = 1U;
                    __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched__v10 
                        = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[2U];
                    __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched__v11 
                        = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[3U];
                }
            } else {
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__result_error_latched = 1U;
                __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__state = 6U;
            }
        }
        if (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__memory_handshake) {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__response_error_latched 
                = vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_error_code;
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__response_target_latched 
                = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__current_op;
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__response_data_latched 
                = ((- (IData)(((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_valid) 
                               & ((0U == (3U & vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr)) 
                                  & ((~ (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_write)) 
                                     & ((0U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_wstrb)) 
                                        & (0U == (IData)(vlSelfRef.__VdfgRegularize_h6e95ff9d_0_6)))))))) 
                   & ((((0x0000ff00U & (((8U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_rstrb))
                                          ? ((0U == vlSelfRef.__VdfgRegularize_h6e95ff9d_0_17)
                                              ? (vlSelfRef.tb_s2a_network_backend_golden__DOT__input_bytes
                                                 [(0x0007ffffU 
                                                   & ((IData)(3U) 
                                                      + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr))] 
                                                 & (- (IData)(
                                                              (0x0007ebffU 
                                                               >= 
                                                               (0x0007ffffU 
                                                                & ((IData)(3U) 
                                                                   + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr))))))
                                              : ((1U 
                                                  == vlSelfRef.__VdfgRegularize_h6e95ff9d_0_17)
                                                  ? 
                                                 (vlSelfRef.tb_s2a_network_backend_golden__DOT__weight_bytes
                                                  [
                                                  (0x007fffffU 
                                                   & ((IData)(0x00700003U) 
                                                      + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr))] 
                                                  & (- (IData)(
                                                               (0x005a12fbU 
                                                                >= 
                                                                (0x007fffffU 
                                                                 & ((IData)(0x00700003U) 
                                                                    + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr))))))
                                                  : 
                                                 ((IData)(vlSelfRef.__VdfgRegularize_h6e95ff9d_0_187)
                                                   ? 
                                                  (vlSelfRef.tb_s2a_network_backend_golden__DOT__feature_bytes
                                                   [
                                                   (0x00ffffffU 
                                                    & ((IData)(3U) 
                                                       + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr))] 
                                                   & (- (IData)(
                                                                (0x00adadb7U 
                                                                 >= 
                                                                 (0x00ffffffU 
                                                                  & ((IData)(3U) 
                                                                     + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr))))))
                                                   : 
                                                  (vlSelfRef.__VdfgRegularize_h6e95ff9d_0_16 
                                                   >> 0x00000018U))))
                                          : (vlSelfRef.__VdfgRegularize_h6e95ff9d_0_16 
                                             >> 0x00000018U)) 
                                        << 8U)) | (0x000000ffU 
                                                   & ((4U 
                                                       & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_rstrb))
                                                       ? 
                                                      ((0U 
                                                        == vlSelfRef.__VdfgRegularize_h6e95ff9d_0_10)
                                                        ? 
                                                       (vlSelfRef.tb_s2a_network_backend_golden__DOT__input_bytes
                                                        [
                                                        (0x0007ffffU 
                                                         & ((IData)(2U) 
                                                            + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr))] 
                                                        & (- (IData)(
                                                                     (0x0007ebffU 
                                                                      >= 
                                                                      (0x0007ffffU 
                                                                       & ((IData)(2U) 
                                                                          + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr))))))
                                                        : 
                                                       ((1U 
                                                         == vlSelfRef.__VdfgRegularize_h6e95ff9d_0_10)
                                                         ? 
                                                        (vlSelfRef.tb_s2a_network_backend_golden__DOT__weight_bytes
                                                         [
                                                         (0x007fffffU 
                                                          & ((IData)(0x00700002U) 
                                                             + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr))] 
                                                         & (- (IData)(
                                                                      (0x005a12fbU 
                                                                       >= 
                                                                       (0x007fffffU 
                                                                        & ((IData)(0x00700002U) 
                                                                           + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr))))))
                                                         : 
                                                        ((IData)(vlSelfRef.__VdfgRegularize_h6e95ff9d_0_188)
                                                          ? 
                                                         (vlSelfRef.tb_s2a_network_backend_golden__DOT__feature_bytes
                                                          [
                                                          (0x00ffffffU 
                                                           & ((IData)(2U) 
                                                              + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr))] 
                                                          & (- (IData)(
                                                                       (0x00adadb7U 
                                                                        >= 
                                                                        (0x00ffffffU 
                                                                         & ((IData)(2U) 
                                                                            + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr))))))
                                                          : 
                                                         (vlSelfRef.__VdfgRegularize_h6e95ff9d_0_16 
                                                          >> 0x00000010U))))
                                                       : 
                                                      (vlSelfRef.__VdfgRegularize_h6e95ff9d_0_16 
                                                       >> 0x00000010U)))) 
                       << 0x00000010U) | ((0x0000ff00U 
                                           & (((2U 
                                                & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_rstrb))
                                                ? (
                                                   (0U 
                                                    == vlSelfRef.__VdfgRegularize_h6e95ff9d_0_11)
                                                    ? 
                                                   (vlSelfRef.tb_s2a_network_backend_golden__DOT__input_bytes
                                                    [
                                                    (0x0007ffffU 
                                                     & ((IData)(1U) 
                                                        + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr))] 
                                                    & (- (IData)(
                                                                 (0x0007ebffU 
                                                                  >= 
                                                                  (0x0007ffffU 
                                                                   & ((IData)(1U) 
                                                                      + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr))))))
                                                    : 
                                                   ((1U 
                                                     == vlSelfRef.__VdfgRegularize_h6e95ff9d_0_11)
                                                     ? 
                                                    (vlSelfRef.tb_s2a_network_backend_golden__DOT__weight_bytes
                                                     [
                                                     (0x007fffffU 
                                                      & ((IData)(0x00700001U) 
                                                         + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr))] 
                                                     & (- (IData)(
                                                                  (0x005a12fbU 
                                                                   >= 
                                                                   (0x007fffffU 
                                                                    & ((IData)(0x00700001U) 
                                                                       + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr))))))
                                                     : 
                                                    ((IData)(vlSelfRef.__VdfgRegularize_h6e95ff9d_0_189)
                                                      ? 
                                                     (vlSelfRef.tb_s2a_network_backend_golden__DOT__feature_bytes
                                                      [
                                                      (0x00ffffffU 
                                                       & ((IData)(1U) 
                                                          + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr))] 
                                                      & (- (IData)(
                                                                   (0x00adadb7U 
                                                                    >= 
                                                                    (0x00ffffffU 
                                                                     & ((IData)(1U) 
                                                                        + vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_addr))))))
                                                      : 
                                                     (vlSelfRef.__VdfgRegularize_h6e95ff9d_0_16 
                                                      >> 8U))))
                                                : (vlSelfRef.__VdfgRegularize_h6e95ff9d_0_16 
                                                   >> 8U)) 
                                              << 8U)) 
                                          | (0x000000ffU 
                                             & vlSelfRef.__VdfgRegularize_h6e95ff9d_0_16))));
        }
    }
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__response_pending 
        = __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__response_pending;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__cycle_count 
        = __Vdly__tb_s2a_network_backend_golden__DOT__cycle_count;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__next_progress_cycle 
        = __Vdly__tb_s2a_network_backend_golden__DOT__next_progress_cycle;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__stalled_previous 
        = __Vdly__tb_s2a_network_backend_golden__DOT__stalled_previous;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__stalled_address 
        = __Vdly__tb_s2a_network_backend_golden__DOT__stalled_address;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__stalled_data 
        = __Vdly__tb_s2a_network_backend_golden__DOT__stalled_data;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__stalled_write 
        = __Vdly__tb_s2a_network_backend_golden__DOT__stalled_write;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__stalled_rstrb 
        = __Vdly__tb_s2a_network_backend_golden__DOT__stalled_rstrb;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__stalled_wstrb 
        = __Vdly__tb_s2a_network_backend_golden__DOT__stalled_wstrb;
    if (__VdlySet__tb_s2a_network_backend_golden__DOT__layer_write_count__v0) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__layer_write_count[__VdlyDim0__tb_s2a_network_backend_golden__DOT__layer_write_count__v0] 
            = __VdlyVal__tb_s2a_network_backend_golden__DOT__layer_write_count__v0;
    }
    if (__VdlySet__tb_s2a_network_backend_golden__DOT__class_selected_byte_count__v0) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__class_selected_byte_count[__VdlyDim0__tb_s2a_network_backend_golden__DOT__class_selected_byte_count__v0] 
            = __VdlyVal__tb_s2a_network_backend_golden__DOT__class_selected_byte_count__v0;
    }
    if (__VdlySet__tb_s2a_network_backend_golden__DOT__golden_byte_seen__v0) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__golden_byte_seen[__VdlyDim0__tb_s2a_network_backend_golden__DOT__golden_byte_seen__v0] = 1U;
    }
    if (__VdlySet__tb_s2a_network_backend_golden__DOT__golden_byte_seen__v1) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__golden_byte_seen[__VdlyDim0__tb_s2a_network_backend_golden__DOT__golden_byte_seen__v1] = 1U;
    }
    if (__VdlySet__tb_s2a_network_backend_golden__DOT__golden_byte_seen__v2) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__golden_byte_seen[__VdlyDim0__tb_s2a_network_backend_golden__DOT__golden_byte_seen__v2] = 1U;
    }
    if (__VdlySet__tb_s2a_network_backend_golden__DOT__golden_byte_seen__v3) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__golden_byte_seen[__VdlyDim0__tb_s2a_network_backend_golden__DOT__golden_byte_seen__v3] = 1U;
    }
    vlSelfRef.tb_s2a_network_backend_golden__DOT__class_wait_count 
        = __Vdly__tb_s2a_network_backend_golden__DOT__class_wait_count;
    if (__VdlySet__tb_s2a_network_backend_golden__DOT__class_transfer_index__v0) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__class_accepted_count[__VdlyDim0__tb_s2a_network_backend_golden__DOT__class_accepted_count__v0] 
            = __VdlyVal__tb_s2a_network_backend_golden__DOT__class_accepted_count__v0;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__class_transfer_index[__VdlyDim0__tb_s2a_network_backend_golden__DOT__class_transfer_index__v0] 
            = __VdlyVal__tb_s2a_network_backend_golden__DOT__class_transfer_index__v0;
    }
    if (__VdlySet__tb_s2a_network_backend_golden__DOT__feature_byte_valid__v0) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__feature_byte_valid[__VdlyDim0__tb_s2a_network_backend_golden__DOT__feature_byte_valid__v0] = 1U;
    }
    if (__VdlySet__tb_s2a_network_backend_golden__DOT__feature_byte_valid__v1) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__feature_byte_valid[__VdlyDim0__tb_s2a_network_backend_golden__DOT__feature_byte_valid__v1] = 1U;
    }
    if (__VdlySet__tb_s2a_network_backend_golden__DOT__feature_byte_valid__v2) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__feature_byte_valid[__VdlyDim0__tb_s2a_network_backend_golden__DOT__feature_byte_valid__v2] = 1U;
    }
    if (__VdlySet__tb_s2a_network_backend_golden__DOT__feature_byte_valid__v3) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__feature_byte_valid[__VdlyDim0__tb_s2a_network_backend_golden__DOT__feature_byte_valid__v3] = 1U;
    }
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_element_index 
        = __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_element_index;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__state 
        = __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__state;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_height 
        = __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_height;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__patch_byte_count 
        = __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__patch_byte_count;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_point_count 
        = __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_point_count;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_lane_index 
        = __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_lane_index;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_reduction_index 
        = __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_reduction_index;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_point_index 
        = __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_point_index;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_lane_index 
        = __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_lane_index;
    if (__VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v0) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block[__VdlyDim0__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v0] 
            = __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v0;
    }
    if (__VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v1) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block[__VdlyDim0__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v1] 
            = __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v1;
    }
    if (__VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v2) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block[__VdlyDim0__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v2] 
            = __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v2;
    }
    if (__VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v3) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block[__VdlyDim0__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v3] 
            = __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v3;
    }
    if (__VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v4) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block[__VdlyDim0__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v4] 
            = __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v4;
    }
    if (__VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v5) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block[__VdlyDim0__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v5] 
            = __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v5;
    }
    if (__VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v6) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block[__VdlyDim0__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v6] 
            = __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v6;
    }
    if (__VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v7) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block[__VdlyDim0__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v7] 
            = __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block__v7;
    }
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base 
        = __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_channels_latched 
        = __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_channels_latched;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_channels_latched 
        = __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_channels_latched;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_index 
        = __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_index;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_reduction_index 
        = __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_reduction_index;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_index 
        = __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_index;
    if (__VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_group__v0) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_group[__VdlyDim0__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_group__v0] 
            = __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_group__v0;
    }
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_latched 
        = __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_latched;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_latched 
        = __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_latched;
    if (__VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_patch__v0) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_patch[__VdlyDim0__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_patch__v0] 
            = __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_patch__v0;
    }
    if (__VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_patch__v1) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_patch[__VdlyDim0__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_patch__v1] = 0U;
    }
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_latched 
        = __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_latched;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_width 
        = __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_width;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_x 
        = __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_x;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_y 
        = __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_y;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched 
        = __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count 
        = __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count;
    if (__VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v0) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[0U] 
            = __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v0;
    }
    if (__VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v1) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[1U] 
            = __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v1;
    }
    if (__VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v2) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[2U] 
            = __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v2;
    }
    if (__VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v3) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[3U] 
            = __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v3;
    }
    if (__VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v4) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[4U] 
            = __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v4;
    }
    if (__VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v5) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[5U] 
            = __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v5;
    }
    if (__VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v6) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[6U] 
            = __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v6;
    }
    if (__VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v7) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[7U] 
            = __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v7;
    }
    if (__VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v8) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[0U] 
            = __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v8;
    }
    if (__VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v9) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[1U] 
            = __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v9;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[2U] 
            = __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v10;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[3U] 
            = __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v11;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[4U] 
            = __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v12;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[5U] 
            = __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v13;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[6U] 
            = __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v14;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[7U] 
            = __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v15;
    }
    if (__VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v16) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[0U] 
            = __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v16;
    }
    if (__VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v17) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[1U] 
            = __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v17;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[2U] 
            = __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v18;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[3U] 
            = __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v19;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[4U] 
            = __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v20;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[5U] 
            = __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v21;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[6U] 
            = __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v22;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[7U] 
            = __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator__v23;
    }
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_height_latched 
        = __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_height_latched;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_width_latched 
        = __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_width_latched;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__stride_y_latched 
        = __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__stride_y_latched;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__stride_x_latched 
        = __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__stride_x_latched;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state 
        = __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_base_latched 
        = __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_base_latched;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_length_latched 
        = __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_length_latched;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_channels_latched 
        = __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_channels_latched;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source_index_latched 
        = __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source_index_latched;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_height_latched 
        = __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_height_latched;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_width_latched 
        = __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_width_latched;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor 
        = __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__state 
        = __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__state;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__source_address_latched 
        = __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__source_address_latched;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__state 
        = __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__state;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__read_tap_index 
        = __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__read_tap_index;
    if (__VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched__v0) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched[0U] = 0U;
    }
    if (__VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched__v1) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched[1U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched[2U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched[3U] = 0U;
    }
    if (__VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched__v4) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched[0U] = 0U;
    }
    if (__VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched__v5) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched[1U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched[2U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched[3U] = 0U;
    }
    if (__VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched__v8) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched[0U] 
            = __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched__v8;
    }
    if (__VdlySet__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched__v9) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched[1U] 
            = __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched__v9;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched[2U] 
            = __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched__v10;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched[3U] 
            = __VdlyVal__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched__v11;
    }
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__state 
        = __Vdly__tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__state;
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
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mapped_response_error = 6U;
    if ((0U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__response_error_latched))) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mapped_response_error = 0U;
    } else if ((((1U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__response_error_latched)) 
                 | (2U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__response_error_latched))) 
                | (6U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__response_error_latched)))) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mapped_response_error 
            = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__response_error_latched;
    }
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_source_address_wide 
        = ((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_package_base_latched)) 
           + ((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__quantized_weight_offset_latched)) 
              + ((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_reduction_index)) 
                 + ((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_latched)) 
                    * (QData)((IData)((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base 
                                       + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_lane_index)))))));
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_byte_offset_wide 
        = ((QData)((IData)((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_x 
                            + (VL_MODDIV_III(32, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_point_index, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_width) 
                               & (- (IData)((0U != vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_width))))))) 
           + ((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_latched)) 
              * ((QData)((IData)((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_y 
                                  + (VL_DIV_III(32, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_point_index, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_width) 
                                     & (- (IData)((0U 
                                                   != vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_width))))))) 
                 + ((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_latched)) 
                    * (QData)((IData)((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base 
                                       + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_lane_index)))))));
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_group_invalid = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[0U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[0U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[0U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product[0U] = 0ULL;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add[0U] = 0ULL;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[0U] = 0ULL;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[0U] = 0ULL;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requantized_value[0U] = 0U;
    if ((0x00000026U > vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U] 
            = (((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                 ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                [(0x0000003fU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                 : 0U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base);
        if ((0x00000c5cU > vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])) {
            if ((0U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U]))) {
                    __Vtemp_17[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_17[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_17[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][2U];
                    __Vtemp_18[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_18[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_18[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][2U];
                    __Vtemp_19[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_19[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_19[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][2U];
                    __Vtemp_20[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_20[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_20[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][2U];
                    __Vtemp_21[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_21[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_21[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][2U];
                    __Vtemp_22[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_22[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_22[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][2U];
                    __Vtemp_23[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_23[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_23[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][2U];
                    __Vtemp_24[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_24[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_24[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][2U];
                    __Vtemp_25[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_25[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_25[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][2U];
                    __Vtemp_26[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_26[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_26[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][2U];
                } else {
                    __Vtemp_17[1U] = 0U;
                    __Vtemp_17[2U] = 0U;
                    __Vtemp_18[0U] = 0U;
                    __Vtemp_18[1U] = 0U;
                    __Vtemp_19[1U] = 0U;
                    __Vtemp_19[2U] = 0U;
                    __Vtemp_20[0U] = 0U;
                    __Vtemp_20[1U] = 0U;
                    __Vtemp_21[1U] = 0U;
                    __Vtemp_22[0U] = 0U;
                    __Vtemp_23[1U] = 0U;
                    __Vtemp_23[2U] = 0U;
                    __Vtemp_24[0U] = 0U;
                    __Vtemp_24[1U] = 0U;
                    __Vtemp_25[1U] = 0U;
                    __Vtemp_26[0U] = 0U;
                }
                if (((((((((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U] 
                            >= (((0x25U >= (0x0000003fU 
                                            & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                 [(0x0000003fU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                  : 0U) + ((0x25U >= 
                                            (0x0000003fU 
                                             & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                            ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                                           [(0x0000003fU 
                                             & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                            : 0U))) 
                           | (0U == ((__Vtemp_17[2U] 
                                      << 0x00000010U) 
                                     | (__Vtemp_17[1U] 
                                        >> 0x00000010U)))) 
                          | (0U == ((__Vtemp_18[1U] 
                                     << 0x00000018U) 
                                    | (__Vtemp_18[0U] 
                                       >> 8U)))) | 
                         (0x3fffffffU < ((__Vtemp_19[2U] 
                                          << 0x00000010U) 
                                         | (__Vtemp_19[1U] 
                                            >> 0x00000010U)))) 
                        | (0x3fffffffU < ((__Vtemp_20[1U] 
                                           << 0x00000018U) 
                                          | (__Vtemp_20[0U] 
                                             >> 8U)))) 
                       | (0x2fU < (0x000000ffU & (__Vtemp_21[1U] 
                                                  >> 8U)))) 
                      | (0x2fU < (0x000000ffU & __Vtemp_22[0U]))) 
                     | ((0U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__activation_mode_latched)) 
                        & ((((__Vtemp_23[2U] << 0x00000010U) 
                             | (__Vtemp_23[1U] >> 0x00000010U)) 
                            != ((__Vtemp_24[1U] << 0x00000018U) 
                                | (__Vtemp_24[0U] >> 8U))) 
                           | ((0x000000ffU & (__Vtemp_25[1U] 
                                              >> 8U)) 
                              != (0x000000ffU & __Vtemp_26[0U])))))) {
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_group_invalid = 1U;
                }
            }
            if ((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[0U] 
                 >> 0x1fU)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U]))) {
                    __Vtemp_27[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_27[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_27[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][2U];
                    __Vtemp_28[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_28[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_28[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][2U];
                } else {
                    __Vtemp_27[0U] = 0U;
                    __Vtemp_27[1U] = 0U;
                    __Vtemp_28[0U] = 0U;
                }
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[0U] 
                    = ((__Vtemp_27[1U] << 0x00000018U) 
                       | (__Vtemp_27[0U] >> 8U));
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[0U] 
                    = ((IData)(1U) + (~ vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[0U]));
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[0U] 
                    = (0x000000ffU & __Vtemp_28[0U]);
            } else {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U]))) {
                    __Vtemp_29[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_29[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_29[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][2U];
                    __Vtemp_30[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_30[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_30[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[0U])][2U];
                } else {
                    __Vtemp_29[1U] = 0U;
                    __Vtemp_29[2U] = 0U;
                    __Vtemp_30[1U] = 0U;
                }
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[0U] 
                    = ((__Vtemp_29[2U] << 0x00000010U) 
                       | (__Vtemp_29[1U] >> 0x00000010U));
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[0U] 
                    = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[0U];
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[0U] 
                    = (0x000000ffU & (__Vtemp_30[1U] 
                                      >> 8U));
            }
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product[0U] 
                = ((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[0U])) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[0U])));
            if ((0U != vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[0U])) {
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add[0U] 
                    = VL_SHIFTL_QQI(64,64,32, 1ULL, 
                                    (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[0U] 
                                     - (IData)(1U)));
            }
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[0U] 
                = VL_SHIFTR_QQI(64,64,32, (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product[0U] 
                                           + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add[0U]), vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[0U]);
            __Vtemp_32[0U] = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[0U]);
            __Vtemp_32[1U] = (IData)((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[0U] 
                                      >> 0x00000020U));
            __Vtemp_32[2U] = 0U;
            VL_NEGATE_W(3, __Vtemp_33, __Vtemp_32);
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[0U] 
                = ((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[0U] 
                    >> 0x1fU) ? (((QData)((IData)(__Vtemp_33[1U])) 
                                  << 0x00000020U) | (QData)((IData)(__Vtemp_33[0U])))
                    : vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[0U]);
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requantized_value[0U] 
                = (VL_LTS_IQQ(64, 0x000000000000007fULL, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[0U])
                    ? 0x0000007fU : (VL_GTS_IQQ(64, 0xffffffffffffff81ULL, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[0U])
                                      ? 0x00000081U
                                      : (0x000000ffU 
                                         & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[0U]))));
        } else if ((0U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[1U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[1U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[1U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product[1U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add[1U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[1U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[1U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requantized_value[1U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U] 
            = ((IData)(1U) + (((0x25U >= (0x0000003fU 
                                          & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                               [(0x0000003fU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                : 0U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base));
        if ((0x00000c5cU > vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])) {
            if ((1U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U]))) {
                    __Vtemp_35[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_35[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_35[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][2U];
                    __Vtemp_36[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_36[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_36[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][2U];
                    __Vtemp_37[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_37[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_37[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][2U];
                    __Vtemp_38[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_38[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_38[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][2U];
                    __Vtemp_39[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_39[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_39[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][2U];
                    __Vtemp_40[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_40[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_40[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][2U];
                    __Vtemp_41[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_41[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_41[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][2U];
                    __Vtemp_42[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_42[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_42[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][2U];
                    __Vtemp_43[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_43[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_43[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][2U];
                    __Vtemp_44[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_44[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_44[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][2U];
                } else {
                    __Vtemp_35[1U] = 0U;
                    __Vtemp_35[2U] = 0U;
                    __Vtemp_36[0U] = 0U;
                    __Vtemp_36[1U] = 0U;
                    __Vtemp_37[1U] = 0U;
                    __Vtemp_37[2U] = 0U;
                    __Vtemp_38[0U] = 0U;
                    __Vtemp_38[1U] = 0U;
                    __Vtemp_39[1U] = 0U;
                    __Vtemp_40[0U] = 0U;
                    __Vtemp_41[1U] = 0U;
                    __Vtemp_41[2U] = 0U;
                    __Vtemp_42[0U] = 0U;
                    __Vtemp_42[1U] = 0U;
                    __Vtemp_43[1U] = 0U;
                    __Vtemp_44[0U] = 0U;
                }
                if (((((((((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U] 
                            >= (((0x25U >= (0x0000003fU 
                                            & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                 [(0x0000003fU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                  : 0U) + ((0x25U >= 
                                            (0x0000003fU 
                                             & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                            ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                                           [(0x0000003fU 
                                             & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                            : 0U))) 
                           | (0U == ((__Vtemp_35[2U] 
                                      << 0x00000010U) 
                                     | (__Vtemp_35[1U] 
                                        >> 0x00000010U)))) 
                          | (0U == ((__Vtemp_36[1U] 
                                     << 0x00000018U) 
                                    | (__Vtemp_36[0U] 
                                       >> 8U)))) | 
                         (0x3fffffffU < ((__Vtemp_37[2U] 
                                          << 0x00000010U) 
                                         | (__Vtemp_37[1U] 
                                            >> 0x00000010U)))) 
                        | (0x3fffffffU < ((__Vtemp_38[1U] 
                                           << 0x00000018U) 
                                          | (__Vtemp_38[0U] 
                                             >> 8U)))) 
                       | (0x2fU < (0x000000ffU & (__Vtemp_39[1U] 
                                                  >> 8U)))) 
                      | (0x2fU < (0x000000ffU & __Vtemp_40[0U]))) 
                     | ((0U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__activation_mode_latched)) 
                        & ((((__Vtemp_41[2U] << 0x00000010U) 
                             | (__Vtemp_41[1U] >> 0x00000010U)) 
                            != ((__Vtemp_42[1U] << 0x00000018U) 
                                | (__Vtemp_42[0U] >> 8U))) 
                           | ((0x000000ffU & (__Vtemp_43[1U] 
                                              >> 8U)) 
                              != (0x000000ffU & __Vtemp_44[0U])))))) {
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_group_invalid = 1U;
                }
            }
            if ((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[1U] 
                 >> 0x1fU)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U]))) {
                    __Vtemp_45[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_45[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_45[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][2U];
                    __Vtemp_46[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_46[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_46[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][2U];
                } else {
                    __Vtemp_45[0U] = 0U;
                    __Vtemp_45[1U] = 0U;
                    __Vtemp_46[0U] = 0U;
                }
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[1U] 
                    = ((__Vtemp_45[1U] << 0x00000018U) 
                       | (__Vtemp_45[0U] >> 8U));
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[1U] 
                    = ((IData)(1U) + (~ vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[1U]));
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[1U] 
                    = (0x000000ffU & __Vtemp_46[0U]);
            } else {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U]))) {
                    __Vtemp_47[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_47[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_47[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][2U];
                    __Vtemp_48[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_48[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_48[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U])][2U];
                } else {
                    __Vtemp_47[1U] = 0U;
                    __Vtemp_47[2U] = 0U;
                    __Vtemp_48[1U] = 0U;
                }
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[1U] 
                    = ((__Vtemp_47[2U] << 0x00000010U) 
                       | (__Vtemp_47[1U] >> 0x00000010U));
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[1U] 
                    = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[1U];
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[1U] 
                    = (0x000000ffU & (__Vtemp_48[1U] 
                                      >> 8U));
            }
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product[1U] 
                = ((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[1U])) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[1U])));
            if ((0U != vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[1U])) {
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add[1U] 
                    = VL_SHIFTL_QQI(64,64,32, 1ULL, 
                                    (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[1U] 
                                     - (IData)(1U)));
            }
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[1U] 
                = VL_SHIFTR_QQI(64,64,32, (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product[1U] 
                                           + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add[1U]), vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[1U]);
            __Vtemp_50[0U] = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[1U]);
            __Vtemp_50[1U] = (IData)((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[1U] 
                                      >> 0x00000020U));
            __Vtemp_50[2U] = 0U;
            VL_NEGATE_W(3, __Vtemp_51, __Vtemp_50);
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[1U] 
                = ((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[1U] 
                    >> 0x1fU) ? (((QData)((IData)(__Vtemp_51[1U])) 
                                  << 0x00000020U) | (QData)((IData)(__Vtemp_51[0U])))
                    : vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[1U]);
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requantized_value[1U] 
                = (VL_LTS_IQQ(64, 0x000000000000007fULL, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[1U])
                    ? 0x0000007fU : (VL_GTS_IQQ(64, 0xffffffffffffff81ULL, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[1U])
                                      ? 0x00000081U
                                      : (0x000000ffU 
                                         & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[1U]))));
        } else if ((1U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[2U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[2U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[2U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product[2U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add[2U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[2U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[2U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requantized_value[2U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U] 
            = ((IData)(2U) + (((0x25U >= (0x0000003fU 
                                          & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                               [(0x0000003fU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                : 0U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base));
        if ((0x00000c5cU > vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])) {
            if ((2U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U]))) {
                    __Vtemp_53[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_53[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_53[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][2U];
                    __Vtemp_54[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_54[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_54[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][2U];
                    __Vtemp_55[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_55[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_55[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][2U];
                    __Vtemp_56[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_56[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_56[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][2U];
                    __Vtemp_57[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_57[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_57[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][2U];
                    __Vtemp_58[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_58[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_58[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][2U];
                    __Vtemp_59[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_59[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_59[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][2U];
                    __Vtemp_60[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_60[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_60[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][2U];
                    __Vtemp_61[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_61[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_61[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][2U];
                    __Vtemp_62[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_62[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_62[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][2U];
                } else {
                    __Vtemp_53[1U] = 0U;
                    __Vtemp_53[2U] = 0U;
                    __Vtemp_54[0U] = 0U;
                    __Vtemp_54[1U] = 0U;
                    __Vtemp_55[1U] = 0U;
                    __Vtemp_55[2U] = 0U;
                    __Vtemp_56[0U] = 0U;
                    __Vtemp_56[1U] = 0U;
                    __Vtemp_57[1U] = 0U;
                    __Vtemp_58[0U] = 0U;
                    __Vtemp_59[1U] = 0U;
                    __Vtemp_59[2U] = 0U;
                    __Vtemp_60[0U] = 0U;
                    __Vtemp_60[1U] = 0U;
                    __Vtemp_61[1U] = 0U;
                    __Vtemp_62[0U] = 0U;
                }
                if (((((((((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U] 
                            >= (((0x25U >= (0x0000003fU 
                                            & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                 [(0x0000003fU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                  : 0U) + ((0x25U >= 
                                            (0x0000003fU 
                                             & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                            ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                                           [(0x0000003fU 
                                             & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                            : 0U))) 
                           | (0U == ((__Vtemp_53[2U] 
                                      << 0x00000010U) 
                                     | (__Vtemp_53[1U] 
                                        >> 0x00000010U)))) 
                          | (0U == ((__Vtemp_54[1U] 
                                     << 0x00000018U) 
                                    | (__Vtemp_54[0U] 
                                       >> 8U)))) | 
                         (0x3fffffffU < ((__Vtemp_55[2U] 
                                          << 0x00000010U) 
                                         | (__Vtemp_55[1U] 
                                            >> 0x00000010U)))) 
                        | (0x3fffffffU < ((__Vtemp_56[1U] 
                                           << 0x00000018U) 
                                          | (__Vtemp_56[0U] 
                                             >> 8U)))) 
                       | (0x2fU < (0x000000ffU & (__Vtemp_57[1U] 
                                                  >> 8U)))) 
                      | (0x2fU < (0x000000ffU & __Vtemp_58[0U]))) 
                     | ((0U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__activation_mode_latched)) 
                        & ((((__Vtemp_59[2U] << 0x00000010U) 
                             | (__Vtemp_59[1U] >> 0x00000010U)) 
                            != ((__Vtemp_60[1U] << 0x00000018U) 
                                | (__Vtemp_60[0U] >> 8U))) 
                           | ((0x000000ffU & (__Vtemp_61[1U] 
                                              >> 8U)) 
                              != (0x000000ffU & __Vtemp_62[0U])))))) {
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_group_invalid = 1U;
                }
            }
            if ((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[2U] 
                 >> 0x1fU)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U]))) {
                    __Vtemp_63[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_63[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_63[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][2U];
                    __Vtemp_64[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_64[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_64[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][2U];
                } else {
                    __Vtemp_63[0U] = 0U;
                    __Vtemp_63[1U] = 0U;
                    __Vtemp_64[0U] = 0U;
                }
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[2U] 
                    = ((__Vtemp_63[1U] << 0x00000018U) 
                       | (__Vtemp_63[0U] >> 8U));
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[2U] 
                    = ((IData)(1U) + (~ vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[2U]));
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[2U] 
                    = (0x000000ffU & __Vtemp_64[0U]);
            } else {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U]))) {
                    __Vtemp_65[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_65[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_65[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][2U];
                    __Vtemp_66[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_66[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_66[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U])][2U];
                } else {
                    __Vtemp_65[1U] = 0U;
                    __Vtemp_65[2U] = 0U;
                    __Vtemp_66[1U] = 0U;
                }
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[2U] 
                    = ((__Vtemp_65[2U] << 0x00000010U) 
                       | (__Vtemp_65[1U] >> 0x00000010U));
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[2U] 
                    = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[2U];
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[2U] 
                    = (0x000000ffU & (__Vtemp_66[1U] 
                                      >> 8U));
            }
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product[2U] 
                = ((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[2U])) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[2U])));
            if ((0U != vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[2U])) {
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add[2U] 
                    = VL_SHIFTL_QQI(64,64,32, 1ULL, 
                                    (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[2U] 
                                     - (IData)(1U)));
            }
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[2U] 
                = VL_SHIFTR_QQI(64,64,32, (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product[2U] 
                                           + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add[2U]), vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[2U]);
            __Vtemp_68[0U] = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[2U]);
            __Vtemp_68[1U] = (IData)((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[2U] 
                                      >> 0x00000020U));
            __Vtemp_68[2U] = 0U;
            VL_NEGATE_W(3, __Vtemp_69, __Vtemp_68);
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[2U] 
                = ((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[2U] 
                    >> 0x1fU) ? (((QData)((IData)(__Vtemp_69[1U])) 
                                  << 0x00000020U) | (QData)((IData)(__Vtemp_69[0U])))
                    : vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[2U]);
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requantized_value[2U] 
                = (VL_LTS_IQQ(64, 0x000000000000007fULL, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[2U])
                    ? 0x0000007fU : (VL_GTS_IQQ(64, 0xffffffffffffff81ULL, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[2U])
                                      ? 0x00000081U
                                      : (0x000000ffU 
                                         & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[2U]))));
        } else if ((2U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[3U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[3U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[3U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product[3U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add[3U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[3U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[3U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requantized_value[3U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U] 
            = ((IData)(3U) + (((0x25U >= (0x0000003fU 
                                          & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                               [(0x0000003fU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                : 0U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base));
        if ((0x00000c5cU > vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])) {
            if ((3U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U]))) {
                    __Vtemp_71[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_71[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_71[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][2U];
                    __Vtemp_72[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_72[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_72[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][2U];
                    __Vtemp_73[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_73[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_73[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][2U];
                    __Vtemp_74[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_74[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_74[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][2U];
                    __Vtemp_75[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_75[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_75[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][2U];
                    __Vtemp_76[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_76[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_76[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][2U];
                    __Vtemp_77[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_77[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_77[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][2U];
                    __Vtemp_78[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_78[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_78[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][2U];
                    __Vtemp_79[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_79[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_79[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][2U];
                    __Vtemp_80[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_80[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_80[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][2U];
                } else {
                    __Vtemp_71[1U] = 0U;
                    __Vtemp_71[2U] = 0U;
                    __Vtemp_72[0U] = 0U;
                    __Vtemp_72[1U] = 0U;
                    __Vtemp_73[1U] = 0U;
                    __Vtemp_73[2U] = 0U;
                    __Vtemp_74[0U] = 0U;
                    __Vtemp_74[1U] = 0U;
                    __Vtemp_75[1U] = 0U;
                    __Vtemp_76[0U] = 0U;
                    __Vtemp_77[1U] = 0U;
                    __Vtemp_77[2U] = 0U;
                    __Vtemp_78[0U] = 0U;
                    __Vtemp_78[1U] = 0U;
                    __Vtemp_79[1U] = 0U;
                    __Vtemp_80[0U] = 0U;
                }
                if (((((((((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U] 
                            >= (((0x25U >= (0x0000003fU 
                                            & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                 [(0x0000003fU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                  : 0U) + ((0x25U >= 
                                            (0x0000003fU 
                                             & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                            ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                                           [(0x0000003fU 
                                             & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                            : 0U))) 
                           | (0U == ((__Vtemp_71[2U] 
                                      << 0x00000010U) 
                                     | (__Vtemp_71[1U] 
                                        >> 0x00000010U)))) 
                          | (0U == ((__Vtemp_72[1U] 
                                     << 0x00000018U) 
                                    | (__Vtemp_72[0U] 
                                       >> 8U)))) | 
                         (0x3fffffffU < ((__Vtemp_73[2U] 
                                          << 0x00000010U) 
                                         | (__Vtemp_73[1U] 
                                            >> 0x00000010U)))) 
                        | (0x3fffffffU < ((__Vtemp_74[1U] 
                                           << 0x00000018U) 
                                          | (__Vtemp_74[0U] 
                                             >> 8U)))) 
                       | (0x2fU < (0x000000ffU & (__Vtemp_75[1U] 
                                                  >> 8U)))) 
                      | (0x2fU < (0x000000ffU & __Vtemp_76[0U]))) 
                     | ((0U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__activation_mode_latched)) 
                        & ((((__Vtemp_77[2U] << 0x00000010U) 
                             | (__Vtemp_77[1U] >> 0x00000010U)) 
                            != ((__Vtemp_78[1U] << 0x00000018U) 
                                | (__Vtemp_78[0U] >> 8U))) 
                           | ((0x000000ffU & (__Vtemp_79[1U] 
                                              >> 8U)) 
                              != (0x000000ffU & __Vtemp_80[0U])))))) {
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_group_invalid = 1U;
                }
            }
            if ((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[3U] 
                 >> 0x1fU)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U]))) {
                    __Vtemp_81[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_81[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_81[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][2U];
                    __Vtemp_82[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_82[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_82[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][2U];
                } else {
                    __Vtemp_81[0U] = 0U;
                    __Vtemp_81[1U] = 0U;
                    __Vtemp_82[0U] = 0U;
                }
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[3U] 
                    = ((__Vtemp_81[1U] << 0x00000018U) 
                       | (__Vtemp_81[0U] >> 8U));
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[3U] 
                    = ((IData)(1U) + (~ vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[3U]));
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[3U] 
                    = (0x000000ffU & __Vtemp_82[0U]);
            } else {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U]))) {
                    __Vtemp_83[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_83[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_83[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][2U];
                    __Vtemp_84[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_84[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_84[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U])][2U];
                } else {
                    __Vtemp_83[1U] = 0U;
                    __Vtemp_83[2U] = 0U;
                    __Vtemp_84[1U] = 0U;
                }
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[3U] 
                    = ((__Vtemp_83[2U] << 0x00000010U) 
                       | (__Vtemp_83[1U] >> 0x00000010U));
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[3U] 
                    = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[3U];
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[3U] 
                    = (0x000000ffU & (__Vtemp_84[1U] 
                                      >> 8U));
            }
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product[3U] 
                = ((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[3U])) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[3U])));
            if ((0U != vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[3U])) {
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add[3U] 
                    = VL_SHIFTL_QQI(64,64,32, 1ULL, 
                                    (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[3U] 
                                     - (IData)(1U)));
            }
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[3U] 
                = VL_SHIFTR_QQI(64,64,32, (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product[3U] 
                                           + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add[3U]), vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[3U]);
            __Vtemp_86[0U] = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[3U]);
            __Vtemp_86[1U] = (IData)((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[3U] 
                                      >> 0x00000020U));
            __Vtemp_86[2U] = 0U;
            VL_NEGATE_W(3, __Vtemp_87, __Vtemp_86);
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[3U] 
                = ((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[3U] 
                    >> 0x1fU) ? (((QData)((IData)(__Vtemp_87[1U])) 
                                  << 0x00000020U) | (QData)((IData)(__Vtemp_87[0U])))
                    : vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[3U]);
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requantized_value[3U] 
                = (VL_LTS_IQQ(64, 0x000000000000007fULL, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[3U])
                    ? 0x0000007fU : (VL_GTS_IQQ(64, 0xffffffffffffff81ULL, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[3U])
                                      ? 0x00000081U
                                      : (0x000000ffU 
                                         & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[3U]))));
        } else if ((3U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[4U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[4U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[4U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product[4U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add[4U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[4U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[4U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requantized_value[4U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U] 
            = ((IData)(4U) + (((0x25U >= (0x0000003fU 
                                          & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                               [(0x0000003fU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                : 0U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base));
        if ((0x00000c5cU > vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])) {
            if ((4U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U]))) {
                    __Vtemp_89[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_89[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_89[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][2U];
                    __Vtemp_90[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_90[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_90[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][2U];
                    __Vtemp_91[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_91[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_91[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][2U];
                    __Vtemp_92[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_92[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_92[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][2U];
                    __Vtemp_93[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_93[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_93[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][2U];
                    __Vtemp_94[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_94[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_94[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][2U];
                    __Vtemp_95[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_95[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_95[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][2U];
                    __Vtemp_96[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_96[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_96[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][2U];
                    __Vtemp_97[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_97[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_97[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][2U];
                    __Vtemp_98[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_98[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_98[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][2U];
                } else {
                    __Vtemp_89[1U] = 0U;
                    __Vtemp_89[2U] = 0U;
                    __Vtemp_90[0U] = 0U;
                    __Vtemp_90[1U] = 0U;
                    __Vtemp_91[1U] = 0U;
                    __Vtemp_91[2U] = 0U;
                    __Vtemp_92[0U] = 0U;
                    __Vtemp_92[1U] = 0U;
                    __Vtemp_93[1U] = 0U;
                    __Vtemp_94[0U] = 0U;
                    __Vtemp_95[1U] = 0U;
                    __Vtemp_95[2U] = 0U;
                    __Vtemp_96[0U] = 0U;
                    __Vtemp_96[1U] = 0U;
                    __Vtemp_97[1U] = 0U;
                    __Vtemp_98[0U] = 0U;
                }
                if (((((((((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U] 
                            >= (((0x25U >= (0x0000003fU 
                                            & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                 [(0x0000003fU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                  : 0U) + ((0x25U >= 
                                            (0x0000003fU 
                                             & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                            ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                                           [(0x0000003fU 
                                             & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                            : 0U))) 
                           | (0U == ((__Vtemp_89[2U] 
                                      << 0x00000010U) 
                                     | (__Vtemp_89[1U] 
                                        >> 0x00000010U)))) 
                          | (0U == ((__Vtemp_90[1U] 
                                     << 0x00000018U) 
                                    | (__Vtemp_90[0U] 
                                       >> 8U)))) | 
                         (0x3fffffffU < ((__Vtemp_91[2U] 
                                          << 0x00000010U) 
                                         | (__Vtemp_91[1U] 
                                            >> 0x00000010U)))) 
                        | (0x3fffffffU < ((__Vtemp_92[1U] 
                                           << 0x00000018U) 
                                          | (__Vtemp_92[0U] 
                                             >> 8U)))) 
                       | (0x2fU < (0x000000ffU & (__Vtemp_93[1U] 
                                                  >> 8U)))) 
                      | (0x2fU < (0x000000ffU & __Vtemp_94[0U]))) 
                     | ((0U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__activation_mode_latched)) 
                        & ((((__Vtemp_95[2U] << 0x00000010U) 
                             | (__Vtemp_95[1U] >> 0x00000010U)) 
                            != ((__Vtemp_96[1U] << 0x00000018U) 
                                | (__Vtemp_96[0U] >> 8U))) 
                           | ((0x000000ffU & (__Vtemp_97[1U] 
                                              >> 8U)) 
                              != (0x000000ffU & __Vtemp_98[0U])))))) {
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_group_invalid = 1U;
                }
            }
            if ((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[4U] 
                 >> 0x1fU)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U]))) {
                    __Vtemp_99[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_99[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_99[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][2U];
                    __Vtemp_100[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_100[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_100[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][2U];
                } else {
                    __Vtemp_99[0U] = 0U;
                    __Vtemp_99[1U] = 0U;
                    __Vtemp_100[0U] = 0U;
                }
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[4U] 
                    = ((__Vtemp_99[1U] << 0x00000018U) 
                       | (__Vtemp_99[0U] >> 8U));
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[4U] 
                    = ((IData)(1U) + (~ vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[4U]));
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[4U] 
                    = (0x000000ffU & __Vtemp_100[0U]);
            } else {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U]))) {
                    __Vtemp_101[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_101[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_101[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][2U];
                    __Vtemp_102[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_102[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_102[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U])][2U];
                } else {
                    __Vtemp_101[1U] = 0U;
                    __Vtemp_101[2U] = 0U;
                    __Vtemp_102[1U] = 0U;
                }
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[4U] 
                    = ((__Vtemp_101[2U] << 0x00000010U) 
                       | (__Vtemp_101[1U] >> 0x00000010U));
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[4U] 
                    = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[4U];
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[4U] 
                    = (0x000000ffU & (__Vtemp_102[1U] 
                                      >> 8U));
            }
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product[4U] 
                = ((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[4U])) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[4U])));
            if ((0U != vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[4U])) {
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add[4U] 
                    = VL_SHIFTL_QQI(64,64,32, 1ULL, 
                                    (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[4U] 
                                     - (IData)(1U)));
            }
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[4U] 
                = VL_SHIFTR_QQI(64,64,32, (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product[4U] 
                                           + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add[4U]), vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[4U]);
            __Vtemp_104[0U] = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[4U]);
            __Vtemp_104[1U] = (IData)((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[4U] 
                                       >> 0x00000020U));
            __Vtemp_104[2U] = 0U;
            VL_NEGATE_W(3, __Vtemp_105, __Vtemp_104);
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[4U] 
                = ((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[4U] 
                    >> 0x1fU) ? (((QData)((IData)(__Vtemp_105[1U])) 
                                  << 0x00000020U) | (QData)((IData)(__Vtemp_105[0U])))
                    : vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[4U]);
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requantized_value[4U] 
                = (VL_LTS_IQQ(64, 0x000000000000007fULL, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[4U])
                    ? 0x0000007fU : (VL_GTS_IQQ(64, 0xffffffffffffff81ULL, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[4U])
                                      ? 0x00000081U
                                      : (0x000000ffU 
                                         & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[4U]))));
        } else if ((4U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[5U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[5U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[5U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product[5U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add[5U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[5U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[5U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requantized_value[5U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U] 
            = ((IData)(5U) + (((0x25U >= (0x0000003fU 
                                          & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                               [(0x0000003fU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                : 0U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base));
        if ((0x00000c5cU > vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])) {
            if ((5U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U]))) {
                    __Vtemp_107[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_107[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_107[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][2U];
                    __Vtemp_108[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_108[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_108[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][2U];
                    __Vtemp_109[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_109[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_109[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][2U];
                    __Vtemp_110[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_110[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_110[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][2U];
                    __Vtemp_111[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_111[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_111[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][2U];
                    __Vtemp_112[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_112[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_112[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][2U];
                    __Vtemp_113[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_113[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_113[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][2U];
                    __Vtemp_114[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_114[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_114[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][2U];
                    __Vtemp_115[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_115[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_115[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][2U];
                    __Vtemp_116[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_116[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_116[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][2U];
                } else {
                    __Vtemp_107[1U] = 0U;
                    __Vtemp_107[2U] = 0U;
                    __Vtemp_108[0U] = 0U;
                    __Vtemp_108[1U] = 0U;
                    __Vtemp_109[1U] = 0U;
                    __Vtemp_109[2U] = 0U;
                    __Vtemp_110[0U] = 0U;
                    __Vtemp_110[1U] = 0U;
                    __Vtemp_111[1U] = 0U;
                    __Vtemp_112[0U] = 0U;
                    __Vtemp_113[1U] = 0U;
                    __Vtemp_113[2U] = 0U;
                    __Vtemp_114[0U] = 0U;
                    __Vtemp_114[1U] = 0U;
                    __Vtemp_115[1U] = 0U;
                    __Vtemp_116[0U] = 0U;
                }
                if (((((((((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U] 
                            >= (((0x25U >= (0x0000003fU 
                                            & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                 [(0x0000003fU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                  : 0U) + ((0x25U >= 
                                            (0x0000003fU 
                                             & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                            ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                                           [(0x0000003fU 
                                             & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                            : 0U))) 
                           | (0U == ((__Vtemp_107[2U] 
                                      << 0x00000010U) 
                                     | (__Vtemp_107[1U] 
                                        >> 0x00000010U)))) 
                          | (0U == ((__Vtemp_108[1U] 
                                     << 0x00000018U) 
                                    | (__Vtemp_108[0U] 
                                       >> 8U)))) | 
                         (0x3fffffffU < ((__Vtemp_109[2U] 
                                          << 0x00000010U) 
                                         | (__Vtemp_109[1U] 
                                            >> 0x00000010U)))) 
                        | (0x3fffffffU < ((__Vtemp_110[1U] 
                                           << 0x00000018U) 
                                          | (__Vtemp_110[0U] 
                                             >> 8U)))) 
                       | (0x2fU < (0x000000ffU & (__Vtemp_111[1U] 
                                                  >> 8U)))) 
                      | (0x2fU < (0x000000ffU & __Vtemp_112[0U]))) 
                     | ((0U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__activation_mode_latched)) 
                        & ((((__Vtemp_113[2U] << 0x00000010U) 
                             | (__Vtemp_113[1U] >> 0x00000010U)) 
                            != ((__Vtemp_114[1U] << 0x00000018U) 
                                | (__Vtemp_114[0U] 
                                   >> 8U))) | ((0x000000ffU 
                                                & (__Vtemp_115[1U] 
                                                   >> 8U)) 
                                               != (0x000000ffU 
                                                   & __Vtemp_116[0U])))))) {
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_group_invalid = 1U;
                }
            }
            if ((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[5U] 
                 >> 0x1fU)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U]))) {
                    __Vtemp_117[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_117[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_117[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][2U];
                    __Vtemp_118[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_118[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_118[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][2U];
                } else {
                    __Vtemp_117[0U] = 0U;
                    __Vtemp_117[1U] = 0U;
                    __Vtemp_118[0U] = 0U;
                }
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[5U] 
                    = ((__Vtemp_117[1U] << 0x00000018U) 
                       | (__Vtemp_117[0U] >> 8U));
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[5U] 
                    = ((IData)(1U) + (~ vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[5U]));
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[5U] 
                    = (0x000000ffU & __Vtemp_118[0U]);
            } else {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U]))) {
                    __Vtemp_119[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_119[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_119[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][2U];
                    __Vtemp_120[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_120[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_120[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U])][2U];
                } else {
                    __Vtemp_119[1U] = 0U;
                    __Vtemp_119[2U] = 0U;
                    __Vtemp_120[1U] = 0U;
                }
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[5U] 
                    = ((__Vtemp_119[2U] << 0x00000010U) 
                       | (__Vtemp_119[1U] >> 0x00000010U));
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[5U] 
                    = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[5U];
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[5U] 
                    = (0x000000ffU & (__Vtemp_120[1U] 
                                      >> 8U));
            }
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product[5U] 
                = ((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[5U])) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[5U])));
            if ((0U != vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[5U])) {
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add[5U] 
                    = VL_SHIFTL_QQI(64,64,32, 1ULL, 
                                    (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[5U] 
                                     - (IData)(1U)));
            }
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[5U] 
                = VL_SHIFTR_QQI(64,64,32, (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product[5U] 
                                           + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add[5U]), vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[5U]);
            __Vtemp_122[0U] = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[5U]);
            __Vtemp_122[1U] = (IData)((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[5U] 
                                       >> 0x00000020U));
            __Vtemp_122[2U] = 0U;
            VL_NEGATE_W(3, __Vtemp_123, __Vtemp_122);
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[5U] 
                = ((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[5U] 
                    >> 0x1fU) ? (((QData)((IData)(__Vtemp_123[1U])) 
                                  << 0x00000020U) | (QData)((IData)(__Vtemp_123[0U])))
                    : vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[5U]);
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requantized_value[5U] 
                = (VL_LTS_IQQ(64, 0x000000000000007fULL, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[5U])
                    ? 0x0000007fU : (VL_GTS_IQQ(64, 0xffffffffffffff81ULL, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[5U])
                                      ? 0x00000081U
                                      : (0x000000ffU 
                                         & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[5U]))));
        } else if ((5U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[6U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[6U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[6U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product[6U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add[6U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[6U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[6U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requantized_value[6U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U] 
            = ((IData)(6U) + (((0x25U >= (0x0000003fU 
                                          & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                               [(0x0000003fU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                : 0U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base));
        if ((0x00000c5cU > vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])) {
            if ((6U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U]))) {
                    __Vtemp_125[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_125[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_125[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][2U];
                    __Vtemp_126[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_126[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_126[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][2U];
                    __Vtemp_127[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_127[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_127[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][2U];
                    __Vtemp_128[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_128[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_128[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][2U];
                    __Vtemp_129[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_129[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_129[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][2U];
                    __Vtemp_130[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_130[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_130[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][2U];
                    __Vtemp_131[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_131[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_131[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][2U];
                    __Vtemp_132[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_132[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_132[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][2U];
                    __Vtemp_133[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_133[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_133[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][2U];
                    __Vtemp_134[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_134[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_134[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][2U];
                } else {
                    __Vtemp_125[1U] = 0U;
                    __Vtemp_125[2U] = 0U;
                    __Vtemp_126[0U] = 0U;
                    __Vtemp_126[1U] = 0U;
                    __Vtemp_127[1U] = 0U;
                    __Vtemp_127[2U] = 0U;
                    __Vtemp_128[0U] = 0U;
                    __Vtemp_128[1U] = 0U;
                    __Vtemp_129[1U] = 0U;
                    __Vtemp_130[0U] = 0U;
                    __Vtemp_131[1U] = 0U;
                    __Vtemp_131[2U] = 0U;
                    __Vtemp_132[0U] = 0U;
                    __Vtemp_132[1U] = 0U;
                    __Vtemp_133[1U] = 0U;
                    __Vtemp_134[0U] = 0U;
                }
                if (((((((((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U] 
                            >= (((0x25U >= (0x0000003fU 
                                            & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                 [(0x0000003fU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                  : 0U) + ((0x25U >= 
                                            (0x0000003fU 
                                             & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                            ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                                           [(0x0000003fU 
                                             & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                            : 0U))) 
                           | (0U == ((__Vtemp_125[2U] 
                                      << 0x00000010U) 
                                     | (__Vtemp_125[1U] 
                                        >> 0x00000010U)))) 
                          | (0U == ((__Vtemp_126[1U] 
                                     << 0x00000018U) 
                                    | (__Vtemp_126[0U] 
                                       >> 8U)))) | 
                         (0x3fffffffU < ((__Vtemp_127[2U] 
                                          << 0x00000010U) 
                                         | (__Vtemp_127[1U] 
                                            >> 0x00000010U)))) 
                        | (0x3fffffffU < ((__Vtemp_128[1U] 
                                           << 0x00000018U) 
                                          | (__Vtemp_128[0U] 
                                             >> 8U)))) 
                       | (0x2fU < (0x000000ffU & (__Vtemp_129[1U] 
                                                  >> 8U)))) 
                      | (0x2fU < (0x000000ffU & __Vtemp_130[0U]))) 
                     | ((0U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__activation_mode_latched)) 
                        & ((((__Vtemp_131[2U] << 0x00000010U) 
                             | (__Vtemp_131[1U] >> 0x00000010U)) 
                            != ((__Vtemp_132[1U] << 0x00000018U) 
                                | (__Vtemp_132[0U] 
                                   >> 8U))) | ((0x000000ffU 
                                                & (__Vtemp_133[1U] 
                                                   >> 8U)) 
                                               != (0x000000ffU 
                                                   & __Vtemp_134[0U])))))) {
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_group_invalid = 1U;
                }
            }
            if ((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[6U] 
                 >> 0x1fU)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U]))) {
                    __Vtemp_135[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_135[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_135[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][2U];
                    __Vtemp_136[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_136[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_136[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][2U];
                } else {
                    __Vtemp_135[0U] = 0U;
                    __Vtemp_135[1U] = 0U;
                    __Vtemp_136[0U] = 0U;
                }
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[6U] 
                    = ((__Vtemp_135[1U] << 0x00000018U) 
                       | (__Vtemp_135[0U] >> 8U));
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[6U] 
                    = ((IData)(1U) + (~ vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[6U]));
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[6U] 
                    = (0x000000ffU & __Vtemp_136[0U]);
            } else {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U]))) {
                    __Vtemp_137[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_137[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_137[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][2U];
                    __Vtemp_138[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_138[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_138[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U])][2U];
                } else {
                    __Vtemp_137[1U] = 0U;
                    __Vtemp_137[2U] = 0U;
                    __Vtemp_138[1U] = 0U;
                }
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[6U] 
                    = ((__Vtemp_137[2U] << 0x00000010U) 
                       | (__Vtemp_137[1U] >> 0x00000010U));
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[6U] 
                    = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[6U];
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[6U] 
                    = (0x000000ffU & (__Vtemp_138[1U] 
                                      >> 8U));
            }
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product[6U] 
                = ((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[6U])) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[6U])));
            if ((0U != vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[6U])) {
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add[6U] 
                    = VL_SHIFTL_QQI(64,64,32, 1ULL, 
                                    (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[6U] 
                                     - (IData)(1U)));
            }
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[6U] 
                = VL_SHIFTR_QQI(64,64,32, (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product[6U] 
                                           + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add[6U]), vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[6U]);
            __Vtemp_140[0U] = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[6U]);
            __Vtemp_140[1U] = (IData)((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[6U] 
                                       >> 0x00000020U));
            __Vtemp_140[2U] = 0U;
            VL_NEGATE_W(3, __Vtemp_141, __Vtemp_140);
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[6U] 
                = ((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[6U] 
                    >> 0x1fU) ? (((QData)((IData)(__Vtemp_141[1U])) 
                                  << 0x00000020U) | (QData)((IData)(__Vtemp_141[0U])))
                    : vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[6U]);
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requantized_value[6U] 
                = (VL_LTS_IQQ(64, 0x000000000000007fULL, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[6U])
                    ? 0x0000007fU : (VL_GTS_IQQ(64, 0xffffffffffffff81ULL, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[6U])
                                      ? 0x00000081U
                                      : (0x000000ffU 
                                         & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[6U]))));
        } else if ((6U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[7U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[7U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[7U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product[7U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add[7U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[7U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[7U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requantized_value[7U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U] 
            = ((IData)(7U) + (((0x25U >= (0x0000003fU 
                                          & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                               [(0x0000003fU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                : 0U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base));
        if ((0x00000c5cU > vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])) {
            if ((7U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U]))) {
                    __Vtemp_143[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_143[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_143[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][2U];
                    __Vtemp_144[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_144[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_144[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][2U];
                    __Vtemp_145[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_145[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_145[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][2U];
                    __Vtemp_146[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_146[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_146[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][2U];
                    __Vtemp_147[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_147[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_147[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][2U];
                    __Vtemp_148[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_148[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_148[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][2U];
                    __Vtemp_149[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_149[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_149[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][2U];
                    __Vtemp_150[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_150[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_150[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][2U];
                    __Vtemp_151[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_151[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_151[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][2U];
                    __Vtemp_152[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_152[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_152[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][2U];
                } else {
                    __Vtemp_143[1U] = 0U;
                    __Vtemp_143[2U] = 0U;
                    __Vtemp_144[0U] = 0U;
                    __Vtemp_144[1U] = 0U;
                    __Vtemp_145[1U] = 0U;
                    __Vtemp_145[2U] = 0U;
                    __Vtemp_146[0U] = 0U;
                    __Vtemp_146[1U] = 0U;
                    __Vtemp_147[1U] = 0U;
                    __Vtemp_148[0U] = 0U;
                    __Vtemp_149[1U] = 0U;
                    __Vtemp_149[2U] = 0U;
                    __Vtemp_150[0U] = 0U;
                    __Vtemp_150[1U] = 0U;
                    __Vtemp_151[1U] = 0U;
                    __Vtemp_152[0U] = 0U;
                }
                if (((((((((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U] 
                            >= (((0x25U >= (0x0000003fU 
                                            & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                 [(0x0000003fU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                  : 0U) + ((0x25U >= 
                                            (0x0000003fU 
                                             & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                                            ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                                           [(0x0000003fU 
                                             & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                                            : 0U))) 
                           | (0U == ((__Vtemp_143[2U] 
                                      << 0x00000010U) 
                                     | (__Vtemp_143[1U] 
                                        >> 0x00000010U)))) 
                          | (0U == ((__Vtemp_144[1U] 
                                     << 0x00000018U) 
                                    | (__Vtemp_144[0U] 
                                       >> 8U)))) | 
                         (0x3fffffffU < ((__Vtemp_145[2U] 
                                          << 0x00000010U) 
                                         | (__Vtemp_145[1U] 
                                            >> 0x00000010U)))) 
                        | (0x3fffffffU < ((__Vtemp_146[1U] 
                                           << 0x00000018U) 
                                          | (__Vtemp_146[0U] 
                                             >> 8U)))) 
                       | (0x2fU < (0x000000ffU & (__Vtemp_147[1U] 
                                                  >> 8U)))) 
                      | (0x2fU < (0x000000ffU & __Vtemp_148[0U]))) 
                     | ((0U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__activation_mode_latched)) 
                        & ((((__Vtemp_149[2U] << 0x00000010U) 
                             | (__Vtemp_149[1U] >> 0x00000010U)) 
                            != ((__Vtemp_150[1U] << 0x00000018U) 
                                | (__Vtemp_150[0U] 
                                   >> 8U))) | ((0x000000ffU 
                                                & (__Vtemp_151[1U] 
                                                   >> 8U)) 
                                               != (0x000000ffU 
                                                   & __Vtemp_152[0U])))))) {
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_group_invalid = 1U;
                }
            }
            if ((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[7U] 
                 >> 0x1fU)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U]))) {
                    __Vtemp_153[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_153[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_153[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][2U];
                    __Vtemp_154[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_154[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_154[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][2U];
                } else {
                    __Vtemp_153[0U] = 0U;
                    __Vtemp_153[1U] = 0U;
                    __Vtemp_154[0U] = 0U;
                }
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[7U] 
                    = ((__Vtemp_153[1U] << 0x00000018U) 
                       | (__Vtemp_153[0U] >> 8U));
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[7U] 
                    = ((IData)(1U) + (~ vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[7U]));
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[7U] 
                    = (0x000000ffU & __Vtemp_154[0U]);
            } else {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U]))) {
                    __Vtemp_155[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_155[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_155[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][2U];
                    __Vtemp_156[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_156[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_156[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U])][2U];
                } else {
                    __Vtemp_155[1U] = 0U;
                    __Vtemp_155[2U] = 0U;
                    __Vtemp_156[1U] = 0U;
                }
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[7U] 
                    = ((__Vtemp_155[2U] << 0x00000010U) 
                       | (__Vtemp_155[1U] >> 0x00000010U));
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[7U] 
                    = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[7U];
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[7U] 
                    = (0x000000ffU & (__Vtemp_156[1U] 
                                      >> 8U));
            }
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product[7U] 
                = ((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[7U])) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[7U])));
            if ((0U != vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[7U])) {
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add[7U] 
                    = VL_SHIFTL_QQI(64,64,32, 1ULL, 
                                    (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[7U] 
                                     - (IData)(1U)));
            }
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[7U] 
                = VL_SHIFTR_QQI(64,64,32, (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product[7U] 
                                           + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add[7U]), vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[7U]);
            __Vtemp_158[0U] = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[7U]);
            __Vtemp_158[1U] = (IData)((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[7U] 
                                       >> 0x00000020U));
            __Vtemp_158[2U] = 0U;
            VL_NEGATE_W(3, __Vtemp_159, __Vtemp_158);
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[7U] 
                = ((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[7U] 
                    >> 0x1fU) ? (((QData)((IData)(__Vtemp_159[1U])) 
                                  << 0x00000020U) | (QData)((IData)(__Vtemp_159[0U])))
                    : vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[7U]);
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requantized_value[7U] 
                = (VL_LTS_IQQ(64, 0x000000000000007fULL, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[7U])
                    ? 0x0000007fU : (VL_GTS_IQQ(64, 0xffffffffffffff81ULL, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[7U])
                                      ? 0x00000081U
                                      : (0x000000ffU 
                                         & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[7U]))));
        } else if ((7U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_group_invalid = 1U;
        }
    } else {
        if ((0U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[1U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[1U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[1U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[1U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product[1U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add[1U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[1U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[1U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requantized_value[1U] = 0U;
        if ((1U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[2U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[2U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[2U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[2U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product[2U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add[2U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[2U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[2U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requantized_value[2U] = 0U;
        if ((2U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[3U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[3U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[3U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[3U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product[3U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add[3U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[3U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[3U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requantized_value[3U] = 0U;
        if ((3U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[4U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[4U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[4U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[4U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product[4U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add[4U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[4U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[4U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requantized_value[4U] = 0U;
        if ((4U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[5U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[5U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[5U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[5U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product[5U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add[5U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[5U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[5U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requantized_value[5U] = 0U;
        if ((5U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[6U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[6U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[6U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[6U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product[6U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add[6U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[6U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[6U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requantized_value[6U] = 0U;
        if ((6U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[7U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[7U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[7U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[7U] = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product[7U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add[7U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[7U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[7U] = 0ULL;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requantized_value[7U] = 0U;
        if ((7U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_group_invalid = 1U;
        }
    }
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__patch_plane_bytes 
        = ((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__patch_height)) 
           * (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__patch_width)));
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_channel = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_rem = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_y = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_x = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_input_y = 0ULL;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_input_x = 0ULL;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_in_bounds = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_source_offset = 0ULL;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_source_address_wide = 0ULL;
    if (((0ULL != tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__patch_plane_bytes) 
         & (0U != vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__patch_width))) {
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_channel 
            = (IData)(VL_DIV_QQQ(64, (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_index)), tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__patch_plane_bytes));
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_rem 
            = (IData)(VL_MODDIV_QQQ(64, (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_index)), tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__patch_plane_bytes));
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_y 
            = VL_DIV_III(32, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_rem, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__patch_width);
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_x 
            = VL_MODDIV_III(32, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_rem, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__patch_width);
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_input_y 
            = ((((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_y)) 
                 * (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__stride_y_latched))) 
                + (QData)((IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_y))) 
               - (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__pad_top_latched)));
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_input_x 
            = ((((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_x)) 
                 * (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__stride_x_latched))) 
                + (QData)((IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_x))) 
               - (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__pad_left_latched)));
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_in_bounds 
            = (((VL_LTES_IQQ(64, 0ULL, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_input_y) 
                 & VL_LTS_IQQ(64, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_input_y, (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_height_latched)))) 
                & VL_LTES_IQQ(64, 0ULL, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_input_x)) 
               & VL_LTS_IQQ(64, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_input_x, (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_width_latched))));
        if (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_in_bounds) {
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_source_offset 
                = (((((QData)((IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_channel)) 
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
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_input_channel = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_y = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_x = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_y = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_x = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_input_y = 0ULL;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_input_x = 0ULL;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_tap_in_bounds = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index_wide = 0ULL;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_bad_argument = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_overflow = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[0U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[0U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[0U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[0U] = 0ULL;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[1U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[1U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[1U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[1U] = 0ULL;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[2U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[2U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[2U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[2U] = 0ULL;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[3U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[3U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[3U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[3U] = 0ULL;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[4U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[4U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[4U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[4U] = 0ULL;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[5U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[5U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[5U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[5U] = 0ULL;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[6U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[6U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[6U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[6U] = 0ULL;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[7U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[7U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[7U] = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[7U] = 0ULL;
    if (((0U != tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_area) 
         & (0U != vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_width))) {
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_input_channel 
            = VL_DIV_III(32, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_reduction_index, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_area);
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_y 
            = VL_DIV_III(32, VL_MODDIV_III(32, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_reduction_index, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_area), vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_width_latched);
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_x 
            = VL_MODDIV_III(32, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_reduction_index, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_width_latched);
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_y 
            = VL_DIV_III(32, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_index, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_width);
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_x 
            = VL_MODDIV_III(32, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_index, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_width);
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_input_y 
            = (((((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_y)) 
                  * (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__stride_y_latched))) 
                 + ((QData)((IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_y)) 
                    * (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__stride_y_latched)))) 
                + (QData)((IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_y))) 
               - (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__pad_top_latched)));
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_input_x 
            = (((((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_x)) 
                  * (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__stride_x_latched))) 
                 + ((QData)((IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_x)) 
                    * (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__stride_x_latched)))) 
                + (QData)((IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_x))) 
               - (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__pad_left_latched)));
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_tap_in_bounds 
            = (((VL_LTES_IQQ(64, 0ULL, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_input_y) 
                 & VL_LTS_IQQ(64, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_input_y, (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_height_latched)))) 
                & VL_LTES_IQQ(64, 0ULL, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_input_x)) 
               & VL_LTS_IQQ(64, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_input_x, (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_width_latched))));
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index_wide 
            = (((((QData)((IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_input_channel)) 
                  * tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__patch_plane_bytes) 
                 + ((((QData)((IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_y)) 
                      * (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__stride_y_latched))) 
                     + (QData)((IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_y))) 
                    * (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__patch_width)))) 
                + ((QData)((IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_x)) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__stride_x_latched)))) 
               + (QData)((IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_x)));
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index 
            = (IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index_wide);
        if ((0U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[0U] 
                = ((IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_tap_in_bounds)
                    ? ((0xc7ffU >= (0x0000ffffU & tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index))
                        ? vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_patch
                       [(0x0000ffffU & tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index)]
                        : 0U) : 0U);
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[0U] 
                = ((0x8fffU >= (0x0000ffffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_reduction_index))
                    ? vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_group
                   [(0x0000ffffU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_reduction_index)]
                    : 0U);
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
            if (((IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_tap_in_bounds) 
                 & ((0x80U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[0U]) 
                    | (0x80U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[0U])))) {
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_bad_argument = 1U;
            }
            if (((1U & (IData)((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[0U] 
                                >> 0x20U))) != (1U 
                                                & (IData)(
                                                          (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[0U] 
                                                           >> 0x1fU))))) {
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_overflow = 1U;
            }
        } else {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[0U] = 0U;
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[0U] = 0U;
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[0U] = 0U;
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[0U] = 0ULL;
        }
        if ((1U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[1U] 
                = ((IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_tap_in_bounds)
                    ? ((0xc7ffU >= (0x0000ffffU & tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index))
                        ? vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_patch
                       [(0x0000ffffU & tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index)]
                        : 0U) : 0U);
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[1U] 
                = ((0x8fffU >= (0x0000ffffU & (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_latched 
                                               + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_reduction_index)))
                    ? vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_group
                   [(0x0000ffffU & (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_latched 
                                    + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_reduction_index))]
                    : 0U);
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
            if (((IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_tap_in_bounds) 
                 & ((0x80U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[1U]) 
                    | (0x80U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[1U])))) {
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_bad_argument = 1U;
            }
            if (((1U & (IData)((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[1U] 
                                >> 0x20U))) != (1U 
                                                & (IData)(
                                                          (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[1U] 
                                                           >> 0x1fU))))) {
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_overflow = 1U;
            }
        } else {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[1U] = 0U;
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[1U] = 0U;
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[1U] = 0U;
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[1U] = 0ULL;
        }
        if ((2U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[2U] 
                = ((IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_tap_in_bounds)
                    ? ((0xc7ffU >= (0x0000ffffU & tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index))
                        ? vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_patch
                       [(0x0000ffffU & tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index)]
                        : 0U) : 0U);
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[2U] 
                = ((0x8fffU >= (0x0000ffffU & ((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_latched 
                                                << 1U) 
                                               + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_reduction_index)))
                    ? vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_group
                   [(0x0000ffffU & ((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_latched 
                                     << 1U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_reduction_index))]
                    : 0U);
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
            if (((IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_tap_in_bounds) 
                 & ((0x80U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[2U]) 
                    | (0x80U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[2U])))) {
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_bad_argument = 1U;
            }
            if (((1U & (IData)((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[2U] 
                                >> 0x20U))) != (1U 
                                                & (IData)(
                                                          (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[2U] 
                                                           >> 0x1fU))))) {
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_overflow = 1U;
            }
        } else {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[2U] = 0U;
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[2U] = 0U;
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[2U] = 0U;
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[2U] = 0ULL;
        }
        if ((3U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[3U] 
                = ((IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_tap_in_bounds)
                    ? ((0xc7ffU >= (0x0000ffffU & tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index))
                        ? vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_patch
                       [(0x0000ffffU & tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index)]
                        : 0U) : 0U);
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[3U] 
                = ((0x8fffU >= (0x0000ffffU & (((IData)(3U) 
                                                * vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_latched) 
                                               + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_reduction_index)))
                    ? vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_group
                   [(0x0000ffffU & (((IData)(3U) * vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_latched) 
                                    + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_reduction_index))]
                    : 0U);
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
            if (((IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_tap_in_bounds) 
                 & ((0x80U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[3U]) 
                    | (0x80U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[3U])))) {
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_bad_argument = 1U;
            }
            if (((1U & (IData)((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[3U] 
                                >> 0x20U))) != (1U 
                                                & (IData)(
                                                          (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[3U] 
                                                           >> 0x1fU))))) {
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_overflow = 1U;
            }
        } else {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[3U] = 0U;
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[3U] = 0U;
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[3U] = 0U;
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[3U] = 0ULL;
        }
        if ((4U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[4U] 
                = ((IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_tap_in_bounds)
                    ? ((0xc7ffU >= (0x0000ffffU & tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index))
                        ? vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_patch
                       [(0x0000ffffU & tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index)]
                        : 0U) : 0U);
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[4U] 
                = ((0x8fffU >= (0x0000ffffU & ((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_latched 
                                                << 2U) 
                                               + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_reduction_index)))
                    ? vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_group
                   [(0x0000ffffU & ((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_latched 
                                     << 2U) + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_reduction_index))]
                    : 0U);
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
            if (((IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_tap_in_bounds) 
                 & ((0x80U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[4U]) 
                    | (0x80U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[4U])))) {
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_bad_argument = 1U;
            }
            if (((1U & (IData)((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[4U] 
                                >> 0x20U))) != (1U 
                                                & (IData)(
                                                          (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[4U] 
                                                           >> 0x1fU))))) {
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_overflow = 1U;
            }
        } else {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[4U] = 0U;
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[4U] = 0U;
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[4U] = 0U;
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[4U] = 0ULL;
        }
        if ((5U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[5U] 
                = ((IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_tap_in_bounds)
                    ? ((0xc7ffU >= (0x0000ffffU & tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index))
                        ? vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_patch
                       [(0x0000ffffU & tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index)]
                        : 0U) : 0U);
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[5U] 
                = ((0x8fffU >= (0x0000ffffU & (((IData)(5U) 
                                                * vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_latched) 
                                               + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_reduction_index)))
                    ? vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_group
                   [(0x0000ffffU & (((IData)(5U) * vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_latched) 
                                    + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_reduction_index))]
                    : 0U);
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
            if (((IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_tap_in_bounds) 
                 & ((0x80U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[5U]) 
                    | (0x80U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[5U])))) {
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_bad_argument = 1U;
            }
            if (((1U & (IData)((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[5U] 
                                >> 0x20U))) != (1U 
                                                & (IData)(
                                                          (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[5U] 
                                                           >> 0x1fU))))) {
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_overflow = 1U;
            }
        } else {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[5U] = 0U;
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[5U] = 0U;
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[5U] = 0U;
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[5U] = 0ULL;
        }
        if ((6U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[6U] 
                = ((IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_tap_in_bounds)
                    ? ((0xc7ffU >= (0x0000ffffU & tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index))
                        ? vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_patch
                       [(0x0000ffffU & tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index)]
                        : 0U) : 0U);
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[6U] 
                = ((0x8fffU >= (0x0000ffffU & (((IData)(6U) 
                                                * vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_latched) 
                                               + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_reduction_index)))
                    ? vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_group
                   [(0x0000ffffU & (((IData)(6U) * vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_latched) 
                                    + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_reduction_index))]
                    : 0U);
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
            if (((IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_tap_in_bounds) 
                 & ((0x80U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[6U]) 
                    | (0x80U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[6U])))) {
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_bad_argument = 1U;
            }
            if (((1U & (IData)((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[6U] 
                                >> 0x20U))) != (1U 
                                                & (IData)(
                                                          (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[6U] 
                                                           >> 0x1fU))))) {
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_overflow = 1U;
            }
        } else {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[6U] = 0U;
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[6U] = 0U;
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[6U] = 0U;
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[6U] = 0ULL;
        }
        if ((7U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[7U] 
                = ((IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_tap_in_bounds)
                    ? ((0xc7ffU >= (0x0000ffffU & tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index))
                        ? vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_patch
                       [(0x0000ffffU & tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index)]
                        : 0U) : 0U);
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[7U] 
                = ((0x8fffU >= (0x0000ffffU & (((IData)(7U) 
                                                * vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_latched) 
                                               + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_reduction_index)))
                    ? vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_group
                   [(0x0000ffffU & (((IData)(7U) * vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_latched) 
                                    + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_reduction_index))]
                    : 0U);
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
            if (((IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_tap_in_bounds) 
                 & ((0x80U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[7U]) 
                    | (0x80U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[7U])))) {
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_bad_argument = 1U;
            }
            if (((1U & (IData)((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[7U] 
                                >> 0x20U))) != (1U 
                                                & (IData)(
                                                          (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[7U] 
                                                           >> 0x1fU))))) {
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_overflow = 1U;
            }
        } else {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[7U] = 0U;
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[7U] = 0U;
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[7U] = 0U;
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[7U] = 0ULL;
        }
    }
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__request_byte_lane 
        = (3U & (0x00030210U >> ((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__request_strobe_latched) 
                                 << 1U)));
    vlSelfRef.__VdfgRegularize_h6e95ff9d_0_198[0U] 
        = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_height_latched;
    vlSelfRef.__VdfgRegularize_h6e95ff9d_0_198[1U] = 0U;
    vlSelfRef.__VdfgRegularize_h6e95ff9d_0_198[2U] = 0U;
    vlSelfRef.__VdfgRegularize_h6e95ff9d_0_197[0U] 
        = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_width_latched;
    vlSelfRef.__VdfgRegularize_h6e95ff9d_0_197[1U] = 0U;
    vlSelfRef.__VdfgRegularize_h6e95ff9d_0_197[2U] = 0U;
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
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__rounded_magnitude = 0ULL;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__scaled_signed = 0ULL;
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
    } else if ((1U < vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__groups_latched)) {
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
            = (0x000000ffU & (VL_GTS_III(8, 0U, (IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_value))
                               ? (- (IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_value))
                               : (IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_value)));
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__scaled_product 
            = ((QData)((IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_magnitude)) 
               * (QData)((IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_multiplier)));
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
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__rounded_magnitude 
            = ((0x0000000040000000ULL + tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__scaled_product) 
               >> 0x0000001fU);
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__scaled_signed 
            = (VL_GTS_III(8, 0U, (IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_value))
                ? (- tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__rounded_magnitude)
                : tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__rounded_magnitude);
        if (VL_LTS_IQQ(64, 0x000000000000007fULL, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__scaled_signed)) {
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__scaled_signed = 0x000000000000007fULL;
        } else if (VL_GTS_IQQ(64, 0xffffffffffffff81ULL, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__scaled_signed)) {
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__scaled_signed = 0xffffffffffffff81ULL;
        }
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__query_output_value 
            = (0x000000ffU & (IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__scaled_signed));
    }
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
    } else {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__layer_index = 0U;
        __Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__map_conv_activation__26__descriptor_activation = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_upsample_engine__stride = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__darknet_padding_parameter = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_x = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_y = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width = 0U;
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_height = 0U;
    }
    __Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__map_conv_activation__26__Vfuncout 
        = (3U & (0xd0U >> ((IData)(__Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__map_conv_activation__26__descriptor_activation) 
                           << 1U)));
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_conv_engine__activation_mode 
        = __Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__map_conv_activation__26__Vfuncout;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__selected_byte_shift 
        = (0x00000018U & (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source_address_latched 
                          << 3U));
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
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__selected_result_error = 6U;
    if ((4U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__state))) {
        if ((1U & (~ ((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__state) 
                      >> 1U)))) {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__selected_result_error 
                = ((1U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__state))
                    ? (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__result_error_latched)
                    : (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__result_error_latched));
        }
    } else if ((2U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__state))) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__selected_result_error 
            = ((1U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__state))
                ? (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__result_error_latched)
                : (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__result_error_latched));
    }
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_address_wide 
        = ((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_base_latched)) 
           + vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_byte_offset_wide);
    __Vtemp_162[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_x_latched;
    __Vtemp_162[1U] = 0U;
    __Vtemp_162[2U] = 0U;
    __Vtemp_164[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_y_latched;
    __Vtemp_164[1U] = 0U;
    __Vtemp_164[2U] = 0U;
    __Vtemp_165[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_channel_latched;
    __Vtemp_165[1U] = 0U;
    __Vtemp_165[2U] = 0U;
    VL_MUL_W(3, __Vtemp_166, vlSelfRef.__VdfgRegularize_h6e95ff9d_0_198, __Vtemp_165);
    VL_ADD_W(3, __Vtemp_167, __Vtemp_164, __Vtemp_166);
    __Vtemp_168[0U] = __Vtemp_167[0U];
    __Vtemp_168[1U] = __Vtemp_167[1U];
    __Vtemp_168[2U] = (1U & __Vtemp_167[2U]);
    VL_MUL_W(3, __Vtemp_169, vlSelfRef.__VdfgRegularize_h6e95ff9d_0_197, __Vtemp_168);
    VL_ADD_W(3, __Vtemp_170, __Vtemp_162, __Vtemp_169);
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_offset_work[0U] 
        = __Vtemp_170[0U];
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_offset_work[1U] 
        = __Vtemp_170[1U];
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_offset_work[2U] 
        = (1U & __Vtemp_170[2U]);
    if (__VdlySet__tb_s2a_network_backend_golden__DOT__feature_bytes__v0) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__feature_bytes[__VdlyDim0__tb_s2a_network_backend_golden__DOT__feature_bytes__v0] 
            = __VdlyVal__tb_s2a_network_backend_golden__DOT__feature_bytes__v0;
    }
    if (__VdlySet__tb_s2a_network_backend_golden__DOT__feature_bytes__v1) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__feature_bytes[__VdlyDim0__tb_s2a_network_backend_golden__DOT__feature_bytes__v1] 
            = __VdlyVal__tb_s2a_network_backend_golden__DOT__feature_bytes__v1;
    }
    if (__VdlySet__tb_s2a_network_backend_golden__DOT__feature_bytes__v2) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__feature_bytes[__VdlyDim0__tb_s2a_network_backend_golden__DOT__feature_bytes__v2] 
            = __VdlyVal__tb_s2a_network_backend_golden__DOT__feature_bytes__v2;
    }
    if (__VdlySet__tb_s2a_network_backend_golden__DOT__feature_bytes__v3) {
        vlSelfRef.tb_s2a_network_backend_golden__DOT__feature_bytes[__VdlyDim0__tb_s2a_network_backend_golden__DOT__feature_bytes__v3] 
            = __VdlyVal__tb_s2a_network_backend_golden__DOT__feature_bytes__v3;
    }
}
