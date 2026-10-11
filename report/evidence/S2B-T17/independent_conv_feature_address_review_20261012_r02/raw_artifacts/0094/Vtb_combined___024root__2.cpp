// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vtb_combined.h for the primary calling header

#include "Vtb_combined__pch.h"

void Vtb_combined___024root___nba_sequent__TOP__29(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_sequent__TOP__29\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_point_count 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_point_count;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_point_index 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_point_index;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_point_index 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_point_index;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_block__v0 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_patch__v0 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_patch__v1 = 0U;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_lane_index 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_lane_index;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_reduction_index 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_reduction_index;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_lane_index 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_lane_index;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_point_scan_y 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_point_scan_y;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_point_scan_x 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_point_scan_x;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_lane 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_lane;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_lane_index 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_lane_index;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter__v0 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter__v8 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter__v16 = 0U;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_group_base 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_group_base;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__input_channels_latched 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__input_channels_latched;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_channels_latched 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_channels_latched;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_height_latched 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_height_latched;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_width_latched 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_width_latched;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_width 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_width;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__patch_height 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__patch_height;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__patch_width 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__patch_width;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__patch_byte_count 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__patch_byte_count;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_index 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_index;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_channel 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_channel;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_y 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_y;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_x 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_x;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_point_scan_y 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_point_scan_y;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_point_scan_x 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_point_scan_x;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_reduction_index 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_reduction_index;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_input_channel 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_input_channel;
}

void Vtb_combined___024root___nba_sequent__TOP__30(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_sequent__TOP__30\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_kernel_y 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_kernel_y;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_kernel_x 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_kernel_x;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__reduction_count_latched 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__reduction_count_latched;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_start_y 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_start_y;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_start_x 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_start_x;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__group_lane_count 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__group_lane_count;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v0 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v1 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v2 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v3 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v4 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v5 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v6 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v7 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v8 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v9 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v16 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v17 = 0U;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__kernel_height_latched 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__kernel_height_latched;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__kernel_width_latched 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__kernel_width_latched;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__stride_y_latched 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__stride_y_latched;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__stride_x_latched 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__stride_x_latched;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0 = 0U;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_height 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_height;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_point_count 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_point_count;
}

void Vtb_combined___024root___nba_sequent__TOP__31(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_sequent__TOP__31\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_point_index 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_point_index;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_point_index 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_point_index;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_block__v0 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_patch__v0 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_patch__v1 = 0U;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_lane_index 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_lane_index;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_reduction_index 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_reduction_index;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_lane_index 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_lane_index;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_point_scan_y 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_point_scan_y;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_point_scan_x 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_point_scan_x;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_lane 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_lane;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_lane_index 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_lane_index;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter__v0 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter__v8 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter__v16 = 0U;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_group_base 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_group_base;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_width 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_width;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__patch_height 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__patch_height;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__patch_width 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__patch_width;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__patch_byte_count 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__patch_byte_count;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_index 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_index;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_channel 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_channel;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_y 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_y;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_x 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_x;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_point_scan_y 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_point_scan_y;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_point_scan_x 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_point_scan_x;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_reduction_index 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_reduction_index;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_input_channel 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_input_channel;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_kernel_y 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_kernel_y;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_kernel_x 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_kernel_x;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__input_channels_latched 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__input_channels_latched;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_channels_latched 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_channels_latched;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__reduction_count_latched 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__reduction_count_latched;
}

void Vtb_combined___024root___nba_sequent__TOP__32(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_sequent__TOP__32\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_start_y 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_start_y;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_start_x 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_start_x;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_height_latched 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_height_latched;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_width_latched 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_width_latched;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__group_lane_count 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__group_lane_count;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v0 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v1 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v2 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v3 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v4 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v5 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v6 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v7 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v8 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v9 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v16 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v17 = 0U;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__kernel_height_latched 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__kernel_height_latched;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__kernel_width_latched 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__kernel_width_latched;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__stride_y_latched 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__stride_y_latched;
    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__stride_x_latched 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__stride_x_latched;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0 = 0U;
    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0 = 0U;
}

void Vtb_combined___024root___nba_sequent__TOP__34(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_sequent__TOP__34\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if (((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__hard_reset) 
         | (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__abort))) {
        vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v0 = 1U;
        vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v2 = 1U;
    } else {
        if (((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_enable) 
             & (0U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__group_lane_count))) {
            vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v1 
                = ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_reduction_index))
                    ? vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory
                   [(0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_reduction_index)]
                    : 0U);
            vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v1 = 1U;
        }
        if (((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_enable) 
             & (1U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__group_lane_count))) {
            vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v3 
                = ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_reduction_index))
                    ? vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory
                   [(0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_reduction_index)]
                    : 0U);
            vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v3 = 1U;
        }
    }
}

void Vtb_combined___024root___nba_sequent__TOP__35(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_sequent__TOP__35\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if (((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__hard_reset) 
         | (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__abort))) {
        vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v4 = 1U;
        vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v6 = 1U;
        vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v8 = 1U;
        vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v10 = 1U;
    } else {
        if (((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_enable) 
             & (2U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__group_lane_count))) {
            vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v5 
                = ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_reduction_index))
                    ? vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory
                   [(0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_reduction_index)]
                    : 0U);
            vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v5 = 1U;
        }
        if (((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_enable) 
             & (3U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__group_lane_count))) {
            vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v7 
                = ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_reduction_index))
                    ? vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory
                   [(0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_reduction_index)]
                    : 0U);
            vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v7 = 1U;
        }
        if (((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_enable) 
             & (4U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__group_lane_count))) {
            vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v9 
                = ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_reduction_index))
                    ? vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory
                   [(0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_reduction_index)]
                    : 0U);
            vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v9 = 1U;
        }
        if (((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_enable) 
             & (5U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__group_lane_count))) {
            vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v11 
                = ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_reduction_index))
                    ? vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory
                   [(0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_reduction_index)]
                    : 0U);
            vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v11 = 1U;
        }
    }
}

void Vtb_combined___024root___nba_sequent__TOP__36(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_sequent__TOP__36\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if (((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__hard_reset) 
         | (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__abort))) {
        vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v12 = 1U;
        vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v14 = 1U;
        vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v0 = 1U;
        vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v2 = 1U;
    } else {
        if (((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_enable) 
             & (6U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__group_lane_count))) {
            vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v13 
                = ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_reduction_index))
                    ? vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory
                   [(0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_reduction_index)]
                    : 0U);
            vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v13 = 1U;
        }
        if (((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_enable) 
             & (7U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__group_lane_count))) {
            vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v15 
                = ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_reduction_index))
                    ? vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory
                   [(0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_reduction_index)]
                    : 0U);
            vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v15 = 1U;
        }
        if (((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_enable) 
             & (0U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__group_lane_count))) {
            vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v1 
                = ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_reduction_index))
                    ? vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory
                   [(0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_reduction_index)]
                    : 0U);
            vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v1 = 1U;
        }
        if (((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_enable) 
             & (1U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__group_lane_count))) {
            vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v3 
                = ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_reduction_index))
                    ? vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory
                   [(0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_reduction_index)]
                    : 0U);
            vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v3 = 1U;
        }
    }
}

void Vtb_combined___024root___nba_sequent__TOP__37(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_sequent__TOP__37\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if (((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__hard_reset) 
         | (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__abort))) {
        vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v4 = 1U;
        vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v6 = 1U;
        vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v8 = 1U;
        vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v10 = 1U;
    } else {
        if (((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_enable) 
             & (2U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__group_lane_count))) {
            vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v5 
                = ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_reduction_index))
                    ? vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory
                   [(0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_reduction_index)]
                    : 0U);
            vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v5 = 1U;
        }
        if (((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_enable) 
             & (3U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__group_lane_count))) {
            vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v7 
                = ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_reduction_index))
                    ? vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory
                   [(0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_reduction_index)]
                    : 0U);
            vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v7 = 1U;
        }
        if (((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_enable) 
             & (4U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__group_lane_count))) {
            vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v9 
                = ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_reduction_index))
                    ? vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory
                   [(0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_reduction_index)]
                    : 0U);
            vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v9 = 1U;
        }
        if (((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_enable) 
             & (5U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__group_lane_count))) {
            vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v11 
                = ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_reduction_index))
                    ? vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory
                   [(0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_reduction_index)]
                    : 0U);
            vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v11 = 1U;
        }
    }
}

void Vtb_combined___024root___nba_sequent__TOP__38(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_sequent__TOP__38\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if (((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__hard_reset) 
         | (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__abort))) {
        vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v12 = 1U;
        vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v14 = 1U;
    } else {
        if (((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_enable) 
             & (6U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__group_lane_count))) {
            vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v13 
                = ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_reduction_index))
                    ? vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory
                   [(0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_reduction_index)]
                    : 0U);
            vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v13 = 1U;
        }
        if (((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_enable) 
             & (7U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__group_lane_count))) {
            vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v15 
                = ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_reduction_index))
                    ? vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory
                   [(0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_reduction_index)]
                    : 0U);
            vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v15 = 1U;
        }
    }
    if ((1U & (~ ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__hard_reset) 
                  | (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__abort))))) {
        if ((((((9U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state)) 
                & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_valid)) 
               & (0U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mapped_response_error))) 
              & (0U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_lane_index)) 
             & (0x00001200U > vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_reduction_index))) {
            if ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_reduction_index))) {
                vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0 
                    = (0x000000ffU & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_rdata 
                                      >> (0x00000018U 
                                          & ((0x00030210U 
                                              >> ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__request_strobe_latched) 
                                                  << 1U)) 
                                             << 3U))));
                vlSelfRef.__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0 
                    = (0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_reduction_index);
                vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0 = 1U;
            }
        }
    }
}

void Vtb_combined___024root___nba_sequent__TOP__39(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_sequent__TOP__39\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if ((1U & (~ ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__hard_reset) 
                  | (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__abort))))) {
        if ((((((9U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state)) 
                & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_valid)) 
               & (0U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mapped_response_error))) 
              & (1U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_lane_index)) 
             & (0x00001200U > vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_reduction_index))) {
            if ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_reduction_index))) {
                vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0 
                    = (0x000000ffU & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_rdata 
                                      >> (0x00000018U 
                                          & ((0x00030210U 
                                              >> ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__request_strobe_latched) 
                                                  << 1U)) 
                                             << 3U))));
                vlSelfRef.__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0 
                    = (0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_reduction_index);
                vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0 = 1U;
            }
        }
        if ((((((9U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state)) 
                & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_valid)) 
               & (0U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mapped_response_error))) 
              & (2U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_lane_index)) 
             & (0x00001200U > vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_reduction_index))) {
            if ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_reduction_index))) {
                vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0 
                    = (0x000000ffU & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_rdata 
                                      >> (0x00000018U 
                                          & ((0x00030210U 
                                              >> ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__request_strobe_latched) 
                                                  << 1U)) 
                                             << 3U))));
                vlSelfRef.__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0 
                    = (0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_reduction_index);
                vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0 = 1U;
            }
        }
    }
}

void Vtb_combined___024root___nba_sequent__TOP__40(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_sequent__TOP__40\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if ((1U & (~ ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__hard_reset) 
                  | (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__abort))))) {
        if ((((((9U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state)) 
                & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_valid)) 
               & (0U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mapped_response_error))) 
              & (3U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_lane_index)) 
             & (0x00001200U > vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_reduction_index))) {
            if ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_reduction_index))) {
                vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0 
                    = (0x000000ffU & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_rdata 
                                      >> (0x00000018U 
                                          & ((0x00030210U 
                                              >> ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__request_strobe_latched) 
                                                  << 1U)) 
                                             << 3U))));
                vlSelfRef.__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0 
                    = (0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_reduction_index);
                vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0 = 1U;
            }
        }
        if ((((((9U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state)) 
                & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_valid)) 
               & (0U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mapped_response_error))) 
              & (4U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_lane_index)) 
             & (0x00001200U > vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_reduction_index))) {
            if ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_reduction_index))) {
                vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0 
                    = (0x000000ffU & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_rdata 
                                      >> (0x00000018U 
                                          & ((0x00030210U 
                                              >> ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__request_strobe_latched) 
                                                  << 1U)) 
                                             << 3U))));
                vlSelfRef.__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0 
                    = (0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_reduction_index);
                vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0 = 1U;
            }
        }
    }
}

