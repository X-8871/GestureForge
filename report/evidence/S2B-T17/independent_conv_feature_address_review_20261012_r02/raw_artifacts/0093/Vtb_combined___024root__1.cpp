// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vtb_combined.h for the primary calling header

#include "Vtb_combined__pch.h"

void Vtb_combined___024root___act_sequent__TOP__0(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___act_sequent__TOP__0\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
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

void Vtb_combined___024root___act_sequent__TOP__1(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___act_sequent__TOP__1\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_kernel_area 
        = (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__kernel_height_latched 
           * vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__kernel_width_latched);
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_next_input_channel 
        = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_input_channel;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_next_kernel_y 
        = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_kernel_y;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_next_reduction_index 
        = ((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_reduction_index);
    if ((((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_kernel_x) 
         >= vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__kernel_width_latched)) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_next_kernel_x = 0U;
        if ((((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_kernel_y) 
             >= vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__kernel_height_latched)) {
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_next_kernel_y = 0U;
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_next_input_channel 
                = ((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_input_channel);
        } else {
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_next_kernel_y 
                = ((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_kernel_y);
        }
    } else {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_next_kernel_x 
            = ((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_kernel_x);
    }
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_point_y 
        = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_point_scan_y;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_point_x 
        = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_point_scan_x;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_input_channel 
        = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_input_channel;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_kernel_y 
        = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_kernel_y;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_kernel_x 
        = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_kernel_x;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_reduction_index 
        = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_reduction_index;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_input_y = 0ULL;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_input_x = 0ULL;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_tap_in_bounds = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_feature_index_wide = 0ULL;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_feature_index = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_enable = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_bad_argument = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_overflow = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_feature_byte[0U] = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_weight_byte[0U] = 0U;
}

void Vtb_combined___024root___act_sequent__TOP__2(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___act_sequent__TOP__2\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_product[0U] = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_sum[0U] = 0ULL;
    if ((0U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__group_lane_count)) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_feature_byte[0U] 
            = ((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_weight_byte[0U] 
            = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte[0U];
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_product[0U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_feature_byte[0U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_feature_byte[0U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_weight_byte[0U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_weight_byte[0U])));
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_sum[0U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator[0U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator[0U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_product[0U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_product[0U])))));
        if (((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_feature_byte[0U]) 
                | (0x80U == vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_weight_byte[0U])))) {
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_sum[0U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_sum[0U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_overflow = 1U;
        }
    }
}

void Vtb_combined___024root___act_sequent__TOP__3(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___act_sequent__TOP__3\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_feature_byte[1U] = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_weight_byte[1U] = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_product[1U] = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_sum[1U] = 0ULL;
    if ((1U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__group_lane_count)) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_feature_byte[1U] 
            = ((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_weight_byte[1U] 
            = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte[1U];
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_product[1U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_feature_byte[1U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_feature_byte[1U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_weight_byte[1U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_weight_byte[1U])));
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_sum[1U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator[1U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator[1U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_product[1U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_product[1U])))));
        if (((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_feature_byte[1U]) 
                | (0x80U == vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_weight_byte[1U])))) {
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_sum[1U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_sum[1U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_overflow = 1U;
        }
    }
}

void Vtb_combined___024root___act_sequent__TOP__4(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___act_sequent__TOP__4\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_feature_byte[2U] = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_weight_byte[2U] = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_product[2U] = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_sum[2U] = 0ULL;
    if ((2U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__group_lane_count)) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_feature_byte[2U] 
            = ((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_weight_byte[2U] 
            = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte[2U];
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_product[2U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_feature_byte[2U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_feature_byte[2U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_weight_byte[2U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_weight_byte[2U])));
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_sum[2U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator[2U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator[2U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_product[2U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_product[2U])))));
        if (((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_feature_byte[2U]) 
                | (0x80U == vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_weight_byte[2U])))) {
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_sum[2U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_sum[2U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_overflow = 1U;
        }
    }
}

void Vtb_combined___024root___act_sequent__TOP__5(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___act_sequent__TOP__5\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_feature_byte[3U] = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_weight_byte[3U] = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_product[3U] = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_sum[3U] = 0ULL;
    if ((3U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__group_lane_count)) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_feature_byte[3U] 
            = ((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_weight_byte[3U] 
            = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte[3U];
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_product[3U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_feature_byte[3U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_feature_byte[3U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_weight_byte[3U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_weight_byte[3U])));
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_sum[3U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator[3U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator[3U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_product[3U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_product[3U])))));
        if (((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_feature_byte[3U]) 
                | (0x80U == vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_weight_byte[3U])))) {
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_sum[3U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_sum[3U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_overflow = 1U;
        }
    }
}

void Vtb_combined___024root___act_sequent__TOP__6(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___act_sequent__TOP__6\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_feature_byte[4U] = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_weight_byte[4U] = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_product[4U] = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_sum[4U] = 0ULL;
    if ((4U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__group_lane_count)) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_feature_byte[4U] 
            = ((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_weight_byte[4U] 
            = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte[4U];
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_product[4U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_feature_byte[4U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_feature_byte[4U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_weight_byte[4U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_weight_byte[4U])));
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_sum[4U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator[4U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator[4U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_product[4U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_product[4U])))));
        if (((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_feature_byte[4U]) 
                | (0x80U == vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_weight_byte[4U])))) {
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_sum[4U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_sum[4U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_overflow = 1U;
        }
    }
}

void Vtb_combined___024root___act_sequent__TOP__7(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___act_sequent__TOP__7\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_feature_byte[5U] = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_weight_byte[5U] = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_product[5U] = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_sum[5U] = 0ULL;
    if ((5U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__group_lane_count)) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_feature_byte[5U] 
            = ((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_weight_byte[5U] 
            = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte[5U];
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_product[5U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_feature_byte[5U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_feature_byte[5U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_weight_byte[5U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_weight_byte[5U])));
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_sum[5U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator[5U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator[5U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_product[5U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_product[5U])))));
        if (((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_feature_byte[5U]) 
                | (0x80U == vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_weight_byte[5U])))) {
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_sum[5U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_sum[5U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_overflow = 1U;
        }
    }
}

void Vtb_combined___024root___act_sequent__TOP__8(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___act_sequent__TOP__8\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_feature_byte[6U] = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_weight_byte[6U] = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_product[6U] = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_sum[6U] = 0ULL;
    if ((6U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__group_lane_count)) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_feature_byte[6U] 
            = ((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_weight_byte[6U] 
            = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte[6U];
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_product[6U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_feature_byte[6U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_feature_byte[6U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_weight_byte[6U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_weight_byte[6U])));
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_sum[6U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator[6U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator[6U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_product[6U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_product[6U])))));
        if (((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_feature_byte[6U]) 
                | (0x80U == vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_weight_byte[6U])))) {
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_sum[6U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_sum[6U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_overflow = 1U;
        }
    }
}

void Vtb_combined___024root___act_sequent__TOP__9(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___act_sequent__TOP__9\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_feature_byte[7U] = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_weight_byte[7U] = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_product[7U] = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_sum[7U] = 0ULL;
    if ((7U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__group_lane_count)) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_feature_byte[7U] 
            = ((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_weight_byte[7U] 
            = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte[7U];
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_product[7U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_feature_byte[7U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_feature_byte[7U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_weight_byte[7U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_weight_byte[7U])));
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_sum[7U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator[7U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator[7U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_product[7U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_product[7U])))));
        if (((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_feature_byte[7U]) 
                | (0x80U == vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_weight_byte[7U])))) {
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_sum[7U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_sum[7U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_overflow = 1U;
        }
    }
}

void Vtb_combined___024root___act_sequent__TOP__10(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___act_sequent__TOP__10\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if (((0x0bU == (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__state)) 
         | (0x0cU == (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__state)))) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_point_y 
            = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_point_scan_y;
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_point_x 
            = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_point_scan_x;
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_input_channel = 0U;
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_kernel_y = 0U;
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_kernel_x = 0U;
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_reduction_index = 0U;
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_enable = 1U;
    } else if ((0x0dU == (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__state))) {
        if ((((((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_reduction_index) 
               < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__reduction_count_latched) 
              & (~ (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_bad_argument))) 
             & (~ (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_overflow)))) {
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_point_y 
                = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_point_scan_y;
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_point_x 
                = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_point_scan_x;
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_input_channel 
                = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_next_input_channel;
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_kernel_y 
                = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_next_kernel_y;
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_kernel_x 
                = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_next_kernel_x;
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_reduction_index 
                = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_next_reduction_index;
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_enable = 1U;
        }
    }
    if (((0U != vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_kernel_area) 
         & (0U != vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__tile_width))) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_input_y 
            = (((((QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__tile_start_y)) 
                  * (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__stride_y_latched))) 
                 + ((QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_point_y)) 
                    * (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__stride_y_latched)))) 
                + (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_kernel_y))) 
               - (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__pad_top_latched)));
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_input_x 
            = (((((QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__tile_start_x)) 
                  * (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__stride_x_latched))) 
                 + ((QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_point_x)) 
                    * (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__stride_x_latched)))) 
                + (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_kernel_x))) 
               - (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__pad_left_latched)));
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_tap_in_bounds 
            = (((VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_input_y) 
                 & VL_LTS_IQQ(64, vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_input_y, (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__input_height_latched)))) 
                & VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_input_x)) 
               & VL_LTS_IQQ(64, vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_input_x, (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__input_width_latched))));
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_feature_index_wide 
            = (((((QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_input_channel)) 
                  * vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__patch_plane_bytes) 
                 + ((((QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_point_y)) 
                      * (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__stride_y_latched))) 
                     + (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_kernel_y))) 
                    * (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__patch_width)))) 
                + ((QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_point_x)) 
                   * (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__stride_x_latched)))) 
               + (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_kernel_x)));
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_feature_index 
            = (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_feature_index_wide);
    }
}

