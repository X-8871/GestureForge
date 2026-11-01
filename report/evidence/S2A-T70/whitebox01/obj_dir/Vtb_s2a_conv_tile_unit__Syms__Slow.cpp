// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Symbol table implementation internals

#include "Vtb_s2a_conv_tile_unit__pch.h"

Vtb_s2a_conv_tile_unit__Syms::Vtb_s2a_conv_tile_unit__Syms(VerilatedContext* contextp, const char* namep, Vtb_s2a_conv_tile_unit* modelp)
    : VerilatedSyms{contextp}
    // Setup internal state of the Syms class
    , __Vm_modelp{modelp}
    // Setup top module instance
    , TOP{this, namep}
{
    // Check resources
    Verilated::stackCheck(15024);
    // Setup sub module instances
    TOP__s2a_network_descriptor_pkg.ctor(this, "s2a_network_descriptor_pkg");
    // Configure time unit / time precision
    _vm_contextp__->timeunit(-9);
    _vm_contextp__->timeprecision(-12);
    // Setup each module's pointers to their submodules
    TOP.__PVT__s2a_network_descriptor_pkg = &TOP__s2a_network_descriptor_pkg;
    // Setup each module's pointer back to symbol table (for public functions)
    TOP.__Vconfigure(true);
    TOP__s2a_network_descriptor_pkg.__Vconfigure(true);
    // Setup scopes
}

Vtb_s2a_conv_tile_unit__Syms::~Vtb_s2a_conv_tile_unit__Syms() {
    // Tear down scopes
    // Tear down sub module instances
    TOP__s2a_network_descriptor_pkg.dtor();
}