void Vtb_combined___024root___nba_sequent__TOP__41(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_sequent__TOP__41\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if ((1U & (~ ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__hard_reset) 
                  | (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__abort))))) {
        if ((((((9U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state)) 
                & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_valid)) 
               & (0U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mapped_response_error))) 
              & (5U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_lane_index)) 
             & (0x00001200U > vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_reduction_index))) {
            if ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_reduction_index))) {
                vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0 
                    = (0x000000ffU & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_rdata 
                                      >> (0x00000018U 
                                          & ((0x00030210U 
                                              >> ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__request_strobe_latched) 
                                                  << 1U)) 
                                             << 3U))));
                vlSelfRef.__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0 
                    = (0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_reduction_index);
                vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0 = 1U;
            }
        }
        if ((((((9U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state)) 
                & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_valid)) 
               & (0U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mapped_response_error))) 
              & (6U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_lane_index)) 
             & (0x00001200U > vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_reduction_index))) {
            if ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_reduction_index))) {
                vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0 
                    = (0x000000ffU & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_rdata 
                                      >> (0x00000018U 
                                          & ((0x00030210U 
                                              >> ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__request_strobe_latched) 
                                                  << 1U)) 
                                             << 3U))));
                vlSelfRef.__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0 
                    = (0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_reduction_index);
                vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0 = 1U;
            }
        }
    }
}

void Vtb_combined___024root___nba_sequent__TOP__42(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_sequent__TOP__42\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if ((1U & (~ ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__hard_reset) 
                  | (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__abort))))) {
        if ((((((9U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state)) 
                & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_valid)) 
               & (0U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mapped_response_error))) 
              & (7U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_lane_index)) 
             & (0x00001200U > vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_reduction_index))) {
            if ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_reduction_index))) {
                vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0 
                    = (0x000000ffU & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_rdata 
                                      >> (0x00000018U 
                                          & ((0x00030210U 
                                              >> ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__request_strobe_latched) 
                                                  << 1U)) 
                                             << 3U))));
                vlSelfRef.__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0 
                    = (0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_reduction_index);
                vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0 = 1U;
            }
        }
        if ((((((9U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state)) 
                & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_valid)) 
               & (0U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mapped_response_error))) 
              & (0U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_lane_index)) 
             & (0x00001200U > vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_reduction_index))) {
            if ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_reduction_index))) {
                vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0 
                    = (0x000000ffU & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_rdata 
                                      >> (0x00000018U 
                                          & ((0x00030210U 
                                              >> ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__request_strobe_latched) 
                                                  << 1U)) 
                                             << 3U))));
                vlSelfRef.__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0 
                    = (0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_reduction_index);
                vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0 = 1U;
            }
        }
    }
}

void Vtb_combined___024root___nba_sequent__TOP__43(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_sequent__TOP__43\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if ((1U & (~ ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__hard_reset) 
                  | (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__abort))))) {
        if ((((((9U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state)) 
                & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_valid)) 
               & (0U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mapped_response_error))) 
              & (1U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_lane_index)) 
             & (0x00001200U > vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_reduction_index))) {
            if ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_reduction_index))) {
                vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0 
                    = (0x000000ffU & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_rdata 
                                      >> (0x00000018U 
                                          & ((0x00030210U 
                                              >> ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__request_strobe_latched) 
                                                  << 1U)) 
                                             << 3U))));
                vlSelfRef.__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0 
                    = (0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_reduction_index);
                vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0 = 1U;
            }
        }
        if ((((((9U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state)) 
                & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_valid)) 
               & (0U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mapped_response_error))) 
              & (2U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_lane_index)) 
             & (0x00001200U > vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_reduction_index))) {
            if ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_reduction_index))) {
                vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0 
                    = (0x000000ffU & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_rdata 
                                      >> (0x00000018U 
                                          & ((0x00030210U 
                                              >> ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__request_strobe_latched) 
                                                  << 1U)) 
                                             << 3U))));
                vlSelfRef.__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0 
                    = (0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_reduction_index);
                vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0 = 1U;
            }
        }
    }
}

void Vtb_combined___024root___nba_sequent__TOP__44(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_sequent__TOP__44\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if ((1U & (~ ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__hard_reset) 
                  | (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__abort))))) {
        if ((((((9U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state)) 
                & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_valid)) 
               & (0U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mapped_response_error))) 
              & (3U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_lane_index)) 
             & (0x00001200U > vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_reduction_index))) {
            if ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_reduction_index))) {
                vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0 
                    = (0x000000ffU & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_rdata 
                                      >> (0x00000018U 
                                          & ((0x00030210U 
                                              >> ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__request_strobe_latched) 
                                                  << 1U)) 
                                             << 3U))));
                vlSelfRef.__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0 
                    = (0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_reduction_index);
                vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0 = 1U;
            }
        }
        if ((((((9U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state)) 
                & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_valid)) 
               & (0U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mapped_response_error))) 
              & (4U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_lane_index)) 
             & (0x00001200U > vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_reduction_index))) {
            if ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_reduction_index))) {
                vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0 
                    = (0x000000ffU & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_rdata 
                                      >> (0x00000018U 
                                          & ((0x00030210U 
                                              >> ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__request_strobe_latched) 
                                                  << 1U)) 
                                             << 3U))));
                vlSelfRef.__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0 
                    = (0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_reduction_index);
                vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0 = 1U;
            }
        }
    }
}

void Vtb_combined___024root___nba_sequent__TOP__45(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_sequent__TOP__45\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if ((1U & (~ ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__hard_reset) 
                  | (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__abort))))) {
        if ((((((9U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state)) 
                & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_valid)) 
               & (0U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mapped_response_error))) 
              & (5U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_lane_index)) 
             & (0x00001200U > vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_reduction_index))) {
            if ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_reduction_index))) {
                vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0 
                    = (0x000000ffU & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_rdata 
                                      >> (0x00000018U 
                                          & ((0x00030210U 
                                              >> ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__request_strobe_latched) 
                                                  << 1U)) 
                                             << 3U))));
                vlSelfRef.__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0 
                    = (0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_reduction_index);
                vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0 = 1U;
            }
        }
        if ((((((9U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state)) 
                & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_valid)) 
               & (0U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mapped_response_error))) 
              & (6U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_lane_index)) 
             & (0x00001200U > vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_reduction_index))) {
            if ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_reduction_index))) {
                vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0 
                    = (0x000000ffU & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_rdata 
                                      >> (0x00000018U 
                                          & ((0x00030210U 
                                              >> ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__request_strobe_latched) 
                                                  << 1U)) 
                                             << 3U))));
                vlSelfRef.__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0 
                    = (0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_reduction_index);
                vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0 = 1U;
            }
        }
    }
}

void Vtb_combined___024root___nba_sequent__TOP__46(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_sequent__TOP__46\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if ((1U & (~ ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__hard_reset) 
                  | (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__abort))))) {
        if ((((((9U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state)) 
                & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_valid)) 
               & (0U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mapped_response_error))) 
              & (7U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_lane_index)) 
             & (0x00001200U > vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_reduction_index))) {
            if ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_reduction_index))) {
                vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0 
                    = (0x000000ffU & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_rdata 
                                      >> (0x00000018U 
                                          & ((0x00030210U 
                                              >> ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__request_strobe_latched) 
                                                  << 1U)) 
                                             << 3U))));
                vlSelfRef.__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0 
                    = (0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_reduction_index);
                vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0 = 1U;
            }
        }
    }
    if (vlSelfRef.tb_combined__DOT__boundary_test__DOT__hard_reset) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_read_in_bounds = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_read_in_bounds = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_read_data = 0U;
    } else if (vlSelfRef.tb_combined__DOT__boundary_test__DOT__abort) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_read_in_bounds = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_read_in_bounds = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_read_data = 0U;
    } else {
        if (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_enable) {
            if (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_tap_in_bounds) {
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_read_in_bounds = 1U;
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_read_data 
                    = ((0xc7ffU >= (0x0000ffffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_feature_index))
                        ? vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_patch
                       [(0x0000ffffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_feature_index)]
                        : 0U);
            } else {
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_read_in_bounds = 0U;
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_read_data = 0U;
            }
        }
        if (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_enable) {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_read_in_bounds 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_tap_in_bounds;
        }
    }
}

void Vtb_combined___024root___nba_sequent__TOP__47(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_sequent__TOP__47\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if (vlSelfRef.tb_combined__DOT__boundary_test__DOT__hard_reset) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_read_data = 0U;
    } else if (vlSelfRef.tb_combined__DOT__boundary_test__DOT__abort) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_read_data = 0U;
    } else if (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_enable) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_read_data 
            = ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_tap_in_bounds)
                ? ((0xc7ffU >= (0x0000ffffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_feature_index))
                    ? vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_patch
                   [(0x0000ffffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_feature_index)]
                    : 0U) : 0U);
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v0) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte[0U] = 0U;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v1) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte[0U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v1;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v2) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte[1U] = 0U;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v3) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte[1U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v3;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v4) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte[2U] = 0U;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v5) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte[2U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v5;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v6) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte[3U] = 0U;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v7) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte[3U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v7;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v8) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte[4U] = 0U;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v9) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte[4U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v9;
    }
}

void Vtb_combined___024root___nba_sequent__TOP__48(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_sequent__TOP__48\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v10) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte[5U] = 0U;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v11) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte[5U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v11;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v12) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte[6U] = 0U;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v13) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte[6U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v13;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v14) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte[7U] = 0U;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v15) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte[7U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte__v15;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v0) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte[0U] = 0U;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v1) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte[0U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v1;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v2) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte[1U] = 0U;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v3) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte[1U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v3;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v4) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte[2U] = 0U;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v5) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte[2U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v5;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v6) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte[3U] = 0U;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v7) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte[3U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v7;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v8) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte[4U] = 0U;
    }
}

