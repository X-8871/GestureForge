// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vtb_s2a_network_backend_golden.h for the primary calling header

#include "Vtb_s2a_network_backend_golden__pch.h"

extern const VlWide<10>/*319:0*/ Vtb_s2a_network_backend_golden__ConstPool__CONST_hb4617e49_0;
extern const VlUnpacked<IData/*31:0*/, 5> Vtb_s2a_network_backend_golden__ConstPool__TABLE_hc6a14c36_0;

void Vtb_s2a_network_backend_golden___024root___nba_comb__TOP__1(Vtb_s2a_network_backend_golden___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_network_backend_golden___024root___nba_comb__TOP__1\n"); );
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
    QData/*63:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_y_step;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_y_step = 0;
    QData/*63:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_x_step;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_x_step = 0;
    QData/*63:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_y_work;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_y_work = 0;
    QData/*63:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_x_work;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_x_work = 0;
    VlWide<3>/*95:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work;
    VL_ZERO_W(96, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work);
    VlWide<3>/*95:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work;
    VL_ZERO_W(96, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work);
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
    QData/*63:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__channel_row_work;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__channel_row_work = 0;
    QData/*63:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__row_work;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__row_work = 0;
    QData/*63:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__byte_offset_work;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__byte_offset_work = 0;
    VlWide<3>/*64:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__address_work;
    VL_ZERO_W(65, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__address_work);
    IData/*31:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__selected_word_address;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__selected_word_address = 0;
    CData/*3:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__selected_read_lane;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__selected_read_lane = 0;
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
    VlWide<4>/*127:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_height_wide;
    VL_ZERO_W(128, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_height_wide);
    VlWide<4>/*127:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_width_wide;
    VL_ZERO_W(128, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_width_wide);
    VlWide<4>/*127:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_bytes_wide;
    VL_ZERO_W(128, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_bytes_wide);
    VlWide<4>/*127:0*/ tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__full_weight_group_bytes_wide;
    VL_ZERO_W(128, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__full_weight_group_bytes_wide);
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
    VlWide<4>/*127:0*/ __Vtemp_1;
    VlWide<4>/*127:0*/ __Vtemp_2;
    VlWide<4>/*127:0*/ __Vtemp_3;
    VlWide<4>/*127:0*/ __Vtemp_4;
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
    VlWide<4>/*127:0*/ __Vtemp_43;
    VlWide<4>/*127:0*/ __Vtemp_44;
    VlWide<4>/*127:0*/ __Vtemp_45;
    VlWide<4>/*127:0*/ __Vtemp_46;
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
    VlWide<3>/*95:0*/ __Vtemp_58;
    VlWide<3>/*95:0*/ __Vtemp_59;
    VlWide<3>/*95:0*/ __Vtemp_60;
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
    VlWide<3>/*95:0*/ __Vtemp_131;
    VlWide<3>/*95:0*/ __Vtemp_132;
    VlWide<3>/*95:0*/ __Vtemp_133;
    VlWide<3>/*95:0*/ __Vtemp_134;
    VlWide<3>/*95:0*/ __Vtemp_135;
    VlWide<3>/*95:0*/ __Vtemp_136;
    VlWide<4>/*127:0*/ __Vtemp_138;
    VlWide<4>/*127:0*/ __Vtemp_139;
    VlWide<4>/*127:0*/ __Vtemp_140;
    VlWide<3>/*95:0*/ __Vtemp_145;
    VlWide<3>/*95:0*/ __Vtemp_146;
    VlWide<3>/*95:0*/ __Vtemp_147;
    VlWide<3>/*95:0*/ __Vtemp_148;
    VlWide<3>/*95:0*/ __Vtemp_149;
    VlWide<3>/*95:0*/ __Vtemp_150;
    VlWide<4>/*127:0*/ __Vtemp_152;
    VlWide<4>/*127:0*/ __Vtemp_153;
    VlWide<4>/*127:0*/ __Vtemp_154;
    VlWide<3>/*95:0*/ __Vtemp_159;
    VlWide<3>/*95:0*/ __Vtemp_160;
    VlWide<3>/*95:0*/ __Vtemp_161;
    VlWide<3>/*95:0*/ __Vtemp_162;
    VlWide<3>/*95:0*/ __Vtemp_163;
    VlWide<3>/*95:0*/ __Vtemp_164;
    VlWide<4>/*127:0*/ __Vtemp_166;
    VlWide<4>/*127:0*/ __Vtemp_167;
    VlWide<4>/*127:0*/ __Vtemp_168;
    VlWide<3>/*95:0*/ __Vtemp_173;
    VlWide<3>/*95:0*/ __Vtemp_174;
    VlWide<3>/*95:0*/ __Vtemp_175;
    VlWide<3>/*95:0*/ __Vtemp_176;
    VlWide<3>/*95:0*/ __Vtemp_177;
    VlWide<3>/*95:0*/ __Vtemp_178;
    VlWide<4>/*127:0*/ __Vtemp_180;
    VlWide<4>/*127:0*/ __Vtemp_181;
    VlWide<4>/*127:0*/ __Vtemp_182;
    VlWide<3>/*95:0*/ __Vtemp_188;
    VlWide<3>/*95:0*/ __Vtemp_189;
    VlWide<3>/*95:0*/ __Vtemp_191;
    VlWide<3>/*95:0*/ __Vtemp_192;
    IData/*31:0*/ __Vtemp_193;
    // Body
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
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__conv_rsp_valid 
        = ((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__response_pending) 
           & ((~ (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__hard_reset)) 
              & (0U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__response_target_latched))));
    __Vtemp_1[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_batch_count_latched;
    __Vtemp_1[1U] = 0U;
    __Vtemp_1[2U] = 0U;
    __Vtemp_1[3U] = 0U;
    __Vtemp_2[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_channels_latched;
    __Vtemp_2[1U] = 0U;
    __Vtemp_2[2U] = 0U;
    __Vtemp_2[3U] = 0U;
    VL_MUL_W(4, __Vtemp_3, __Vtemp_1, __Vtemp_2);
    __Vtemp_4[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_height_latched;
    __Vtemp_4[1U] = 0U;
    __Vtemp_4[2U] = 0U;
    __Vtemp_4[3U] = 0U;
    VL_MUL_W(4, __Vtemp_5, __Vtemp_3, __Vtemp_4);
    __Vtemp_6[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_width_latched;
    __Vtemp_6[1U] = 0U;
    __Vtemp_6[2U] = 0U;
    __Vtemp_6[3U] = 0U;
    VL_MUL_W(4, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_elements_wide, __Vtemp_5, __Vtemp_6);
    __Vtemp_7[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_batch_count_latched;
    __Vtemp_7[1U] = 0U;
    __Vtemp_7[2U] = 0U;
    __Vtemp_7[3U] = 0U;
    __Vtemp_8[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_channels_latched;
    __Vtemp_8[1U] = 0U;
    __Vtemp_8[2U] = 0U;
    __Vtemp_8[3U] = 0U;
    VL_MUL_W(4, __Vtemp_9, __Vtemp_7, __Vtemp_8);
    __Vtemp_10[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_latched;
    __Vtemp_10[1U] = 0U;
    __Vtemp_10[2U] = 0U;
    __Vtemp_10[3U] = 0U;
    VL_MUL_W(4, __Vtemp_11, __Vtemp_9, __Vtemp_10);
    __Vtemp_12[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_latched;
    __Vtemp_12[1U] = 0U;
    __Vtemp_12[2U] = 0U;
    __Vtemp_12[3U] = 0U;
    VL_MUL_W(4, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_elements_wide, __Vtemp_11, __Vtemp_12);
    __Vtemp_13[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_channels_latched;
    __Vtemp_13[1U] = 0U;
    __Vtemp_13[2U] = 0U;
    __Vtemp_13[3U] = 0U;
    __Vtemp_14[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_channels_latched;
    __Vtemp_14[1U] = 0U;
    __Vtemp_14[2U] = 0U;
    __Vtemp_14[3U] = 0U;
    VL_MUL_W(4, __Vtemp_15, __Vtemp_13, __Vtemp_14);
    __Vtemp_16[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_height_latched;
    __Vtemp_16[1U] = 0U;
    __Vtemp_16[2U] = 0U;
    __Vtemp_16[3U] = 0U;
    VL_MUL_W(4, __Vtemp_17, __Vtemp_15, __Vtemp_16);
    __Vtemp_18[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_width_latched;
    __Vtemp_18[1U] = 0U;
    __Vtemp_18[2U] = 0U;
    __Vtemp_18[3U] = 0U;
    VL_MUL_W(4, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__expected_weight_bytes_wide, __Vtemp_17, __Vtemp_18);
    __Vtemp_19[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_channels_latched;
    __Vtemp_19[1U] = 0U;
    __Vtemp_19[2U] = 0U;
    __Vtemp_19[3U] = 0U;
    __Vtemp_20[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_height_latched;
    __Vtemp_20[1U] = 0U;
    __Vtemp_20[2U] = 0U;
    __Vtemp_20[3U] = 0U;
    VL_MUL_W(4, __Vtemp_21, __Vtemp_19, __Vtemp_20);
    __Vtemp_22[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_width_latched;
    __Vtemp_22[1U] = 0U;
    __Vtemp_22[2U] = 0U;
    __Vtemp_22[3U] = 0U;
    VL_MUL_W(4, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_wide, __Vtemp_21, __Vtemp_22);
    __Vtemp_23[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_base_latched;
    __Vtemp_23[1U] = 0U;
    __Vtemp_23[2U] = 0U;
    __Vtemp_23[3U] = 0U;
    __Vtemp_24[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_length_latched;
    __Vtemp_24[1U] = 0U;
    __Vtemp_24[2U] = 0U;
    __Vtemp_24[3U] = 0U;
    VL_ADD_W(4, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_end_wide, __Vtemp_23, __Vtemp_24);
    __Vtemp_25[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_base_latched;
    __Vtemp_25[1U] = 0U;
    __Vtemp_25[2U] = 0U;
    __Vtemp_25[3U] = 0U;
    __Vtemp_26[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_length_latched;
    __Vtemp_26[1U] = 0U;
    __Vtemp_26[2U] = 0U;
    __Vtemp_26[3U] = 0U;
    VL_ADD_W(4, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_end_wide, __Vtemp_25, __Vtemp_26);
    __Vtemp_27[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_package_base_latched;
    __Vtemp_27[1U] = 0U;
    __Vtemp_27[2U] = 0U;
    __Vtemp_27[3U] = 0U;
    __Vtemp_28[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_package_length_latched;
    __Vtemp_28[1U] = 0U;
    __Vtemp_28[2U] = 0U;
    __Vtemp_28[3U] = 0U;
    VL_ADD_W(4, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_package_end_wide, __Vtemp_27, __Vtemp_28);
    __Vtemp_29[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__quantized_weight_offset_latched;
    __Vtemp_29[1U] = 0U;
    __Vtemp_29[2U] = 0U;
    __Vtemp_29[3U] = 0U;
    __Vtemp_30[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__quantized_weight_bytes_latched;
    __Vtemp_30[1U] = 0U;
    __Vtemp_30[2U] = 0U;
    __Vtemp_30[3U] = 0U;
    VL_ADD_W(4, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__quantized_weight_end_wide, __Vtemp_29, __Vtemp_30);
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_numerator 
        = (((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_height_latched)) 
            + (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__pad_top_latched))) 
           + (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__pad_bottom_latched)));
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_numerator 
        = (((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_width_latched)) 
            + (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__pad_left_latched))) 
           + (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__pad_right_latched)));
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
        __Vtemp_31[0U] = (((8U > vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_latched)
                            ? vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_latched
                            : 8U) - (IData)(1U));
        __Vtemp_31[1U] = 0U;
        __Vtemp_31[2U] = 0U;
        __Vtemp_31[3U] = 0U;
        __Vtemp_32[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__stride_y_latched;
        __Vtemp_32[1U] = 0U;
        __Vtemp_32[2U] = 0U;
        __Vtemp_32[3U] = 0U;
        VL_MUL_W(4, __Vtemp_33, __Vtemp_31, __Vtemp_32);
        __Vtemp_34[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_height_latched;
        __Vtemp_34[1U] = 0U;
        __Vtemp_34[2U] = 0U;
        __Vtemp_34[3U] = 0U;
        VL_ADD_W(4, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_height_wide, __Vtemp_33, __Vtemp_34);
        __Vtemp_35[0U] = (((8U > vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_latched)
                            ? vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_latched
                            : 8U) - (IData)(1U));
        __Vtemp_35[1U] = 0U;
        __Vtemp_35[2U] = 0U;
        __Vtemp_35[3U] = 0U;
        __Vtemp_36[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__stride_x_latched;
        __Vtemp_36[1U] = 0U;
        __Vtemp_36[2U] = 0U;
        __Vtemp_36[3U] = 0U;
        VL_MUL_W(4, __Vtemp_37, __Vtemp_35, __Vtemp_36);
        __Vtemp_38[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_width_latched;
        __Vtemp_38[1U] = 0U;
        __Vtemp_38[2U] = 0U;
        __Vtemp_38[3U] = 0U;
        VL_ADD_W(4, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_width_wide, __Vtemp_37, __Vtemp_38);
        VL_MUL_W(4, __Vtemp_39, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_height_wide, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_width_wide);
        __Vtemp_40[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_channels_latched;
        __Vtemp_40[1U] = 0U;
        __Vtemp_40[2U] = 0U;
        __Vtemp_40[3U] = 0U;
        VL_MUL_W(4, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_bytes_wide, __Vtemp_39, __Vtemp_40);
    }
    __Vtemp_41[0U] = ((8U > vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_channels_latched)
                       ? vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_channels_latched
                       : 8U);
    __Vtemp_41[1U] = 0U;
    __Vtemp_41[2U] = 0U;
    __Vtemp_41[3U] = 0U;
    VL_MUL_W(4, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__full_weight_group_bytes_wide, __Vtemp_41, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_wide);
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__validation_ok = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__validation_error = 1U;
    __Vtemp_43[0U] = 0x00001fffU;
    __Vtemp_43[1U] = 0U;
    __Vtemp_43[2U] = 0U;
    __Vtemp_43[3U] = 0U;
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
                  | VL_LT_W(4, __Vtemp_43, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_wide)) 
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
        __Vtemp_44[0U] = 0xffffffffU;
        __Vtemp_44[1U] = 0U;
        __Vtemp_44[2U] = 0U;
        __Vtemp_44[3U] = 0U;
        __Vtemp_45[0U] = 0xffffffffU;
        __Vtemp_45[1U] = 0U;
        __Vtemp_45[2U] = 0U;
        __Vtemp_45[3U] = 0U;
        __Vtemp_46[0U] = 0xffffffffU;
        __Vtemp_46[1U] = 0U;
        __Vtemp_46[2U] = 0U;
        __Vtemp_46[3U] = 0U;
        if ((((((VL_LT_W(4, __Vtemp_44, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_elements_wide) 
                 | (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_length_latched 
                    != tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_elements_wide[0U])) 
                | VL_LT_W(4, __Vtemp_45, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_elements_wide)) 
               | (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_length_latched 
                  != vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_elements_wide[0U])) 
              | VL_LT_W(4, __Vtemp_46, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__expected_weight_bytes_wide)) 
             | (vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__quantized_weight_bytes_latched 
                != tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__expected_weight_bytes_wide[0U]))) {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__validation_error = 3U;
        } else {
            __Vtemp_47[0U] = 0U;
            __Vtemp_47[1U] = 1U;
            __Vtemp_47[2U] = 0U;
            __Vtemp_47[3U] = 0U;
            __Vtemp_48[0U] = 0U;
            __Vtemp_48[1U] = 1U;
            __Vtemp_48[2U] = 0U;
            __Vtemp_48[3U] = 0U;
            __Vtemp_49[0U] = 0U;
            __Vtemp_49[1U] = 1U;
            __Vtemp_49[2U] = 0U;
            __Vtemp_49[3U] = 0U;
            __Vtemp_50[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_package_length_latched;
            __Vtemp_50[1U] = 0U;
            __Vtemp_50[2U] = 0U;
            __Vtemp_50[3U] = 0U;
            __Vtemp_51[0U] = 0x00000c5cU;
            __Vtemp_51[1U] = 0U;
            __Vtemp_51[2U] = 0U;
            __Vtemp_51[3U] = 0U;
            __Vtemp_52[0U] = ((0x25U >= (0x0000003fU 
                                         & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                               ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                              [(0x0000003fU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                               : 0U);
            __Vtemp_52[1U] = 0U;
            __Vtemp_52[2U] = 0U;
            __Vtemp_52[3U] = 0U;
            __Vtemp_53[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_channels_latched;
            __Vtemp_53[1U] = 0U;
            __Vtemp_53[2U] = 0U;
            __Vtemp_53[3U] = 0U;
            VL_ADD_W(4, __Vtemp_54, __Vtemp_52, __Vtemp_53);
            __Vtemp_55[0U] = 0x0000c800U;
            __Vtemp_55[1U] = 0U;
            __Vtemp_55[2U] = 0U;
            __Vtemp_55[3U] = 0U;
            __Vtemp_56[0U] = 0x00009000U;
            __Vtemp_56[1U] = 0U;
            __Vtemp_56[2U] = 0U;
            __Vtemp_56[3U] = 0U;
            if (((((((((VL_LT_W(4, __Vtemp_47, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_end_wide) 
                        | VL_LT_W(4, __Vtemp_48, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_end_wide)) 
                       | VL_LT_W(4, __Vtemp_49, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_package_end_wide)) 
                      | (0U == vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_package_length_latched)) 
                     | VL_GT_W(4, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__quantized_weight_end_wide, __Vtemp_50)) 
                    | (((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched))
                         ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                        [(0x0000003fU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched)]
                         : 0U) != vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_channels_latched)) 
                   | VL_LT_W(4, __Vtemp_51, __Vtemp_54)) 
                  | VL_LT_W(4, __Vtemp_55, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_bytes_wide)) 
                 | VL_LT_W(4, __Vtemp_56, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__full_weight_group_bytes_wide))) {
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__validation_error = 2U;
            } else if (((((tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_numerator 
                           < (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_height_latched))) 
                          | (tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_numerator 
                             < (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_width_latched)))) 
                         | ((1ULL + VL_DIV_QQQ(64, 
                                               (tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_numerator 
                                                - (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_height_latched))), (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__stride_y_latched)))) 
                            != (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_latched)))) 
                        | ((1ULL + VL_DIV_QQQ(64, (tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_numerator 
                                                   - (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_width_latched))), (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__stride_x_latched)))) 
                           != (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_latched))))) {
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__validation_error = 1U;
            } else {
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__validation_ok = 1U;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__validation_error = 0U;
            }
        }
    }
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__conv_req_write = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__conv_req_wstrb = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__conv_start_ready 
        = ((~ (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__hard_reset)) 
           & (0U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state)));
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__conv_req_rstrb = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__conv_req_valid = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__route_req_wdata = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__route_req_write = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__route_req_wstrb = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__route_start_ready 
        = ((~ (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__hard_reset)) 
           & (0U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__state)));
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__selected_read_lane 
        = (0x0000000fU & ((IData)(1U) << (3U & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source_address_latched)));
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__route_req_rstrb = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__route_req_valid = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__selected_word_address 
        = (0xfffffffcU & vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source_address_latched);
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__route_req_addr = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__upsample_req_wdata = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__upsample_req_write = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__upsample_req_wstrb = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__upsample_start_ready 
        = ((~ (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__hard_reset)) 
           & (0U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__state)));
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__upsample_req_rstrb = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__upsample_req_valid = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__upsample_req_addr = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__maxpool_req_wdata = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__selected_result_valid = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__conv_result_ready 
        = (((~ (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__hard_reset)) 
            & (2U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__state))) 
           & (0x12U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state)));
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
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__maxpool_req_write = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__maxpool_req_wstrb = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__maxpool_start_ready 
        = ((~ (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__hard_reset)) 
           & (0U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__state)));
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__maxpool_req_rstrb = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__selected_input_lane = 0U;
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__maxpool_req_valid = 0U;
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
        if (((4U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state)) 
             || (8U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state)))) {
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__conv_req_write = 0U;
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__conv_req_rstrb 
                = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__request_strobe_latched;
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__conv_req_valid = 1U;
        } else if ((0x0fU == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state))) {
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__conv_req_write = 1U;
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__conv_req_valid = 1U;
        }
        if ((1U & (~ ((4U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state)) 
                      || (8U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state)))))) {
            if ((0x0fU == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state))) {
                tb_s2a_network_backend_golden__DOT__u_backend__DOT__conv_req_wstrb 
                    = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__request_strobe_latched;
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
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__selected_req_wdata = 0U;
    if ((4U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__state))) {
        if ((1U & (~ ((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__state) 
                      >> 1U)))) {
            if ((1U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__state))) {
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__selected_result_valid 
                    = ((5U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__state)) 
                       & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__upsample_result_ready));
                tb_s2a_network_backend_golden__DOT__u_backend__DOT__selected_req_wdata 
                    = tb_s2a_network_backend_golden__DOT__u_backend__DOT__upsample_req_wdata;
            } else {
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__selected_result_valid 
                    = ((7U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__state)) 
                       & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__route_result_ready));
                tb_s2a_network_backend_golden__DOT__u_backend__DOT__selected_req_wdata 
                    = tb_s2a_network_backend_golden__DOT__u_backend__DOT__route_req_wdata;
            }
        }
    } else if ((2U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__state))) {
        if ((1U & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__state))) {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__selected_result_valid 
                = ((6U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__state)) 
                   & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__maxpool_result_ready));
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__selected_req_wdata 
                = tb_s2a_network_backend_golden__DOT__u_backend__DOT__maxpool_req_wdata;
        } else {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__selected_result_valid 
                = ((0x12U == (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state)) 
                   & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__conv_result_ready));
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__selected_req_wdata 
                = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__request_wdata_latched;
        }
    }
    vlSelfRef.tb_s2a_network_backend_golden__DOT__mem_wdata 
        = tb_s2a_network_backend_golden__DOT__u_backend__DOT__selected_req_wdata;
    if ((0x25U >= (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor))) {
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
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__channel_row_work = 0ULL;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__row_work = 0ULL;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__byte_offset_work = 0ULL;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__address_work[0U] = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__address_work[1U] = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__address_work[2U] = 0U;
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
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__output_height_work 
            = ((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_h[0U])) 
               * (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_upsample_engine__stride)));
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__output_width_work 
            = ((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_w[0U])) 
               * (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_upsample_engine__stride)));
        if ((((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_channel 
               >= vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_c[0U]) 
              | ((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_y)) 
                 >= tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__output_height_work)) 
             | ((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_x)) 
                >= tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__output_width_work))) {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__query_error_code = 1U;
        } else {
            vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_channel 
                = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_channel;
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_y 
                = VL_DIV_III(32, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_y, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_upsample_engine__stride);
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_x 
                = VL_DIV_III(32, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_x, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_upsample_engine__stride);
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__channel_row_work 
                = ((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_channel)) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_h[0U])));
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__row_work 
                = (tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__channel_row_work 
                   + (QData)((IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_y)));
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__byte_offset_work 
                = ((tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__row_work 
                    * (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_w[0U]))) 
                   + (QData)((IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_x)));
            __Vtemp_58[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_base[0U];
            __Vtemp_58[1U] = 0U;
            __Vtemp_58[2U] = 0U;
            __Vtemp_59[0U] = (IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__byte_offset_work);
            __Vtemp_59[1U] = (IData)((tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__byte_offset_work 
                                      >> 0x00000020U));
            __Vtemp_59[2U] = 0U;
            VL_ADD_W(3, __Vtemp_60, __Vtemp_58, __Vtemp_59);
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__address_work[0U] 
                = __Vtemp_60[0U];
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__address_work[1U] 
                = __Vtemp_60[1U];
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__address_work[2U] 
                = (1U & __Vtemp_60[2U]);
            if ((0ULL != (0x00000001ffffffffULL & (
                                                   ((QData)((IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__address_work[2U])) 
                                                    << 0x00000020U) 
                                                   | (QData)((IData)(tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__address_work[1U])))))) {
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__query_error_code = 2U;
            } else {
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_address 
                    = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__address_work[0U];
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
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work[0U] = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work[1U] = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work[2U] = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work[0U] = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work[1U] = 0U;
    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work[2U] = 0U;
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
            = (0x00000001ffffffffULL & (1ULL + VL_DIV_QQQ(33, 
                                                          (0x00000001ffffffffULL 
                                                           & (tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__extent_y 
                                                              - (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_height)))), (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_y)))));
        tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_width_work 
            = (0x00000001ffffffffULL & (1ULL + VL_DIV_QQQ(33, 
                                                          (0x00000001ffffffffULL 
                                                           & (tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__extent_x 
                                                              - (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width)))), (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_x)))));
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
                = ((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_y)) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_y)));
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_x_step 
                = ((QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_x)) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_x)));
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_y_work 
                = (tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__origin_y 
                   + tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_y_step);
            tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_x_work 
                = (tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__origin_x 
                   + tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_x_step);
            if ((0U < (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_count))) {
                tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work 
                    = VL_MODDIV_III(32, (IData)(0U), vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width);
                tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work = 0U;
                tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[0U] 
                    = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_channel;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[0U] 
                    = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_y_work;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[0U] 
                    = (tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_x_work 
                       + VL_EXTENDS_QI(64,32, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work));
                if ((((VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[0U]) 
                       & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[0U], (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_h[0U])))) 
                      & VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[0U])) 
                     & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[0U], (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_w[0U]))))) {
                    __Vtemp_61[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_channel;
                    __Vtemp_61[1U] = 0U;
                    __Vtemp_61[2U] = 0U;
                    __Vtemp_62[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_h[0U];
                    __Vtemp_62[1U] = 0U;
                    __Vtemp_62[2U] = 0U;
                    VL_MUL_W(3, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_61, __Vtemp_62);
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask 
                        = (1U | (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask));
                    __Vtemp_63[0U] = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[0U]);
                    __Vtemp_63[1U] = 0U;
                    __Vtemp_63[2U] = 0U;
                    VL_ADD_W(3, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_63);
                    __Vtemp_64[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_w[0U];
                    __Vtemp_64[1U] = 0U;
                    __Vtemp_64[2U] = 0U;
                    VL_MUL_W(3, __Vtemp_65, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, __Vtemp_64);
                    __Vtemp_66[0U] = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[0U]);
                    __Vtemp_66[1U] = 0U;
                    __Vtemp_66[2U] = 0U;
                    VL_ADD_W(3, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, __Vtemp_65, __Vtemp_66);
                    __Vtemp_68[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_base[0U];
                    __Vtemp_68[1U] = 0U;
                    __Vtemp_68[2U] = 0U;
                    __Vtemp_68[3U] = 0U;
                    __Vtemp_69[0U] = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U];
                    __Vtemp_69[1U] = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U];
                    __Vtemp_69[2U] = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U];
                    __Vtemp_69[3U] = 0U;
                    VL_ADD_W(4, __Vtemp_70, __Vtemp_68, __Vtemp_69);
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U] 
                        = __Vtemp_70[0U];
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                        = __Vtemp_70[1U];
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U] 
                        = __Vtemp_70[2U];
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U] 
                        = (1U & __Vtemp_70[3U]);
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
                tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work 
                    = VL_DIV_III(32, (IData)(1U), vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width);
                tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work 
                    = VL_MODDIV_III(32, (IData)(1U), vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width);
                tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[1U] 
                    = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_channel;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[1U] 
                    = (tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_y_work 
                       + VL_EXTENDS_QI(64,32, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work));
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[1U] 
                    = (tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_x_work 
                       + VL_EXTENDS_QI(64,32, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work));
                if ((((VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[1U]) 
                       & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[1U], (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_h[0U])))) 
                      & VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[1U])) 
                     & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[1U], (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_w[0U]))))) {
                    __Vtemp_75[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_channel;
                    __Vtemp_75[1U] = 0U;
                    __Vtemp_75[2U] = 0U;
                    __Vtemp_76[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_h[0U];
                    __Vtemp_76[1U] = 0U;
                    __Vtemp_76[2U] = 0U;
                    VL_MUL_W(3, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_75, __Vtemp_76);
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask 
                        = (2U | (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask));
                    __Vtemp_77[0U] = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[1U]);
                    __Vtemp_77[1U] = 0U;
                    __Vtemp_77[2U] = 0U;
                    VL_ADD_W(3, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_77);
                    __Vtemp_78[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_w[0U];
                    __Vtemp_78[1U] = 0U;
                    __Vtemp_78[2U] = 0U;
                    VL_MUL_W(3, __Vtemp_79, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, __Vtemp_78);
                    __Vtemp_80[0U] = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[1U]);
                    __Vtemp_80[1U] = 0U;
                    __Vtemp_80[2U] = 0U;
                    VL_ADD_W(3, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, __Vtemp_79, __Vtemp_80);
                    __Vtemp_82[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_base[0U];
                    __Vtemp_82[1U] = 0U;
                    __Vtemp_82[2U] = 0U;
                    __Vtemp_82[3U] = 0U;
                    __Vtemp_83[0U] = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U];
                    __Vtemp_83[1U] = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U];
                    __Vtemp_83[2U] = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U];
                    __Vtemp_83[3U] = 0U;
                    VL_ADD_W(4, __Vtemp_84, __Vtemp_82, __Vtemp_83);
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U] 
                        = __Vtemp_84[0U];
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                        = __Vtemp_84[1U];
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U] 
                        = __Vtemp_84[2U];
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U] 
                        = (1U & __Vtemp_84[3U]);
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
                tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work 
                    = VL_DIV_III(32, (IData)(2U), vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width);
                tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work 
                    = VL_MODDIV_III(32, (IData)(2U), vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width);
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
                    __Vtemp_89[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_channel;
                    __Vtemp_89[1U] = 0U;
                    __Vtemp_89[2U] = 0U;
                    __Vtemp_90[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_h[0U];
                    __Vtemp_90[1U] = 0U;
                    __Vtemp_90[2U] = 0U;
                    VL_MUL_W(3, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_89, __Vtemp_90);
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask 
                        = (4U | (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask));
                    __Vtemp_91[0U] = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[2U]);
                    __Vtemp_91[1U] = 0U;
                    __Vtemp_91[2U] = 0U;
                    VL_ADD_W(3, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_91);
                    __Vtemp_92[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_w[0U];
                    __Vtemp_92[1U] = 0U;
                    __Vtemp_92[2U] = 0U;
                    VL_MUL_W(3, __Vtemp_93, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, __Vtemp_92);
                    __Vtemp_94[0U] = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[2U]);
                    __Vtemp_94[1U] = 0U;
                    __Vtemp_94[2U] = 0U;
                    VL_ADD_W(3, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, __Vtemp_93, __Vtemp_94);
                    __Vtemp_96[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_base[0U];
                    __Vtemp_96[1U] = 0U;
                    __Vtemp_96[2U] = 0U;
                    __Vtemp_96[3U] = 0U;
                    __Vtemp_97[0U] = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U];
                    __Vtemp_97[1U] = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U];
                    __Vtemp_97[2U] = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U];
                    __Vtemp_97[3U] = 0U;
                    VL_ADD_W(4, __Vtemp_98, __Vtemp_96, __Vtemp_97);
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U] 
                        = __Vtemp_98[0U];
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                        = __Vtemp_98[1U];
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U] 
                        = __Vtemp_98[2U];
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U] 
                        = (1U & __Vtemp_98[3U]);
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
                tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work 
                    = VL_DIV_III(32, (IData)(3U), vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width);
                tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work 
                    = VL_MODDIV_III(32, (IData)(3U), vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width);
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
                    __Vtemp_103[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_channel;
                    __Vtemp_103[1U] = 0U;
                    __Vtemp_103[2U] = 0U;
                    __Vtemp_104[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_h[0U];
                    __Vtemp_104[1U] = 0U;
                    __Vtemp_104[2U] = 0U;
                    VL_MUL_W(3, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_103, __Vtemp_104);
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask 
                        = (8U | (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask));
                    __Vtemp_105[0U] = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[3U]);
                    __Vtemp_105[1U] = 0U;
                    __Vtemp_105[2U] = 0U;
                    VL_ADD_W(3, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_105);
                    __Vtemp_106[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_w[0U];
                    __Vtemp_106[1U] = 0U;
                    __Vtemp_106[2U] = 0U;
                    VL_MUL_W(3, __Vtemp_107, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, __Vtemp_106);
                    __Vtemp_108[0U] = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[3U]);
                    __Vtemp_108[1U] = 0U;
                    __Vtemp_108[2U] = 0U;
                    VL_ADD_W(3, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, __Vtemp_107, __Vtemp_108);
                    __Vtemp_110[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_base[0U];
                    __Vtemp_110[1U] = 0U;
                    __Vtemp_110[2U] = 0U;
                    __Vtemp_110[3U] = 0U;
                    __Vtemp_111[0U] = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U];
                    __Vtemp_111[1U] = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U];
                    __Vtemp_111[2U] = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U];
                    __Vtemp_111[3U] = 0U;
                    VL_ADD_W(4, __Vtemp_112, __Vtemp_110, __Vtemp_111);
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U] 
                        = __Vtemp_112[0U];
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                        = __Vtemp_112[1U];
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U] 
                        = __Vtemp_112[2U];
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U] 
                        = (1U & __Vtemp_112[3U]);
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
                tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work 
                    = VL_DIV_III(32, (IData)(4U), vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width);
                tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work 
                    = VL_MODDIV_III(32, (IData)(4U), vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width);
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
                    __Vtemp_117[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_channel;
                    __Vtemp_117[1U] = 0U;
                    __Vtemp_117[2U] = 0U;
                    __Vtemp_118[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_h[0U];
                    __Vtemp_118[1U] = 0U;
                    __Vtemp_118[2U] = 0U;
                    VL_MUL_W(3, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_117, __Vtemp_118);
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask 
                        = (0x00000010U | (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask));
                    __Vtemp_119[0U] = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[4U]);
                    __Vtemp_119[1U] = 0U;
                    __Vtemp_119[2U] = 0U;
                    VL_ADD_W(3, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_119);
                    __Vtemp_120[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_w[0U];
                    __Vtemp_120[1U] = 0U;
                    __Vtemp_120[2U] = 0U;
                    VL_MUL_W(3, __Vtemp_121, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, __Vtemp_120);
                    __Vtemp_122[0U] = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[4U]);
                    __Vtemp_122[1U] = 0U;
                    __Vtemp_122[2U] = 0U;
                    VL_ADD_W(3, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, __Vtemp_121, __Vtemp_122);
                    __Vtemp_124[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_base[0U];
                    __Vtemp_124[1U] = 0U;
                    __Vtemp_124[2U] = 0U;
                    __Vtemp_124[3U] = 0U;
                    __Vtemp_125[0U] = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U];
                    __Vtemp_125[1U] = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U];
                    __Vtemp_125[2U] = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U];
                    __Vtemp_125[3U] = 0U;
                    VL_ADD_W(4, __Vtemp_126, __Vtemp_124, __Vtemp_125);
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U] 
                        = __Vtemp_126[0U];
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                        = __Vtemp_126[1U];
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U] 
                        = __Vtemp_126[2U];
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U] 
                        = (1U & __Vtemp_126[3U]);
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
                tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work 
                    = VL_DIV_III(32, (IData)(5U), vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width);
                tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work 
                    = VL_MODDIV_III(32, (IData)(5U), vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width);
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
                    __Vtemp_131[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_channel;
                    __Vtemp_131[1U] = 0U;
                    __Vtemp_131[2U] = 0U;
                    __Vtemp_132[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_h[0U];
                    __Vtemp_132[1U] = 0U;
                    __Vtemp_132[2U] = 0U;
                    VL_MUL_W(3, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_131, __Vtemp_132);
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask 
                        = (0x00000020U | (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask));
                    __Vtemp_133[0U] = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[5U]);
                    __Vtemp_133[1U] = 0U;
                    __Vtemp_133[2U] = 0U;
                    VL_ADD_W(3, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_133);
                    __Vtemp_134[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_w[0U];
                    __Vtemp_134[1U] = 0U;
                    __Vtemp_134[2U] = 0U;
                    VL_MUL_W(3, __Vtemp_135, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, __Vtemp_134);
                    __Vtemp_136[0U] = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[5U]);
                    __Vtemp_136[1U] = 0U;
                    __Vtemp_136[2U] = 0U;
                    VL_ADD_W(3, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, __Vtemp_135, __Vtemp_136);
                    __Vtemp_138[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_base[0U];
                    __Vtemp_138[1U] = 0U;
                    __Vtemp_138[2U] = 0U;
                    __Vtemp_138[3U] = 0U;
                    __Vtemp_139[0U] = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U];
                    __Vtemp_139[1U] = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U];
                    __Vtemp_139[2U] = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U];
                    __Vtemp_139[3U] = 0U;
                    VL_ADD_W(4, __Vtemp_140, __Vtemp_138, __Vtemp_139);
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U] 
                        = __Vtemp_140[0U];
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                        = __Vtemp_140[1U];
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U] 
                        = __Vtemp_140[2U];
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U] 
                        = (1U & __Vtemp_140[3U]);
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
                    = VL_DIV_III(32, (IData)(6U), vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width);
                tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work 
                    = VL_MODDIV_III(32, (IData)(6U), vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width);
                tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[6U] 
                    = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_channel;
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[6U] 
                    = (tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_y_work 
                       + VL_EXTENDS_QI(64,32, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work));
                vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[6U] 
                    = (tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_x_work 
                       + VL_EXTENDS_QI(64,32, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work));
                if ((((VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[6U]) 
                       & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[6U], (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_h[0U])))) 
                      & VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[6U])) 
                     & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[6U], (QData)((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_w[0U]))))) {
                    __Vtemp_145[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_channel;
                    __Vtemp_145[1U] = 0U;
                    __Vtemp_145[2U] = 0U;
                    __Vtemp_146[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_h[0U];
                    __Vtemp_146[1U] = 0U;
                    __Vtemp_146[2U] = 0U;
                    VL_MUL_W(3, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_145, __Vtemp_146);
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask 
                        = (0x00000040U | (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask));
                    __Vtemp_147[0U] = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[6U]);
                    __Vtemp_147[1U] = 0U;
                    __Vtemp_147[2U] = 0U;
                    VL_ADD_W(3, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_147);
                    __Vtemp_148[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_w[0U];
                    __Vtemp_148[1U] = 0U;
                    __Vtemp_148[2U] = 0U;
                    VL_MUL_W(3, __Vtemp_149, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, __Vtemp_148);
                    __Vtemp_150[0U] = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[6U]);
                    __Vtemp_150[1U] = 0U;
                    __Vtemp_150[2U] = 0U;
                    VL_ADD_W(3, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, __Vtemp_149, __Vtemp_150);
                    __Vtemp_152[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_base[0U];
                    __Vtemp_152[1U] = 0U;
                    __Vtemp_152[2U] = 0U;
                    __Vtemp_152[3U] = 0U;
                    __Vtemp_153[0U] = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U];
                    __Vtemp_153[1U] = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U];
                    __Vtemp_153[2U] = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U];
                    __Vtemp_153[3U] = 0U;
                    VL_ADD_W(4, __Vtemp_154, __Vtemp_152, __Vtemp_153);
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U] 
                        = __Vtemp_154[0U];
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                        = __Vtemp_154[1U];
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U] 
                        = __Vtemp_154[2U];
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U] 
                        = (1U & __Vtemp_154[3U]);
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
                tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work 
                    = VL_DIV_III(32, (IData)(7U), vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width);
                tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work 
                    = VL_MODDIV_III(32, (IData)(7U), vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width);
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
                    __Vtemp_159[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_channel;
                    __Vtemp_159[1U] = 0U;
                    __Vtemp_159[2U] = 0U;
                    __Vtemp_160[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_h[0U];
                    __Vtemp_160[1U] = 0U;
                    __Vtemp_160[2U] = 0U;
                    VL_MUL_W(3, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_159, __Vtemp_160);
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask 
                        = (0x00000080U | (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask));
                    __Vtemp_161[0U] = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[7U]);
                    __Vtemp_161[1U] = 0U;
                    __Vtemp_161[2U] = 0U;
                    VL_ADD_W(3, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_161);
                    __Vtemp_162[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_w[0U];
                    __Vtemp_162[1U] = 0U;
                    __Vtemp_162[2U] = 0U;
                    VL_MUL_W(3, __Vtemp_163, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, __Vtemp_162);
                    __Vtemp_164[0U] = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[7U]);
                    __Vtemp_164[1U] = 0U;
                    __Vtemp_164[2U] = 0U;
                    VL_ADD_W(3, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, __Vtemp_163, __Vtemp_164);
                    __Vtemp_166[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_base[0U];
                    __Vtemp_166[1U] = 0U;
                    __Vtemp_166[2U] = 0U;
                    __Vtemp_166[3U] = 0U;
                    __Vtemp_167[0U] = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U];
                    __Vtemp_167[1U] = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U];
                    __Vtemp_167[2U] = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U];
                    __Vtemp_167[3U] = 0U;
                    VL_ADD_W(4, __Vtemp_168, __Vtemp_166, __Vtemp_167);
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U] 
                        = __Vtemp_168[0U];
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                        = __Vtemp_168[1U];
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U] 
                        = __Vtemp_168[2U];
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U] 
                        = (1U & __Vtemp_168[3U]);
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
                tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work 
                    = VL_DIV_III(32, (IData)(8U), vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width);
                tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work 
                    = VL_MODDIV_III(32, (IData)(8U), vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width);
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
                    __Vtemp_173[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_channel;
                    __Vtemp_173[1U] = 0U;
                    __Vtemp_173[2U] = 0U;
                    __Vtemp_174[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_h[0U];
                    __Vtemp_174[1U] = 0U;
                    __Vtemp_174[2U] = 0U;
                    VL_MUL_W(3, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_173, __Vtemp_174);
                    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask 
                        = (0x00000100U | (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask));
                    __Vtemp_175[0U] = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[8U]);
                    __Vtemp_175[1U] = 0U;
                    __Vtemp_175[2U] = 0U;
                    VL_ADD_W(3, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work, __Vtemp_175);
                    __Vtemp_176[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_w[0U];
                    __Vtemp_176[1U] = 0U;
                    __Vtemp_176[2U] = 0U;
                    VL_MUL_W(3, __Vtemp_177, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work, __Vtemp_176);
                    __Vtemp_178[0U] = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[8U]);
                    __Vtemp_178[1U] = 0U;
                    __Vtemp_178[2U] = 0U;
                    VL_ADD_W(3, tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, __Vtemp_177, __Vtemp_178);
                    __Vtemp_180[0U] = vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_base[0U];
                    __Vtemp_180[1U] = 0U;
                    __Vtemp_180[2U] = 0U;
                    __Vtemp_180[3U] = 0U;
                    __Vtemp_181[0U] = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U];
                    __Vtemp_181[1U] = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U];
                    __Vtemp_181[2U] = tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U];
                    __Vtemp_181[3U] = 0U;
                    VL_ADD_W(4, __Vtemp_182, __Vtemp_180, __Vtemp_181);
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U] 
                        = __Vtemp_182[0U];
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                        = __Vtemp_182[1U];
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U] 
                        = __Vtemp_182[2U];
                    tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U] 
                        = (1U & __Vtemp_182[3U]);
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
    __Vtemp_188[0U] = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__output_offset_work);
    __Vtemp_188[1U] = (IData)((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__output_offset_work 
                               >> 0x00000020U));
    __Vtemp_188[2U] = 0U;
    VL_ADD_W(3, __Vtemp_189, __Vtemp_188, __VdfgRegularize_h6e95ff9d_0_196);
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__output_address_work[0U] 
        = __Vtemp_189[0U];
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__output_address_work[1U] 
        = __Vtemp_189[1U];
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__output_address_work[2U] 
        = (1U & __Vtemp_189[2U]);
    __Vtemp_191[0U] = (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_offset_work);
    __Vtemp_191[1U] = (IData)((vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_offset_work 
                               >> 0x00000020U));
    __Vtemp_191[2U] = 0U;
    VL_ADD_W(3, __Vtemp_192, __Vtemp_191, __VdfgRegularize_h6e95ff9d_0_196);
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_address_work[0U] 
        = __Vtemp_192[0U];
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_address_work[1U] 
        = __Vtemp_192[1U];
    vlSelfRef.tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_address_work[2U] 
        = (1U & __Vtemp_192[2U]);
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
    __Vtemp_193 = VL_MATCHMASKED_I(32, VL_MODDIVS_III(32, vlSelfRef.tb_s2a_network_backend_golden__DOT__class_transfer_index
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
                           [__Vtemp_193]) & (IData)(vlSelfRef.__VdfgRegularize_h6e95ff9d_0_27))
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

