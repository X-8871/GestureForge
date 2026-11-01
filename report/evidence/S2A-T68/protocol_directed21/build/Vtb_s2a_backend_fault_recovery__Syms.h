// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Symbol table internal header
//
// Internal details; most calling programs do not need this header,
// unless using verilator public meta comments.

#ifndef VERILATED_VTB_S2A_BACKEND_FAULT_RECOVERY__SYMS_H_
#define VERILATED_VTB_S2A_BACKEND_FAULT_RECOVERY__SYMS_H_  // guard

#include "verilated.h"
#include "verilated_vcd_c.h"

// INCLUDE MODEL CLASS

#include "Vtb_s2a_backend_fault_recovery.h"

// INCLUDE MODULE CLASSES
#include "Vtb_s2a_backend_fault_recovery___024root.h"
#include "Vtb_s2a_backend_fault_recovery_s2a_network_descriptor_pkg.h"

// SYMS CLASS (contains all model state)
class alignas(VL_CACHE_LINE_BYTES) Vtb_s2a_backend_fault_recovery__Syms final : public VerilatedSyms {
  public:
    // INTERNAL STATE
    Vtb_s2a_backend_fault_recovery* const __Vm_modelp;
    bool __Vm_dumping = false;  // Dumping is active
    VerilatedMutex __Vm_dumperMutex;  // Protect __Vm_dumperp
    VerilatedVcdC* __Vm_dumperp VL_GUARDED_BY(__Vm_dumperMutex) = nullptr;  /// Trace class for $dump*
    bool __Vm_activity = false;  ///< Used by trace routines to determine change occurred
    uint32_t __Vm_baseCode = 0;  ///< Used by trace routines when tracing multiple models
    VlDeleter __Vm_deleter;
    bool __Vm_didInit = false;

    // MODULE INSTANCE STATE
    Vtb_s2a_backend_fault_recovery___024root TOP;
    Vtb_s2a_backend_fault_recovery_s2a_network_descriptor_pkg TOP__s2a_network_descriptor_pkg;

    // CONSTRUCTORS
    Vtb_s2a_backend_fault_recovery__Syms(VerilatedContext* contextp, const char* namep, Vtb_s2a_backend_fault_recovery* modelp);
    ~Vtb_s2a_backend_fault_recovery__Syms();

    // METHODS
    const char* name() const { return TOP.vlNamep; }
    void _traceDump();
    void _traceDumpOpen();
    void _traceDumpClose();
};

#endif  // guard