void Vtb_combined___024root___act_sequent__TOP__11(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___act_sequent__TOP__11\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    QData/*63:0*/ tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_channel_plane_offset;
    tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_channel_plane_offset = 0;
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

void Vtb_combined___024root___act_sequent__TOP__12(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___act_sequent__TOP__12\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_kernel_area 
        = (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__kernel_height_latched 
           * vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__kernel_width_latched);
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_next_input_channel 
        = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_input_channel;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_next_kernel_y 
        = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_kernel_y;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_next_reduction_index 
        = ((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_reduction_index);
    if ((((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_kernel_x) 
         >= vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__kernel_width_latched)) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_next_kernel_x = 0U;
        if ((((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_kernel_y) 
             >= vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__kernel_height_latched)) {
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_next_kernel_y = 0U;
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_next_input_channel 
                = ((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_input_channel);
        } else {
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_next_kernel_y 
                = ((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_kernel_y);
        }
    } else {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_next_kernel_x 
            = ((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_kernel_x);
    }
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_point_y 
        = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_point_scan_y;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_point_x 
        = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_point_scan_x;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_input_channel 
        = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_input_channel;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_kernel_y 
        = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_kernel_y;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_kernel_x 
        = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_kernel_x;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_reduction_index 
        = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_reduction_index;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_input_y = 0ULL;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_input_x = 0ULL;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_tap_in_bounds = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_feature_index_wide = 0ULL;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_feature_index = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_enable = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_bad_argument = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_overflow = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_feature_byte[0U] = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_weight_byte[0U] = 0U;
}

void Vtb_combined___024root___act_sequent__TOP__13(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___act_sequent__TOP__13\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_product[0U] = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_sum[0U] = 0ULL;
    if ((0U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__group_lane_count)) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_feature_byte[0U] 
            = ((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_weight_byte[0U] 
            = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte[0U];
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_product[0U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_feature_byte[0U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_feature_byte[0U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_weight_byte[0U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_weight_byte[0U])));
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_sum[0U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator[0U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator[0U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_product[0U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_product[0U])))));
        if (((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_feature_byte[0U]) 
                | (0x80U == vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_weight_byte[0U])))) {
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_sum[0U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_sum[0U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_overflow = 1U;
        }
    }
}

void Vtb_combined___024root___act_sequent__TOP__14(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___act_sequent__TOP__14\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_feature_byte[1U] = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_weight_byte[1U] = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_product[1U] = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_sum[1U] = 0ULL;
    if ((1U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__group_lane_count)) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_feature_byte[1U] 
            = ((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_weight_byte[1U] 
            = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte[1U];
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_product[1U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_feature_byte[1U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_feature_byte[1U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_weight_byte[1U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_weight_byte[1U])));
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_sum[1U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator[1U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator[1U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_product[1U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_product[1U])))));
        if (((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_feature_byte[1U]) 
                | (0x80U == vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_weight_byte[1U])))) {
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_sum[1U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_sum[1U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_overflow = 1U;
        }
    }
}

void Vtb_combined___024root___act_sequent__TOP__15(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___act_sequent__TOP__15\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_feature_byte[2U] = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_weight_byte[2U] = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_product[2U] = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_sum[2U] = 0ULL;
    if ((2U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__group_lane_count)) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_feature_byte[2U] 
            = ((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_weight_byte[2U] 
            = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte[2U];
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_product[2U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_feature_byte[2U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_feature_byte[2U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_weight_byte[2U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_weight_byte[2U])));
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_sum[2U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator[2U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator[2U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_product[2U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_product[2U])))));
        if (((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_feature_byte[2U]) 
                | (0x80U == vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_weight_byte[2U])))) {
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_sum[2U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_sum[2U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_overflow = 1U;
        }
    }
}

void Vtb_combined___024root___act_sequent__TOP__16(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___act_sequent__TOP__16\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_feature_byte[3U] = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_weight_byte[3U] = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_product[3U] = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_sum[3U] = 0ULL;
    if ((3U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__group_lane_count)) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_feature_byte[3U] 
            = ((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_weight_byte[3U] 
            = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte[3U];
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_product[3U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_feature_byte[3U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_feature_byte[3U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_weight_byte[3U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_weight_byte[3U])));
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_sum[3U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator[3U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator[3U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_product[3U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_product[3U])))));
        if (((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_feature_byte[3U]) 
                | (0x80U == vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_weight_byte[3U])))) {
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_sum[3U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_sum[3U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_overflow = 1U;
        }
    }
}

void Vtb_combined___024root___act_sequent__TOP__17(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___act_sequent__TOP__17\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_feature_byte[4U] = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_weight_byte[4U] = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_product[4U] = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_sum[4U] = 0ULL;
    if ((4U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__group_lane_count)) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_feature_byte[4U] 
            = ((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_weight_byte[4U] 
            = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte[4U];
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_product[4U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_feature_byte[4U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_feature_byte[4U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_weight_byte[4U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_weight_byte[4U])));
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_sum[4U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator[4U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator[4U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_product[4U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_product[4U])))));
        if (((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_feature_byte[4U]) 
                | (0x80U == vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_weight_byte[4U])))) {
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_sum[4U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_sum[4U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_overflow = 1U;
        }
    }
}

void Vtb_combined___024root___act_sequent__TOP__18(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___act_sequent__TOP__18\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_feature_byte[5U] = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_weight_byte[5U] = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_product[5U] = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_sum[5U] = 0ULL;
    if ((5U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__group_lane_count)) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_feature_byte[5U] 
            = ((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_weight_byte[5U] 
            = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte[5U];
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_product[5U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_feature_byte[5U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_feature_byte[5U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_weight_byte[5U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_weight_byte[5U])));
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_sum[5U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator[5U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator[5U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_product[5U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_product[5U])))));
        if (((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_feature_byte[5U]) 
                | (0x80U == vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_weight_byte[5U])))) {
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_sum[5U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_sum[5U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_overflow = 1U;
        }
    }
}

void Vtb_combined___024root___act_sequent__TOP__19(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___act_sequent__TOP__19\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_feature_byte[6U] = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_weight_byte[6U] = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_product[6U] = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_sum[6U] = 0ULL;
    if ((6U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__group_lane_count)) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_feature_byte[6U] 
            = ((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_weight_byte[6U] 
            = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte[6U];
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_product[6U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_feature_byte[6U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_feature_byte[6U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_weight_byte[6U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_weight_byte[6U])));
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_sum[6U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator[6U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator[6U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_product[6U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_product[6U])))));
        if (((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_feature_byte[6U]) 
                | (0x80U == vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_weight_byte[6U])))) {
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_sum[6U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_sum[6U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_overflow = 1U;
        }
    }
}

void Vtb_combined___024root___act_sequent__TOP__20(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___act_sequent__TOP__20\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_feature_byte[7U] = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_weight_byte[7U] = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_product[7U] = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_sum[7U] = 0ULL;
    if ((7U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__group_lane_count)) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_feature_byte[7U] 
            = ((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_weight_byte[7U] 
            = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte[7U];
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_product[7U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_feature_byte[7U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_feature_byte[7U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_weight_byte[7U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_weight_byte[7U])));
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_sum[7U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator[7U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator[7U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_product[7U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_product[7U])))));
        if (((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_feature_byte[7U]) 
                | (0x80U == vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_weight_byte[7U])))) {
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_sum[7U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_sum[7U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_overflow = 1U;
        }
    }
}

void Vtb_combined___024root___act_sequent__TOP__21(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___act_sequent__TOP__21\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if (((0x0bU == (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__state)) 
         | (0x0cU == (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__state)))) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_point_y 
            = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_point_scan_y;
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_point_x 
            = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_point_scan_x;
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_input_channel = 0U;
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_kernel_y = 0U;
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_kernel_x = 0U;
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_reduction_index = 0U;
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_enable = 1U;
    } else if ((0x0dU == (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__state))) {
        if ((((((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_reduction_index) 
               < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__reduction_count_latched) 
              & (~ (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_bad_argument))) 
             & (~ (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_overflow)))) {
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_point_y 
                = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_point_scan_y;
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_point_x 
                = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_point_scan_x;
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_input_channel 
                = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_next_input_channel;
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_kernel_y 
                = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_next_kernel_y;
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_kernel_x 
                = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_next_kernel_x;
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_reduction_index 
                = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_next_reduction_index;
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_enable = 1U;
        }
    }
    if (((0U != vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_kernel_area) 
         & (0U != vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__tile_width))) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_input_y 
            = (((((QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__tile_start_y)) 
                  * (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__stride_y_latched))) 
                 + ((QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_point_y)) 
                    * (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__stride_y_latched)))) 
                + (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_kernel_y))) 
               - (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__pad_top_latched)));
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_input_x 
            = (((((QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__tile_start_x)) 
                  * (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__stride_x_latched))) 
                 + ((QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_point_x)) 
                    * (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__stride_x_latched)))) 
                + (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_kernel_x))) 
               - (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__pad_left_latched)));
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_tap_in_bounds 
            = (((VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_input_y) 
                 & VL_LTS_IQQ(64, vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_input_y, (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__input_height_latched)))) 
                & VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_input_x)) 
               & VL_LTS_IQQ(64, vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_input_x, (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__input_width_latched))));
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_feature_index_wide 
            = (((((QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_input_channel)) 
                  * vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__patch_plane_bytes) 
                 + ((((QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_point_y)) 
                      * (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__stride_y_latched))) 
                     + (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_kernel_y))) 
                    * (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__patch_width)))) 
                + ((QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_point_x)) 
                   * (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__stride_x_latched)))) 
               + (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_kernel_x)));
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_feature_index 
            = (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_feature_index_wide);
    }
}

void Vtb_combined___024root___act_sequent__TOP__22(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___act_sequent__TOP__22\n"); );
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
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_address_wide 
        = ((QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_base_latched)) 
           + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_byte_offset_wide);
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_address_wide 
        = ((QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_base_latched)) 
           + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_byte_offset_wide);
}

void Vtb_combined___024root___act_comb__TOP__0(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_comb__TOP__1(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_comb__TOP__2(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_comb__TOP__3(Vtb_combined___024root* vlSelf);
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
void Vtb_combined___024root___act_comb__TOP__16(Vtb_combined___024root* vlSelf);
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
void Vtb_combined___024root___act_comb__TOP__27(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_comb__TOP__28(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_comb__TOP__29(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_comb__TOP__30(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___eval_act__1(Vtb_combined___024root* vlSelf);

void Vtb_combined___024root___eval_act(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___eval_act\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    {
        // Inlined CFunc: _eval_act__0
        if ((0x0000000000000013ULL & vlSelfRef.__VactTriggered[0U])) {
            Vtb_combined___024root___act_comb__TOP__0(vlSelf);
            Vtb_combined___024root___act_comb__TOP__1(vlSelf);
            Vtb_combined___024root___act_comb__TOP__2(vlSelf);
            Vtb_combined___024root___act_comb__TOP__3(vlSelf);
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
            Vtb_combined___024root___act_comb__TOP__16(vlSelf);
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
            Vtb_combined___024root___act_comb__TOP__27(vlSelf);
            Vtb_combined___024root___act_comb__TOP__28(vlSelf);
            Vtb_combined___024root___act_comb__TOP__29(vlSelf);
            Vtb_combined___024root___act_comb__TOP__30(vlSelf);
            {
                // Inlined CFunc: _act_comb__TOP__31
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_cancel 
                    = vlSelfRef.tb_combined__DOT__boundary_test__DOT__candidate_backend_cancel;
            }
        }
    }
    Vtb_combined___024root___eval_act__1(vlSelf);
}

void Vtb_combined___024root___eval_act__1(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___eval_act__1\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if ((0x0000000000000010ULL & vlSelfRef.__VactTriggered[0U])) {
        Vtb_combined___024root___act_sequent__TOP__0(vlSelf);
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
        Vtb_combined___024root___act_sequent__TOP__11(vlSelf);
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
        Vtb_combined___024root___act_sequent__TOP__22(vlSelf);
    }
}

void Vtb_combined___024root___nba_sequent__TOP__0(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_sequent__TOP__0\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte__v0 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte__v1 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte__v2 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte__v3 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte__v4 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte__v5 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte__v6 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte__v7 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte__v0 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte__v1 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte__v2 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte__v3 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte__v4 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte__v5 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte__v6 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte__v7 = 0U;
    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__output_point_index 
        = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_point_index;
    vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__output_block__v0 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_patch__v0 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_patch__v1 = 0U;
    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_reduction_index 
        = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_reduction_index;
    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__output_point_scan_x 
        = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_point_scan_x;
    vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_mq_parameter__v0 = 0U;
    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__output_group_base 
        = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_group_base;
}

void Vtb_combined___024root___nba_sequent__TOP__1(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_sequent__TOP__1\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_point_scan_x 
        = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_point_scan_x;
    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_reduction_index 
        = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_reduction_index;
    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_kernel_y 
        = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_kernel_y;
    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_kernel_x 
        = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_kernel_x;
    vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v0 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v1 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v2 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v3 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v4 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v5 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v6 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v7 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v8 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v9 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v16 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v17 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0 = 0U;
    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_point_index 
        = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_point_index;
    vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_block__v0 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_patch__v0 = 0U;
}

void Vtb_combined___024root___nba_sequent__TOP__2(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_sequent__TOP__2\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_patch__v1 = 0U;
    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_reduction_index 
        = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_reduction_index;
    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_point_scan_x 
        = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_point_scan_x;
    vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_mq_parameter__v0 = 0U;
    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_group_base 
        = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_group_base;
    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_point_scan_x 
        = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_point_scan_x;
    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_reduction_index 
        = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_reduction_index;
    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_kernel_y 
        = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_kernel_y;
    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_kernel_x 
        = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_kernel_x;
    vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v0 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v1 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v2 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v3 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v4 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v5 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v6 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v7 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v8 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v9 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v16 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v17 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0 = 0U;
}

void Vtb_combined___024root___nba_sequent__TOP__3(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_sequent__TOP__3\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0 = 0U;
    if (((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_enable) 
         & (0U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__group_lane_count))) {
        vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte__v0 
            = ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_reduction_index))
                ? vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory
               [(0x00001fffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_reduction_index)]
                : 0U);
        vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte__v0 = 1U;
    }
    if (((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_enable) 
         & (1U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__group_lane_count))) {
        vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte__v1 
            = ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_reduction_index))
                ? vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory
               [(0x00001fffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_reduction_index)]
                : 0U);
        vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte__v1 = 1U;
    }
    if (((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_enable) 
         & (2U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__group_lane_count))) {
        vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte__v2 
            = ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_reduction_index))
                ? vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory
               [(0x00001fffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_reduction_index)]
                : 0U);
        vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte__v2 = 1U;
    }
    if (((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_enable) 
         & (3U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__group_lane_count))) {
        vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte__v3 
            = ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_reduction_index))
                ? vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory
               [(0x00001fffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_reduction_index)]
                : 0U);
        vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte__v3 = 1U;
    }
}