void Vtb_s2a_network_backend_golden___024root___timing_ready(Vtb_s2a_network_backend_golden___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_network_backend_golden___024root___timing_ready\n"); );
    Vtb_s2a_network_backend_golden__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if ((2ULL & vlSelfRef.__VactTriggered[0U])) {
        vlSelfRef.__VtrigSched_h43aa703c__0.ready("@(negedge tb_s2a_network_backend_golden.clk)");
    }
}

void Vtb_s2a_network_backend_golden___024root___timing_resume(Vtb_s2a_network_backend_golden___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_network_backend_golden___024root___timing_resume\n"); );
    Vtb_s2a_network_backend_golden__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.__VtrigSched_h43aa703c__0.moveToResumeQueue(
                                                          "@(negedge tb_s2a_network_backend_golden.clk)");
    vlSelfRef.__VtrigSched_h43aa703c__0.resume("@(negedge tb_s2a_network_backend_golden.clk)");
    if ((4ULL & vlSelfRef.__VactTriggered[0U])) {
        vlSelfRef.__VdlySched.resume();
    }
}

void Vtb_s2a_network_backend_golden___024root___trigger_orInto__act_vec_vec(VlUnpacked<QData/*63:0*/, 1> &out, const VlUnpacked<QData/*63:0*/, 1> &in) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_network_backend_golden___024root___trigger_orInto__act_vec_vec\n"); );
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
VL_ATTR_COLD void Vtb_s2a_network_backend_golden___024root___dump_triggers__act(const VlUnpacked<QData/*63:0*/, 1> &triggers, const std::string &tag);
#endif  // VL_DEBUG
bool Vtb_s2a_network_backend_golden___024root___trigger_anySet__act(const VlUnpacked<QData/*63:0*/, 1> &in);
void Vtb_s2a_network_backend_golden___024root___act_comb__TOP__0(Vtb_s2a_network_backend_golden___024root* vlSelf);

