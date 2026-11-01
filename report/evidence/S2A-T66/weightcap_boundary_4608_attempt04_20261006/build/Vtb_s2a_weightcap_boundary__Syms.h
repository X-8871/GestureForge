// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Symbol table internal header
//
// Internal details; most calling programs do not need this header,
// unless using verilator public meta comments.

#ifndef VERILATED_VTB_S2A_WEIGHTCAP_BOUNDARY__SYMS_H_
#define VERILATED_VTB_S2A_WEIGHTCAP_BOUNDARY__SYMS_H_  // guard

#include "verilated.h"

// INCLUDE MODEL CLASS

#include "Vtb_s2a_weightcap_boundary.h"

// INCLUDE MODULE CLASSES
#include "Vtb_s2a_weightcap_boundary___024root.h"
#include "Vtb_s2a_weightcap_boundary_s2a_network_descriptor_pkg.h"

// SYMS CLASS (contains all model state)
class alignas(VL_CACHE_LINE_BYTES) Vtb_s2a_weightcap_boundary__Syms final : public VerilatedSyms {
  public:
    // INTERNAL STATE
    Vtb_s2a_weightcap_boundary* const __Vm_modelp;
    VlDeleter __Vm_deleter;
    bool __Vm_didInit = false;

    // MODULE INSTANCE STATE
    Vtb_s2a_weightcap_boundary___024root TOP;
    Vtb_s2a_weightcap_boundary_s2a_network_descriptor_pkg TOP__s2a_network_descriptor_pkg;

    // CONSTRUCTORS
    Vtb_s2a_weightcap_boundary__Syms(VerilatedContext* contextp, const char* namep, Vtb_s2a_weightcap_boundary* modelp);
    ~Vtb_s2a_weightcap_boundary__Syms();

    // METHODS
    const char* name() const { return TOP.vlNamep; }
};

#endif  // guard