void Vtb_combined___024root___nba_sequent__TOP__4(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_sequent__TOP__4\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if (((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_enable) 
         & (4U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__group_lane_count))) {
        vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte__v4 
            = ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_reduction_index))
                ? vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory
               [(0x00001fffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_reduction_index)]
                : 0U);
        vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte__v4 = 1U;
    }
    if (((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_enable) 
         & (5U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__group_lane_count))) {
        vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte__v5 
            = ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_reduction_index))
                ? vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory
               [(0x00001fffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_reduction_index)]
                : 0U);
        vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte__v5 = 1U;
    }
    if (((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_enable) 
         & (6U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__group_lane_count))) {
        vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte__v6 
            = ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_reduction_index))
                ? vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory
               [(0x00001fffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_reduction_index)]
                : 0U);
        vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte__v6 = 1U;
    }
    if (((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_enable) 
         & (7U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__group_lane_count))) {
        vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte__v7 
            = ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_reduction_index))
                ? vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory
               [(0x00001fffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_reduction_index)]
                : 0U);
        vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte__v7 = 1U;
    }
    if (((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_enable) 
         & (0U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__group_lane_count))) {
        vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte__v0 
            = ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_reduction_index))
                ? vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory
               [(0x00001fffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_reduction_index)]
                : 0U);
        vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte__v0 = 1U;
    }
}

void Vtb_combined___024root___nba_sequent__TOP__5(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_sequent__TOP__5\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if (((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_enable) 
         & (1U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__group_lane_count))) {
        vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte__v1 
            = ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_reduction_index))
                ? vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory
               [(0x00001fffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_reduction_index)]
                : 0U);
        vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte__v1 = 1U;
    }
    if (((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_enable) 
         & (2U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__group_lane_count))) {
        vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte__v2 
            = ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_reduction_index))
                ? vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory
               [(0x00001fffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_reduction_index)]
                : 0U);
        vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte__v2 = 1U;
    }
    if (((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_enable) 
         & (3U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__group_lane_count))) {
        vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte__v3 
            = ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_reduction_index))
                ? vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory
               [(0x00001fffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_reduction_index)]
                : 0U);
        vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte__v3 = 1U;
    }
    if (((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_enable) 
         & (4U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__group_lane_count))) {
        vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte__v4 
            = ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_reduction_index))
                ? vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory
               [(0x00001fffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_reduction_index)]
                : 0U);
        vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte__v4 = 1U;
    }
    if (((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_enable) 
         & (5U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__group_lane_count))) {
        vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte__v5 
            = ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_reduction_index))
                ? vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory
               [(0x00001fffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_reduction_index)]
                : 0U);
        vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte__v5 = 1U;
    }
}

void Vtb_combined___024root___nba_sequent__TOP__6(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_sequent__TOP__6\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if (((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_enable) 
         & (6U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__group_lane_count))) {
        vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte__v6 
            = ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_reduction_index))
                ? vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory
               [(0x00001fffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_reduction_index)]
                : 0U);
        vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte__v6 = 1U;
    }
    if (((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_enable) 
         & (7U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__group_lane_count))) {
        vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte__v7 
            = ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_reduction_index))
                ? vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory
               [(0x00001fffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_reduction_index)]
                : 0U);
        vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte__v7 = 1U;
    }
    if ((((((9U == (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__state)) 
            & (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__v_rsp_valid)) 
           & (0U == (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__mapped_response_error))) 
          & (0U == vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_lane_index)) 
         & (0x00001200U > vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_reduction_index))) {
        if ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_reduction_index))) {
            vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0 = 0U;
            vlSelfRef.__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0 
                = (0x00001fffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_reduction_index);
            vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0 = 1U;
        }
    }
    if ((((((9U == (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__state)) 
            & (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__v_rsp_valid)) 
           & (0U == (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__mapped_response_error))) 
          & (1U == vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_lane_index)) 
         & (0x00001200U > vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_reduction_index))) {
        if ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_reduction_index))) {
            vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0 = 0U;
            vlSelfRef.__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0 
                = (0x00001fffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_reduction_index);
            vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0 = 1U;
        }
    }
}

void Vtb_combined___024root___nba_sequent__TOP__7(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_sequent__TOP__7\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if ((((((9U == (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__state)) 
            & (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__v_rsp_valid)) 
           & (0U == (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__mapped_response_error))) 
          & (2U == vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_lane_index)) 
         & (0x00001200U > vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_reduction_index))) {
        if ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_reduction_index))) {
            vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0 = 0U;
            vlSelfRef.__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0 
                = (0x00001fffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_reduction_index);
            vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0 = 1U;
        }
    }
    if ((((((9U == (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__state)) 
            & (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__v_rsp_valid)) 
           & (0U == (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__mapped_response_error))) 
          & (3U == vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_lane_index)) 
         & (0x00001200U > vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_reduction_index))) {
        if ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_reduction_index))) {
            vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0 = 0U;
            vlSelfRef.__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0 
                = (0x00001fffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_reduction_index);
            vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0 = 1U;
        }
    }
    if ((((((9U == (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__state)) 
            & (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__v_rsp_valid)) 
           & (0U == (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__mapped_response_error))) 
          & (4U == vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_lane_index)) 
         & (0x00001200U > vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_reduction_index))) {
        if ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_reduction_index))) {
            vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0 = 0U;
            vlSelfRef.__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0 
                = (0x00001fffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_reduction_index);
            vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0 = 1U;
        }
    }
}

void Vtb_combined___024root___nba_sequent__TOP__8(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_sequent__TOP__8\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if ((((((9U == (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__state)) 
            & (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__v_rsp_valid)) 
           & (0U == (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__mapped_response_error))) 
          & (5U == vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_lane_index)) 
         & (0x00001200U > vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_reduction_index))) {
        if ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_reduction_index))) {
            vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0 = 0U;
            vlSelfRef.__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0 
                = (0x00001fffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_reduction_index);
            vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0 = 1U;
        }
    }
    if ((((((9U == (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__state)) 
            & (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__v_rsp_valid)) 
           & (0U == (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__mapped_response_error))) 
          & (6U == vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_lane_index)) 
         & (0x00001200U > vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_reduction_index))) {
        if ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_reduction_index))) {
            vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0 = 0U;
            vlSelfRef.__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0 
                = (0x00001fffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_reduction_index);
            vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0 = 1U;
        }
    }
    if ((((((9U == (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__state)) 
            & (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__v_rsp_valid)) 
           & (0U == (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__mapped_response_error))) 
          & (7U == vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_lane_index)) 
         & (0x00001200U > vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_reduction_index))) {
        if ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_reduction_index))) {
            vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0 = 0U;
            vlSelfRef.__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0 
                = (0x00001fffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_reduction_index);
            vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0 = 1U;
        }
    }
}

void Vtb_combined___024root___nba_sequent__TOP__9(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_sequent__TOP__9\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if ((((((9U == (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__state)) 
            & (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__v_rsp_valid)) 
           & (0U == (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__mapped_response_error))) 
          & (0U == vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_lane_index)) 
         & (0x00001200U > vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_reduction_index))) {
        if ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_reduction_index))) {
            vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0 = 0U;
            vlSelfRef.__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0 
                = (0x00001fffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_reduction_index);
            vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0 = 1U;
        }
    }
    if ((((((9U == (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__state)) 
            & (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__v_rsp_valid)) 
           & (0U == (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__mapped_response_error))) 
          & (1U == vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_lane_index)) 
         & (0x00001200U > vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_reduction_index))) {
        if ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_reduction_index))) {
            vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0 = 0U;
            vlSelfRef.__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0 
                = (0x00001fffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_reduction_index);
            vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0 = 1U;
        }
    }
    if ((((((9U == (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__state)) 
            & (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__v_rsp_valid)) 
           & (0U == (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__mapped_response_error))) 
          & (2U == vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_lane_index)) 
         & (0x00001200U > vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_reduction_index))) {
        if ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_reduction_index))) {
            vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0 = 0U;
            vlSelfRef.__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0 
                = (0x00001fffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_reduction_index);
            vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0 = 1U;
        }
    }
}

void Vtb_combined___024root___nba_sequent__TOP__10(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_sequent__TOP__10\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if ((((((9U == (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__state)) 
            & (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__v_rsp_valid)) 
           & (0U == (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__mapped_response_error))) 
          & (3U == vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_lane_index)) 
         & (0x00001200U > vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_reduction_index))) {
        if ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_reduction_index))) {
            vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0 = 0U;
            vlSelfRef.__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0 
                = (0x00001fffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_reduction_index);
            vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0 = 1U;
        }
    }
    if ((((((9U == (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__state)) 
            & (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__v_rsp_valid)) 
           & (0U == (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__mapped_response_error))) 
          & (4U == vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_lane_index)) 
         & (0x00001200U > vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_reduction_index))) {
        if ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_reduction_index))) {
            vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0 = 0U;
            vlSelfRef.__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0 
                = (0x00001fffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_reduction_index);
            vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0 = 1U;
        }
    }
    if ((((((9U == (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__state)) 
            & (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__v_rsp_valid)) 
           & (0U == (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__mapped_response_error))) 
          & (5U == vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_lane_index)) 
         & (0x00001200U > vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_reduction_index))) {
        if ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_reduction_index))) {
            vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0 = 0U;
            vlSelfRef.__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0 
                = (0x00001fffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_reduction_index);
            vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0 = 1U;
        }
    }
}