bool Vtb_s2a_network_backend_golden___024root___eval_phase__act(Vtb_s2a_network_backend_golden___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_network_backend_golden___024root___eval_phase__act\n"); );
    Vtb_s2a_network_backend_golden__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    CData/*0:0*/ __VactExecute;
    // Body
    {
        // Inlined CFunc: _eval_triggers_vec__act
        vlSelfRef.__VactTriggered[0U] = (QData)((IData)(
                                                        ((vlSelfRef.__VdlySched.awaitingCurrentTime() 
                                                          << 2U) 
                                                         | ((((~ (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__clk)) 
                                                              & (IData)(vlSelfRef.__Vtrigprevexpr___TOP__tb_s2a_network_backend_golden__DOT__clk__0)) 
                                                             << 1U) 
                                                            | ((IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__clk) 
                                                               & (~ (IData)(vlSelfRef.__Vtrigprevexpr___TOP__tb_s2a_network_backend_golden__DOT__clk__0)))))));
        vlSelfRef.__Vtrigprevexpr___TOP__tb_s2a_network_backend_golden__DOT__clk__0 
            = vlSelfRef.tb_s2a_network_backend_golden__DOT__clk;
    }
    Vtb_s2a_network_backend_golden___024root___timing_ready(vlSelf);
    Vtb_s2a_network_backend_golden___024root___trigger_orInto__act_vec_vec(vlSelfRef.__VactTriggered, vlSelfRef.__VactTriggeredAcc);
#ifdef VL_DEBUG
    if (VL_UNLIKELY(vlSymsp->_vm_contextp__->debug())) {
        Vtb_s2a_network_backend_golden___024root___dump_triggers__act(vlSelfRef.__VactTriggered, "act"s);
    }
#endif
    Vtb_s2a_network_backend_golden___024root___trigger_orInto__act_vec_vec(vlSelfRef.__VnbaTriggered, vlSelfRef.__VactTriggered);
    __VactExecute = Vtb_s2a_network_backend_golden___024root___trigger_anySet__act(vlSelfRef.__VactTriggered);
    if (__VactExecute) {
        vlSelfRef.__VactTriggeredAcc.fill(0ULL);
        Vtb_s2a_network_backend_golden___024root___timing_resume(vlSelf);
        {
            // Inlined CFunc: _eval_act
            if ((6ULL & vlSelfRef.__VactTriggered[0U])) {
                Vtb_s2a_network_backend_golden___024root___act_comb__TOP__0(vlSelf);
            }
        }
    }
    return (__VactExecute);
}

