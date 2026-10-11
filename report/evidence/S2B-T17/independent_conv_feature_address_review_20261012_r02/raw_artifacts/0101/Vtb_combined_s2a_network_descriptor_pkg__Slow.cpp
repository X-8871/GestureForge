// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vtb_combined.h for the primary calling header

#include "Vtb_combined__pch.h"

// Parameter definitions for Vtb_combined_s2a_network_descriptor_pkg
constexpr VlUnpacked<CData/*2:0*/, 38> Vtb_combined_s2a_network_descriptor_pkg::S2A_OP;
constexpr VlUnpacked<SData/*15:0*/, 38> Vtb_combined_s2a_network_descriptor_pkg::S2A_T23_MQ_BASE;
constexpr VlUnpacked<SData/*15:0*/, 38> Vtb_combined_s2a_network_descriptor_pkg::S2A_T23_MQ_CHANNEL_COUNT;
constexpr VlUnpacked<IData/*31:0*/, 3164> Vtb_combined_s2a_network_descriptor_pkg::S2A_CONV_BIAS_ACCUMULATOR_INT32;
constexpr VlUnpacked<VlWide<3>/*79:0*/, 3164> Vtb_combined_s2a_network_descriptor_pkg::S2A_T23_MQ_ROM;



Vtb_combined_s2a_network_descriptor_pkg::Vtb_combined_s2a_network_descriptor_pkg() = default;
Vtb_combined_s2a_network_descriptor_pkg::~Vtb_combined_s2a_network_descriptor_pkg() = default;

void Vtb_combined_s2a_network_descriptor_pkg::ctor(Vtb_combined__Syms* symsp, const char* namep) {
    vlSymsp = symsp;
    vlNamep = strdup(Verilated::catName(vlSymsp->name(), namep));
    // Reset structure values
}

void Vtb_combined_s2a_network_descriptor_pkg::__Vconfigure(bool first) {
    (void)first;  // Prevent unused variable warning
}

void Vtb_combined_s2a_network_descriptor_pkg::dtor() {
    VL_DO_DANGLING(std::free(const_cast<char*>(vlNamep)), vlNamep);
}
