// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Symbol table implementation internals

#include "Vtb_s2a_backend_fault_recovery__pch.h"

Vtb_s2a_backend_fault_recovery__Syms::Vtb_s2a_backend_fault_recovery__Syms(VerilatedContext* contextp, const char* namep, Vtb_s2a_backend_fault_recovery* modelp)
    : VerilatedSyms{contextp}
    // Setup internal state of the Syms class
    , __Vm_modelp{modelp}
    // Setup top module instance
    , TOP{this, namep}
{
    // Check resources
    Verilated::stackCheck(14208);
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

Vtb_s2a_backend_fault_recovery__Syms::~Vtb_s2a_backend_fault_recovery__Syms() {
    if (__Vm_dumping) _traceDumpClose();
    // Tear down scopes
    // Tear down sub module instances
    TOP__s2a_network_descriptor_pkg.dtor();
}

void Vtb_s2a_backend_fault_recovery__Syms::_traceDump() {
    const VerilatedLockGuard lock{__Vm_dumperMutex};
    __Vm_dumperp->dump(VL_TIME_Q());
}

void Vtb_s2a_backend_fault_recovery__Syms::_traceDumpOpen() {
    const VerilatedLockGuard lock{__Vm_dumperMutex};
    if (VL_UNLIKELY(!__Vm_dumperp)) {
        __Vm_dumperp = new VerilatedVcdC();
        __Vm_modelp->trace(__Vm_dumperp, 0, 0);
        const std::string dumpfile = _vm_contextp__->dumpfileCheck();
        __Vm_dumperp->open(dumpfile.c_str());
        __Vm_dumping = true;
    }
}

void Vtb_s2a_backend_fault_recovery__Syms::_traceDumpClose() {
    const VerilatedLockGuard lock{__Vm_dumperMutex};
    __Vm_dumping = false;
    VL_DO_CLEAR(delete __Vm_dumperp, __Vm_dumperp = nullptr);
}
