// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Symbol table internal header
//
// Internal details; most calling programs do not need this header,
// unless using verilator public meta comments.

#ifndef VERILATED_VTB_S2A_T66_LAYER0_TILE__SYMS_H_
#define VERILATED_VTB_S2A_T66_LAYER0_TILE__SYMS_H_  // guard

#include "verilated.h"

// INCLUDE MODEL CLASS

#include "Vtb_s2a_t66_layer0_tile.h"

// INCLUDE MODULE CLASSES
#include "Vtb_s2a_t66_layer0_tile___024root.h"
#include "Vtb_s2a_t66_layer0_tile_s2a_network_descriptor_pkg.h"

// SYMS CLASS (contains all model state)
class alignas(VL_CACHE_LINE_BYTES) Vtb_s2a_t66_layer0_tile__Syms final : public VerilatedSyms {
  public:
    // INTERNAL STATE
    Vtb_s2a_t66_layer0_tile* const __Vm_modelp;
    VlDeleter __Vm_deleter;
    bool __Vm_didInit = false;

    // MODULE INSTANCE STATE
    Vtb_s2a_t66_layer0_tile___024root TOP;
    Vtb_s2a_t66_layer0_tile_s2a_network_descriptor_pkg TOP__s2a_network_descriptor_pkg;

    // CONSTRUCTORS
    Vtb_s2a_t66_layer0_tile__Syms(VerilatedContext* contextp, const char* namep, Vtb_s2a_t66_layer0_tile* modelp);
    ~Vtb_s2a_t66_layer0_tile__Syms();

    // METHODS
    const char* name() const { return TOP.vlNamep; }
};

#endif  // guard
