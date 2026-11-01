// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design internal header
// See Vtb_s2a_conv_tile_unit.h for the primary calling header

#ifndef VERILATED_VTB_S2A_CONV_TILE_UNIT___024ROOT_H_
#define VERILATED_VTB_S2A_CONV_TILE_UNIT___024ROOT_H_  // guard

#include "verilated.h"
#include "verilated_timing.h"
class Vtb_s2a_conv_tile_unit_s2a_network_descriptor_pkg;


class Vtb_s2a_conv_tile_unit__Syms;

class alignas(VL_CACHE_LINE_BYTES) Vtb_s2a_conv_tile_unit___024root final {
  public:
    // CELLS
    Vtb_s2a_conv_tile_unit_s2a_network_descriptor_pkg* __PVT__s2a_network_descriptor_pkg;

    // DESIGN SPECIFIC STATE
    // Anonymous structures to workaround compiler member-count bugs
    struct {
        CData/*0:0*/ tb_s2a_conv_tile_unit__DOT__clk;
        CData/*0:0*/ tb_s2a_conv_tile_unit__DOT__hard_reset;
        CData/*0:0*/ tb_s2a_conv_tile_unit__DOT__abort;
        CData/*0:0*/ tb_s2a_conv_tile_unit__DOT__start_valid;
        CData/*0:0*/ tb_s2a_conv_tile_unit__DOT__start_ready;
        CData/*4:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__state;
        CData/*1:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__activation_mode_latched;
        CData/*2:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__result_error_latched;
        CData/*0:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__validation_ok;
        CData/*2:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__validation_error;
        CData/*0:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_scan_in_bounds;
        CData/*0:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_bad_argument;
        CData/*0:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_overflow;
        CData/*0:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_invalid;
        CData/*7:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__requantized_value;
        CData/*0:0*/ __VstlFirstIteration;
        CData/*0:0*/ __VstlPhaseResult;
        CData/*0:0*/ __Vtrigprevexpr___TOP__tb_s2a_conv_tile_unit__DOT__clk__0;
        CData/*0:0*/ __VactPhaseResult;
        CData/*0:0*/ __VinactPhaseResult;
        CData/*0:0*/ __VnbaPhaseResult;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT____VlemExpr_0;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__layer_id;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__ordinal;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__channel;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__y;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__x;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__k;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__lanes;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__i;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__l;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__ic;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__ky;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__kx;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__idx;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__group_base;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__ty;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__tx;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__th;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__tw;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__ph;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__pw;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__point;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__query_count;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__lane_checks;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__cycles;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__word_work;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__byte_work;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_layer_index_latched;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__input_base_latched;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__input_length_latched;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__input_batch_count_latched;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__input_channels_latched;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__input_height_latched;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__input_width_latched;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__output_base_latched;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__output_length_latched;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__output_batch_count_latched;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__output_channels_latched;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__output_height_latched;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__output_width_latched;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__kernel_height_latched;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__kernel_width_latched;
    };
    struct {
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__stride_y_latched;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__stride_x_latched;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__pad_left_latched;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__pad_right_latched;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__pad_top_latched;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__pad_bottom_latched;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__groups_latched;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__padding_latched;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_package_base_latched;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_package_length_latched;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__quantized_weight_offset_latched;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__quantized_weight_bytes_latched;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__output_batch_latched;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__reduction_count_latched;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__output_group_base;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_start_y;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_start_x;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_height;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_width;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__patch_height;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__patch_width;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__patch_byte_count;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_point_count;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_scan_index;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_lane_index;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_reduction_index;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_point_index;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_reduction_index;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__output_lane_index;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__output_point_index;
        VlWide<4>/*127:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__output_elements_wide;
        VlWide<4>/*127:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__reduction_count_wide;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_lane;
        VlWide<3>/*79:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_parameter;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_bias;
        IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_lane_index;
        IData/*31:0*/ __VactIterCount;
        IData/*31:0*/ __VinactIterCount;
        IData/*31:0*/ __Vi;
        QData/*63:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_source_address_wide;
        QData/*63:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_source_address_wide;
        QData/*63:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__output_byte_offset_wide;
        QData/*63:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__output_address_wide;
        VlUnpacked<IData/*31:0*/, 8> tb_s2a_conv_tile_unit__DOT__expected_acc;
        VlUnpacked<IData/*31:0*/, 8> tb_s2a_conv_tile_unit__DOT__expected_byte;
        VlUnpacked<IData/*31:0*/, 8> tb_s2a_conv_tile_unit__DOT__hdr;
        VlUnpacked<CData/*7:0*/, 8192> tb_s2a_conv_tile_unit__DOT__activations;
        VlUnpacked<CData/*7:0*/, 36864> tb_s2a_conv_tile_unit__DOT__weights;
        VlUnpacked<CData/*7:0*/, 51200> tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_patch;
        VlUnpacked<CData/*7:0*/, 36864> tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_group;
        VlUnpacked<CData/*7:0*/, 512> tb_s2a_conv_tile_unit__DOT__dut__DOT__output_block;
        VlUnpacked<IData/*31:0*/, 8> tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator;
        VlUnpacked<CData/*7:0*/, 8> tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_byte;
        VlUnpacked<CData/*7:0*/, 8> tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_weight_byte;
        VlUnpacked<SData/*15:0*/, 8> tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_product;
        VlUnpacked<QData/*32:0*/, 8> tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_sum;
        VlUnpacked<VlWide<3>/*79:0*/, 8> tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_mq_parameter;
        VlUnpacked<IData/*31:0*/, 8> tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_bias;
        VlUnpacked<QData/*63:0*/, 1> __VstlTriggered;
        VlUnpacked<QData/*63:0*/, 1> __VactTriggered;
        VlUnpacked<QData/*63:0*/, 1> __VactTriggeredAcc;
        VlUnpacked<QData/*63:0*/, 1> __VnbaTriggered;
    };
    VlDelayScheduler __VdlySched;
    VlTriggerScheduler __VtrigSched_h5ceb9ffd__0;

    // INTERNAL VARIABLES
    Vtb_s2a_conv_tile_unit__Syms* vlSymsp;
    const char* vlNamep;

    // CONSTRUCTORS
    Vtb_s2a_conv_tile_unit___024root(Vtb_s2a_conv_tile_unit__Syms* symsp, const char* namep);
    ~Vtb_s2a_conv_tile_unit___024root();
    VL_UNCOPYABLE(Vtb_s2a_conv_tile_unit___024root);

    // INTERNAL METHODS
    void __Vconfigure(bool first);
};


#endif  // guard
