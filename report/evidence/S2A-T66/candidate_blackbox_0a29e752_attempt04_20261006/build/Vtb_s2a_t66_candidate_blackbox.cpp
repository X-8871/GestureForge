// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Model implementation (design independent parts)

#include "Vtb_s2a_t66_candidate_blackbox__pch.h"

//============================================================
// Constructors

Vtb_s2a_t66_candidate_blackbox::Vtb_s2a_t66_candidate_blackbox(VerilatedContext* _vcontextp__, const char* _vcname__)
    : VerilatedModel{*_vcontextp__}
    , vlSymsp{new Vtb_s2a_t66_candidate_blackbox__Syms(contextp(), _vcname__, this)}
    , __PVT__s2a_network_descriptor_pkg{vlSymsp->TOP.__PVT__s2a_network_descriptor_pkg}
    , rootp{&(vlSymsp->TOP)}
{
    // Register model with the context
    contextp()->addModel(this);
}

Vtb_s2a_t66_candidate_blackbox::Vtb_s2a_t66_candidate_blackbox(const char* _vcname__)
    : Vtb_s2a_t66_candidate_blackbox(Verilated::threadContextp(), _vcname__)
{
}

//============================================================
// Destructor

Vtb_s2a_t66_candidate_blackbox::~Vtb_s2a_t66_candidate_blackbox() {
    delete vlSymsp;
}

//============================================================
// Evaluation function

#ifdef VL_DEBUG
void Vtb_s2a_t66_candidate_blackbox___024root___eval_debug_assertions(Vtb_s2a_t66_candidate_blackbox___024root* vlSelf);
#endif  // VL_DEBUG
void Vtb_s2a_t66_candidate_blackbox___024root___eval_static(Vtb_s2a_t66_candidate_blackbox___024root* vlSelf);
void Vtb_s2a_t66_candidate_blackbox___024root___eval_initial(Vtb_s2a_t66_candidate_blackbox___024root* vlSelf);
void Vtb_s2a_t66_candidate_blackbox___024root___eval_settle(Vtb_s2a_t66_candidate_blackbox___024root* vlSelf);
void Vtb_s2a_t66_candidate_blackbox___024root___eval(Vtb_s2a_t66_candidate_blackbox___024root* vlSelf);

void Vtb_s2a_t66_candidate_blackbox::eval_step() {
    VL_DEBUG_IF(VL_DBG_MSGF("+++++TOP Evaluate Vtb_s2a_t66_candidate_blackbox::eval_step\n"); );
#ifdef VL_DEBUG
    // Debug assertions
    Vtb_s2a_t66_candidate_blackbox___024root___eval_debug_assertions(&(vlSymsp->TOP));
#endif  // VL_DEBUG
    vlSymsp->__Vm_deleter.deleteAll();
    if (VL_UNLIKELY(!vlSymsp->__Vm_didInit)) {
        VL_DEBUG_IF(VL_DBG_MSGF("+ Initial\n"););
        Vtb_s2a_t66_candidate_blackbox___024root___eval_static(&(vlSymsp->TOP));
        Vtb_s2a_t66_candidate_blackbox___024root___eval_initial(&(vlSymsp->TOP));
        Vtb_s2a_t66_candidate_blackbox___024root___eval_settle(&(vlSymsp->TOP));
        vlSymsp->__Vm_didInit = true;
    }
    VL_DEBUG_IF(VL_DBG_MSGF("+ Eval\n"););
    Vtb_s2a_t66_candidate_blackbox___024root___eval(&(vlSymsp->TOP));
    // Evaluate cleanup
    Verilated::endOfEval(vlSymsp->__Vm_evalMsgQp);
}

//============================================================
// Events and timing
bool Vtb_s2a_t66_candidate_blackbox::eventsPending() { return !vlSymsp->TOP.__VdlySched.empty() && !contextp()->gotFinish(); }

uint64_t Vtb_s2a_t66_candidate_blackbox::nextTimeSlot() { return vlSymsp->TOP.__VdlySched.nextTimeSlot(); }

//============================================================
// Utilities

const char* Vtb_s2a_t66_candidate_blackbox::name() const {
    return vlSymsp->name();
}

//============================================================
// Invoke final blocks

void Vtb_s2a_t66_candidate_blackbox___024root___eval_final(Vtb_s2a_t66_candidate_blackbox___024root* vlSelf);

VL_ATTR_COLD void Vtb_s2a_t66_candidate_blackbox::final() {
    contextp()->executingFinal(true);
    Vtb_s2a_t66_candidate_blackbox___024root___eval_final(&(vlSymsp->TOP));
    contextp()->executingFinal(false);
}

//============================================================
// Implementations of abstract methods from VerilatedModel

const char* Vtb_s2a_t66_candidate_blackbox::hierName() const { return vlSymsp->name(); }
const char* Vtb_s2a_t66_candidate_blackbox::modelName() const { return "Vtb_s2a_t66_candidate_blackbox"; }
unsigned Vtb_s2a_t66_candidate_blackbox::threads() const { return 1; }
void Vtb_s2a_t66_candidate_blackbox::prepareClone() const { contextp()->prepareClone(); }
void Vtb_s2a_t66_candidate_blackbox::atClone() const {
    contextp()->threadPoolpOnClone();
}
