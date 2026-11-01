// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design internal header
// See Vtb_s2a_weightcap_boundary.h for the primary calling header

#ifndef VERILATED_VTB_S2A_WEIGHTCAP_BOUNDARY___024ROOT_H_
#define VERILATED_VTB_S2A_WEIGHTCAP_BOUNDARY___024ROOT_H_  // guard

#include "verilated.h"
#include "verilated_timing.h"
class Vtb_s2a_weightcap_boundary_s2a_network_descriptor_pkg;


class Vtb_s2a_weightcap_boundary__Syms;

class alignas(VL_CACHE_LINE_BYTES) Vtb_s2a_weightcap_boundary___024root final {
  public:
    // CELLS
    Vtb_s2a_weightcap_boundary_s2a_network_descriptor_pkg* __PVT__s2a_network_descriptor_pkg;

    // DESIGN SPECIFIC STATE
    // Anonymous structures to workaround compiler member-count bugs
    struct {
        CData/*0:0*/ tb_s2a_weightcap_boundary__DOT__clk;
        CData/*0:0*/ tb_s2a_weightcap_boundary__DOT__hard_reset;
        CData/*0:0*/ tb_s2a_weightcap_boundary__DOT__abort;
        CData/*0:0*/ tb_s2a_weightcap_boundary__DOT__start_valid;
        CData/*0:0*/ tb_s2a_weightcap_boundary__DOT__start_ready;
        CData/*0:0*/ tb_s2a_weightcap_boundary__DOT__backend_req_valid;
        CData/*0:0*/ tb_s2a_weightcap_boundary__DOT__backend_req_ready;
        CData/*0:0*/ tb_s2a_weightcap_boundary__DOT__backend_req_write;
        CData/*3:0*/ tb_s2a_weightcap_boundary__DOT__backend_req_rstrb;
        CData/*3:0*/ tb_s2a_weightcap_boundary__DOT__backend_req_wstrb;
        CData/*0:0*/ tb_s2a_weightcap_boundary__DOT__memory_pending;
        CData/*0:0*/ tb_s2a_weightcap_boundary__DOT__storage_boundary_abort_done;
        CData/*4:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state;
        CData/*1:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__activation_mode_latched;
        CData/*7:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_read_data;
        CData/*0:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_read_in_bounds;
        CData/*3:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__request_strobe_latched;
        CData/*2:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__result_error_latched;
        CData/*0:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__validation_ok;
        CData/*2:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__validation_error;
        CData/*0:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_advance;
        CData/*0:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_in_bounds;
        CData/*0:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_tap_in_bounds;
        CData/*0:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_enable;
        CData/*0:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_bad_argument;
        CData/*0:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_overflow;
        CData/*0:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_invalid;
        CData/*7:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requantized_value;
        CData/*2:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mapped_response_error;
        CData/*1:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__request_byte_lane;
        CData/*0:0*/ __VstlFirstIteration;
        CData/*0:0*/ __VstlPhaseResult;
        CData/*0:0*/ __Vtrigprevexpr___TOP__tb_s2a_weightcap_boundary__DOT__clk__0;
        CData/*0:0*/ __Vtrigprevexpr___TOP__tb_s2a_weightcap_boundary__DOT__start_ready__0;
        CData/*0:0*/ __VactPhaseResult;
        CData/*0:0*/ __VinactPhaseResult;
        CData/*0:0*/ __VnbaPhaseResult;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__input_length_bytes;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__input_channels;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__input_height;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__input_width;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__output_length_bytes;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__output_channels;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__output_height;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__output_width;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__kernel_height;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__kernel_width;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__weight_package_length_bytes;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__quantized_weight_offset;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__quantized_weight_bytes;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__response_data;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__request_count;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__feature_read_count;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__weight_read_count;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__output_write_count;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__lane7_index4607_request_count;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__first_group_last_weight_byte_count;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__bad_k_request_baseline;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__selected_lane;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__run_boundary_cases__DOT__wait_cycles;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__layer_index_latched;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_layer_index_latched;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__input_base_latched;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__input_length_latched;
    };
    struct {
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__input_batch_count_latched;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__input_channels_latched;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__input_height_latched;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__input_width_latched;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_base_latched;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_length_latched;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_batch_count_latched;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_channels_latched;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_height_latched;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_width_latched;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__kernel_height_latched;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__kernel_width_latched;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__stride_y_latched;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__stride_x_latched;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__pad_left_latched;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__pad_right_latched;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__pad_top_latched;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__pad_bottom_latched;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__groups_latched;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__padding_latched;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_package_base_latched;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_package_length_latched;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__quantized_weight_offset_latched;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__quantized_weight_bytes_latched;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_batch_latched;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__reduction_count_latched;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_group_base;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_start_y;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_start_x;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_height;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_width;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__patch_height;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__patch_width;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__patch_byte_count;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_point_count;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__group_lane_count;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_index;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_lane_index;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_reduction_index;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_point_index;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_point_scan_y;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_point_scan_x;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_reduction_index;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_lane_index;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_point_index;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__request_address_latched;
        VlWide<4>/*127:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_elements_wide;
        VlWide<4>/*127:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__reduction_count_wide;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_channel;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_y;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_x;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_input_channel;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_kernel_y;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_kernel_x;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_next_kernel_x;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_reduction_index;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_feature_index;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_lane;
        VlWide<3>/*79:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_parameter;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_bias;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_lane_index;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_point_scan_y;
        IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_point_scan_x;
        IData/*31:0*/ __VactIterCount;
    };
    struct {
        IData/*31:0*/ __VinactIterCount;
        IData/*31:0*/ __Vi;
        QData/*63:0*/ tb_s2a_weightcap_boundary__DOT__selected_byte_address;
        QData/*63:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_source_address_wide;
        QData/*63:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_source_address_wide;
        QData/*63:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_byte_offset_wide;
        QData/*63:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_address_wide;
        VlUnpacked<CData/*7:0*/, 51200> tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_patch;
        VlUnpacked<IData/*31:0*/, 8> tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator;
        VlUnpacked<CData/*7:0*/, 8> tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte;
        VlUnpacked<CData/*7:0*/, 8> tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_feature_byte;
        VlUnpacked<CData/*7:0*/, 8> tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_weight_byte;
        VlUnpacked<SData/*15:0*/, 8> tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_product;
        VlUnpacked<QData/*32:0*/, 8> tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_sum;
        VlUnpacked<VlWide<3>/*79:0*/, 8> tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_mq_parameter;
        VlUnpacked<IData/*31:0*/, 8> tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_bias;
        VlUnpacked<CData/*7:0*/, 4608> tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory;
        VlUnpacked<CData/*7:0*/, 4608> tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory;
        VlUnpacked<CData/*7:0*/, 4608> tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory;
        VlUnpacked<CData/*7:0*/, 4608> tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory;
        VlUnpacked<CData/*7:0*/, 4608> tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory;
        VlUnpacked<CData/*7:0*/, 4608> tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory;
        VlUnpacked<CData/*7:0*/, 4608> tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory;
        VlUnpacked<CData/*7:0*/, 4608> tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory;
        VlUnpacked<QData/*63:0*/, 1> __VstlTriggered;
        VlUnpacked<QData/*63:0*/, 1> __VactTriggered;
        VlUnpacked<QData/*63:0*/, 1> __VactTriggeredAcc;
        VlUnpacked<QData/*63:0*/, 1> __VnbaTriggered;
    };
    VlDelayScheduler __VdlySched;
    VlTriggerScheduler __VtrigSched_h7384c754__0;
    VlTriggerScheduler __VtrigSched_h2a9b4c34__0;
    VlTriggerScheduler __VtrigSched_h7384c695__0;

    // INTERNAL VARIABLES
    Vtb_s2a_weightcap_boundary__Syms* vlSymsp;
    const char* vlNamep;

    // CONSTRUCTORS
    Vtb_s2a_weightcap_boundary___024root(Vtb_s2a_weightcap_boundary__Syms* symsp, const char* namep);
    ~Vtb_s2a_weightcap_boundary___024root();
    VL_UNCOPYABLE(Vtb_s2a_weightcap_boundary___024root);

    // INTERNAL METHODS
    void __Vconfigure(bool first);
};


#endif  // guard
