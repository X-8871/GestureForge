// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Symbol table implementation internals

#include "Vtb_combined__pch.h"

void Vtb_combined__Syms::Vtb_combined__Syms__ctor__0() {
    // Check resources
    Verilated::stackCheck(11937);
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