void Vtb_combined___024root___nba_sequent__TOP__49(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_sequent__TOP__49\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v9) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte[4U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v9;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v10) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte[5U] = 0U;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v11) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte[5U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v11;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v12) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte[6U] = 0U;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v13) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte[6U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v13;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v14) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte[7U] = 0U;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v15) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte[7U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte__v15;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory[vlSelfRef.__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory[vlSelfRef.__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory[vlSelfRef.__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory[vlSelfRef.__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory[vlSelfRef.__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory[vlSelfRef.__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory[vlSelfRef.__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory[vlSelfRef.__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0;
    }
}

void Vtb_combined___024root___nba_sequent__TOP__50(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_sequent__TOP__50\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    VlWide<4>/*127:0*/ __Vtemp_1;
    // Body
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory[vlSelfRef.__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory[vlSelfRef.__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory[vlSelfRef.__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory[vlSelfRef.__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory[vlSelfRef.__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory[vlSelfRef.__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory[vlSelfRef.__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory[vlSelfRef.__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0;
    }
    if (vlSelfRef.tb_combined__DOT__boundary_test__DOT__hard_reset) {
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__layer_index_latched = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_layer_index_latched = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__input_base_latched = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__input_length_latched = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__input_batch_count_latched = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__input_channels_latched = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__input_height_latched = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__input_width_latched = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_base_latched = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_length_latched = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_batch_count_latched = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_channels_latched = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_height_latched = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_width_latched = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__kernel_height_latched = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__kernel_width_latched = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__stride_y_latched = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__stride_x_latched = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__pad_left_latched = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__pad_right_latched = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__pad_top_latched = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__pad_bottom_latched = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__groups_latched = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__padding_latched = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_package_base_latched = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_package_length_latched = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__quantized_weight_offset_latched = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__quantized_weight_bytes_latched = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_batch_latched = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__activation_mode_latched = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__reduction_count_latched = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_group_base = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_start_y = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_start_x = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_height = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_width = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__patch_height = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__patch_width = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__patch_byte_count = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_point_count = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__group_lane_count = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_index = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_channel = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_y = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_x = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_lane_index = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_reduction_index = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_point_index = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_point_scan_y = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_point_scan_x = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_reduction_index = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_input_channel = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_kernel_y = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_kernel_x = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_lane_index = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_point_index = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_point_scan_y = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_point_scan_x = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_lane = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_lane_index = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__request_address_latched = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__request_strobe_latched = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__request_wdata_latched = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__result_error_latched = 0U;
        vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter__v0 = 1U;
    } else if (vlSelfRef.tb_combined__DOT__boundary_test__DOT__abort) {
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__reduction_count_latched = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_index = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_channel = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_y = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_x = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_lane_index = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_reduction_index = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_point_index = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_point_scan_y = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_point_scan_x = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_reduction_index = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_input_channel = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_kernel_y = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_kernel_x = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_lane_index = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_point_index = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_point_scan_y = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_point_scan_x = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_lane = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_lane_index = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__request_strobe_latched = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__request_wdata_latched = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__result_error_latched = 0U;
        vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter__v8 = 1U;
    } else {
        if (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_advance) {
            if ((((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_x) 
                 >= vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__patch_width)) {
                if ((((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_y) 
                     >= vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__patch_height)) {
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_channel 
                        = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_channel);
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_y = 0U;
                } else {
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_y 
                        = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_y);
                }
                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_x = 0U;
            } else {
                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_x 
                    = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_x);
            }
        }
        if ((0x00000010U & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state))) {
            if ((8U & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state))) {
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__result_error_latched = 6U;
                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state = 0x13U;
            } else if ((4U & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state))) {
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__result_error_latched = 6U;
                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state = 0x13U;
            } else if ((2U & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state))) {
                if ((1U & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state))) {
                    if (((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__result_valid) 
                         & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__result_ready))) {
                        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__result_error_latched = 0U;
                        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state = 0U;
                    }
                } else if ((((IData)(8U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_group_base) 
                            < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_channels_latched)) {
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_group_base 
                        = ((IData)(8U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_group_base);
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state = 6U;
                } else if (((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_start_x 
                             + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_width) 
                            < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_width_latched)) {
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_start_x 
                        = ((IData)(8U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_start_x);
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_group_base = 0U;
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state = 2U;
                } else if (((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_start_y 
                             + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_height) 
                            < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_height_latched)) {
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_start_y 
                        = ((IData)(8U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_start_y);
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_group_base = 0U;
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_start_x = 0U;
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state = 2U;
                } else {
                    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__result_error_latched = 0U;
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state = 0x13U;
                }
            } else if ((1U & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state))) {
                if (vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_valid) {
                    if ((0U != (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mapped_response_error))) {
                        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__result_error_latched 
                            = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mapped_response_error;
                        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state = 0x13U;
                    } else {
                        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_point_index 
                            = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_point_index);
                        if ((((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_point_scan_x) 
                             >= vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_width)) {
                            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_point_scan_y 
                                = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_point_scan_y);
                            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_point_scan_x = 0U;
                        } else {
                            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_point_scan_x 
                                = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_point_scan_x);
                        }
                        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state = 0x0fU;
                    }
                }
            } else if (((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_valid) 
                        & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_ready))) {
                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state = 0x11U;
            }
        } else if ((8U & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state))) {
            if ((4U & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state))) {
                if ((2U & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state))) {
                    if ((1U & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state))) {
                        if ((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_lane_index 
                             >= vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__group_lane_count)) {
                            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state = 0x12U;
                        } else if ((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_point_index 
                                    >= vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_point_count)) {
                            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_lane_index 
                                = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_lane_index);
                            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_point_index = 0U;
                            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_point_scan_y = 0U;
                            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_point_scan_x = 0U;
                        } else {
                            __Vtemp_1[0U] = (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_byte_offset_wide);
                            __Vtemp_1[1U] = (IData)(
                                                    (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_byte_offset_wide 
                                                     >> 0x00000020U));
                            __Vtemp_1[2U] = 0U;
                            __Vtemp_1[3U] = 0U;
                            if (((0x00000000ffffffffULL 
                                  < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_address_wide) 
                                 | VL_GTE_W(4, __Vtemp_1, vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_elements_wide))) {
                                vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__result_error_latched = 2U;
                                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state = 0x13U;
                            } else {
                                vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__request_address_latched 
                                    = ((IData)((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_address_wide 
                                                >> 2U)) 
                                       << 2U);
                                vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__request_strobe_latched 
                                    = (0x0000000fU 
                                       & ((IData)(1U) 
                                          << (3U & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_address_wide))));
                                vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__request_wdata_latched 
                                    = VL_SHIFTL_III(32,32,32, vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_block
                                                    [
                                                    (0x000001ffU 
                                                     & ((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_lane_index 
                                                         << 6U) 
                                                        + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_point_index))], 
                                                    (0x00000018U 
                                                     & ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_address_wide) 
                                                        << 3U)));
                                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state = 0x10U;
                            }
                        }
                    } else {
                        if ((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_lane_index 
                             < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__group_lane_count)) {
                            vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_block__v0 
                                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requantized_value;
                            vlSelfRef.__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_block__v0 
                                = (0x000001ffU & ((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_lane_index 
                                                   << 6U) 
                                                  + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_point_index));
                            vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_block__v0 = 1U;
                        }
                        if ((((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_lane_index) 
                             >= vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__group_lane_count)) {
                            if ((((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_point_index) 
                                 >= vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_point_count)) {
                                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_lane_index = 0U;
                                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_point_index = 0U;
                                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_point_scan_y = 0U;
                                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_point_scan_x = 0U;
                                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state = 0x0fU;
                            } else {
                                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_point_index 
                                    = ((IData)(1U) 
                                       + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_point_index);
                                if ((((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_point_scan_x) 
                                     >= vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_width)) {
                                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_point_scan_y 
                                        = ((IData)(1U) 
                                           + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_point_scan_y);
                                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_point_scan_x = 0U;
                                } else {
                                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_point_scan_x 
                                        = ((IData)(1U) 
                                           + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_point_scan_x);
                                }
                                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_reduction_index = 0U;
                                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state = 0x0cU;
                            }
                        } else {
                            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_lane_index 
                                = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_lane_index);
                        }
                    }
                } else if ((1U & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state))) {
                    if (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_bad_argument) {
                        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__result_error_latched = 1U;
                        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state = 0x13U;
                    } else if (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_overflow) {
                        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__result_error_latched = 7U;
                        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state = 0x13U;
                    } else {
                        if ((0U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__group_lane_count)) {
                            vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v0 
                                = (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_sum[0U]);
                            vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v0 = 1U;
                        }
                        if ((((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_reduction_index) 
                             >= vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__reduction_count_latched)) {
                            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_lane_index = 0U;
                            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state = 0x0eU;
                        } else {
                            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_reduction_index 
                                = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_reduction_index);
                            if ((((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_kernel_x) 
                                 >= vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__kernel_width_latched)) {
                                if ((((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_kernel_y) 
                                     >= vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__kernel_height_latched)) {
                                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_input_channel 
                                        = ((IData)(1U) 
                                           + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_input_channel);
                                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_kernel_y = 0U;
                                } else {
                                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_kernel_y 
                                        = ((IData)(1U) 
                                           + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_kernel_y);
                                }
                                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_kernel_x = 0U;
                            } else {
                                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_kernel_x 
                                    = ((IData)(1U) 
                                       + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_kernel_x);
                            }
                        }
                        if ((1U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__group_lane_count)) {
                            vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v1 
                                = (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_sum[1U]);
                            vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v1 = 1U;
                        }
                        if ((2U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__group_lane_count)) {
                            vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v2 
                                = (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_sum[2U]);
                            vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v2 = 1U;
                        }
                        if ((3U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__group_lane_count)) {
                            vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v3 
                                = (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_sum[3U]);
                            vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v3 = 1U;
                        }
                        if ((4U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__group_lane_count)) {
                            vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v4 
                                = (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_sum[4U]);
                            vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v4 = 1U;
                        }
                        if ((5U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__group_lane_count)) {
                            vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v5 
                                = (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_sum[5U]);
                            vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v5 = 1U;
                        }
                        if ((6U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__group_lane_count)) {
                            vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v6 
                                = (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_sum[6U]);
                            vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v6 = 1U;
                        }
                        if ((7U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__group_lane_count)) {
                            vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v7 
                                = (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_sum[7U]);
                            vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v7 = 1U;
                        }
                    }
                } else {
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_input_channel = 0U;
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_kernel_y = 0U;
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_kernel_x = 0U;
                    vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v8 
                        = ((0U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_bias[0U]
                            : 0U);
                    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v8 = 1U;
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_reduction_index = 0U;
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state = 0x0dU;
                    vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v9 
                        = ((1U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_bias[1U]
                            : 0U);
                    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v9 = 1U;
                    vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v10 
                        = ((2U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_bias[2U]
                            : 0U);
                    vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v11 
                        = ((3U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_bias[3U]
                            : 0U);
                    vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v12 
                        = ((4U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_bias[4U]
                            : 0U);
                    vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v13 
                        = ((5U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_bias[5U]
                            : 0U);
                    vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v14 
                        = ((6U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_bias[6U]
                            : 0U);
                    vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v15 
                        = ((7U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_bias[7U]
                            : 0U);
                }
            } else if ((2U & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state))) {
                if ((1U & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state))) {
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_input_channel = 0U;
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_kernel_y = 0U;
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_kernel_x = 0U;
                    vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v16 
                        = ((0U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_bias[0U]
                            : 0U);
                    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v16 = 1U;
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_point_index = 0U;
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_reduction_index = 0U;
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state = 0x0dU;
                    vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v17 
                        = ((1U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_bias[1U]
                            : 0U);
                    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v17 = 1U;
                    vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v18 
                        = ((2U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_bias[2U]
                            : 0U);
                    vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v19 
                        = ((3U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_bias[3U]
                            : 0U);
                    vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v20 
                        = ((4U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_bias[4U]
                            : 0U);
                    vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v21 
                        = ((5U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_bias[5U]
                            : 0U);
                    vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v22 
                        = ((6U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_bias[6U]
                            : 0U);
                    vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v23 
                        = ((7U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_bias[7U]
                            : 0U);
                } else if (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_invalid) {
                    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__result_error_latched = 1U;
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state = 0x13U;
                } else {
                    vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter__v16[0U] 
                        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_parameter[0U];
                    vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter__v16[1U] 
                        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_parameter[1U];
                    vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter__v16[2U] 
                        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_parameter[2U];
                    vlSelfRef.__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter__v16 
                        = (7U & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_lane);
                    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter__v16 = 1U;
                    vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_bias__v16 
                        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_bias;
                    vlSelfRef.__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_bias__v16 
                        = (7U & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_lane);
                    if ((((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_lane) 
                         >= vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__group_lane_count)) {
                        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state = 0x0bU;
                    } else {
                        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_lane 
                            = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_lane);
                    }
                }
            } else if ((1U & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state))) {
                if (vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_valid) {
                    if ((0U != (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mapped_response_error))) {
                        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__result_error_latched 
                            = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mapped_response_error;
                        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state = 0x13U;
                    } else {
                        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_reduction_index 
                            = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_reduction_index);
                        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state = 7U;
                    }
                }
            } else if (((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_valid) 
                        & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_ready))) {
                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state = 9U;
            }
        } else if ((4U & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state))) {
            if ((2U & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state))) {
                if ((1U & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state))) {
                    if ((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_lane_index 
                         >= vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__group_lane_count)) {
                        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_lane = 0U;
                        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state = 0x0aU;
                    } else if ((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_reduction_index 
                                >= vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__reduction_count_latched)) {
                        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_lane_index 
                            = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_lane_index);
                        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_reduction_index = 0U;
                    } else if ((0x00000000ffffffffULL 
                                < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_source_address_wide)) {
                        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__result_error_latched = 2U;
                        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state = 0x13U;
                    } else {
                        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__request_address_latched 
                            = ((IData)((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_source_address_wide 
                                        >> 2U)) << 2U);
                        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__request_strobe_latched 
                            = (0x0000000fU & ((IData)(1U) 
                                              << (3U 
                                                  & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_source_address_wide))));
                        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__request_wdata_latched = 0U;
                        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state = 8U;
                    }
                } else if ((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_group_base 
                            >= vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_channels_latched)) {
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state = 0x12U;
                } else {
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__group_lane_count 
                        = ((8U <= (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_channels_latched 
                                   - vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_group_base))
                            ? 8U : (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_channels_latched 
                                    - vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_group_base));
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_point_scan_y = 0U;
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_point_scan_x = 0U;
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_lane_index = 0U;
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_reduction_index = 0U;
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_lane = 0U;
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state = 7U;
                }
            } else if ((1U & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state))) {
                if (vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_valid) {
                    if ((0U != (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mapped_response_error))) {
                        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__result_error_latched 
                            = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mapped_response_error;
                        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state = 0x13U;
                    } else {
                        if ((0xc7ffU >= (0x0000ffffU 
                                         & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_index))) {
                            vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_patch__v0 
                                = (0x000000ffU & VL_SHIFTR_III(8,32,32, vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_rdata, 
                                                               ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__request_byte_lane) 
                                                                << 3U)));
                            vlSelfRef.__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_patch__v0 
                                = (0x0000ffffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_index);
                            vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_patch__v0 = 1U;
                        }
                        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state = 3U;
                        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_index 
                            = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_index);
                    }
                }
            } else if (((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_valid) 
                        & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_ready))) {
                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state = 5U;
            }
        } else if ((2U & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state))) {
            if ((1U & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state))) {
                if ((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_index 
                     >= vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__patch_byte_count)) {
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_group_base = 0U;
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state = 6U;
                } else if (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_in_bounds) {
                    if ((0x00000000ffffffffULL < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_source_address_wide)) {
                        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__result_error_latched = 2U;
                        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state = 0x13U;
                    } else {
                        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__request_address_latched 
                            = ((IData)((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_source_address_wide 
                                        >> 2U)) << 2U);
                        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__request_strobe_latched 
                            = (0x0000000fU & ((IData)(1U) 
                                              << (3U 
                                                  & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_source_address_wide))));
                        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__request_wdata_latched = 0U;
                        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state = 4U;
                    }
                } else {
                    if ((0xc7ffU >= (0x0000ffffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_index))) {
                        vlSelfRef.__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_patch__v1 
                            = (0x0000ffffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_index);
                        vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_patch__v1 = 1U;
                    }
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_index 
                        = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_index);
                }
            } else {
                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_height 
                    = ((8U <= (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_height_latched 
                               - vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_start_y))
                        ? 8U : (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_height_latched 
                                - vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_start_y));
                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_channel = 0U;
                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_y = 0U;
                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_x = 0U;
                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_point_scan_y = 0U;
                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_point_scan_x = 0U;
                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_index = 0U;
                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state = 3U;
                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_width 
                    = ((8U <= (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_width_latched 
                               - vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_start_x))
                        ? 8U : (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_width_latched 
                                - vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_start_x));
                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__patch_height 
                    = (((((8U <= (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_height_latched 
                                  - vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_start_y))
                           ? 8U : (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_height_latched 
                                   - vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_start_y)) 
                         - (IData)(1U)) * vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__stride_y_latched) 
                       + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__kernel_height_latched);
                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__patch_width 
                    = (((((8U <= (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_width_latched 
                                  - vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_start_x))
                           ? 8U : (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_width_latched 
                                   - vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_start_x)) 
                         - (IData)(1U)) * vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__stride_x_latched) 
                       + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__kernel_width_latched);
                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__patch_byte_count 
                    = (((((((8U <= (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_height_latched 
                                    - vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_start_y))
                             ? 8U : (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_height_latched 
                                     - vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_start_y)) 
                           - (IData)(1U)) * vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__stride_y_latched) 
                         + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__kernel_height_latched) 
                        * (((((8U <= (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_width_latched 
                                      - vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_start_x))
                               ? 8U : (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_width_latched 
                                       - vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_start_x)) 
                             - (IData)(1U)) * vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__stride_x_latched) 
                           + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__kernel_width_latched)) 
                       * vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__input_channels_latched);
                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_point_count 
                    = (((8U <= (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_height_latched 
                                - vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_start_y))
                         ? 8U : (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_height_latched 
                                 - vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_start_y)) 
                       * ((8U <= (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_width_latched 
                                  - vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_start_x))
                           ? 8U : (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_width_latched 
                                   - vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_start_x)));
            }
        } else if ((1U & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state))) {
            if (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__validation_ok) {
                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__reduction_count_latched 
                    = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__reduction_count_wide[0U];
                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state = 2U;
            } else {
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__result_error_latched 
                    = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__validation_error;
                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state = 0x13U;
            }
        } else if (((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__start_valid) 
                    & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__start_ready))) {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__layer_index_latched 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__layer_index;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_layer_index_latched 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__weight_layer_index;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__input_base_latched 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__input_base_address;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__input_length_latched 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__input_length_bytes;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__input_batch_count_latched 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__input_batch_count;
            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__input_channels_latched 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__input_channels;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__input_height_latched 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__input_height;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__input_width_latched 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__input_width;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_base_latched 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__output_base_address;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_length_latched 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__output_length_bytes;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_batch_count_latched 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__output_batch_count;
            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_channels_latched 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__output_channels;
            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_height_latched 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__output_height;
            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_width_latched 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__output_width;
            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__kernel_height_latched 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__kernel_height;
            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__kernel_width_latched 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__kernel_width;
            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__stride_y_latched 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__stride_y;
            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__stride_x_latched 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__stride_x;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__pad_left_latched 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__pad_left;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__pad_right_latched 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__pad_right;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__pad_top_latched 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__pad_top;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__pad_bottom_latched 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__pad_bottom;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__groups_latched 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__groups;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__padding_latched 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__padding_value_int8;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_package_base_latched 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__weight_package_base_address;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_package_length_latched 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__weight_package_length_bytes;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__quantized_weight_offset_latched 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__quantized_weight_offset;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__quantized_weight_bytes_latched 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__quantized_weight_bytes;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_batch_latched 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__output_batch;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__activation_mode_latched 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__activation_mode;
            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__reduction_count_latched = 0U;
            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_group_base = 0U;
            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_start_y = 0U;
            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_start_x = 0U;
            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_index = 0U;
            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_channel = 0U;
            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_y = 0U;
            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_x = 0U;
            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_lane_index = 0U;
            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_reduction_index = 0U;
            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_point_index = 0U;
            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_point_scan_y = 0U;
            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_point_scan_x = 0U;
            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_reduction_index = 0U;
            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_input_channel = 0U;
            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_kernel_y = 0U;
            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_kernel_x = 0U;
            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_lane_index = 0U;
            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_point_index = 0U;
            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_point_scan_y = 0U;
            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_point_scan_x = 0U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__result_error_latched = 0U;
            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state = 1U;
        }
    }
}