bool Vtb_s2a_network_backend_golden___024root___eval_phase__inact(Vtb_s2a_network_backend_golden___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_network_backend_golden___024root___eval_phase__inact\n"); );
    Vtb_s2a_network_backend_golden__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    CData/*0:0*/ __VinactExecute;
    // Body
    __VinactExecute = vlSelfRef.__VdlySched.awaitingZeroDelay();
    if (__VinactExecute) {
        VL_FATAL_MT("D:\\FPGA_Competition\\sim\\tb_s2a_network_backend_golden.sv", 3, "", "ZERODLY: Design Verilated with '--no-sched-zero-delay', but #0 delay executed at runtime");
    }
    return (__VinactExecute);
}

void Vtb_s2a_network_backend_golden___024root___trigger_clear__act(VlUnpacked<QData/*63:0*/, 1> &out) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_network_backend_golden___024root___trigger_clear__act\n"); );
    // Locals
    IData/*31:0*/ n;
    // Body
    n = 0U;
    do {
        out[n] = 0ULL;
        n = ((IData)(1U) + n);
    } while ((1U > n));
}

void Vtb_s2a_network_backend_golden___024root___nba_sequent__TOP__0(Vtb_s2a_network_backend_golden___024root* vlSelf);

bool Vtb_s2a_network_backend_golden___024root___eval_phase__nba(Vtb_s2a_network_backend_golden___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_network_backend_golden___024root___eval_phase__nba\n"); );
    Vtb_s2a_network_backend_golden__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    CData/*0:0*/ __VnbaExecute;
    // Body
    __VnbaExecute = Vtb_s2a_network_backend_golden___024root___trigger_anySet__act(vlSelfRef.__VnbaTriggered);
    if (__VnbaExecute) {
        {
            // Inlined CFunc: _eval_nba
            if ((1ULL & vlSelfRef.__VnbaTriggered[0U])) {
                Vtb_s2a_network_backend_golden___024root___nba_sequent__TOP__0(vlSelf);
            }
            if ((6ULL & vlSelfRef.__VnbaTriggered[0U])) {
                {
                    // Inlined CFunc: _nba_comb__TOP__0
                    vlSelfRef.__VdfgRegularize_h6e95ff9d_0_27 
                        = ((~ (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__hard_reset)) 
                           & (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__buffer_owner_pl));
                }
            }
            if ((7ULL & vlSelfRef.__VnbaTriggered[0U])) {
                Vtb_s2a_network_backend_golden___024root___nba_comb__TOP__1(vlSelf);
            }
        }
        Vtb_s2a_network_backend_golden___024root___trigger_clear__act(vlSelfRef.__VnbaTriggered);
    }
    return (__VnbaExecute);
}

