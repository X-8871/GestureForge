// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Model implementation (design independent parts)

#include "Vtb_runtime__pch.h"

//============================================================
// Constructors

Vtb_runtime::Vtb_runtime(VerilatedContext* _vcontextp__, const char* _vcname__)
    : VerilatedModel{*_vcontextp__}
    , vlSymsp{new Vtb_runtime__Syms(contextp(), _vcname__, this)}
    , rootp{&(vlSymsp->TOP)}
{
    // Register model with the context
    contextp()->addModel(this);
}

Vtb_runtime::Vtb_runtime(const char* _vcname__)
    : Vtb_runtime(Verilated::threadContextp(), _vcname__)
{
}

//============================================================
// Destructor

Vtb_runtime::~Vtb_runtime() {
    delete vlSymsp;
}

//============================================================
// Evaluation function

#ifdef VL_DEBUG
void Vtb_runtime___024root___eval_debug_assertions(Vtb_runtime___024root* vlSelf);
#endif  // VL_DEBUG
void Vtb_runtime___024root___eval_static(Vtb_runtime___024root* vlSelf);
void Vtb_runtime___024root___eval_initial(Vtb_runtime___024root* vlSelf);
void Vtb_runtime___024root___eval_settle(Vtb_runtime___024root* vlSelf);
void Vtb_runtime___024root___eval(Vtb_runtime___024root* vlSelf);

void Vtb_runtime::eval_step() {
    VL_DEBUG_IF(VL_DBG_MSGF("+++++TOP Evaluate Vtb_runtime::eval_step\n"); );
#ifdef VL_DEBUG
    // Debug assertions
    Vtb_runtime___024root___eval_debug_assertions(&(vlSymsp->TOP));
#endif  // VL_DEBUG
    vlSymsp->__Vm_deleter.deleteAll();
    if (VL_UNLIKELY(!vlSymsp->__Vm_didInit)) {
        VL_DEBUG_IF(VL_DBG_MSGF("+ Initial\n"););
        Vtb_runtime___024root___eval_static(&(vlSymsp->TOP));
        Vtb_runtime___024root___eval_initial(&(vlSymsp->TOP));
        Vtb_runtime___024root___eval_settle(&(vlSymsp->TOP));
        vlSymsp->__Vm_didInit = true;
    }
    VL_DEBUG_IF(VL_DBG_MSGF("+ Eval\n"););
    Vtb_runtime___024root___eval(&(vlSymsp->TOP));
    // Evaluate cleanup
    Verilated::endOfEval(vlSymsp->__Vm_evalMsgQp);
}

//============================================================
// Events and timing
bool Vtb_runtime::eventsPending() { return !vlSymsp->TOP.__VdlySched.empty() && !contextp()->gotFinish(); }

uint64_t Vtb_runtime::nextTimeSlot() { return vlSymsp->TOP.__VdlySched.nextTimeSlot(); }

//============================================================
// Utilities

const char* Vtb_runtime::name() const {
    return vlSymsp->name();
}

//============================================================
// Invoke final blocks

void Vtb_runtime___024root___eval_final(Vtb_runtime___024root* vlSelf);

VL_ATTR_COLD void Vtb_runtime::final() {
    contextp()->executingFinal(true);
    Vtb_runtime___024root___eval_final(&(vlSymsp->TOP));
    contextp()->executingFinal(false);
}

//============================================================
// Implementations of abstract methods from VerilatedModel

const char* Vtb_runtime::hierName() const { return vlSymsp->name(); }
const char* Vtb_runtime::modelName() const { return "Vtb_runtime"; }
unsigned Vtb_runtime::threads() const { return 1; }
void Vtb_runtime::prepareClone() const { contextp()->prepareClone(); }
void Vtb_runtime::atClone() const {
    contextp()->threadPoolpOnClone();
}
