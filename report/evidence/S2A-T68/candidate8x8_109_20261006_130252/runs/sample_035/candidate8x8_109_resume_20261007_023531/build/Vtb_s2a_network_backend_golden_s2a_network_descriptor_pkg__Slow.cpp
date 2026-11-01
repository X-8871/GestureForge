// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vtb_s2a_network_backend_golden.h for the primary calling header

#include "Vtb_s2a_network_backend_golden__pch.h"

// Parameter definitions for Vtb_s2a_network_backend_golden_s2a_network_descriptor_pkg
constexpr VlUnpacked<CData/*5:0*/, 38> Vtb_s2a_network_backend_golden_s2a_network_descriptor_pkg::S2A_LAYER_INDEX;
constexpr VlUnpacked<CData/*2:0*/, 38> Vtb_s2a_network_backend_golden_s2a_network_descriptor_pkg::S2A_OP;
constexpr VlUnpacked<CData/*1:0*/, 38> Vtb_s2a_network_backend_golden_s2a_network_descriptor_pkg::S2A_INPUT_COUNT;
constexpr VlUnpacked<VlUnpacked<CData/*0:0*/, 2>, 38> Vtb_s2a_network_backend_golden_s2a_network_descriptor_pkg::S2A_INPUT_KIND;
constexpr VlUnpacked<VlUnpacked<IData/*31:0*/, 2>, 38> Vtb_s2a_network_backend_golden_s2a_network_descriptor_pkg::S2A_INPUT_ADDRESS;
constexpr VlUnpacked<VlUnpacked<IData/*31:0*/, 2>, 38> Vtb_s2a_network_backend_golden_s2a_network_descriptor_pkg::S2A_INPUT_LENGTH_BYTES;
constexpr VlUnpacked<VlUnpacked<SData/*15:0*/, 2>, 38> Vtb_s2a_network_backend_golden_s2a_network_descriptor_pkg::S2A_INPUT_N;
constexpr VlUnpacked<VlUnpacked<SData/*15:0*/, 2>, 38> Vtb_s2a_network_backend_golden_s2a_network_descriptor_pkg::S2A_INPUT_C;
constexpr VlUnpacked<VlUnpacked<SData/*15:0*/, 2>, 38> Vtb_s2a_network_backend_golden_s2a_network_descriptor_pkg::S2A_INPUT_H;
constexpr VlUnpacked<VlUnpacked<SData/*15:0*/, 2>, 38> Vtb_s2a_network_backend_golden_s2a_network_descriptor_pkg::S2A_INPUT_W;
constexpr VlUnpacked<CData/*5:0*/, 38> Vtb_s2a_network_backend_golden_s2a_network_descriptor_pkg::S2A_OUTPUT_TENSOR_INDEX;
constexpr VlUnpacked<CData/*0:0*/, 38> Vtb_s2a_network_backend_golden_s2a_network_descriptor_pkg::S2A_OUTPUT_ALLOCATION_KIND;
constexpr VlUnpacked<CData/*5:0*/, 38> Vtb_s2a_network_backend_golden_s2a_network_descriptor_pkg::S2A_OUTPUT_ALIAS_LAYER_INDEX;
constexpr VlUnpacked<CData/*0:0*/, 38> Vtb_s2a_network_backend_golden_s2a_network_descriptor_pkg::S2A_OUTPUT_MEMORY_WRITE_REQUIRED;
constexpr VlUnpacked<IData/*31:0*/, 38> Vtb_s2a_network_backend_golden_s2a_network_descriptor_pkg::S2A_OUTPUT_ADDRESS;
constexpr VlUnpacked<IData/*31:0*/, 38> Vtb_s2a_network_backend_golden_s2a_network_descriptor_pkg::S2A_OUTPUT_LENGTH_BYTES;
constexpr VlUnpacked<SData/*15:0*/, 38> Vtb_s2a_network_backend_golden_s2a_network_descriptor_pkg::S2A_OUTPUT_N;
constexpr VlUnpacked<SData/*15:0*/, 38> Vtb_s2a_network_backend_golden_s2a_network_descriptor_pkg::S2A_OUTPUT_C;
constexpr VlUnpacked<SData/*15:0*/, 38> Vtb_s2a_network_backend_golden_s2a_network_descriptor_pkg::S2A_OUTPUT_H;
constexpr VlUnpacked<SData/*15:0*/, 38> Vtb_s2a_network_backend_golden_s2a_network_descriptor_pkg::S2A_OUTPUT_W;
constexpr VlUnpacked<CData/*7:0*/, 38> Vtb_s2a_network_backend_golden_s2a_network_descriptor_pkg::S2A_KERNEL_H;
constexpr VlUnpacked<CData/*7:0*/, 38> Vtb_s2a_network_backend_golden_s2a_network_descriptor_pkg::S2A_KERNEL_W;
constexpr VlUnpacked<CData/*7:0*/, 38> Vtb_s2a_network_backend_golden_s2a_network_descriptor_pkg::S2A_STRIDE_H;
constexpr VlUnpacked<CData/*7:0*/, 38> Vtb_s2a_network_backend_golden_s2a_network_descriptor_pkg::S2A_STRIDE_W;
constexpr VlUnpacked<CData/*7:0*/, 38> Vtb_s2a_network_backend_golden_s2a_network_descriptor_pkg::S2A_PADDING_LEFT;
constexpr VlUnpacked<CData/*7:0*/, 38> Vtb_s2a_network_backend_golden_s2a_network_descriptor_pkg::S2A_PADDING_RIGHT;
constexpr VlUnpacked<CData/*7:0*/, 38> Vtb_s2a_network_backend_golden_s2a_network_descriptor_pkg::S2A_PADDING_TOP;
constexpr VlUnpacked<CData/*7:0*/, 38> Vtb_s2a_network_backend_golden_s2a_network_descriptor_pkg::S2A_PADDING_BOTTOM;
constexpr VlUnpacked<SData/*15:0*/, 38> Vtb_s2a_network_backend_golden_s2a_network_descriptor_pkg::S2A_GROUP_COUNT;
constexpr VlUnpacked<SData/*15:0*/, 38> Vtb_s2a_network_backend_golden_s2a_network_descriptor_pkg::S2A_ROUTE_GROUP_ID;
constexpr VlUnpacked<CData/*7:0*/, 38> Vtb_s2a_network_backend_golden_s2a_network_descriptor_pkg::S2A_PADDING_VALUE_INT8;
constexpr VlUnpacked<CData/*1:0*/, 38> Vtb_s2a_network_backend_golden_s2a_network_descriptor_pkg::S2A_ACTIVATION;
constexpr VlUnpacked<CData/*5:0*/, 38> Vtb_s2a_network_backend_golden_s2a_network_descriptor_pkg::S2A_WEIGHT_LAYER_INDEX;
constexpr VlUnpacked<IData/*31:0*/, 38> Vtb_s2a_network_backend_golden_s2a_network_descriptor_pkg::S2A_GF8_WEIGHT_OFFSET;
constexpr VlUnpacked<IData/*31:0*/, 38> Vtb_s2a_network_backend_golden_s2a_network_descriptor_pkg::S2A_GF8_WEIGHT_BYTES;
constexpr VlUnpacked<SData/*15:0*/, 38> Vtb_s2a_network_backend_golden_s2a_network_descriptor_pkg::S2A_T23_MQ_BASE;
constexpr VlUnpacked<SData/*15:0*/, 38> Vtb_s2a_network_backend_golden_s2a_network_descriptor_pkg::S2A_T23_MQ_CHANNEL_COUNT;
constexpr VlUnpacked<CData/*7:0*/, 38> Vtb_s2a_network_backend_golden_s2a_network_descriptor_pkg::S2A_MAXPOOL_DARKNET_PADDING;
constexpr VlUnpacked<SData/*15:0*/, 38> Vtb_s2a_network_backend_golden_s2a_network_descriptor_pkg::S2A_UPSAMPLE_STRIDE;
constexpr VlUnpacked<VlUnpacked<SData/*15:0*/, 2>, 38> Vtb_s2a_network_backend_golden_s2a_network_descriptor_pkg::S2A_ROUTE_CHANNEL_START;
constexpr VlUnpacked<VlUnpacked<SData/*15:0*/, 2>, 38> Vtb_s2a_network_backend_golden_s2a_network_descriptor_pkg::S2A_ROUTE_CHANNEL_END;
constexpr VlUnpacked<VlUnpacked<IData/*31:0*/, 2>, 38> Vtb_s2a_network_backend_golden_s2a_network_descriptor_pkg::S2A_ROUTE_SOURCE_MULTIPLIER_Q31;
constexpr VlUnpacked<IData/*31:0*/, 3164> Vtb_s2a_network_backend_golden_s2a_network_descriptor_pkg::S2A_CONV_BIAS_ACCUMULATOR_INT32;
constexpr VlUnpacked<VlWide<3>/*79:0*/, 3164> Vtb_s2a_network_backend_golden_s2a_network_descriptor_pkg::S2A_T23_MQ_ROM;



Vtb_s2a_network_backend_golden_s2a_network_descriptor_pkg::Vtb_s2a_network_backend_golden_s2a_network_descriptor_pkg() = default;
Vtb_s2a_network_backend_golden_s2a_network_descriptor_pkg::~Vtb_s2a_network_backend_golden_s2a_network_descriptor_pkg() = default;

void Vtb_s2a_network_backend_golden_s2a_network_descriptor_pkg::ctor(Vtb_s2a_network_backend_golden__Syms* symsp, const char* namep) {
    vlSymsp = symsp;
    vlNamep = strdup(Verilated::catName(vlSymsp->name(), namep));
    // Reset structure values
}

void Vtb_s2a_network_backend_golden_s2a_network_descriptor_pkg::__Vconfigure(bool first) {
    (void)first;  // Prevent unused variable warning
}

void Vtb_s2a_network_backend_golden_s2a_network_descriptor_pkg::dtor() {
    VL_DO_DANGLING(std::free(const_cast<char*>(vlNamep)), vlNamep);
}
