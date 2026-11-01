// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design internal header
// See Vtb_s2a_conv_tile_unit.h for the primary calling header

#ifndef VERILATED_VTB_S2A_CONV_TILE_UNIT___024UNIT_H_
#define VERILATED_VTB_S2A_CONV_TILE_UNIT___024UNIT_H_  // guard

#include "verilated.h"
#include "verilated_timing.h"


class Vtb_s2a_conv_tile_unit__Syms;

class alignas(VL_CACHE_LINE_BYTES) Vtb_s2a_conv_tile_unit___024unit final {
  public:

    // INTERNAL VARIABLES
    Vtb_s2a_conv_tile_unit__Syms* vlSymsp;
    const char* vlNamep;

    // CONSTRUCTORS
    Vtb_s2a_conv_tile_unit___024unit();
    ~Vtb_s2a_conv_tile_unit___024unit();
    void ctor(Vtb_s2a_conv_tile_unit__Syms* symsp, const char* namep);
    void dtor();
    VL_UNCOPYABLE(Vtb_s2a_conv_tile_unit___024unit);

    // INTERNAL METHODS
    void __Vconfigure(bool first);
};


#endif  // guard