void Vtb_combined___024root___nba_sequent__TOP__51(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_sequent__TOP__51\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    VlWide<4>/*127:0*/ __Vtemp_1;
    // Body
    if (vlSelfRef.tb_combined__DOT__boundary_test__DOT__hard_reset) {
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__layer_index_latched = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_layer_index_latched = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__input_base_latched = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__input_length_latched = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__input_batch_count_latched = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__input_channels_latched = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__input_height_latched = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__input_width_latched = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_base_latched = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_length_latched = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_batch_count_latched = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_channels_latched = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_height_latched = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_width_latched = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__kernel_height_latched = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__kernel_width_latched = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__stride_y_latched = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__stride_x_latched = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__pad_left_latched = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__pad_right_latched = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__pad_top_latched = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__pad_bottom_latched = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__groups_latched = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__padding_latched = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_package_base_latched = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_package_length_latched = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__quantized_weight_offset_latched = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__quantized_weight_bytes_latched = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_batch_latched = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__activation_mode_latched = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__reduction_count_latched = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_group_base = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_start_y = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_start_x = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_height = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_width = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__patch_height = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__patch_width = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__patch_byte_count = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_point_count = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__group_lane_count = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_index = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_channel = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_y = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_x = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_lane_index = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_reduction_index = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_point_index = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_point_scan_y = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_point_scan_x = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_reduction_index = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_input_channel = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_kernel_y = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_kernel_x = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_lane_index = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_point_index = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_point_scan_y = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_point_scan_x = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_lane = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_lane_index = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__request_address_latched = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__request_strobe_latched = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__request_wdata_latched = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__result_error_latched = 0U;
        vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter__v0 = 1U;
    } else if (vlSelfRef.tb_combined__DOT__boundary_test__DOT__abort) {
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__reduction_count_latched = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_index = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_channel = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_y = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_x = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_lane_index = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_reduction_index = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_point_index = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_point_scan_y = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_point_scan_x = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_reduction_index = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_input_channel = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_kernel_y = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_kernel_x = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_lane_index = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_point_index = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_point_scan_y = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_point_scan_x = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_lane = 0U;
        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_lane_index = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__request_strobe_latched = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__request_wdata_latched = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__result_error_latched = 0U;
        vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter__v8 = 1U;
    } else {
        if (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_advance) {
            if ((((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_x) 
                 >= vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__patch_width)) {
                if ((((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_y) 
                     >= vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__patch_height)) {
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_channel 
                        = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_channel);
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_y = 0U;
                } else {
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_y 
                        = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_y);
                }
                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_x = 0U;
            } else {
                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_x 
                    = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_x);
            }
        }
        if ((0x00000010U & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state))) {
            if ((8U & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state))) {
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__result_error_latched = 6U;
                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state = 0x13U;
            } else if ((4U & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state))) {
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__result_error_latched = 6U;
                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state = 0x13U;
            } else if ((2U & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state))) {
                if ((1U & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state))) {
                    if (((0x13U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state)) 
                         & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__result_ready))) {
                        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__result_error_latched = 0U;
                        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state = 0U;
                    }
                } else if ((((IData)(8U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_group_base) 
                            < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_channels_latched)) {
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_group_base 
                        = ((IData)(8U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_group_base);
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state = 6U;
                } else if (((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_start_x 
                             + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_width) 
                            < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_width_latched)) {
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_start_x 
                        = ((IData)(8U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_start_x);
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_group_base = 0U;
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state = 2U;
                } else if (((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_start_y 
                             + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_height) 
                            < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_height_latched)) {
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_start_y 
                        = ((IData)(8U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_start_y);
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_group_base = 0U;
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_start_x = 0U;
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state = 2U;
                } else {
                    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__result_error_latched = 0U;
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state = 0x13U;
                }
            } else if ((1U & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state))) {
                if (vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_valid) {
                    if ((0U != (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mapped_response_error))) {
                        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__result_error_latched 
                            = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mapped_response_error;
                        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state = 0x13U;
                    } else {
                        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_point_index 
                            = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_point_index);
                        if ((((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_point_scan_x) 
                             >= vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_width)) {
                            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_point_scan_y 
                                = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_point_scan_y);
                            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_point_scan_x = 0U;
                        } else {
                            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_point_scan_x 
                                = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_point_scan_x);
                        }
                        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state = 0x0fU;
                    }
                }
            } else if (((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__candidate_backend_req_valid) 
                        & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_ready))) {
                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state = 0x11U;
            }
        } else if ((8U & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state))) {
            if ((4U & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state))) {
                if ((2U & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state))) {
                    if ((1U & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state))) {
                        if ((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_lane_index 
                             >= vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__group_lane_count)) {
                            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state = 0x12U;
                        } else if ((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_point_index 
                                    >= vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_point_count)) {
                            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_lane_index 
                                = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_lane_index);
                            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_point_index = 0U;
                            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_point_scan_y = 0U;
                            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_point_scan_x = 0U;
                        } else {
                            __Vtemp_1[0U] = (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_byte_offset_wide);
                            __Vtemp_1[1U] = (IData)(
                                                    (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_byte_offset_wide 
                                                     >> 0x00000020U));
                            __Vtemp_1[2U] = 0U;
                            __Vtemp_1[3U] = 0U;
                            if (((0x00000000ffffffffULL 
                                  < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_address_wide) 
                                 | VL_GTE_W(4, __Vtemp_1, vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_elements_wide))) {
                                vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__result_error_latched = 2U;
                                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state = 0x13U;
                            } else {
                                vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__request_address_latched 
                                    = ((IData)((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_address_wide 
                                                >> 2U)) 
                                       << 2U);
                                vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__request_strobe_latched 
                                    = (0x0000000fU 
                                       & ((IData)(1U) 
                                          << (3U & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_address_wide))));
                                vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__request_wdata_latched 
                                    = VL_SHIFTL_III(32,32,32, vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_block
                                                    [
                                                    (0x000001ffU 
                                                     & ((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_lane_index 
                                                         << 6U) 
                                                        + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_point_index))], 
                                                    (0x00000018U 
                                                     & ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_address_wide) 
                                                        << 3U)));
                                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state = 0x10U;
                            }
                        }
                    } else {
                        if ((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_lane_index 
                             < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__group_lane_count)) {
                            vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_block__v0 
                                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requantized_value;
                            vlSelfRef.__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_block__v0 
                                = (0x000001ffU & ((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_lane_index 
                                                   << 6U) 
                                                  + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_point_index));
                            vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_block__v0 = 1U;
                        }
                        if ((((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_lane_index) 
                             >= vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__group_lane_count)) {
                            if ((((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_point_index) 
                                 >= vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_point_count)) {
                                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_lane_index = 0U;
                                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_point_index = 0U;
                                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_point_scan_y = 0U;
                                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_point_scan_x = 0U;
                                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state = 0x0fU;
                            } else {
                                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_point_index 
                                    = ((IData)(1U) 
                                       + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_point_index);
                                if ((((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_point_scan_x) 
                                     >= vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_width)) {
                                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_point_scan_y 
                                        = ((IData)(1U) 
                                           + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_point_scan_y);
                                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_point_scan_x = 0U;
                                } else {
                                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_point_scan_x 
                                        = ((IData)(1U) 
                                           + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_point_scan_x);
                                }
                                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_reduction_index = 0U;
                                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state = 0x0cU;
                            }
                        } else {
                            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_lane_index 
                                = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_lane_index);
                        }
                    }
                } else if ((1U & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state))) {
                    if (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_bad_argument) {
                        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__result_error_latched = 1U;
                        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state = 0x13U;
                    } else if (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_overflow) {
                        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__result_error_latched = 7U;
                        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state = 0x13U;
                    } else {
                        if ((0U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__group_lane_count)) {
                            vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v0 
                                = (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_sum[0U]);
                            vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v0 = 1U;
                        }
                        if ((((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_reduction_index) 
                             >= vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__reduction_count_latched)) {
                            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_lane_index = 0U;
                            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state = 0x0eU;
                        } else {
                            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_reduction_index 
                                = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_reduction_index);
                            if ((((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_kernel_x) 
                                 >= vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__kernel_width_latched)) {
                                if ((((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_kernel_y) 
                                     >= vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__kernel_height_latched)) {
                                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_input_channel 
                                        = ((IData)(1U) 
                                           + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_input_channel);
                                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_kernel_y = 0U;
                                } else {
                                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_kernel_y 
                                        = ((IData)(1U) 
                                           + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_kernel_y);
                                }
                                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_kernel_x = 0U;
                            } else {
                                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_kernel_x 
                                    = ((IData)(1U) 
                                       + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_kernel_x);
                            }
                        }
                        if ((1U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__group_lane_count)) {
                            vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v1 
                                = (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_sum[1U]);
                            vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v1 = 1U;
                        }
                        if ((2U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__group_lane_count)) {
                            vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v2 
                                = (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_sum[2U]);
                            vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v2 = 1U;
                        }
                        if ((3U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__group_lane_count)) {
                            vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v3 
                                = (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_sum[3U]);
                            vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v3 = 1U;
                        }
                        if ((4U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__group_lane_count)) {
                            vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v4 
                                = (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_sum[4U]);
                            vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v4 = 1U;
                        }
                        if ((5U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__group_lane_count)) {
                            vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v5 
                                = (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_sum[5U]);
                            vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v5 = 1U;
                        }
                        if ((6U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__group_lane_count)) {
                            vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v6 
                                = (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_sum[6U]);
                            vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v6 = 1U;
                        }
                        if ((7U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__group_lane_count)) {
                            vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v7 
                                = (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_sum[7U]);
                            vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v7 = 1U;
                        }
                    }
                } else {
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_input_channel = 0U;
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_kernel_y = 0U;
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_kernel_x = 0U;
                    vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v8 
                        = ((0U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__group_lane_count)
                            ? vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_bias[0U]
                            : 0U);
                    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v8 = 1U;
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_reduction_index = 0U;
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state = 0x0dU;
                    vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v9 
                        = ((1U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__group_lane_count)
                            ? vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_bias[1U]
                            : 0U);
                    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v9 = 1U;
                    vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v10 
                        = ((2U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__group_lane_count)
                            ? vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_bias[2U]
                            : 0U);
                    vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v11 
                        = ((3U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__group_lane_count)
                            ? vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_bias[3U]
                            : 0U);
                    vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v12 
                        = ((4U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__group_lane_count)
                            ? vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_bias[4U]
                            : 0U);
                    vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v13 
                        = ((5U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__group_lane_count)
                            ? vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_bias[5U]
                            : 0U);
                    vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v14 
                        = ((6U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__group_lane_count)
                            ? vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_bias[6U]
                            : 0U);
                    vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v15 
                        = ((7U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__group_lane_count)
                            ? vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_bias[7U]
                            : 0U);
                }
            } else if ((2U & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state))) {
                if ((1U & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state))) {
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_input_channel = 0U;
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_kernel_y = 0U;
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_kernel_x = 0U;
                    vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v16 
                        = ((0U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__group_lane_count)
                            ? vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_bias[0U]
                            : 0U);
                    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v16 = 1U;
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_point_index = 0U;
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_reduction_index = 0U;
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state = 0x0dU;
                    vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v17 
                        = ((1U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__group_lane_count)
                            ? vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_bias[1U]
                            : 0U);
                    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v17 = 1U;
                    vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v18 
                        = ((2U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__group_lane_count)
                            ? vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_bias[2U]
                            : 0U);
                    vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v19 
                        = ((3U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__group_lane_count)
                            ? vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_bias[3U]
                            : 0U);
                    vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v20 
                        = ((4U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__group_lane_count)
                            ? vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_bias[4U]
                            : 0U);
                    vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v21 
                        = ((5U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__group_lane_count)
                            ? vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_bias[5U]
                            : 0U);
                    vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v22 
                        = ((6U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__group_lane_count)
                            ? vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_bias[6U]
                            : 0U);
                    vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v23 
                        = ((7U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__group_lane_count)
                            ? vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_bias[7U]
                            : 0U);
                } else if (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_invalid) {
                    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__result_error_latched = 1U;
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state = 0x13U;
                } else {
                    vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter__v16[0U] 
                        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_parameter[0U];
                    vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter__v16[1U] 
                        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_parameter[1U];
                    vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter__v16[2U] 
                        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_parameter[2U];
                    vlSelfRef.__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter__v16 
                        = (7U & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_lane);
                    vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter__v16 = 1U;
                    vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_bias__v16 
                        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_bias;
                    vlSelfRef.__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_bias__v16 
                        = (7U & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_lane);
                    if ((((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_lane) 
                         >= vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__group_lane_count)) {
                        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state = 0x0bU;
                    } else {
                        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_lane 
                            = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_lane);
                    }
                }
            } else if ((1U & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state))) {
                if (vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_valid) {
                    if ((0U != (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mapped_response_error))) {
                        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__result_error_latched 
                            = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mapped_response_error;
                        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state = 0x13U;
                    } else {
                        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_reduction_index 
                            = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_reduction_index);
                        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state = 7U;
                    }
                }
            } else if (((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__candidate_backend_req_valid) 
                        & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_ready))) {
                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state = 9U;
            }
        } else if ((4U & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state))) {
            if ((2U & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state))) {
                if ((1U & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state))) {
                    if ((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_lane_index 
                         >= vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__group_lane_count)) {
                        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_lane = 0U;
                        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state = 0x0aU;
                    } else if ((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_reduction_index 
                                >= vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__reduction_count_latched)) {
                        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_lane_index 
                            = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_lane_index);
                        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_reduction_index = 0U;
                    } else if ((0x00000000ffffffffULL 
                                < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_source_address_wide)) {
                        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__result_error_latched = 2U;
                        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state = 0x13U;
                    } else {
                        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__request_address_latched 
                            = ((IData)((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_source_address_wide 
                                        >> 2U)) << 2U);
                        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__request_strobe_latched 
                            = (0x0000000fU & ((IData)(1U) 
                                              << (3U 
                                                  & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_source_address_wide))));
                        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__request_wdata_latched = 0U;
                        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state = 8U;
                    }
                } else if ((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_group_base 
                            >= vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_channels_latched)) {
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state = 0x12U;
                } else {
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__group_lane_count 
                        = ((8U <= (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_channels_latched 
                                   - vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_group_base))
                            ? 8U : (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_channels_latched 
                                    - vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_group_base));
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_point_scan_y = 0U;
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_point_scan_x = 0U;
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_lane_index = 0U;
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_reduction_index = 0U;
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_lane = 0U;
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state = 7U;
                }
            } else if ((1U & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state))) {
                if (vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_valid) {
                    if ((0U != (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mapped_response_error))) {
                        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__result_error_latched 
                            = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mapped_response_error;
                        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state = 0x13U;
                    } else {
                        if ((0xc7ffU >= (0x0000ffffU 
                                         & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_index))) {
                            vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_patch__v0 
                                = (0x000000ffU & VL_SHIFTR_III(8,32,32, vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_rdata, 
                                                               ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__request_byte_lane) 
                                                                << 3U)));
                            vlSelfRef.__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_patch__v0 
                                = (0x0000ffffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_index);
                            vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_patch__v0 = 1U;
                        }
                        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state = 3U;
                        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_index 
                            = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_index);
                    }
                }
            } else if (((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__candidate_backend_req_valid) 
                        & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_ready))) {
                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state = 5U;
            }
        } else if ((2U & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state))) {
            if ((1U & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state))) {
                if ((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_index 
                     >= vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__patch_byte_count)) {
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_group_base = 0U;
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state = 6U;
                } else if (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_in_bounds) {
                    if ((0x00000000ffffffffULL < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_source_address_wide)) {
                        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__result_error_latched = 2U;
                        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state = 0x13U;
                    } else {
                        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__request_address_latched 
                            = ((IData)((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_source_address_wide 
                                        >> 2U)) << 2U);
                        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__request_strobe_latched 
                            = (0x0000000fU & ((IData)(1U) 
                                              << (3U 
                                                  & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_source_address_wide))));
                        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__request_wdata_latched = 0U;
                        vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state = 4U;
                    }
                } else {
                    if ((0xc7ffU >= (0x0000ffffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_index))) {
                        vlSelfRef.__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_patch__v1 
                            = (0x0000ffffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_index);
                        vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_patch__v1 = 1U;
                    }
                    vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_index 
                        = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_index);
                }
            } else {
                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_height 
                    = ((8U <= (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_height_latched 
                               - vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_start_y))
                        ? 8U : (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_height_latched 
                                - vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_start_y));
                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_channel = 0U;
                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_y = 0U;
                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_x = 0U;
                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_point_scan_y = 0U;
                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_point_scan_x = 0U;
                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_index = 0U;
                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state = 3U;
                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_width 
                    = ((8U <= (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_width_latched 
                               - vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_start_x))
                        ? 8U : (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_width_latched 
                                - vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_start_x));
                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__patch_height 
                    = (((((8U <= (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_height_latched 
                                  - vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_start_y))
                           ? 8U : (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_height_latched 
                                   - vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_start_y)) 
                         - (IData)(1U)) * vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__stride_y_latched) 
                       + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__kernel_height_latched);
                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__patch_width 
                    = (((((8U <= (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_width_latched 
                                  - vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_start_x))
                           ? 8U : (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_width_latched 
                                   - vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_start_x)) 
                         - (IData)(1U)) * vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__stride_x_latched) 
                       + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__kernel_width_latched);
                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__patch_byte_count 
                    = (((((((8U <= (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_height_latched 
                                    - vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_start_y))
                             ? 8U : (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_height_latched 
                                     - vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_start_y)) 
                           - (IData)(1U)) * vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__stride_y_latched) 
                         + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__kernel_height_latched) 
                        * (((((8U <= (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_width_latched 
                                      - vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_start_x))
                               ? 8U : (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_width_latched 
                                       - vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_start_x)) 
                             - (IData)(1U)) * vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__stride_x_latched) 
                           + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__kernel_width_latched)) 
                       * vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__input_channels_latched);
                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_point_count 
                    = (((8U <= (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_height_latched 
                                - vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_start_y))
                         ? 8U : (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_height_latched 
                                 - vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_start_y)) 
                       * ((8U <= (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_width_latched 
                                  - vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_start_x))
                           ? 8U : (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_width_latched 
                                   - vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_start_x)));
            }
        } else if ((1U & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state))) {
            if (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__validation_ok) {
                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__reduction_count_latched 
                    = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__reduction_count_wide[0U];
                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state = 2U;
            } else {
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__result_error_latched 
                    = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__validation_error;
                vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state = 0x13U;
            }
        } else if (((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__start_valid) 
                    & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__candidate_start_ready))) {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__layer_index_latched 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__layer_index;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_layer_index_latched 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__weight_layer_index;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__input_base_latched 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__input_base_address;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__input_length_latched 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__input_length_bytes;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__input_batch_count_latched 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__input_batch_count;
            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__input_channels_latched 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__input_channels;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__input_height_latched 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__input_height;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__input_width_latched 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__input_width;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_base_latched 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__output_base_address;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_length_latched 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__output_length_bytes;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_batch_count_latched 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__output_batch_count;
            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_channels_latched 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__output_channels;
            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_height_latched 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__output_height;
            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_width_latched 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__output_width;
            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__kernel_height_latched 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__kernel_height;
            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__kernel_width_latched 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__kernel_width;
            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__stride_y_latched 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__stride_y;
            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__stride_x_latched 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__stride_x;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__pad_left_latched 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__pad_left;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__pad_right_latched 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__pad_right;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__pad_top_latched 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__pad_top;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__pad_bottom_latched 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__pad_bottom;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__groups_latched 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__groups;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__padding_latched 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__padding_value_int8;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_package_base_latched 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__weight_package_base_address;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_package_length_latched 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__weight_package_length_bytes;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__quantized_weight_offset_latched 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__quantized_weight_offset;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__quantized_weight_bytes_latched 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__quantized_weight_bytes;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_batch_latched 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__output_batch;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__activation_mode_latched 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__activation_mode;
            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__reduction_count_latched = 0U;
            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_group_base = 0U;
            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_start_y = 0U;
            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_start_x = 0U;
            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_index = 0U;
            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_channel = 0U;
            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_y = 0U;
            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_x = 0U;
            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_lane_index = 0U;
            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_reduction_index = 0U;
            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_point_index = 0U;
            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_point_scan_y = 0U;
            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_point_scan_x = 0U;
            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_reduction_index = 0U;
            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_input_channel = 0U;
            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_kernel_y = 0U;
            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_kernel_x = 0U;
            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_lane_index = 0U;
            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_point_index = 0U;
            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_point_scan_y = 0U;
            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_point_scan_x = 0U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__result_error_latched = 0U;
            vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state = 1U;
        }
    }
}

