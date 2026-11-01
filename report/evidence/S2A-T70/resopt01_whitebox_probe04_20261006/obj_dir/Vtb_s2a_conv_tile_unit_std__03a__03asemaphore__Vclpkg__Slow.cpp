// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vtb_s2a_conv_tile_unit.h for the primary calling header

#include "Vtb_s2a_conv_tile_unit__pch.h"


Vtb_s2a_conv_tile_unit_std__03a__03asemaphore__Vclpkg::Vtb_s2a_conv_tile_unit_std__03a__03asemaphore__Vclpkg() = default;
Vtb_s2a_conv_tile_unit_std__03a__03asemaphore__Vclpkg::~Vtb_s2a_conv_tile_unit_std__03a__03asemaphore__Vclpkg() = default;

void Vtb_s2a_conv_tile_unit_std__03a__03asemaphore__Vclpkg::ctor(Vtb_s2a_conv_tile_unit__Syms* symsp, const char* namep) {
    vlSymsp = symsp;
    vlNamep = strdup(Verilated::catName(vlSymsp->name(), namep));
    // Reset structure values
}

void Vtb_s2a_conv_tile_unit_std__03a__03asemaphore__Vclpkg::__Vconfigure(bool first) {
    (void)first;  // Prevent unused variable warning
}

void Vtb_s2a_conv_tile_unit_std__03a__03asemaphore__Vclpkg::dtor() {
    VL_DO_DANGLING(std::free(const_cast<char*>(vlNamep)), vlNamep);
}
