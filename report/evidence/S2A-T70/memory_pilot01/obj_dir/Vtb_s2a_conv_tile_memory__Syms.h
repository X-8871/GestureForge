// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Symbol table internal header
//
// Internal details; most calling programs do not need this header,
// unless using verilator public meta comments.

#ifndef VERILATED_VTB_S2A_CONV_TILE_MEMORY__SYMS_H_
#define VERILATED_VTB_S2A_CONV_TILE_MEMORY__SYMS_H_  // guard

#include "verilated.h"

// INCLUDE MODEL CLASS

#include "Vtb_s2a_conv_tile_memory.h"

// INCLUDE MODULE CLASSES
#include "Vtb_s2a_conv_tile_memory___024root.h"
#include "Vtb_s2a_conv_tile_memory_s2a_network_descriptor_pkg.h"

// SYMS CLASS (contains all model state)
class alignas(VL_CACHE_LINE_BYTES) Vtb_s2a_conv_tile_memory__Syms final : public VerilatedSyms {
  public:
    // INTERNAL STATE
    Vtb_s2a_conv_tile_memory* const __Vm_modelp;
    VlDeleter __Vm_deleter;
    bool __Vm_didInit = false;

    // MODULE INSTANCE STATE
    Vtb_s2a_conv_tile_memory___024root TOP;
    Vtb_s2a_conv_tile_memory_s2a_network_descriptor_pkg TOP__s2a_network_descriptor_pkg;

    // CONSTRUCTORS
    Vtb_s2a_conv_tile_memory__Syms(VerilatedContext* contextp, const char* namep, Vtb_s2a_conv_tile_memory* modelp);
    ~Vtb_s2a_conv_tile_memory__Syms();

    // METHODS
    const char* name() const { return TOP.vlNamep; }
};

#endif  // guard
