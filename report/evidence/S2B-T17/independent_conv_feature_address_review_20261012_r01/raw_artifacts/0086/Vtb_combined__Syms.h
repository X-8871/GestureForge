// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Symbol table internal header
//
// Internal details; most calling programs do not need this header,
// unless using verilator public meta comments.

#ifndef VERILATED_VTB_COMBINED__SYMS_H_
#define VERILATED_VTB_COMBINED__SYMS_H_  // guard

#include "verilated.h"

// INCLUDE MODEL CLASS

#include "Vtb_combined.h"

// INCLUDE MODULE CLASSES
#include "Vtb_combined___024root.h"
#include "Vtb_combined_s2a_network_descriptor_pkg.h"

// SYMS CLASS (contains all model state)
class alignas(VL_CACHE_LINE_BYTES) Vtb_combined__Syms final : public VerilatedSyms {
  public:
    // INTERNAL STATE
    Vtb_combined* const __Vm_modelp;
    VlDeleter __Vm_deleter;
    bool __Vm_didInit = false;

    // MODULE INSTANCE STATE
    Vtb_combined___024root         TOP;
    Vtb_combined_s2a_network_descriptor_pkg TOP__s2a_network_descriptor_pkg;

    // CONSTRUCTORS
    Vtb_combined__Syms(VerilatedContext* contextp, const char* namep, Vtb_combined* modelp);
    ~Vtb_combined__Syms();
    void Vtb_combined__Syms__ctor__0();
    void Vtb_combined__Syms__dtor__0();

    // METHODS
    const char* name() const { return TOP.vlNamep; }
};

#endif  // guard
