// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vtb_s2a_conv_tile_unit.h for the primary calling header

#include "Vtb_s2a_conv_tile_unit__pch.h"

void Vtb_s2a_conv_tile_unit_std__03a__03asemaphore::init(Vtb_s2a_conv_tile_unit__Syms* __restrict vlSymsp, IData/*31:0*/ keyCount) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtb_s2a_conv_tile_unit_std__03a__03asemaphore::new\n"); );
    // Body
    _ctor_var_reset(vlSymsp);
    this->__PVT__m_nextKeyCount = 0xffffffffU;
    this->__PVT__m_ticket = 0ULL;
    this->__PVT__m_nextTicket = 0ULL;
    this->__PVT__m_keyCount = keyCount;
}

void Vtb_s2a_conv_tile_unit_std__03a__03asemaphore::__VnoInFunc_put(Vtb_s2a_conv_tile_unit__Syms* __restrict vlSymsp, IData/*31:0*/ keyCount) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtb_s2a_conv_tile_unit_std__03a__03asemaphore::__VnoInFunc_put\n"); );
    // Body
    this->__PVT__m_keyCount = (this->__PVT__m_keyCount 
                               + keyCount);
}

VlCoroutine Vtb_s2a_conv_tile_unit_std__03a__03asemaphore::__VnoInFunc_get(Vtb_s2a_conv_tile_unit__Syms* __restrict vlSymsp, IData/*31:0*/ keyCount) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtb_s2a_conv_tile_unit_std__03a__03asemaphore::__VnoInFunc_get\n"); );
    // Locals
    CData/*0:0*/ __Vtrigprevexpr_hf216aab4__0;
    __Vtrigprevexpr_hf216aab4__0 = 0;
    CData/*0:0*/ __Vtrigprevexpr_h40d5940f__0;
    __Vtrigprevexpr_h40d5940f__0 = 0;
    // Body
    VL_KEEP_THIS;
    QData/*63:0*/ __Vincrement1;
    __Vincrement1 = 0;
    QData/*63:0*/ ticket;
    {
        ticket = 0ULL;
        if ((VL_GTES_III(32, this->__PVT__m_keyCount, keyCount) 
             & VL_GTS_III(32, this->__PVT__m_nextKeyCount, this->__PVT__m_keyCount))) {
            this->__PVT__m_keyCount = (this->__PVT__m_keyCount 
                                       - keyCount);
            goto __Vlabel0;
        }
        __Vincrement1 = this->__PVT__m_nextTicket;
        this->__PVT__m_nextTicket = (1ULL + this->__PVT__m_nextTicket);
        ticket = __Vincrement1;
        if ((this->__PVT__m_ticket != ticket)) {
            CData/*0:0*/ __VdynTrigger_h4319c8b5__0;
            __VdynTrigger_h4319c8b5__0 = 0;
            __VdynTrigger_h4319c8b5__0 = 0U;
            while ((1U & (~ (IData)(__VdynTrigger_h4319c8b5__0)))) {
                co_await vlSymsp->TOP.__VdynSched.evaluation(
                                                             nullptr, 
                                                             "@([true] (std::semaphore.m_ticket == std::semaphore.ticket))", 
                                                             "D:\\FPGA_S2A_MSYS2_20261001\\env\\mingw64\\share\\verilator\\include\\verilated_std.sv", 
                                                             127);
                __Vtrigprevexpr_h40d5940f__0 = (this->__PVT__m_ticket 
                                                == ticket);
                __VdynTrigger_h4319c8b5__0 = __Vtrigprevexpr_h40d5940f__0;
                vlSymsp->TOP.__VdynSched.anyTriggered(__VdynTrigger_h4319c8b5__0);
            }
            co_await vlSymsp->TOP.__VdynSched.resumption(
                                                         nullptr, 
                                                         "@([true] (std::semaphore.m_ticket == std::semaphore.ticket))", 
                                                         "D:\\FPGA_S2A_MSYS2_20261001\\env\\mingw64\\share\\verilator\\include\\verilated_std.sv", 
                                                         127);
        }
        this->__PVT__m_nextKeyCount = keyCount;
        if (VL_LTS_III(32, this->__PVT__m_keyCount, keyCount)) {
            CData/*0:0*/ __VdynTrigger_h1458e362__0;
            __VdynTrigger_h1458e362__0 = 0;
            __VdynTrigger_h1458e362__0 = 0U;
            while ((1U & (~ (IData)(__VdynTrigger_h1458e362__0)))) {
                co_await vlSymsp->TOP.__VdynSched.evaluation(
                                                             nullptr, 
                                                             "@([true] (std::semaphore.m_keyCount >= std::semaphore.keyCount))", 
                                                             "D:\\FPGA_S2A_MSYS2_20261001\\env\\mingw64\\share\\verilator\\include\\verilated_std.sv", 
                                                             129);
                __Vtrigprevexpr_hf216aab4__0 = VL_GTES_III(32, this->__PVT__m_keyCount, keyCount);
                __VdynTrigger_h1458e362__0 = __Vtrigprevexpr_hf216aab4__0;
                vlSymsp->TOP.__VdynSched.anyTriggered(__VdynTrigger_h1458e362__0);
            }
            co_await vlSymsp->TOP.__VdynSched.resumption(
                                                         nullptr, 
                                                         "@([true] (std::semaphore.m_keyCount >= std::semaphore.keyCount))", 
                                                         "D:\\FPGA_S2A_MSYS2_20261001\\env\\mingw64\\share\\verilator\\include\\verilated_std.sv", 
                                                         129);
        }
        this->__PVT__m_keyCount = (this->__PVT__m_keyCount 
                                   - keyCount);
        this->__PVT__m_ticket = (1ULL + this->__PVT__m_ticket);
        __Vlabel0: ;
    }
    co_return;
}

void Vtb_s2a_conv_tile_unit_std__03a__03asemaphore::__VnoInFunc_try_get(Vtb_s2a_conv_tile_unit__Syms* __restrict vlSymsp, IData/*31:0*/ keyCount, IData/*31:0*/ &try_get__Vfuncrtn) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtb_s2a_conv_tile_unit_std__03a__03asemaphore::__VnoInFunc_try_get\n"); );
    // Body
    {
        try_get__Vfuncrtn = 0U;
        if (VL_LTS_III(32, this->__PVT__m_keyCount, keyCount)) {
            try_get__Vfuncrtn = 0U;
            goto __Vlabel0;
        }
        this->__PVT__m_keyCount = (this->__PVT__m_keyCount 
                                   - keyCount);
        try_get__Vfuncrtn = 1U;
        __Vlabel0: ;
    }
}

void Vtb_s2a_conv_tile_unit_std__03a__03asemaphore::_ctor_var_reset(Vtb_s2a_conv_tile_unit__Syms* __restrict vlSymsp) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtb_s2a_conv_tile_unit_std__03a__03asemaphore::_ctor_var_reset\n"); );
    // Body
    (void)vlSymsp;  // Prevent unused variable warning
    __PVT__m_keyCount = 0;
}
