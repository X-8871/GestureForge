// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vtb_s2a_conv_tile_boundary.h for the primary calling header

#include "Vtb_s2a_conv_tile_boundary__pch.h"

// Parameter definitions for Vtb_s2a_conv_tile_boundary_s2a_network_descriptor_pkg
constexpr VlUnpacked<CData/*2:0*/, 38> Vtb_s2a_conv_tile_boundary_s2a_network_descriptor_pkg::S2A_OP;
constexpr VlUnpacked<VlUnpacked<IData/*31:0*/, 2>, 38> Vtb_s2a_conv_tile_boundary_s2a_network_descriptor_pkg::S2A_INPUT_ADDRESS;
constexpr VlUnpacked<VlUnpacked<IData/*31:0*/, 2>, 38> Vtb_s2a_conv_tile_boundary_s2a_network_descriptor_pkg::S2A_INPUT_LENGTH_BYTES;
constexpr VlUnpacked<VlUnpacked<SData/*15:0*/, 2>, 38> Vtb_s2a_conv_tile_boundary_s2a_network_descriptor_pkg::S2A_INPUT_N;
constexpr VlUnpacked<VlUnpacked<SData/*15:0*/, 2>, 38> Vtb_s2a_conv_tile_boundary_s2a_network_descriptor_pkg::S2A_INPUT_C;
constexpr VlUnpacked<VlUnpacked<SData/*15:0*/, 2>, 38> Vtb_s2a_conv_tile_boundary_s2a_network_descriptor_pkg::S2A_INPUT_H;
constexpr VlUnpacked<VlUnpacked<SData/*15:0*/, 2>, 38> Vtb_s2a_conv_tile_boundary_s2a_network_descriptor_pkg::S2A_INPUT_W;
constexpr VlUnpacked<IData/*31:0*/, 38> Vtb_s2a_conv_tile_boundary_s2a_network_descriptor_pkg::S2A_OUTPUT_ADDRESS;
constexpr VlUnpacked<IData/*31:0*/, 38> Vtb_s2a_conv_tile_boundary_s2a_network_descriptor_pkg::S2A_OUTPUT_LENGTH_BYTES;
constexpr VlUnpacked<SData/*15:0*/, 38> Vtb_s2a_conv_tile_boundary_s2a_network_descriptor_pkg::S2A_OUTPUT_N;
constexpr VlUnpacked<SData/*15:0*/, 38> Vtb_s2a_conv_tile_boundary_s2a_network_descriptor_pkg::S2A_OUTPUT_C;
constexpr VlUnpacked<SData/*15:0*/, 38> Vtb_s2a_conv_tile_boundary_s2a_network_descriptor_pkg::S2A_OUTPUT_H;
constexpr VlUnpacked<SData/*15:0*/, 38> Vtb_s2a_conv_tile_boundary_s2a_network_descriptor_pkg::S2A_OUTPUT_W;
constexpr VlUnpacked<CData/*7:0*/, 38> Vtb_s2a_conv_tile_boundary_s2a_network_descriptor_pkg::S2A_KERNEL_H;
constexpr VlUnpacked<CData/*7:0*/, 38> Vtb_s2a_conv_tile_boundary_s2a_network_descriptor_pkg::S2A_KERNEL_W;
constexpr VlUnpacked<CData/*7:0*/, 38> Vtb_s2a_conv_tile_boundary_s2a_network_descriptor_pkg::S2A_STRIDE_H;
constexpr VlUnpacked<CData/*7:0*/, 38> Vtb_s2a_conv_tile_boundary_s2a_network_descriptor_pkg::S2A_STRIDE_W;
constexpr VlUnpacked<CData/*7:0*/, 38> Vtb_s2a_conv_tile_boundary_s2a_network_descriptor_pkg::S2A_PADDING_LEFT;
constexpr VlUnpacked<CData/*7:0*/, 38> Vtb_s2a_conv_tile_boundary_s2a_network_descriptor_pkg::S2A_PADDING_RIGHT;
constexpr VlUnpacked<CData/*7:0*/, 38> Vtb_s2a_conv_tile_boundary_s2a_network_descriptor_pkg::S2A_PADDING_TOP;
constexpr VlUnpacked<CData/*7:0*/, 38> Vtb_s2a_conv_tile_boundary_s2a_network_descriptor_pkg::S2A_PADDING_BOTTOM;
constexpr VlUnpacked<IData/*31:0*/, 38> Vtb_s2a_conv_tile_boundary_s2a_network_descriptor_pkg::S2A_GF8_WEIGHT_OFFSET;
constexpr VlUnpacked<IData/*31:0*/, 38> Vtb_s2a_conv_tile_boundary_s2a_network_descriptor_pkg::S2A_GF8_WEIGHT_BYTES;
constexpr VlUnpacked<IData/*31:0*/, 38> Vtb_s2a_conv_tile_boundary_s2a_network_descriptor_pkg::S2A_GF8_PACKAGE_BASE;
constexpr VlUnpacked<IData/*31:0*/, 38> Vtb_s2a_conv_tile_boundary_s2a_network_descriptor_pkg::S2A_GF8_PACKAGE_LENGTH;
constexpr VlUnpacked<SData/*15:0*/, 38> Vtb_s2a_conv_tile_boundary_s2a_network_descriptor_pkg::S2A_T23_MQ_BASE;
constexpr VlUnpacked<SData/*15:0*/, 38> Vtb_s2a_conv_tile_boundary_s2a_network_descriptor_pkg::S2A_T23_MQ_CHANNEL_COUNT;
constexpr VlUnpacked<IData/*31:0*/, 3164> Vtb_s2a_conv_tile_boundary_s2a_network_descriptor_pkg::S2A_CONV_BIAS_ACCUMULATOR_INT32;
constexpr VlUnpacked<VlWide<3>/*79:0*/, 3164> Vtb_s2a_conv_tile_boundary_s2a_network_descriptor_pkg::S2A_T23_MQ_ROM;



Vtb_s2a_conv_tile_boundary_s2a_network_descriptor_pkg::Vtb_s2a_conv_tile_boundary_s2a_network_descriptor_pkg() = default;
Vtb_s2a_conv_tile_boundary_s2a_network_descriptor_pkg::~Vtb_s2a_conv_tile_boundary_s2a_network_descriptor_pkg() = default;

void Vtb_s2a_conv_tile_boundary_s2a_network_descriptor_pkg::ctor(Vtb_s2a_conv_tile_boundary__Syms* symsp, const char* namep) {
    vlSymsp = symsp;
    vlNamep = strdup(Verilated::catName(vlSymsp->name(), namep));
    // Reset structure values
}

void Vtb_s2a_conv_tile_boundary_s2a_network_descriptor_pkg::__Vconfigure(bool first) {
    (void)first;  // Prevent unused variable warning
}

void Vtb_s2a_conv_tile_boundary_s2a_network_descriptor_pkg::dtor() {
    VL_DO_DANGLING(std::free(const_cast<char*>(vlNamep)), vlNamep);
}