void Vtb_combined___024root___nba_sequent__TOP__11(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_sequent__TOP__11\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if ((((((9U == (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__state)) 
            & (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__v_rsp_valid)) 
           & (0U == (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__mapped_response_error))) 
          & (6U == vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_lane_index)) 
         & (0x00001200U > vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_reduction_index))) {
        if ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_reduction_index))) {
            vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0 = 0U;
            vlSelfRef.__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0 
                = (0x00001fffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_reduction_index);
            vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0 = 1U;
        }
    }
    if ((((((9U == (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__state)) 
            & (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__v_rsp_valid)) 
           & (0U == (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__mapped_response_error))) 
          & (7U == vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_lane_index)) 
         & (0x00001200U > vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_reduction_index))) {
        if ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_reduction_index))) {
            vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0 = 0U;
            vlSelfRef.__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0 
                = (0x00001fffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_reduction_index);
            vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0 = 1U;
        }
    }
    if (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_enable) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_read_in_bounds 
            = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_tap_in_bounds;
    }
}

void Vtb_combined___024root___nba_sequent__TOP__12(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_sequent__TOP__12\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_enable) {
        if (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_tap_in_bounds) {
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_read_in_bounds = 1U;
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_read_data 
                = ((0xc7ffU >= (0x0000ffffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_feature_index))
                    ? vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_patch
                   [(0x0000ffffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_read_feature_index)]
                    : 0U);
        } else {
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_read_in_bounds = 0U;
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_read_data = 0U;
        }
    }
    if (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_enable) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_read_data 
            = ((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_tap_in_bounds)
                ? ((0xc7ffU >= (0x0000ffffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_feature_index))
                    ? vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_patch
                   [(0x0000ffffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_read_feature_index)]
                    : 0U) : 0U);
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte__v0) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte[0U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte__v0;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte__v1) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte[1U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte__v1;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte__v2) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte[2U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte__v2;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte__v3) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte[3U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte__v3;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte__v4) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte[4U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte__v4;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte__v5) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte[5U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte__v5;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte__v6) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte[6U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte__v6;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte__v7) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte[7U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_read_byte__v7;
    }
}

