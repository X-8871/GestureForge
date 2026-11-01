// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design internal header
// See Vtb_runtime.h for the primary calling header

#ifndef VERILATED_VTB_RUNTIME___024ROOT_H_
#define VERILATED_VTB_RUNTIME___024ROOT_H_  // guard

#include "verilated.h"
#include "verilated_timing.h"


class Vtb_runtime__Syms;

class alignas(VL_CACHE_LINE_BYTES) Vtb_runtime___024root final {
  public:

    // DESIGN SPECIFIC STATE
    CData/*0:0*/ tb_runtime__DOT__clk;
    CData/*0:0*/ __VactPhaseResult;
    CData/*0:0*/ __VinactPhaseResult;
    CData/*0:0*/ __VnbaPhaseResult;
    IData/*31:0*/ __VactIterCount;
    IData/*31:0*/ __VinactIterCount;
    IData/*31:0*/ __Vi;
    VlUnpacked<QData/*63:0*/, 1> __VactTriggered;
    VlUnpacked<QData/*63:0*/, 1> __VactTriggeredAcc;
    VlUnpacked<QData/*63:0*/, 1> __VnbaTriggered;
    VlDelayScheduler __VdlySched;

    // INTERNAL VARIABLES
    Vtb_runtime__Syms* vlSymsp;
    const char* vlNamep;

    // CONSTRUCTORS
    Vtb_runtime___024root(Vtb_runtime__Syms* symsp, const char* namep);
    ~Vtb_runtime___024root();
    VL_UNCOPYABLE(Vtb_runtime___024root);

    // INTERNAL METHODS
    void __Vconfigure(bool first);
};


#endif  // guard
