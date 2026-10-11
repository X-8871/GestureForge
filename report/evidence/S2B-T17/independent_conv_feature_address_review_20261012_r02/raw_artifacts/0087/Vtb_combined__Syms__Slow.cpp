// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Symbol table implementation internals

#include "Vtb_combined__pch.h"

Vtb_combined__Syms::Vtb_combined__Syms(VerilatedContext* contextp, const char* namep, Vtb_combined* modelp)
    : VerilatedSyms{contextp}
    // Setup internal state of the Syms class
    , __Vm_modelp{modelp}
    // Setup top module instance
    , TOP{this, namep}
{
    Vtb_combined__Syms__ctor__0();
}

Vtb_combined__Syms::~Vtb_combined__Syms() {
    Vtb_combined__Syms__dtor__0();
}