void Vtb_combined___024root___nba_sequent__TOP__13(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_sequent__TOP__13\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if (vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte__v0) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte[0U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte__v0;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte__v1) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte[1U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte__v1;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte__v2) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte[2U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte__v2;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte__v3) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte[3U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte__v3;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte__v4) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte[4U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte__v4;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte__v5) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte[5U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte__v5;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte__v6) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte[6U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte__v6;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte__v7) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte[7U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_read_byte__v7;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory[vlSelfRef.__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory[vlSelfRef.__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory[vlSelfRef.__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory[vlSelfRef.__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory[vlSelfRef.__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory[vlSelfRef.__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory[vlSelfRef.__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0;
    }
}

void Vtb_combined___024root___nba_sequent__TOP__14(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_sequent__TOP__14\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if (vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory[vlSelfRef.__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory[vlSelfRef.__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory[vlSelfRef.__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory[vlSelfRef.__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory[vlSelfRef.__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory[vlSelfRef.__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory[vlSelfRef.__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory[vlSelfRef.__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory[vlSelfRef.__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0;
    }
    if (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_advance) {
        if ((((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_x) 
             >= vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__patch_width)) {
            if ((((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_y) 
                 >= vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__patch_height)) {
                vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_channel 
                    = ((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_channel);
                vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_channel = 0xffffffffU;
                vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_y = 0U;
            } else {
                vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_y 
                    = ((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_y);
            }
            vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_y = 0xffffffffU;
            vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_x = 0U;
        } else {
            vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_x 
                = ((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_x);
        }
        vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_x = 0xffffffffU;
    }
}

void Vtb_combined___024root___nba_sequent__TOP__15(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_sequent__TOP__15\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    VlWide<4>/*127:0*/ __Vtemp_1;
    VlWide<4>/*127:0*/ __Vtemp_2;
    // Body
    if ((0x00000010U & (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__state))) {
        if ((8U & (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__state))) {
            vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__state = 0x13U;
            vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__state = 0x1fU;
        } else if ((4U & (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__state))) {
            vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__state = 0x13U;
            vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__state = 0x1fU;
        } else if ((2U & (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__state))) {
            if ((1U & (~ (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__state)))) {
                if ((((IData)(8U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_group_base) 
                     < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_channels_latched)) {
                    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__output_group_base 
                        = ((IData)(8U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_group_base);
                    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__state = 6U;
                } else if (((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__tile_start_x 
                             + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__tile_width) 
                            < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_width_latched)) {
                    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__output_group_base = 0U;
                    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__tile_start_x 
                        = ((IData)(8U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__tile_start_x);
                    vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__tile_start_x = 0xffffffffU;
                    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__state = 2U;
                } else if (((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__tile_start_y 
                             + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__tile_height) 
                            < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_height_latched)) {
                    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__output_group_base = 0U;
                    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__tile_start_x = 0U;
                    vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__tile_start_x = 0xffffffffU;
                    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__tile_start_y 
                        = ((IData)(8U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__tile_start_y);
                    vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__tile_start_y = 0xffffffffU;
                    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__state = 2U;
                } else {
                    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__state = 0x13U;
                }
                vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__state = 0x1fU;
            }
        } else if ((1U & (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__state))) {
            if (vlSelfRef.tb_combined__DOT__feature_test__DOT__v_rsp_valid) {
                if ((0U != (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__mapped_response_error))) {
                    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__state = 0x13U;
                } else {
                    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__output_point_index 
                        = ((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_point_index);
                    if ((((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_point_scan_x) 
                         >= vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__tile_width)) {
                        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_point_scan_y 
                            = ((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_point_scan_y);
                        vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__output_point_scan_x = 0U;
                    } else {
                        vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__output_point_scan_x 
                            = ((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_point_scan_x);
                    }
                    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__state = 0x0fU;
                }
                vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__state = 0x1fU;
            }
        }
    } else if ((8U & (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__state))) {
        if ((4U & (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__state))) {
            if ((2U & (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__state))) {
                if ((1U & (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__state))) {
                    if ((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_lane_index 
                         >= vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__group_lane_count)) {
                        vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__state = 0x12U;
                        vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__state = 0x1fU;
                    } else if ((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_point_index 
                                >= vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__tile_point_count)) {
                        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_lane_index 
                            = ((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_lane_index);
                        vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__output_point_index = 0U;
                        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_point_scan_y = 0U;
                        vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__output_point_scan_x = 0U;
                    } else {
                        __Vtemp_1[0U] = (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_byte_offset_wide);
                        __Vtemp_1[1U] = (IData)((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_byte_offset_wide 
                                                 >> 0x00000020U));
                        __Vtemp_1[2U] = 0U;
                        __Vtemp_1[3U] = 0U;
                        __Vtemp_2[0U] = (IData)(((QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_width_latched)) 
                                                 * (QData)((IData)(
                                                                   ((QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_height_latched)) 
                                                                    * (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_channels_latched)))))));
                        __Vtemp_2[1U] = (IData)((((QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_width_latched)) 
                                                  * (QData)((IData)(
                                                                    ((QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_height_latched)) 
                                                                     * (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_channels_latched)))))) 
                                                 >> 0x00000020U));
                        __Vtemp_2[2U] = 0U;
                        __Vtemp_2[3U] = 0U;
                        if (((0x00000000ffffffffULL 
                              < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_address_wide) 
                             | VL_GTE_W(4, __Vtemp_1, __Vtemp_2))) {
                            vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__state = 0x13U;
                        } else {
                            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__request_strobe_latched 
                                = (0x0000000fU & ((IData)(1U) 
                                                  << 
                                                  (3U 
                                                   & (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_address_wide))));
                            vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__state = 0x10U;
                        }
                        vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__state = 0x1fU;
                    }
                } else {
                    if ((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_lane_index 
                         < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__group_lane_count)) {
                        vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__output_block__v0 
                            = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__requantized_value;
                        vlSelfRef.__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_old__DOT__output_block__v0 
                            = (0x000001ffU & ((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_lane_index 
                                               << 6U) 
                                              + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_point_index));
                        vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__output_block__v0 = 1U;
                    }
                    if ((((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_lane_index) 
                         >= vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__group_lane_count)) {
                        if ((((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_point_index) 
                             >= vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__tile_point_count)) {
                            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_lane_index = 0U;
                            vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__output_point_index = 0U;
                            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_point_scan_y = 0U;
                            vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__output_point_scan_x = 0U;
                            vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__state = 0x0fU;
                        } else {
                            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_point_index 
                                = ((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_point_index);
                            if ((((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_point_scan_x) 
                                 >= vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__tile_width)) {
                                vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_point_scan_y 
                                    = ((IData)(1U) 
                                       + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_point_scan_y);
                                vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_point_scan_x = 0U;
                            } else {
                                vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_point_scan_x 
                                    = ((IData)(1U) 
                                       + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_point_scan_x);
                            }
                            vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_reduction_index = 0U;
                            vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__state = 0x0cU;
                        }
                        vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__state = 0x1fU;
                    } else {
                        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_lane_index 
                            = ((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_lane_index);
                    }
                }
            } else if ((1U & (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__state))) {
                if (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_bad_argument) {
                    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__state = 0x13U;
                    vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__state = 0x1fU;
                } else if (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_overflow) {
                    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__state = 0x13U;
                    vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__state = 0x1fU;
                } else {
                    if ((0U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__group_lane_count)) {
                        vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v0 
                            = (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_sum[0U]);
                        vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v0 = 1U;
                    }
                    if ((((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_reduction_index) 
                         >= vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__reduction_count_latched)) {
                        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_lane_index = 0U;
                        vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__state = 0x0eU;
                        vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__state = 0x1fU;
                    } else {
                        vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_reduction_index 
                            = ((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_reduction_index);
                        if ((((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_kernel_x) 
                             >= vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__kernel_width_latched)) {
                            if ((((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_kernel_y) 
                                 >= vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__kernel_height_latched)) {
                                vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_input_channel 
                                    = ((IData)(1U) 
                                       + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_input_channel);
                                vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_kernel_y = 0U;
                            } else {
                                vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_kernel_y 
                                    = ((IData)(1U) 
                                       + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_kernel_y);
                            }
                            vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_kernel_x = 0U;
                        } else {
                            vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_kernel_x 
                                = ((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_kernel_x);
                        }
                    }
                    if ((1U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__group_lane_count)) {
                        vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v1 
                            = (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_sum[1U]);
                        vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v1 = 1U;
                    }
                    if ((2U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__group_lane_count)) {
                        vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v2 
                            = (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_sum[2U]);
                        vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v2 = 1U;
                    }
                    if ((3U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__group_lane_count)) {
                        vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v3 
                            = (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_sum[3U]);
                        vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v3 = 1U;
                    }
                    if ((4U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__group_lane_count)) {
                        vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v4 
                            = (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_sum[4U]);
                        vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v4 = 1U;
                    }
                    if ((5U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__group_lane_count)) {
                        vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v5 
                            = (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_sum[5U]);
                        vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v5 = 1U;
                    }
                    if ((6U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__group_lane_count)) {
                        vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v6 
                            = (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_sum[6U]);
                        vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v6 = 1U;
                    }
                    if ((7U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__group_lane_count)) {
                        vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v7 
                            = (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_sum[7U]);
                        vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v7 = 1U;
                    }
                }
            } else {
                vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_input_channel = 0U;
                vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_kernel_y = 0U;
                vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_kernel_x = 0U;
                vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v8 
                    = ((0U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__group_lane_count)
                        ? vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_bias[0U]
                        : 0U);
                vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v8 = 1U;
                vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_reduction_index = 0U;
                vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__state = 0x0dU;
                vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__state = 0x1fU;
                vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v9 
                    = ((1U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__group_lane_count)
                        ? vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_bias[1U]
                        : 0U);
                vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v9 = 1U;
                vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v10 
                    = ((2U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__group_lane_count)
                        ? vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_bias[2U]
                        : 0U);
                vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v11 
                    = ((3U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__group_lane_count)
                        ? vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_bias[3U]
                        : 0U);
                vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v12 
                    = ((4U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__group_lane_count)
                        ? vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_bias[4U]
                        : 0U);
                vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v13 
                    = ((5U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__group_lane_count)
                        ? vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_bias[5U]
                        : 0U);
                vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v14 
                    = ((6U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__group_lane_count)
                        ? vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_bias[6U]
                        : 0U);
                vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v15 
                    = ((7U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__group_lane_count)
                        ? vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_bias[7U]
                        : 0U);
            }
        } else if ((2U & (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__state))) {
            if ((1U & (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__state))) {
                vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_input_channel = 0U;
                vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_kernel_y = 0U;
                vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_kernel_x = 0U;
                vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_point_index = 0U;
                vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v16 
                    = ((0U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__group_lane_count)
                        ? vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_bias[0U]
                        : 0U);
                vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v16 = 1U;
                vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_reduction_index = 0U;
                vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__state = 0x0dU;
                vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__state = 0x1fU;
                vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v17 
                    = ((1U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__group_lane_count)
                        ? vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_bias[1U]
                        : 0U);
                vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v17 = 1U;
                vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v18 
                    = ((2U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__group_lane_count)
                        ? vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_bias[2U]
                        : 0U);
                vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v19 
                    = ((3U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__group_lane_count)
                        ? vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_bias[3U]
                        : 0U);
                vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v20 
                    = ((4U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__group_lane_count)
                        ? vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_bias[4U]
                        : 0U);
                vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v21 
                    = ((5U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__group_lane_count)
                        ? vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_bias[5U]
                        : 0U);
                vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v22 
                    = ((6U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__group_lane_count)
                        ? vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_bias[6U]
                        : 0U);
                vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v23 
                    = ((7U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__group_lane_count)
                        ? vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_bias[7U]
                        : 0U);
            } else if (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__mq_prefetch_invalid) {
                vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__state = 0x13U;
                vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__state = 0x1fU;
            } else {
                vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_mq_parameter__v0[0U] 
                    = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__mq_prefetch_parameter[0U];
                vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_mq_parameter__v0[1U] 
                    = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__mq_prefetch_parameter[1U];
                vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_mq_parameter__v0[2U] 
                    = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__mq_prefetch_parameter[2U];
                vlSelfRef.__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_mq_parameter__v0 
                    = (7U & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__mq_prefetch_lane);
                vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_mq_parameter__v0 = 1U;
                vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_bias__v0 
                    = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__mq_prefetch_bias;
                vlSelfRef.__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_bias__v0 
                    = (7U & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__mq_prefetch_lane);
                if ((((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__mq_prefetch_lane) 
                     >= vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__group_lane_count)) {
                    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__state = 0x0bU;
                    vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__state = 0x1fU;
                } else {
                    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__mq_prefetch_lane 
                        = ((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__mq_prefetch_lane);
                }
            }
        } else if ((1U & (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__state))) {
            if (vlSelfRef.tb_combined__DOT__feature_test__DOT__v_rsp_valid) {
                if ((0U != (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__mapped_response_error))) {
                    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__state = 0x13U;
                } else {
                    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_reduction_index 
                        = ((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_reduction_index);
                    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__state = 7U;
                }
                vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__state = 0x1fU;
            }
        }
    } else if ((4U & (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__state))) {
        if ((2U & (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__state))) {
            if ((1U & (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__state))) {
                if ((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_lane_index 
                     >= vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__group_lane_count)) {
                    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__mq_prefetch_lane = 0U;
                    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__state = 0x0aU;
                    vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__state = 0x1fU;
                } else if ((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_reduction_index 
                            >= vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__reduction_count_latched)) {
                    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_lane_index 
                        = ((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_lane_index);
                    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_reduction_index = 0U;
                } else {
                    if ((0x00000000ffffffffULL < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_source_address_wide)) {
                        vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__state = 0x13U;
                    } else {
                        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__request_strobe_latched 
                            = (0x0000000fU & ((IData)(1U) 
                                              << (3U 
                                                  & (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_source_address_wide))));
                        vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__state = 8U;
                    }
                    vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__state = 0x1fU;
                }
            } else {
                if ((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_group_base 
                     >= vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_channels_latched)) {
                    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__state = 0x12U;
                } else {
                    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_point_scan_y = 0U;
                    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_point_scan_x = 0U;
                    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_lane_index = 0U;
                    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_reduction_index = 0U;
                    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__mq_prefetch_lane = 0U;
                    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__group_lane_count 
                        = ((8U <= (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_channels_latched 
                                   - vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_group_base))
                            ? 8U : (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_channels_latched 
                                    - vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_group_base));
                    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__state = 7U;
                }
                vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__state = 0x1fU;
            }
        } else if ((1U & (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__state))) {
            if (vlSelfRef.tb_combined__DOT__feature_test__DOT__v_rsp_valid) {
                if ((0U != (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__mapped_response_error))) {
                    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__state = 0x13U;
                    vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__state = 0x1fU;
                } else {
                    if ((0xc7ffU >= (0x0000ffffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_index))) {
                        vlSelfRef.__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_patch__v0 
                            = (0x0000ffffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_index);
                        vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_patch__v0 = 1U;
                    }
                    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__state = 3U;
                    vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__state = 0x1fU;
                    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_index 
                        = ((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_index);
                    vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_index = 0xffffffffU;
                }
            }
        }
    } else if ((2U & (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__state))) {
        if ((1U & (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__state))) {
            if ((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_index 
                 >= vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__patch_byte_count)) {
                vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__output_group_base = 0U;
                vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__state = 6U;
                vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__state = 0x1fU;
            } else if (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_in_bounds) {
                if ((0x00000000ffffffffULL < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_source_address_wide)) {
                    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__state = 0x13U;
                } else {
                    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__request_strobe_latched 
                        = (0x0000000fU & ((IData)(1U) 
                                          << (3U & (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_source_address_wide))));
                    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__state = 4U;
                }
                vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__state = 0x1fU;
            } else {
                if ((0xc7ffU >= (0x0000ffffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_index))) {
                    vlSelfRef.__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_patch__v1 
                        = (0x0000ffffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_index);
                    vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_patch__v1 = 1U;
                }
                vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_index 
                    = ((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_index);
                vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_index = 0xffffffffU;
            }
        } else {
            vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_channel = 0U;
            vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_channel = 0xffffffffU;
            vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_y = 0U;
            vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_y = 0xffffffffU;
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_point_scan_y = 0U;
            vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_point_scan_x = 0U;
            vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_index = 0U;
            vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_index = 0xffffffffU;
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__tile_height 
                = ((8U <= (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_height_latched 
                           - vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__tile_start_y))
                    ? 8U : (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_height_latched 
                            - vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__tile_start_y));
            vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_x = 0U;
            vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_x = 0xffffffffU;
            vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__state = 3U;
            vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__state = 0x1fU;
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__tile_width 
                = ((8U <= (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_width_latched 
                           - vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__tile_start_x))
                    ? 8U : (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_width_latched 
                            - vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__tile_start_x));
            vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__patch_height 
                = (((((8U <= (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_height_latched 
                              - vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__tile_start_y))
                       ? 8U : (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_height_latched 
                               - vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__tile_start_y)) 
                     - (IData)(1U)) * vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__stride_y_latched) 
                   + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__kernel_height_latched);
            vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__patch_height = 0xffffffffU;
            vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__patch_width 
                = (((((8U <= (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_width_latched 
                              - vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__tile_start_x))
                       ? 8U : (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_width_latched 
                               - vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__tile_start_x)) 
                     - (IData)(1U)) * vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__stride_x_latched) 
                   + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__kernel_width_latched);
            vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__patch_width = 0xffffffffU;
            vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__patch_byte_count 
                = (((((((8U <= (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_height_latched 
                                - vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__tile_start_y))
                         ? 8U : (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_height_latched 
                                 - vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__tile_start_y)) 
                       - (IData)(1U)) * vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__stride_y_latched) 
                     + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__kernel_height_latched) 
                    * (((((8U <= (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_width_latched 
                                  - vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__tile_start_x))
                           ? 8U : (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_width_latched 
                                   - vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__tile_start_x)) 
                         - (IData)(1U)) * vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__stride_x_latched) 
                       + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__kernel_width_latched)) 
                   * vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__input_channels_latched);
            vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__patch_byte_count = 0xffffffffU;
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__tile_point_count 
                = (((8U <= (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_height_latched 
                            - vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__tile_start_y))
                     ? 8U : (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_height_latched 
                             - vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__tile_start_y)) 
                   * ((8U <= (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_width_latched 
                              - vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__tile_start_x))
                       ? 8U : (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_width_latched 
                               - vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__tile_start_x)));
        }
    } else if ((1U & (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__state))) {
        vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__state = 0x13U;
        vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__state = 0x1fU;
    }
}

void Vtb_combined___024root___nba_sequent__TOP__16(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_sequent__TOP__16\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    VlWide<4>/*127:0*/ __Vtemp_1;
    VlWide<4>/*127:0*/ __Vtemp_2;
    // Body
    if (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_advance) {
        if ((((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_x) 
             >= vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__patch_width)) {
            if ((((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_y) 
                 >= vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__patch_height)) {
                vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_channel 
                    = ((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_channel);
                vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_channel = 0xffffffffU;
                vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_y = 0U;
            } else {
                vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_y 
                    = ((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_y);
            }
            vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_y = 0xffffffffU;
            vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_x = 0U;
        } else {
            vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_x 
                = ((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_x);
        }
        vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_x = 0xffffffffU;
    }
    if ((0x00000010U & (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__state))) {
        if ((8U & (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__state))) {
            vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__state = 0x13U;
            vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__state = 0x1fU;
        } else if ((4U & (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__state))) {
            vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__state = 0x13U;
            vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__state = 0x1fU;
        } else if ((2U & (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__state))) {
            if ((1U & (~ (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__state)))) {
                if ((((IData)(8U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_group_base) 
                     < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_channels_latched)) {
                    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_group_base 
                        = ((IData)(8U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_group_base);
                    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__state = 6U;
                } else if (((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__tile_start_x 
                             + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__tile_width) 
                            < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_width_latched)) {
                    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_group_base = 0U;
                    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__tile_start_x 
                        = ((IData)(8U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__tile_start_x);
                    vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__tile_start_x = 0xffffffffU;
                    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__state = 2U;
                } else if (((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__tile_start_y 
                             + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__tile_height) 
                            < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_height_latched)) {
                    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_group_base = 0U;
                    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__tile_start_x = 0U;
                    vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__tile_start_x = 0xffffffffU;
                    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__tile_start_y 
                        = ((IData)(8U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__tile_start_y);
                    vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__tile_start_y = 0xffffffffU;
                    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__state = 2U;
                } else {
                    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__state = 0x13U;
                }
                vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__state = 0x1fU;
            }
        } else if ((1U & (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__state))) {
            if (vlSelfRef.tb_combined__DOT__feature_test__DOT__v_rsp_valid) {
                if ((0U != (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__mapped_response_error))) {
                    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__state = 0x13U;
                } else {
                    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_point_index 
                        = ((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_point_index);
                    if ((((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_point_scan_x) 
                         >= vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__tile_width)) {
                        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_point_scan_y 
                            = ((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_point_scan_y);
                        vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_point_scan_x = 0U;
                    } else {
                        vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_point_scan_x 
                            = ((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_point_scan_x);
                    }
                    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__state = 0x0fU;
                }
                vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__state = 0x1fU;
            }
        }
    } else if ((8U & (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__state))) {
        if ((4U & (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__state))) {
            if ((2U & (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__state))) {
                if ((1U & (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__state))) {
                    if ((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_lane_index 
                         >= vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__group_lane_count)) {
                        vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__state = 0x12U;
                        vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__state = 0x1fU;
                    } else if ((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_point_index 
                                >= vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__tile_point_count)) {
                        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_lane_index 
                            = ((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_lane_index);
                        vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_point_index = 0U;
                        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_point_scan_y = 0U;
                        vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_point_scan_x = 0U;
                    } else {
                        __Vtemp_1[0U] = (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_byte_offset_wide);
                        __Vtemp_1[1U] = (IData)((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_byte_offset_wide 
                                                 >> 0x00000020U));
                        __Vtemp_1[2U] = 0U;
                        __Vtemp_1[3U] = 0U;
                        __Vtemp_2[0U] = (IData)(((QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_width_latched)) 
                                                 * (QData)((IData)(
                                                                   ((QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_height_latched)) 
                                                                    * (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_channels_latched)))))));
                        __Vtemp_2[1U] = (IData)((((QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_width_latched)) 
                                                  * (QData)((IData)(
                                                                    ((QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_height_latched)) 
                                                                     * (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_channels_latched)))))) 
                                                 >> 0x00000020U));
                        __Vtemp_2[2U] = 0U;
                        __Vtemp_2[3U] = 0U;
                        if (((0x00000000ffffffffULL 
                              < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_address_wide) 
                             | VL_GTE_W(4, __Vtemp_1, __Vtemp_2))) {
                            vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__state = 0x13U;
                        } else {
                            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__request_strobe_latched 
                                = (0x0000000fU & ((IData)(1U) 
                                                  << 
                                                  (3U 
                                                   & (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_address_wide))));
                            vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__state = 0x10U;
                        }
                        vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__state = 0x1fU;
                    }
                } else {
                    if ((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_lane_index 
                         < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__group_lane_count)) {
                        vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_block__v0 
                            = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__requantized_value;
                        vlSelfRef.__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_block__v0 
                            = (0x000001ffU & ((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_lane_index 
                                               << 6U) 
                                              + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_point_index));
                        vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_block__v0 = 1U;
                    }
                    if ((((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_lane_index) 
                         >= vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__group_lane_count)) {
                        if ((((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_point_index) 
                             >= vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__tile_point_count)) {
                            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_lane_index = 0U;
                            vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_point_index = 0U;
                            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_point_scan_y = 0U;
                            vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_point_scan_x = 0U;
                            vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__state = 0x0fU;
                        } else {
                            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_point_index 
                                = ((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_point_index);
                            if ((((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_point_scan_x) 
                                 >= vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__tile_width)) {
                                vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_point_scan_y 
                                    = ((IData)(1U) 
                                       + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_point_scan_y);
                                vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_point_scan_x = 0U;
                            } else {
                                vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_point_scan_x 
                                    = ((IData)(1U) 
                                       + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_point_scan_x);
                            }
                            vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_reduction_index = 0U;
                            vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__state = 0x0cU;
                        }
                        vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__state = 0x1fU;
                    } else {
                        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_lane_index 
                            = ((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_lane_index);
                    }
                }
            } else if ((1U & (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__state))) {
                if (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_bad_argument) {
                    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__state = 0x13U;
                    vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__state = 0x1fU;
                } else if (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_overflow) {
                    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__state = 0x13U;
                    vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__state = 0x1fU;
                } else {
                    if ((0U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__group_lane_count)) {
                        vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v0 
                            = (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_sum[0U]);
                        vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v0 = 1U;
                    }
                    if ((((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_reduction_index) 
                         >= vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__reduction_count_latched)) {
                        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_lane_index = 0U;
                        vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__state = 0x0eU;
                        vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__state = 0x1fU;
                    } else {
                        vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_reduction_index 
                            = ((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_reduction_index);
                        if ((((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_kernel_x) 
                             >= vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__kernel_width_latched)) {
                            if ((((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_kernel_y) 
                                 >= vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__kernel_height_latched)) {
                                vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_input_channel 
                                    = ((IData)(1U) 
                                       + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_input_channel);
                                vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_kernel_y = 0U;
                            } else {
                                vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_kernel_y 
                                    = ((IData)(1U) 
                                       + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_kernel_y);
                            }
                            vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_kernel_x = 0U;
                        } else {
                            vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_kernel_x 
                                = ((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_kernel_x);
                        }
                    }
                    if ((1U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__group_lane_count)) {
                        vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v1 
                            = (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_sum[1U]);
                        vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v1 = 1U;
                    }
                    if ((2U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__group_lane_count)) {
                        vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v2 
                            = (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_sum[2U]);
                        vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v2 = 1U;
                    }
                    if ((3U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__group_lane_count)) {
                        vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v3 
                            = (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_sum[3U]);
                        vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v3 = 1U;
                    }
                    if ((4U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__group_lane_count)) {
                        vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v4 
                            = (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_sum[4U]);
                        vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v4 = 1U;
                    }
                    if ((5U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__group_lane_count)) {
                        vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v5 
                            = (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_sum[5U]);
                        vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v5 = 1U;
                    }
                    if ((6U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__group_lane_count)) {
                        vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v6 
                            = (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_sum[6U]);
                        vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v6 = 1U;
                    }
                    if ((7U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__group_lane_count)) {
                        vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v7 
                            = (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_sum[7U]);
                        vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v7 = 1U;
                    }
                }
            } else {
                vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_input_channel = 0U;
                vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_kernel_y = 0U;
                vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_kernel_x = 0U;
                vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v8 
                    = ((0U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__group_lane_count)
                        ? vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_bias[0U]
                        : 0U);
                vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v8 = 1U;
                vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_reduction_index = 0U;
                vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__state = 0x0dU;
                vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__state = 0x1fU;
                vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v9 
                    = ((1U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__group_lane_count)
                        ? vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_bias[1U]
                        : 0U);
                vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v9 = 1U;
                vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v10 
                    = ((2U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__group_lane_count)
                        ? vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_bias[2U]
                        : 0U);
                vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v11 
                    = ((3U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__group_lane_count)
                        ? vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_bias[3U]
                        : 0U);
                vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v12 
                    = ((4U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__group_lane_count)
                        ? vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_bias[4U]
                        : 0U);
                vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v13 
                    = ((5U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__group_lane_count)
                        ? vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_bias[5U]
                        : 0U);
                vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v14 
                    = ((6U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__group_lane_count)
                        ? vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_bias[6U]
                        : 0U);
                vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v15 
                    = ((7U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__group_lane_count)
                        ? vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_bias[7U]
                        : 0U);
            }
        } else if ((2U & (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__state))) {
            if ((1U & (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__state))) {
                vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_input_channel = 0U;
                vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_kernel_y = 0U;
                vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_kernel_x = 0U;
                vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_point_index = 0U;
                vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v16 
                    = ((0U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__group_lane_count)
                        ? vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_bias[0U]
                        : 0U);
                vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v16 = 1U;
                vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_reduction_index = 0U;
                vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__state = 0x0dU;
                vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__state = 0x1fU;
                vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v17 
                    = ((1U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__group_lane_count)
                        ? vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_bias[1U]
                        : 0U);
                vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v17 = 1U;
                vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v18 
                    = ((2U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__group_lane_count)
                        ? vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_bias[2U]
                        : 0U);
                vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v19 
                    = ((3U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__group_lane_count)
                        ? vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_bias[3U]
                        : 0U);
                vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v20 
                    = ((4U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__group_lane_count)
                        ? vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_bias[4U]
                        : 0U);
                vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v21 
                    = ((5U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__group_lane_count)
                        ? vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_bias[5U]
                        : 0U);
                vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v22 
                    = ((6U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__group_lane_count)
                        ? vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_bias[6U]
                        : 0U);
                vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v23 
                    = ((7U < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__group_lane_count)
                        ? vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_bias[7U]
                        : 0U);
            } else if (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__mq_prefetch_invalid) {
                vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__state = 0x13U;
                vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__state = 0x1fU;
            } else {
                vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_mq_parameter__v0[0U] 
                    = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__mq_prefetch_parameter[0U];
                vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_mq_parameter__v0[1U] 
                    = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__mq_prefetch_parameter[1U];
                vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_mq_parameter__v0[2U] 
                    = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__mq_prefetch_parameter[2U];
                vlSelfRef.__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_mq_parameter__v0 
                    = (7U & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__mq_prefetch_lane);
                vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_mq_parameter__v0 = 1U;
                vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_bias__v0 
                    = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__mq_prefetch_bias;
                vlSelfRef.__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_bias__v0 
                    = (7U & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__mq_prefetch_lane);
                if ((((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__mq_prefetch_lane) 
                     >= vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__group_lane_count)) {
                    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__state = 0x0bU;
                    vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__state = 0x1fU;
                } else {
                    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__mq_prefetch_lane 
                        = ((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__mq_prefetch_lane);
                }
            }
        } else if ((1U & (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__state))) {
            if (vlSelfRef.tb_combined__DOT__feature_test__DOT__v_rsp_valid) {
                if ((0U != (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__mapped_response_error))) {
                    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__state = 0x13U;
                } else {
                    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_reduction_index 
                        = ((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_reduction_index);
                    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__state = 7U;
                }
                vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__state = 0x1fU;
            }
        }
    } else if ((4U & (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__state))) {
        if ((2U & (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__state))) {
            if ((1U & (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__state))) {
                if ((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_lane_index 
                     >= vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__group_lane_count)) {
                    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__mq_prefetch_lane = 0U;
                    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__state = 0x0aU;
                    vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__state = 0x1fU;
                } else if ((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_reduction_index 
                            >= vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__reduction_count_latched)) {
                    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_lane_index 
                        = ((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_lane_index);
                    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_reduction_index = 0U;
                } else {
                    if ((0x00000000ffffffffULL < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_source_address_wide)) {
                        vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__state = 0x13U;
                    } else {
                        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__request_strobe_latched 
                            = (0x0000000fU & ((IData)(1U) 
                                              << (3U 
                                                  & (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_source_address_wide))));
                        vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__state = 8U;
                    }
                    vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__state = 0x1fU;
                }
            } else {
                if ((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_group_base 
                     >= vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_channels_latched)) {
                    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__state = 0x12U;
                } else {
                    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_point_scan_y = 0U;
                    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_point_scan_x = 0U;
                    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_lane_index = 0U;
                    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_reduction_index = 0U;
                    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__mq_prefetch_lane = 0U;
                    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__group_lane_count 
                        = ((8U <= (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_channels_latched 
                                   - vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_group_base))
                            ? 8U : (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_channels_latched 
                                    - vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_group_base));
                    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__state = 7U;
                }
                vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__state = 0x1fU;
            }
        } else if ((1U & (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__state))) {
            if (vlSelfRef.tb_combined__DOT__feature_test__DOT__v_rsp_valid) {
                if ((0U != (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__mapped_response_error))) {
                    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__state = 0x13U;
                    vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__state = 0x1fU;
                } else {
                    if ((0xc7ffU >= (0x0000ffffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_index))) {
                        vlSelfRef.__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_patch__v0 
                            = (0x0000ffffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_index);
                        vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_patch__v0 = 1U;
                    }
                    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__state = 3U;
                    vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__state = 0x1fU;
                    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_index 
                        = ((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_index);
                    vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_index = 0xffffffffU;
                }
            }
        }
    } else if ((2U & (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__state))) {
        if ((1U & (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__state))) {
            if ((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_index 
                 >= vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__patch_byte_count)) {
                vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_group_base = 0U;
                vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__state = 6U;
                vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__state = 0x1fU;
            } else if (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_in_bounds) {
                if ((0x00000000ffffffffULL < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_source_address_wide)) {
                    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__state = 0x13U;
                } else {
                    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__request_strobe_latched 
                        = (0x0000000fU & ((IData)(1U) 
                                          << (3U & (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_source_address_wide))));
                    vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__state = 4U;
                }
                vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__state = 0x1fU;
            } else {
                if ((0xc7ffU >= (0x0000ffffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_index))) {
                    vlSelfRef.__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_patch__v1 
                        = (0x0000ffffU & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_index);
                    vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_patch__v1 = 1U;
                }
                vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_index 
                    = ((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_index);
                vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_index = 0xffffffffU;
            }
        } else {
            vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_channel = 0U;
            vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_channel = 0xffffffffU;
            vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_y = 0U;
            vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_y = 0xffffffffU;
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_point_scan_y = 0U;
            vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_point_scan_x = 0U;
            vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_index = 0U;
            vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_index = 0xffffffffU;
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__tile_height 
                = ((8U <= (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_height_latched 
                           - vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__tile_start_y))
                    ? 8U : (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_height_latched 
                            - vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__tile_start_y));
            vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_x = 0U;
            vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_x = 0xffffffffU;
            vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__state = 3U;
            vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__state = 0x1fU;
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__tile_width 
                = ((8U <= (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_width_latched 
                           - vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__tile_start_x))
                    ? 8U : (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_width_latched 
                            - vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__tile_start_x));
            vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__patch_height 
                = (((((8U <= (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_height_latched 
                              - vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__tile_start_y))
                       ? 8U : (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_height_latched 
                               - vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__tile_start_y)) 
                     - (IData)(1U)) * vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__stride_y_latched) 
                   + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__kernel_height_latched);
            vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__patch_height = 0xffffffffU;
            vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__patch_width 
                = (((((8U <= (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_width_latched 
                              - vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__tile_start_x))
                       ? 8U : (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_width_latched 
                               - vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__tile_start_x)) 
                     - (IData)(1U)) * vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__stride_x_latched) 
                   + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__kernel_width_latched);
            vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__patch_width = 0xffffffffU;
            vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__patch_byte_count 
                = (((((((8U <= (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_height_latched 
                                - vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__tile_start_y))
                         ? 8U : (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_height_latched 
                                 - vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__tile_start_y)) 
                       - (IData)(1U)) * vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__stride_y_latched) 
                     + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__kernel_height_latched) 
                    * (((((8U <= (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_width_latched 
                                  - vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__tile_start_x))
                           ? 8U : (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_width_latched 
                                   - vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__tile_start_x)) 
                         - (IData)(1U)) * vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__stride_x_latched) 
                       + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__kernel_width_latched)) 
                   * vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__input_channels_latched);
            vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__patch_byte_count = 0xffffffffU;
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__tile_point_count 
                = (((8U <= (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_height_latched 
                            - vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__tile_start_y))
                     ? 8U : (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_height_latched 
                             - vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__tile_start_y)) 
                   * ((8U <= (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_width_latched 
                              - vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__tile_start_x))
                       ? 8U : (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_width_latched 
                               - vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__tile_start_x)));
        }
    } else if ((1U & (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__state))) {
        vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__state = 0x13U;
        vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__state = 0x1fU;
    }
}

void Vtb_combined___024root___nba_sequent__TOP__17(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_sequent__TOP__17\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    VlUnpacked<CData/*7:0*/, 512> tb_combined__DOT__feature_test__DOT__u_old__DOT__output_block;
    for (int __Vi0 = 0; __Vi0 < 512; ++__Vi0) {
        tb_combined__DOT__feature_test__DOT__u_old__DOT__output_block[__Vi0] = 0;
    }
    // Body
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_point_index 
        = vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__output_point_index;
    if (vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__output_block__v0) {
        tb_combined__DOT__feature_test__DOT__u_old__DOT__output_block[vlSelfRef.__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_old__DOT__output_block__v0] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__output_block__v0;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_patch__v0) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_patch[vlSelfRef.__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_patch__v0] = 0U;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_patch__v1) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_patch[vlSelfRef.__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_patch__v1] = 0U;
    }
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_point_scan_x 
        = vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__output_point_scan_x;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_reduction_index 
        = vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_reduction_index;
    if (vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_mq_parameter__v0) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_bias[vlSelfRef.__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_bias__v0] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_bias__v0;
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_mq_parameter[vlSelfRef.__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_mq_parameter__v0][0U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_mq_parameter__v0[0U];
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_mq_parameter[vlSelfRef.__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_mq_parameter__v0][1U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_mq_parameter__v0[1U];
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_mq_parameter[vlSelfRef.__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_mq_parameter__v0][2U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_mq_parameter__v0[2U];
    }
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_group_base 
        = vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__output_group_base;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_point_scan_x 
        = vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_point_scan_x;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_reduction_index 
        = vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_reduction_index;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_kernel_y 
        = vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_kernel_y;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_kernel_x 
        = vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__compute_kernel_x;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_channel 
        = ((vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_channel 
            & vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_channel) 
           | (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_channel 
              & (~ vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_channel)));
}

void Vtb_combined___024root___nba_sequent__TOP__18(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_sequent__TOP__18\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_channel = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_y 
        = ((vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_y 
            & vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_y) 
           | (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_y 
              & (~ vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_y)));
    vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_y = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_x 
        = ((vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_x 
            & vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_x) 
           | (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_x 
              & (~ vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_x)));
    vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_x = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_index 
        = ((vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_index 
            & vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_index) 
           | (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_index 
              & (~ vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_index)));
    vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_index = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__patch_height 
        = ((vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__patch_height 
            & vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__patch_height) 
           | (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__patch_height 
              & (~ vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__patch_height)));
    vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__patch_height = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__patch_width 
        = ((vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__patch_width 
            & vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__patch_width) 
           | (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__patch_width 
              & (~ vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__patch_width)));
    vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__patch_width = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__patch_byte_count 
        = ((vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__patch_byte_count 
            & vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__patch_byte_count) 
           | (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__patch_byte_count 
              & (~ vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__patch_byte_count)));
    vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__patch_byte_count = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__state 
        = (((IData)(vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__state) 
            & (IData)(vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__state)) 
           | ((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__state) 
              & (~ (IData)(vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__state))));
    vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__state = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__tile_start_x 
        = ((vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__tile_start_x 
            & vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__tile_start_x) 
           | (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__tile_start_x 
              & (~ vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__tile_start_x)));
}

void Vtb_combined___024root___nba_sequent__TOP__19(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_sequent__TOP__19\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__tile_start_x = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__tile_start_y 
        = ((vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_old__DOT__tile_start_y 
            & vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__tile_start_y) 
           | (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__tile_start_y 
              & (~ vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__tile_start_y)));
    vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_old__DOT__tile_start_y = 0U;
    if (vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v0) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator[0U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v0;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v1) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator[1U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v1;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v2) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator[2U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v2;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v3) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator[3U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v3;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v4) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator[4U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v4;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v5) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator[5U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v5;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v6) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator[6U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v6;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v7) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator[7U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v7;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v8) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator[0U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v8;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v9) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator[1U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v9;
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator[2U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v10;
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator[3U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v11;
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator[4U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v12;
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator[5U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v13;
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator[6U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v14;
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator[7U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v15;
    }
}

void Vtb_combined___024root___nba_sequent__TOP__20(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_sequent__TOP__20\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    VlUnpacked<CData/*7:0*/, 512> tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_block;
    for (int __Vi0 = 0; __Vi0 < 512; ++__Vi0) {
        tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_block[__Vi0] = 0;
    }
    // Body
    if (vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v16) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator[0U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v16;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v17) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator[1U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v17;
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator[2U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v18;
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator[3U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v19;
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator[4U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v20;
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator[5U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v21;
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator[6U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v22;
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator[7U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator__v23;
    }
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_point_index 
        = vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_point_index;
    if (vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_block__v0) {
        tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_block[vlSelfRef.__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_block__v0] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_block__v0;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_patch__v0) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_patch[vlSelfRef.__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_patch__v0] = 0U;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_patch__v1) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_patch[vlSelfRef.__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_patch__v1] = 0U;
    }
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_point_scan_x 
        = vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_point_scan_x;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_reduction_index 
        = vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_reduction_index;
}

void Vtb_combined___024root___nba_sequent__TOP__21(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_sequent__TOP__21\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if (vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_mq_parameter__v0) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_bias[vlSelfRef.__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_bias__v0] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_bias__v0;
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_mq_parameter[vlSelfRef.__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_mq_parameter__v0][0U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_mq_parameter__v0[0U];
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_mq_parameter[vlSelfRef.__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_mq_parameter__v0][1U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_mq_parameter__v0[1U];
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_mq_parameter[vlSelfRef.__VdlyDim0__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_mq_parameter__v0][2U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_mq_parameter__v0[2U];
    }
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_group_base 
        = vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_group_base;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_point_scan_x 
        = vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_point_scan_x;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_reduction_index 
        = vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_reduction_index;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_kernel_y 
        = vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_kernel_y;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_kernel_x 
        = vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__compute_kernel_x;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_channel 
        = ((vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_channel 
            & vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_channel) 
           | (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_channel 
              & (~ vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_channel)));
    vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_channel = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_y 
        = ((vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_y 
            & vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_y) 
           | (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_y 
              & (~ vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_y)));
    vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_y = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_x 
        = ((vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_x 
            & vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_x) 
           | (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_x 
              & (~ vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_x)));
    vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_x = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_index 
        = ((vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_index 
            & vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_index) 
           | (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_index 
              & (~ vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_index)));
    vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_index = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__patch_height 
        = ((vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__patch_height 
            & vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__patch_height) 
           | (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__patch_height 
              & (~ vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__patch_height)));
}

void Vtb_combined___024root___nba_sequent__TOP__22(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_sequent__TOP__22\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__patch_height = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__patch_width 
        = ((vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__patch_width 
            & vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__patch_width) 
           | (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__patch_width 
              & (~ vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__patch_width)));
    vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__patch_width = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__patch_byte_count 
        = ((vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__patch_byte_count 
            & vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__patch_byte_count) 
           | (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__patch_byte_count 
              & (~ vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__patch_byte_count)));
    vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__patch_byte_count = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__state 
        = (((IData)(vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__state) 
            & (IData)(vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__state)) 
           | ((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__state) 
              & (~ (IData)(vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__state))));
    vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__state = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__tile_start_x 
        = ((vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__tile_start_x 
            & vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__tile_start_x) 
           | (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__tile_start_x 
              & (~ vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__tile_start_x)));
    vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__tile_start_x = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__tile_start_y 
        = ((vlSelfRef.__Vdly__tb_combined__DOT__feature_test__DOT__u_dut__DOT__tile_start_y 
            & vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__tile_start_y) 
           | (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__tile_start_y 
              & (~ vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__tile_start_y)));
    vlSelfRef.__VdlyMask__tb_combined__DOT__feature_test__DOT__u_dut__DOT__tile_start_y = 0U;
    if (vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v0) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator[0U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v0;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v1) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator[1U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v1;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v2) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator[2U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v2;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v3) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator[3U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v3;
    }
}

void Vtb_combined___024root___nba_sequent__TOP__23(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_sequent__TOP__23\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if (vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v4) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator[4U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v4;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v5) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator[5U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v5;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v6) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator[6U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v6;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v7) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator[7U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v7;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v8) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator[0U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v8;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v9) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator[1U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v9;
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator[2U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v10;
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator[3U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v11;
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator[4U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v12;
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator[5U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v13;
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator[6U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v14;
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator[7U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v15;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v16) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator[0U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v16;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v17) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator[1U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v17;
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator[2U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v18;
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator[3U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v19;
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator[4U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v20;
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator[5U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v21;
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator[6U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v22;
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator[7U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator__v23;
    }
}

void Vtb_combined___024root___nba_sequent__TOP__24(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_sequent__TOP__24\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    IData/*31:0*/ tb_combined__DOT__feature_test__DOT__u_old__DOT__mq_prefetch_index;
    tb_combined__DOT__feature_test__DOT__u_old__DOT__mq_prefetch_index = 0;
    // Body
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_source_address_wide 
        = ((QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_package_base_latched)) 
           + ((QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__quantized_weight_offset_latched)) 
              + ((QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_reduction_index)) 
                 + ((QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__reduction_count_latched)) 
                    * (QData)((IData)((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_group_base 
                                       + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__weight_lane_index)))))));
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

void Vtb_combined___024root___nba_sequent__TOP__25(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_sequent__TOP__25\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    VlWide<3>/*79:0*/ tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_parameter;
    VL_ZERO_W(80, tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_parameter);
    IData/*31:0*/ tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_accumulator;
    tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_accumulator = 0;
    IData/*31:0*/ tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_multiplier;
    tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_multiplier = 0;
    IData/*31:0*/ tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_q_shift;
    tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_q_shift = 0;
    IData/*31:0*/ tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_magnitude;
    tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_magnitude = 0;
    QData/*63:0*/ tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_product;
    tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_product = 0;
    QData/*63:0*/ tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_rounding_add;
    tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_rounding_add = 0;
    QData/*63:0*/ tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_rounded_magnitude;
    tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_rounded_magnitude = 0;
    QData/*63:0*/ tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_signed_value;
    tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_signed_value = 0;
    VlWide<3>/*95:0*/ __Vtemp_2;
    VlWide<3>/*95:0*/ __Vtemp_3;
    // Body
    tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_parameter[0U] = 0U;
    tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_parameter[1U] = 0U;
    tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_parameter[2U] = 0U;
    tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_accumulator = 0U;
    tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_multiplier = 0U;
    tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_q_shift = 0U;
    tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_magnitude = 0U;
    tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_product = 0ULL;
    tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_rounding_add = 0ULL;
    tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_rounded_magnitude = 0ULL;
    tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_signed_value = 0ULL;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__requantized_value = 0U;
    if (((8U > vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_lane_index) 
         & (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_lane_index 
            < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__group_lane_count))) {
        tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_parameter[0U] 
            = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_mq_parameter
            [(7U & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_lane_index)][0U];
        tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_parameter[1U] 
            = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_mq_parameter
            [(7U & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_lane_index)][1U];
        tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_parameter[2U] 
            = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_mq_parameter
            [(7U & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_lane_index)][2U];
        tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_accumulator 
            = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__lane_accumulator
            [(7U & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_lane_index)];
        if ((tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_accumulator 
             >> 0x1fU)) {
            tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_multiplier 
                = ((tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_parameter[1U] 
                    << 0x00000018U) | (tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_parameter[0U] 
                                       >> 8U));
            tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_magnitude 
                = ((IData)(1U) + (~ tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_accumulator));
            tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_q_shift 
                = (0x000000ffU & tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_parameter[0U]);
        } else {
            tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_multiplier 
                = ((tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_parameter[2U] 
                    << 0x00000010U) | (tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_parameter[1U] 
                                       >> 0x00000010U));
            tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_magnitude 
                = tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_accumulator;
            tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_q_shift 
                = (0x000000ffU & (tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_parameter[1U] 
                                  >> 8U));
        }
        tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_product 
            = ((QData)((IData)(tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_magnitude)) 
               * (QData)((IData)(tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_multiplier)));
        if ((0U != tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_q_shift)) {
            tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_rounding_add 
                = VL_SHIFTL_QQI(64,64,32, 1ULL, (tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_q_shift 
                                                 - (IData)(1U)));
        }
        tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_rounded_magnitude 
            = VL_SHIFTR_QQI(64,64,32, (tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_product 
                                       + tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_rounding_add), tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_q_shift);
        __Vtemp_2[0U] = (IData)(tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_rounded_magnitude);
        __Vtemp_2[1U] = (IData)((tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_rounded_magnitude 
                                 >> 0x00000020U));
        __Vtemp_2[2U] = 0U;
        VL_NEGATE_W(3, __Vtemp_3, __Vtemp_2);
        tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_signed_value 
            = ((tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_accumulator 
                >> 0x1fU) ? (((QData)((IData)(__Vtemp_3[1U])) 
                              << 0x00000020U) | (QData)((IData)(__Vtemp_3[0U])))
                : tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_rounded_magnitude);
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__requantized_value 
            = (VL_LTS_IQQ(64, 0x000000000000007fULL, tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_signed_value)
                ? 0x0000007fU : (VL_GTS_IQQ(64, 0xffffffffffffff81ULL, tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_signed_value)
                                  ? 0x00000081U : (0x000000ffU 
                                                   & (IData)(tb_combined__DOT__feature_test__DOT__u_old__DOT__requant_signed_value))));
    }
}

void Vtb_combined___024root___nba_sequent__TOP__26(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_sequent__TOP__26\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    IData/*31:0*/ tb_combined__DOT__feature_test__DOT__u_dut__DOT__mq_prefetch_index;
    tb_combined__DOT__feature_test__DOT__u_dut__DOT__mq_prefetch_index = 0;
    // Body
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_source_address_wide 
        = ((QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_package_base_latched)) 
           + ((QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__quantized_weight_offset_latched)) 
              + ((QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_reduction_index)) 
                 + ((QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__reduction_count_latched)) 
                    * (QData)((IData)((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_group_base 
                                       + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__weight_lane_index)))))));
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

void Vtb_combined___024root___nba_sequent__TOP__27(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_sequent__TOP__27\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    VlWide<3>/*79:0*/ tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_parameter;
    VL_ZERO_W(80, tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_parameter);
    IData/*31:0*/ tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_accumulator;
    tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_accumulator = 0;
    IData/*31:0*/ tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_multiplier;
    tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_multiplier = 0;
    IData/*31:0*/ tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_q_shift;
    tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_q_shift = 0;
    IData/*31:0*/ tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_magnitude;
    tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_magnitude = 0;
    QData/*63:0*/ tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_product;
    tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_product = 0;
    QData/*63:0*/ tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_rounding_add;
    tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_rounding_add = 0;
    QData/*63:0*/ tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_rounded_magnitude;
    tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_rounded_magnitude = 0;
    QData/*63:0*/ tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_signed_value;
    tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_signed_value = 0;
    VlWide<3>/*95:0*/ __Vtemp_2;
    VlWide<3>/*95:0*/ __Vtemp_3;
    // Body
    tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_parameter[0U] = 0U;
    tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_parameter[1U] = 0U;
    tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_parameter[2U] = 0U;
    tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_accumulator = 0U;
    tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_multiplier = 0U;
    tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_q_shift = 0U;
    tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_magnitude = 0U;
    tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_product = 0ULL;
    tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_rounding_add = 0ULL;
    tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_rounded_magnitude = 0ULL;
    tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_signed_value = 0ULL;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__requantized_value = 0U;
    if (((8U > vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_lane_index) 
         & (vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_lane_index 
            < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__group_lane_count))) {
        tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_parameter[0U] 
            = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_mq_parameter
            [(7U & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_lane_index)][0U];
        tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_parameter[1U] 
            = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_mq_parameter
            [(7U & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_lane_index)][1U];
        tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_parameter[2U] 
            = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_mq_parameter
            [(7U & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_lane_index)][2U];
        tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_accumulator 
            = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__lane_accumulator
            [(7U & vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_lane_index)];
        if ((tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_accumulator 
             >> 0x1fU)) {
            tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_multiplier 
                = ((tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_parameter[1U] 
                    << 0x00000018U) | (tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_parameter[0U] 
                                       >> 8U));
            tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_magnitude 
                = ((IData)(1U) + (~ tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_accumulator));
            tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_q_shift 
                = (0x000000ffU & tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_parameter[0U]);
        } else {
            tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_multiplier 
                = ((tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_parameter[2U] 
                    << 0x00000010U) | (tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_parameter[1U] 
                                       >> 0x00000010U));
            tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_magnitude 
                = tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_accumulator;
            tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_q_shift 
                = (0x000000ffU & (tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_parameter[1U] 
                                  >> 8U));
        }
        tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_product 
            = ((QData)((IData)(tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_magnitude)) 
               * (QData)((IData)(tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_multiplier)));
        if ((0U != tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_q_shift)) {
            tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_rounding_add 
                = VL_SHIFTL_QQI(64,64,32, 1ULL, (tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_q_shift 
                                                 - (IData)(1U)));
        }
        tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_rounded_magnitude 
            = VL_SHIFTR_QQI(64,64,32, (tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_product 
                                       + tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_rounding_add), tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_q_shift);
        __Vtemp_2[0U] = (IData)(tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_rounded_magnitude);
        __Vtemp_2[1U] = (IData)((tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_rounded_magnitude 
                                 >> 0x00000020U));
        __Vtemp_2[2U] = 0U;
        VL_NEGATE_W(3, __Vtemp_3, __Vtemp_2);
        tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_signed_value 
            = ((tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_accumulator 
                >> 0x1fU) ? (((QData)((IData)(__Vtemp_3[1U])) 
                              << 0x00000020U) | (QData)((IData)(__Vtemp_3[0U])))
                : tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_rounded_magnitude);
        vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__requantized_value 
            = (VL_LTS_IQQ(64, 0x000000000000007fULL, tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_signed_value)
                ? 0x0000007fU : (VL_GTS_IQQ(64, 0xffffffffffffff81ULL, tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_signed_value)
                                  ? 0x00000081U : (0x000000ffU 
                                                   & (IData)(tb_combined__DOT__feature_test__DOT__u_dut__DOT__requant_signed_value))));
    }
}

void Vtb_combined___024root___nba_sequent__TOP__28(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_sequent__TOP__28\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v0 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v1 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v2 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v3 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v4 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v5 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v6 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v7 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v8 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v9 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v10 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v11 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v12 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v13 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v14 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v15 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v0 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v1 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v2 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v3 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v4 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v5 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v6 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v7 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v8 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v9 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v10 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v11 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v12 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v13 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v14 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v15 = 0U;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_height 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_height;
}
