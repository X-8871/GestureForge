// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vtb_s2a_t66_layer0_tile.h for the primary calling header

#include "Vtb_s2a_t66_layer0_tile__pch.h"

void Vtb_s2a_t66_layer0_tile___024root___ctor_var_reset(Vtb_s2a_t66_layer0_tile___024root* vlSelf);

Vtb_s2a_t66_layer0_tile___024root::Vtb_s2a_t66_layer0_tile___024root(Vtb_s2a_t66_layer0_tile__Syms* symsp, const char* namep)
    : __VdlySched{*symsp->_vm_contextp__}
 {
    vlSymsp = symsp;
    vlNamep = strdup(namep);
    // Reset structure values
    Vtb_s2a_t66_layer0_tile___024root___ctor_var_reset(this);
}

void Vtb_s2a_t66_layer0_tile___024root::__Vconfigure(bool first) {
    (void)first;  // Prevent unused variable warning
}

Vtb_s2a_t66_layer0_tile___024root::~Vtb_s2a_t66_layer0_tile___024root() {
    VL_DO_DANGLING(std::free(const_cast<char*>(vlNamep)), vlNamep);
}