void Vtb_s2a_network_backend_golden___024root___eval(Vtb_s2a_network_backend_golden___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_network_backend_golden___024root___eval\n"); );
    Vtb_s2a_network_backend_golden__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    IData/*31:0*/ __VnbaIterCount;
    // Body
    __VnbaIterCount = 0U;
    do {
        if (VL_UNLIKELY(((0x00002710U < __VnbaIterCount)))) {
#ifdef VL_DEBUG
            Vtb_s2a_network_backend_golden___024root___dump_triggers__act(vlSelfRef.__VnbaTriggered, "nba"s);
#endif
            VL_FATAL_MT("D:\\FPGA_Competition\\sim\\tb_s2a_network_backend_golden.sv", 3, "", "DIDNOTCONVERGE: NBA region did not converge after '--converge-limit' of 10000 tries");
        }
        __VnbaIterCount = ((IData)(1U) + __VnbaIterCount);
        vlSelfRef.__VinactIterCount = 0U;
        do {
            if (VL_UNLIKELY(((0x00002710U < vlSelfRef.__VinactIterCount)))) {
                VL_FATAL_MT("D:\\FPGA_Competition\\sim\\tb_s2a_network_backend_golden.sv", 3, "", "DIDNOTCONVERGE: Inactive region did not converge after '--converge-limit' of 10000 tries");
            }
            vlSelfRef.__VinactIterCount = ((IData)(1U) 
                                           + vlSelfRef.__VinactIterCount);
            vlSelfRef.__VactIterCount = 0U;
            do {
                if (VL_UNLIKELY(((0x00002710U < vlSelfRef.__VactIterCount)))) {
#ifdef VL_DEBUG
                    Vtb_s2a_network_backend_golden___024root___dump_triggers__act(vlSelfRef.__VactTriggered, "act"s);
#endif
                    VL_FATAL_MT("D:\\FPGA_Competition\\sim\\tb_s2a_network_backend_golden.sv", 3, "", "DIDNOTCONVERGE: Active region did not converge after '--converge-limit' of 10000 tries");
                }
                vlSelfRef.__VactIterCount = ((IData)(1U) 
                                             + vlSelfRef.__VactIterCount);
                vlSelfRef.__VactPhaseResult = Vtb_s2a_network_backend_golden___024root___eval_phase__act(vlSelf);
            } while (vlSelfRef.__VactPhaseResult);
            vlSelfRef.__VinactPhaseResult = Vtb_s2a_network_backend_golden___024root___eval_phase__inact(vlSelf);
        } while (vlSelfRef.__VinactPhaseResult);
        vlSelfRef.__VnbaPhaseResult = Vtb_s2a_network_backend_golden___024root___eval_phase__nba(vlSelf);
    } while (vlSelfRef.__VnbaPhaseResult);
}