void Vtb_combined___024root___nba_sequent__TOP__52(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_sequent__TOP__52\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_height 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_height;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_point_count 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_point_count;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_point_index 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_point_index;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_point_index 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_point_index;
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_block__v0) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_block[vlSelfRef.__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_block__v0] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_block__v0;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_patch__v0) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_patch[vlSelfRef.__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_patch__v0] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_patch__v0;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_patch__v1) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_patch[vlSelfRef.__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_patch__v1] = 0U;
    }
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_lane_index 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_lane_index;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_point_scan_y 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_point_scan_y;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_point_scan_x 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_point_scan_x;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_reduction_index 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_reduction_index;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_lane_index 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_lane_index;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_lane 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_lane;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_lane_index 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_lane_index;
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter__v0) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_bias[0U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_bias[1U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_bias[2U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_bias[3U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_bias[4U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_bias[5U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_bias[6U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_bias[7U] = 0U;
    }
}

void Vtb_combined___024root___nba_sequent__TOP__53(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_sequent__TOP__53\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter__v8) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_bias[0U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_bias[1U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_bias[2U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_bias[3U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_bias[4U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_bias[5U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_bias[6U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_bias[7U] = 0U;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter__v16) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_bias[vlSelfRef.__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_bias__v16] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_bias__v16;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter__v0) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter[0U][0U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter[0U][1U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter[0U][2U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter[1U][0U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter[1U][1U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter[1U][2U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter[2U][0U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter[2U][1U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter[2U][2U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter[3U][0U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter[3U][1U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter[3U][2U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter[4U][0U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter[4U][1U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter[4U][2U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter[5U][0U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter[5U][1U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter[5U][2U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter[6U][0U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter[6U][1U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter[6U][2U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter[7U][0U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter[7U][1U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter[7U][2U] = 0U;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter__v8) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter[0U][0U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter[0U][1U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter[0U][2U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter[1U][0U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter[1U][1U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter[1U][2U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter[2U][0U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter[2U][1U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter[2U][2U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter[3U][0U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter[3U][1U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter[3U][2U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter[4U][0U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter[4U][1U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter[4U][2U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter[5U][0U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter[5U][1U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter[5U][2U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter[6U][0U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter[6U][1U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter[6U][2U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter[7U][0U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter[7U][1U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter[7U][2U] = 0U;
    }
}

void Vtb_combined___024root___nba_sequent__TOP__54(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_sequent__TOP__54\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter__v16) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter[vlSelfRef.__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter__v16][0U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter__v16[0U];
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter[vlSelfRef.__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter__v16][1U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter__v16[1U];
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter[vlSelfRef.__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter__v16][2U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter__v16[2U];
    }
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_group_base 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_group_base;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__input_channels_latched 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__input_channels_latched;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_channels_latched 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_channels_latched;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_height_latched 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_height_latched;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_width_latched 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_width_latched;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_width 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_width;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__patch_height 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__patch_height;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__patch_width 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__patch_width;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__patch_byte_count 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__patch_byte_count;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_index 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_index;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_channel 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_channel;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_y 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_y;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_x 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_x;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_point_scan_y 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_point_scan_y;
}

void Vtb_combined___024root___nba_sequent__TOP__55(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_sequent__TOP__55\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_point_scan_x 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_point_scan_x;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_reduction_index 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_reduction_index;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_input_channel 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_input_channel;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_kernel_y 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_kernel_y;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_kernel_x 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_kernel_x;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__reduction_count_latched 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__reduction_count_latched;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_start_y 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_start_y;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_start_x 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_start_x;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__group_lane_count 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__group_lane_count;
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v0) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator[0U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v0;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v1) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator[1U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v1;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v2) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator[2U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v2;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v3) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator[3U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v3;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v4) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator[4U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v4;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v5) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator[5U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v5;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v6) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator[6U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v6;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v7) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator[7U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v7;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v8) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator[0U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v8;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v9) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator[1U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v9;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator[2U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v10;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator[3U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v11;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator[4U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v12;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator[5U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v13;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator[6U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v14;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator[7U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v15;
    }
}

void Vtb_combined___024root___nba_sequent__TOP__56(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_sequent__TOP__56\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v16) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator[0U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v16;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v17) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator[1U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v17;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator[2U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v18;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator[3U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v19;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator[4U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v20;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator[5U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v21;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator[6U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v22;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator[7U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator__v23;
    }
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__kernel_height_latched 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__kernel_height_latched;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__kernel_width_latched 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__kernel_width_latched;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__stride_y_latched 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__stride_y_latched;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__stride_x_latched 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_dut__DOT__stride_x_latched;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_height 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_height;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_point_count 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_point_count;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_point_index 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_point_index;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_point_index 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_point_index;
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_block__v0) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_block[vlSelfRef.__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_block__v0] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_block__v0;
    }
}

void Vtb_combined___024root___nba_sequent__TOP__57(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_sequent__TOP__57\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_patch__v0) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_patch[vlSelfRef.__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_patch__v0] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_patch__v0;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_patch__v1) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_patch[vlSelfRef.__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_patch__v1] = 0U;
    }
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_lane_index 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_lane_index;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_point_scan_y 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_point_scan_y;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_point_scan_x 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_point_scan_x;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_reduction_index 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_reduction_index;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_lane_index 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_lane_index;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_lane 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_lane;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_lane_index 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_lane_index;
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter__v0) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_bias[0U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_bias[1U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_bias[2U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_bias[3U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_bias[4U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_bias[5U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_bias[6U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_bias[7U] = 0U;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter__v8) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_bias[0U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_bias[1U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_bias[2U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_bias[3U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_bias[4U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_bias[5U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_bias[6U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_bias[7U] = 0U;
    }
}

void Vtb_combined___024root___nba_sequent__TOP__58(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_sequent__TOP__58\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter__v0) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter[0U][0U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter[0U][1U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter[0U][2U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter[1U][0U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter[1U][1U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter[1U][2U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter[2U][0U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter[2U][1U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter[2U][2U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter[3U][0U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter[3U][1U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter[3U][2U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter[4U][0U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter[4U][1U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter[4U][2U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter[5U][0U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter[5U][1U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter[5U][2U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter[6U][0U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter[6U][1U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter[6U][2U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter[7U][0U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter[7U][1U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter[7U][2U] = 0U;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter__v8) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter[0U][0U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter[0U][1U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter[0U][2U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter[1U][0U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter[1U][1U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter[1U][2U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter[2U][0U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter[2U][1U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter[2U][2U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter[3U][0U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter[3U][1U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter[3U][2U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter[4U][0U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter[4U][1U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter[4U][2U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter[5U][0U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter[5U][1U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter[5U][2U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter[6U][0U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter[6U][1U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter[6U][2U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter[7U][0U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter[7U][1U] = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter[7U][2U] = 0U;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter__v16) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_bias[vlSelfRef.__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_bias__v16] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_bias__v16;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter[vlSelfRef.__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter__v16][0U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter__v16[0U];
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter[vlSelfRef.__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter__v16][1U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter__v16[1U];
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter[vlSelfRef.__VdlyDim0__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter__v16][2U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter__v16[2U];
    }
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_group_base 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_group_base;
}

void Vtb_combined___024root___nba_sequent__TOP__59(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_sequent__TOP__59\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_width 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_width;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__patch_height 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__patch_height;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__patch_width 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__patch_width;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__patch_byte_count 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__patch_byte_count;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_index 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_index;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_channel 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_channel;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_y 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_y;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_x 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_x;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_point_scan_y 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_point_scan_y;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_point_scan_x 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_point_scan_x;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_reduction_index 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_reduction_index;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_input_channel 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_input_channel;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_kernel_y 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_kernel_y;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_kernel_x 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_kernel_x;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__input_channels_latched 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__input_channels_latched;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_channels_latched 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_channels_latched;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__reduction_count_latched 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__reduction_count_latched;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_start_y 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_start_y;
}

void Vtb_combined___024root___nba_sequent__TOP__60(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_sequent__TOP__60\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_start_x 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_start_x;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_height_latched 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_height_latched;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_width_latched 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_width_latched;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__group_lane_count 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__group_lane_count;
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v0) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator[0U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v0;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v1) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator[1U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v1;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v2) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator[2U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v2;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v3) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator[3U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v3;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v4) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator[4U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v4;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v5) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator[5U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v5;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v6) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator[6U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v6;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v7) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator[7U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v7;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v8) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator[0U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v8;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v9) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator[1U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v9;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator[2U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v10;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator[3U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v11;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator[4U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v12;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator[5U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v13;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator[6U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v14;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator[7U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v15;
    }
}

void Vtb_combined___024root___nba_sequent__TOP__61(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_sequent__TOP__61\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v16) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator[0U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v16;
    }
    if (vlSelfRef.__VdlySet__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v17) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator[1U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v17;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator[2U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v18;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator[3U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v19;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator[4U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v20;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator[5U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v21;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator[6U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v22;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator[7U] 
            = vlSelfRef.__VdlyVal__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator__v23;
    }
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__kernel_height_latched 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__kernel_height_latched;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__kernel_width_latched 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__kernel_width_latched;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__stride_y_latched 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__stride_y_latched;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__stride_x_latched 
        = vlSelfRef.__Vdly__tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__stride_x_latched;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_addr 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__request_address_latched;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_wdata 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__request_wdata_latched;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__result_error_code 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__result_error_latched;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__request_byte_lane 
        = (3U & (0x00030210U >> ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__request_strobe_latched) 
                                 << 1U)));
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_source_address_wide 
        = ((QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_package_base_latched)) 
           + ((QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__quantized_weight_offset_latched)) 
              + ((QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_reduction_index)) 
                 + ((QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__reduction_count_latched)) 
                    * (QData)((IData)((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_group_base 
                                       + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_lane_index)))))));
}

void Vtb_combined___024root___nba_sequent__TOP__62(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_sequent__TOP__62\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    IData/*31:0*/ tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_index;
    tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mq_prefetch_index = 0;
    // Body
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_byte_offset_wide 
        = ((QData)((IData)((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_point_scan_x 
                            + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_start_x))) 
           + ((QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_width_latched)) 
              * ((QData)((IData)((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_point_scan_y 
                                  + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_start_y))) 
                 + ((QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_height_latched)) 
                    * (QData)((IData)((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_group_base 
                                       + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_lane_index)))))));
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__busy 
        = (0U != (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state));
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__result_valid 
        = (0x13U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state));
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

void Vtb_combined___024root___nba_sequent__TOP__63(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_sequent__TOP__63\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    VlWide<3>/*79:0*/ tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_parameter;
    VL_ZERO_W(80, tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_parameter);
    IData/*31:0*/ tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_accumulator;
    tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_accumulator = 0;
    IData/*31:0*/ tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_multiplier;
    tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_multiplier = 0;
    IData/*31:0*/ tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_q_shift;
    tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_q_shift = 0;
    IData/*31:0*/ tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_magnitude;
    tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_magnitude = 0;
    QData/*63:0*/ tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_product;
    tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_product = 0;
    QData/*63:0*/ tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_rounding_add;
    tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_rounding_add = 0;
    QData/*63:0*/ tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_rounded_magnitude;
    tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_rounded_magnitude = 0;
    QData/*63:0*/ tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_signed_value;
    tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_signed_value = 0;
    VlWide<3>/*95:0*/ __Vtemp_2;
    VlWide<3>/*95:0*/ __Vtemp_3;
    // Body
    tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_parameter[0U] = 0U;
    tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_parameter[1U] = 0U;
    tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_parameter[2U] = 0U;
    tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_accumulator = 0U;
    tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_multiplier = 0U;
    tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_q_shift = 0U;
    tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_magnitude = 0U;
    tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_product = 0ULL;
    tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_rounding_add = 0ULL;
    tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_rounded_magnitude = 0ULL;
    tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_signed_value = 0ULL;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requantized_value = 0U;
    if (((8U > vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_lane_index) 
         & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_lane_index 
            < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__group_lane_count))) {
        tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_parameter[0U] 
            = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter
            [(7U & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_lane_index)][0U];
        tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_parameter[1U] 
            = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter
            [(7U & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_lane_index)][1U];
        tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_parameter[2U] 
            = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_mq_parameter
            [(7U & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_lane_index)][2U];
        tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_accumulator 
            = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator
            [(7U & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_lane_index)];
        if ((tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_accumulator 
             >> 0x1fU)) {
            tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_multiplier 
                = ((tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_parameter[1U] 
                    << 0x00000018U) | (tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_parameter[0U] 
                                       >> 8U));
            tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_magnitude 
                = ((IData)(1U) + (~ tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_accumulator));
            tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_q_shift 
                = (0x000000ffU & tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_parameter[0U]);
        } else {
            tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_multiplier 
                = ((tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_parameter[2U] 
                    << 0x00000010U) | (tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_parameter[1U] 
                                       >> 0x00000010U));
            tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_magnitude 
                = tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_accumulator;
            tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_q_shift 
                = (0x000000ffU & (tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_parameter[1U] 
                                  >> 8U));
        }
        tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_product 
            = ((QData)((IData)(tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_magnitude)) 
               * (QData)((IData)(tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_multiplier)));
        if ((0U != tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_q_shift)) {
            tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_rounding_add 
                = VL_SHIFTL_QQI(64,64,32, 1ULL, (tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_q_shift 
                                                 - (IData)(1U)));
        }
        tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_rounded_magnitude 
            = VL_SHIFTR_QQI(64,64,32, (tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_product 
                                       + tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_rounding_add), tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_q_shift);
        __Vtemp_2[0U] = (IData)(tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_rounded_magnitude);
        __Vtemp_2[1U] = (IData)((tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_rounded_magnitude 
                                 >> 0x00000020U));
        __Vtemp_2[2U] = 0U;
        VL_NEGATE_W(3, __Vtemp_3, __Vtemp_2);
        tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_signed_value 
            = ((tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_accumulator 
                >> 0x1fU) ? (((QData)((IData)(__Vtemp_3[1U])) 
                              << 0x00000020U) | (QData)((IData)(__Vtemp_3[0U])))
                : tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_rounded_magnitude);
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requantized_value 
            = (VL_LTS_IQQ(64, 0x000000000000007fULL, tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_signed_value)
                ? 0x0000007fU : (VL_GTS_IQQ(64, 0xffffffffffffff81ULL, tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_signed_value)
                                  ? 0x00000081U : (0x000000ffU 
                                                   & (IData)(tb_combined__DOT__boundary_test__DOT__u_dut__DOT__requant_signed_value))));
    }
}

void Vtb_combined___024root___nba_sequent__TOP__64(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_sequent__TOP__64\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__request_byte_lane 
        = (3U & (0x00030210U >> ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__request_strobe_latched) 
                                 << 1U)));
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_source_address_wide 
        = ((QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_package_base_latched)) 
           + ((QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__quantized_weight_offset_latched)) 
              + ((QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_reduction_index)) 
                 + ((QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__reduction_count_latched)) 
                    * (QData)((IData)((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_group_base 
                                       + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_lane_index)))))));
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
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mq_prefetch_index = 0U;
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

void Vtb_combined___024root___nba_sequent__TOP__65(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_sequent__TOP__65\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    VlWide<3>/*79:0*/ tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_parameter;
    VL_ZERO_W(80, tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_parameter);
    IData/*31:0*/ tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_accumulator;
    tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_accumulator = 0;
    IData/*31:0*/ tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_multiplier;
    tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_multiplier = 0;
    IData/*31:0*/ tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_q_shift;
    tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_q_shift = 0;
    IData/*31:0*/ tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_magnitude;
    tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_magnitude = 0;
    QData/*63:0*/ tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_product;
    tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_product = 0;
    QData/*63:0*/ tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_rounding_add;
    tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_rounding_add = 0;
    QData/*63:0*/ tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_rounded_magnitude;
    tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_rounded_magnitude = 0;
    QData/*63:0*/ tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_signed_value;
    tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_signed_value = 0;
    VlWide<3>/*95:0*/ __Vtemp_2;
    VlWide<3>/*95:0*/ __Vtemp_3;
    // Body
    tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_parameter[0U] = 0U;
    tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_parameter[1U] = 0U;
    tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_parameter[2U] = 0U;
    tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_accumulator = 0U;
    tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_multiplier = 0U;
    tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_q_shift = 0U;
    tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_magnitude = 0U;
    tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_product = 0ULL;
    tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_rounding_add = 0ULL;
    tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_rounded_magnitude = 0ULL;
    tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_signed_value = 0ULL;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requantized_value = 0U;
    if (((8U > vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_lane_index) 
         & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_lane_index 
            < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__group_lane_count))) {
        tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_parameter[0U] 
            = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter
            [(7U & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_lane_index)][0U];
        tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_parameter[1U] 
            = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter
            [(7U & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_lane_index)][1U];
        tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_parameter[2U] 
            = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_mq_parameter
            [(7U & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_lane_index)][2U];
        tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_accumulator 
            = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator
            [(7U & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_lane_index)];
        if ((tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_accumulator 
             >> 0x1fU)) {
            tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_multiplier 
                = ((tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_parameter[1U] 
                    << 0x00000018U) | (tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_parameter[0U] 
                                       >> 8U));
            tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_magnitude 
                = ((IData)(1U) + (~ tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_accumulator));
            tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_q_shift 
                = (0x000000ffU & tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_parameter[0U]);
        } else {
            tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_multiplier 
                = ((tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_parameter[2U] 
                    << 0x00000010U) | (tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_parameter[1U] 
                                       >> 0x00000010U));
            tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_magnitude 
                = tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_accumulator;
            tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_q_shift 
                = (0x000000ffU & (tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_parameter[1U] 
                                  >> 8U));
        }
        tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_product 
            = ((QData)((IData)(tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_magnitude)) 
               * (QData)((IData)(tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_multiplier)));
        if ((0U != tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_q_shift)) {
            tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_rounding_add 
                = VL_SHIFTL_QQI(64,64,32, 1ULL, (tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_q_shift 
                                                 - (IData)(1U)));
        }
        tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_rounded_magnitude 
            = VL_SHIFTR_QQI(64,64,32, (tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_product 
                                       + tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_rounding_add), tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_q_shift);
        __Vtemp_2[0U] = (IData)(tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_rounded_magnitude);
        __Vtemp_2[1U] = (IData)((tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_rounded_magnitude 
                                 >> 0x00000020U));
        __Vtemp_2[2U] = 0U;
        VL_NEGATE_W(3, __Vtemp_3, __Vtemp_2);
        tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_signed_value 
            = ((tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_accumulator 
                >> 0x1fU) ? (((QData)((IData)(__Vtemp_3[1U])) 
                              << 0x00000020U) | (QData)((IData)(__Vtemp_3[0U])))
                : tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_rounded_magnitude);
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requantized_value 
            = (VL_LTS_IQQ(64, 0x000000000000007fULL, tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_signed_value)
                ? 0x0000007fU : (VL_GTS_IQQ(64, 0xffffffffffffff81ULL, tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_signed_value)
                                  ? 0x00000081U : (0x000000ffU 
                                                   & (IData)(tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__requant_signed_value))));
    }
}

void Vtb_combined___024root___nba_sequent__TOP__66(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_sequent__TOP__66\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_address_wide 
        = ((QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_base_latched)) 
           + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_byte_offset_wide);
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_address_wide 
        = ((QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_base_latched)) 
           + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_byte_offset_wide);
}

void Vtb_combined___024root___nba_sequent__TOP__67(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_sequent__TOP__67\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if (VL_UNLIKELY((((((((((((((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__start_ready) 
                                != (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__candidate_start_ready)) 
                               | ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_cancel) 
                                  != (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__candidate_backend_cancel))) 
                              | ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_valid) 
                                 != (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__candidate_backend_req_valid))) 
                             | ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_write) 
                                != (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__candidate_backend_req_write))) 
                            | (vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_addr 
                               != vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__request_address_latched)) 
                           | (vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_wdata 
                              != vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__request_wdata_latched)) 
                          | ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_rstrb) 
                             != (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__candidate_backend_req_rstrb))) 
                         | ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_wstrb) 
                            != (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__candidate_backend_req_wstrb))) 
                        | ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__busy) 
                           != (0U != (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state)))) 
                       | ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__result_valid) 
                          != (0x13U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state)))) 
                      | ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__result_error_code) 
                         != (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__result_error_latched)))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_boundary.sv:66: Assertion failed in %m: CONV\345\205\254\345\274\200\350\276\223\345\207\272\351\200\220\345\221\250\346\234\237\344\270\215\345\220\214 cycle=%0d\n",4, 'M',vlSymsp->name(),"tb_combined.boundary_test", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , '~',32,vlSelfRef.tb_combined__DOT__boundary_test__DOT__compare_cycles);
        VL_STOP_MT("tb_boundary.sv", 66, "", false);
    }
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__compare_cycles 
        = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__compare_cycles);
}

void Vtb_combined___024root___nba_comb__TOP__0(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_comb__TOP__0\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
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

void Vtb_combined___024root___nba_comb__TOP__11(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_comb__TOP__11\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
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
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__patch_plane_bytes 
        = ((QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__patch_height)) 
           * (QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__patch_width)));
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_input_y = 0ULL;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_input_x = 0ULL;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_in_bounds = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_advance = 0U;
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_geometry_plane = 0ULL;
}

void Vtb_combined___024root___nba_comb__TOP__12(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_comb__TOP__12\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    QData/*63:0*/ tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_channel_plane_offset;
    tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_channel_plane_offset = 0;
    // Body
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

void Vtb_combined___024root___nba_comb__TOP__23(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_comb__TOP__23\n"); );
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
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_address_wide 
        = ((QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_base_latched)) 
           + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__output_byte_offset_wide);
    vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_address_wide 
        = ((QData)((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_base_latched)) 
           + vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__output_byte_offset_wide);
}

void Vtb_combined___024root___nba_comb__TOP__24(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_comb__TOP__24\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
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
    // Body
    __Vtemp_1[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__input_batch_count_latched;
    __Vtemp_1[1U] = 0U;
    __Vtemp_1[2U] = 0U;
    __Vtemp_1[3U] = 0U;
    __Vtemp_2[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__input_channels_latched;
    __Vtemp_2[1U] = 0U;
    __Vtemp_2[2U] = 0U;
    __Vtemp_2[3U] = 0U;
    VL_MUL_W(4, __Vtemp_3, __Vtemp_1, __Vtemp_2);
    __Vtemp_4[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__input_height_latched;
    __Vtemp_4[1U] = 0U;
    __Vtemp_4[2U] = 0U;
    __Vtemp_4[3U] = 0U;
    VL_MUL_W(4, __Vtemp_5, __Vtemp_3, __Vtemp_4);
    __Vtemp_6[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__input_width_latched;
    __Vtemp_6[1U] = 0U;
    __Vtemp_6[2U] = 0U;
    __Vtemp_6[3U] = 0U;
    VL_MUL_W(4, vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__input_elements_wide, __Vtemp_5, __Vtemp_6);
    __Vtemp_7[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_batch_count_latched;
    __Vtemp_7[1U] = 0U;
    __Vtemp_7[2U] = 0U;
    __Vtemp_7[3U] = 0U;
    __Vtemp_8[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_channels_latched;
    __Vtemp_8[1U] = 0U;
    __Vtemp_8[2U] = 0U;
    __Vtemp_8[3U] = 0U;
    VL_MUL_W(4, __Vtemp_9, __Vtemp_7, __Vtemp_8);
    __Vtemp_10[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_height_latched;
    __Vtemp_10[1U] = 0U;
    __Vtemp_10[2U] = 0U;
    __Vtemp_10[3U] = 0U;
    VL_MUL_W(4, __Vtemp_11, __Vtemp_9, __Vtemp_10);
    __Vtemp_12[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_width_latched;
    __Vtemp_12[1U] = 0U;
    __Vtemp_12[2U] = 0U;
    __Vtemp_12[3U] = 0U;
    VL_MUL_W(4, vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_elements_wide, __Vtemp_11, __Vtemp_12);
    __Vtemp_13[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_channels_latched;
    __Vtemp_13[1U] = 0U;
    __Vtemp_13[2U] = 0U;
    __Vtemp_13[3U] = 0U;
    __Vtemp_14[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__input_channels_latched;
    __Vtemp_14[1U] = 0U;
    __Vtemp_14[2U] = 0U;
    __Vtemp_14[3U] = 0U;
    VL_MUL_W(4, __Vtemp_15, __Vtemp_13, __Vtemp_14);
    __Vtemp_16[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__kernel_height_latched;
    __Vtemp_16[1U] = 0U;
    __Vtemp_16[2U] = 0U;
    __Vtemp_16[3U] = 0U;
    VL_MUL_W(4, __Vtemp_17, __Vtemp_15, __Vtemp_16);
    __Vtemp_18[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__kernel_width_latched;
    __Vtemp_18[1U] = 0U;
    __Vtemp_18[2U] = 0U;
    __Vtemp_18[3U] = 0U;
    VL_MUL_W(4, vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__expected_weight_bytes_wide, __Vtemp_17, __Vtemp_18);
    __Vtemp_19[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__input_channels_latched;
    __Vtemp_19[1U] = 0U;
    __Vtemp_19[2U] = 0U;
    __Vtemp_19[3U] = 0U;
    __Vtemp_20[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__kernel_height_latched;
    __Vtemp_20[1U] = 0U;
    __Vtemp_20[2U] = 0U;
    __Vtemp_20[3U] = 0U;
    VL_MUL_W(4, __Vtemp_21, __Vtemp_19, __Vtemp_20);
    __Vtemp_22[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__kernel_width_latched;
    __Vtemp_22[1U] = 0U;
    __Vtemp_22[2U] = 0U;
    __Vtemp_22[3U] = 0U;
    VL_MUL_W(4, vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__reduction_count_wide, __Vtemp_21, __Vtemp_22);
    __Vtemp_23[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__input_base_latched;
    __Vtemp_23[1U] = 0U;
    __Vtemp_23[2U] = 0U;
    __Vtemp_23[3U] = 0U;
    __Vtemp_24[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__input_length_latched;
    __Vtemp_24[1U] = 0U;
    __Vtemp_24[2U] = 0U;
    __Vtemp_24[3U] = 0U;
    VL_ADD_W(4, vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__input_end_wide, __Vtemp_23, __Vtemp_24);
    __Vtemp_25[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_base_latched;
    __Vtemp_25[1U] = 0U;
    __Vtemp_25[2U] = 0U;
    __Vtemp_25[3U] = 0U;
    __Vtemp_26[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_length_latched;
    __Vtemp_26[1U] = 0U;
    __Vtemp_26[2U] = 0U;
    __Vtemp_26[3U] = 0U;
    VL_ADD_W(4, vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_end_wide, __Vtemp_25, __Vtemp_26);
    __Vtemp_27[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_package_base_latched;
    __Vtemp_27[1U] = 0U;
    __Vtemp_27[2U] = 0U;
    __Vtemp_27[3U] = 0U;
    __Vtemp_28[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_package_length_latched;
    __Vtemp_28[1U] = 0U;
    __Vtemp_28[2U] = 0U;
    __Vtemp_28[3U] = 0U;
    VL_ADD_W(4, vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_package_end_wide, __Vtemp_27, __Vtemp_28);
    __Vtemp_29[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__quantized_weight_offset_latched;
    __Vtemp_29[1U] = 0U;
    __Vtemp_29[2U] = 0U;
    __Vtemp_29[3U] = 0U;
    __Vtemp_30[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__quantized_weight_bytes_latched;
    __Vtemp_30[1U] = 0U;
    __Vtemp_30[2U] = 0U;
    __Vtemp_30[3U] = 0U;
    VL_ADD_W(4, vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__quantized_weight_end_wide, __Vtemp_29, __Vtemp_30);
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_height_numerator 
        = (((QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__input_height_latched)) 
            + (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__pad_top_latched))) 
           + (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__pad_bottom_latched)));
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_width_numerator 
        = (((QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__input_width_latched)) 
            + (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__pad_left_latched))) 
           + (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__pad_right_latched)));
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_height_shape_span 
        = (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_height_numerator 
           - (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__kernel_height_latched)));
}

void Vtb_combined___024root___nba_comb__TOP__25(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_comb__TOP__25\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    VlWide<4>/*127:0*/ tb_combined__DOT__boundary_test__DOT__u_dut__DOT__full_tile_patch_height_wide;
    VL_ZERO_W(128, tb_combined__DOT__boundary_test__DOT__u_dut__DOT__full_tile_patch_height_wide);
    VlWide<4>/*127:0*/ tb_combined__DOT__boundary_test__DOT__u_dut__DOT__full_tile_patch_width_wide;
    VL_ZERO_W(128, tb_combined__DOT__boundary_test__DOT__u_dut__DOT__full_tile_patch_width_wide);
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
    // Body
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_width_shape_span 
        = (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_width_numerator 
           - (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__kernel_width_latched)));
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_height_shape_product 
        = ((QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_height_latched)) 
           * (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__stride_y_latched)));
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_width_shape_product 
        = ((QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_width_latched)) 
           * (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__stride_x_latched)));
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_height_span_plus_stride 
        = (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_height_shape_span 
           + (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__stride_y_latched)));
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_width_span_plus_stride 
        = (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_width_shape_span 
           + (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__stride_x_latched)));
    tb_combined__DOT__boundary_test__DOT__u_dut__DOT__full_tile_patch_height_wide[0U] = 0U;
    tb_combined__DOT__boundary_test__DOT__u_dut__DOT__full_tile_patch_height_wide[1U] = 0U;
    tb_combined__DOT__boundary_test__DOT__u_dut__DOT__full_tile_patch_height_wide[2U] = 0U;
    tb_combined__DOT__boundary_test__DOT__u_dut__DOT__full_tile_patch_height_wide[3U] = 0U;
    tb_combined__DOT__boundary_test__DOT__u_dut__DOT__full_tile_patch_width_wide[0U] = 0U;
    tb_combined__DOT__boundary_test__DOT__u_dut__DOT__full_tile_patch_width_wide[1U] = 0U;
    tb_combined__DOT__boundary_test__DOT__u_dut__DOT__full_tile_patch_width_wide[2U] = 0U;
    tb_combined__DOT__boundary_test__DOT__u_dut__DOT__full_tile_patch_width_wide[3U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__full_tile_patch_bytes_wide[0U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__full_tile_patch_bytes_wide[1U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__full_tile_patch_bytes_wide[2U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__full_tile_patch_bytes_wide[3U] = 0U;
    if (((0U != vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_height_latched) 
         & (0U != vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_width_latched))) {
        __Vtemp_1[0U] = (((8U > vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_height_latched)
                           ? vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_height_latched
                           : 8U) - (IData)(1U));
        __Vtemp_1[1U] = 0U;
        __Vtemp_1[2U] = 0U;
        __Vtemp_1[3U] = 0U;
        __Vtemp_2[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__stride_y_latched;
        __Vtemp_2[1U] = 0U;
        __Vtemp_2[2U] = 0U;
        __Vtemp_2[3U] = 0U;
        VL_MUL_W(4, __Vtemp_3, __Vtemp_1, __Vtemp_2);
        __Vtemp_4[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__kernel_height_latched;
        __Vtemp_4[1U] = 0U;
        __Vtemp_4[2U] = 0U;
        __Vtemp_4[3U] = 0U;
        VL_ADD_W(4, tb_combined__DOT__boundary_test__DOT__u_dut__DOT__full_tile_patch_height_wide, __Vtemp_3, __Vtemp_4);
        __Vtemp_5[0U] = (((8U > vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_width_latched)
                           ? vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_width_latched
                           : 8U) - (IData)(1U));
        __Vtemp_5[1U] = 0U;
        __Vtemp_5[2U] = 0U;
        __Vtemp_5[3U] = 0U;
        __Vtemp_6[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__stride_x_latched;
        __Vtemp_6[1U] = 0U;
        __Vtemp_6[2U] = 0U;
        __Vtemp_6[3U] = 0U;
        VL_MUL_W(4, __Vtemp_7, __Vtemp_5, __Vtemp_6);
        __Vtemp_8[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__kernel_width_latched;
        __Vtemp_8[1U] = 0U;
        __Vtemp_8[2U] = 0U;
        __Vtemp_8[3U] = 0U;
        VL_ADD_W(4, tb_combined__DOT__boundary_test__DOT__u_dut__DOT__full_tile_patch_width_wide, __Vtemp_7, __Vtemp_8);
        VL_MUL_W(4, __Vtemp_9, tb_combined__DOT__boundary_test__DOT__u_dut__DOT__full_tile_patch_height_wide, tb_combined__DOT__boundary_test__DOT__u_dut__DOT__full_tile_patch_width_wide);
        __Vtemp_10[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__input_channels_latched;
        __Vtemp_10[1U] = 0U;
        __Vtemp_10[2U] = 0U;
        __Vtemp_10[3U] = 0U;
        VL_MUL_W(4, vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__full_tile_patch_bytes_wide, __Vtemp_9, __Vtemp_10);
    }
    __Vtemp_11[0U] = ((8U > vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_channels_latched)
                       ? vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_channels_latched
                       : 8U);
    __Vtemp_11[1U] = 0U;
    __Vtemp_11[2U] = 0U;
    __Vtemp_11[3U] = 0U;
    VL_MUL_W(4, vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__full_weight_group_bytes_wide, __Vtemp_11, vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__reduction_count_wide);
}

void Vtb_combined___024root___nba_comb__TOP__53(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_comb__TOP__53\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_write = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__candidate_backend_req_write = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_rstrb = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__candidate_backend_req_rstrb = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_wstrb = 0U;
    if ((1U & ((~ (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__hard_reset)) 
               & (~ (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__abort))))) {
        if (((4U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state)) 
             || (8U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state)))) {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_write = 0U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_rstrb 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__request_strobe_latched;
        } else if ((0x10U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state))) {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_write = 1U;
        }
        if (((4U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state)) 
             || (8U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state)))) {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__candidate_backend_req_write = 0U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__candidate_backend_req_rstrb 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__request_strobe_latched;
        } else if ((0x10U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state))) {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__candidate_backend_req_write = 1U;
        }
        if ((1U & (~ ((4U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state)) 
                      || (8U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state)))))) {
            if ((0x10U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state))) {
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_wstrb 
                    = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__request_strobe_latched;
            }
        }
    }
}