void Vtb_s2a_network_backend_golden___024root____VbeforeTrig_h43aa703c__0(Vtb_s2a_network_backend_golden___024root* vlSelf, const char* __VeventDescription) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_network_backend_golden___024root____VbeforeTrig_h43aa703c__0\n"); );
    Vtb_s2a_network_backend_golden__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    VlUnpacked<QData/*63:0*/, 1> __VTmp;
    // Body
    __VTmp[0U] = (QData)((IData)((((~ (IData)(vlSelfRef.tb_s2a_network_backend_golden__DOT__clk)) 
                                   & (IData)(vlSelfRef.__Vtrigprevexpr___TOP__tb_s2a_network_backend_golden__DOT__clk__0)) 
                                  << 1U)));
    vlSelfRef.__Vtrigprevexpr___TOP__tb_s2a_network_backend_golden__DOT__clk__0 
        = vlSelfRef.tb_s2a_network_backend_golden__DOT__clk;
    if ((2ULL & __VTmp[0U])) {
        vlSelfRef.__VtrigSched_h43aa703c__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h43aa703c__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h43aa703c__0.ready(__VeventDescription);
    }
    vlSelfRef.__VactTriggeredAcc[0U] = (vlSelfRef.__VactTriggeredAcc[0U] 
                                        | __VTmp[0U]);
}

#ifdef VL_DEBUG
void Vtb_s2a_network_backend_golden___024root___eval_debug_assertions(Vtb_s2a_network_backend_golden___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_network_backend_golden___024root___eval_debug_assertions\n"); );
    Vtb_s2a_network_backend_golden__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
}
#endif  // VL_DEBUG
