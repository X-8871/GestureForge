// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vtb_s2a_conv_tile_unit.h for the primary calling header

#include "Vtb_s2a_conv_tile_unit__pch.h"

void Vtb_s2a_conv_tile_unit_std__03a__03aprocess__Vclpkg::__VnoInFunc_self(VlProcessRef vlProcess, Vtb_s2a_conv_tile_unit__Syms* __restrict vlSymsp, VlClassRef<Vtb_s2a_conv_tile_unit_std__03a__03aprocess> &self__Vfuncrtn) {
    VL_DEBUG_IF(VL_DBG_MSGF("+  Vtb_s2a_conv_tile_unit_std__03a__03aprocess__Vclpkg::__VnoInFunc_self\n"); );
    // Body
    VlProcess::currentp(vlProcess.get());
    VlClassRef<Vtb_s2a_conv_tile_unit_std__03a__03aprocess> p;
    p = VL_NEW(Vtb_s2a_conv_tile_unit_std__03a__03aprocess, vlSymsp);

// $c statement at D:\FPGA_S2A_MSYS2_20261001\env\mingw64\share\verilator\include\verilated_std.sv:159:7
    VL_NULL_CHECK(p, "D:\\FPGA_S2A_MSYS2_20261001\\env\\mingw64\\share\\verilator\\include\\verilated_std.sv", 159)->m_process = vlProcess;
    self__Vfuncrtn = p;
}

void Vtb_s2a_conv_tile_unit_std__03a__03aprocess__Vclpkg::__VnoInFunc_killQueue(Vtb_s2a_conv_tile_unit__Syms* __restrict vlSymsp, VlQueue<VlClassRef<Vtb_s2a_conv_tile_unit_std__03a__03aprocess>> &processQueue) {
    VL_DEBUG_IF(VL_DBG_MSGF("+  Vtb_s2a_conv_tile_unit_std__03a__03aprocess__Vclpkg::__VnoInFunc_killQueue\n"); );
    // Body
    IData/*31:0*/ unnamedblk1_1__DOT____Vrepeat0;
    unnamedblk1_1__DOT____Vrepeat0 = 0;
    unnamedblk1_1__DOT____Vrepeat0 = processQueue.size();
    while (VL_LTS_III(32, 0U, unnamedblk1_1__DOT____Vrepeat0)) {
        VL_NULL_CHECK(processQueue.pop_front(), "D:\\FPGA_S2A_MSYS2_20261001\\env\\mingw64\\share\\verilator\\include\\verilated_std.sv", 199)->__VnoInFunc_kill(vlSymsp);
        unnamedblk1_1__DOT____Vrepeat0 = (unnamedblk1_1__DOT____Vrepeat0 
                                          - (IData)(1U));
    }
}

void Vtb_s2a_conv_tile_unit_std__03a__03aprocess::__VnoInFunc_set_status(Vtb_s2a_conv_tile_unit__Syms* __restrict vlSymsp, IData/*31:0*/ s) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtb_s2a_conv_tile_unit_std__03a__03aprocess::__VnoInFunc_set_status\n"); );
    // Body

// $c statement at D:\FPGA_S2A_MSYS2_20261001\env\mingw64\share\verilator\include\verilated_std.sv:166:7
    this->m_process->state(s);
}

void Vtb_s2a_conv_tile_unit_std__03a__03aprocess::__VnoInFunc_status(Vtb_s2a_conv_tile_unit__Syms* __restrict vlSymsp, IData/*31:0*/ &status__Vfuncrtn) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtb_s2a_conv_tile_unit_std__03a__03aprocess::__VnoInFunc_status\n"); );
    // Body
    status__Vfuncrtn = 0U;
    status__Vfuncrtn = 
// $cpure expression at D:\FPGA_S2A_MSYS2_20261001\env\mingw64\share\verilator\include\verilated_std.sv:172:21
this->m_process->state()
    ;
}

void Vtb_s2a_conv_tile_unit_std__03a__03aprocess::__VnoInFunc_kill(Vtb_s2a_conv_tile_unit__Syms* __restrict vlSymsp) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtb_s2a_conv_tile_unit_std__03a__03aprocess::__VnoInFunc_kill\n"); );
    // Body
    this->__VnoInFunc_set_status(vlSymsp, 4U);
}

void Vtb_s2a_conv_tile_unit_std__03a__03aprocess::__VnoInFunc_suspend(Vtb_s2a_conv_tile_unit__Syms* __restrict vlSymsp) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtb_s2a_conv_tile_unit_std__03a__03aprocess::__VnoInFunc_suspend\n"); );
    // Body
    VL_WRITEF_NX("[%0t] %%Error: verilated_std.sv:183: Assertion failed in %m: std::process::suspend() not supported\n",3, 'M',vlSymsp->name(),"std.process.suspend", 'T',-9
                 , '#',64,VL_TIME_UNITED_Q(1000));
    VL_STOP_MT("D:\\FPGA_S2A_MSYS2_20261001\\env\\mingw64\\share\\verilator\\include\\verilated_std.sv", 183, "");
}

void Vtb_s2a_conv_tile_unit_std__03a__03aprocess::__VnoInFunc_resume(Vtb_s2a_conv_tile_unit__Syms* __restrict vlSymsp) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtb_s2a_conv_tile_unit_std__03a__03aprocess::__VnoInFunc_resume\n"); );
    // Body
    this->__VnoInFunc_set_status(vlSymsp, 1U);
}

VlCoroutine Vtb_s2a_conv_tile_unit_std__03a__03aprocess::__VnoInFunc_await(Vtb_s2a_conv_tile_unit__Syms* __restrict vlSymsp) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtb_s2a_conv_tile_unit_std__03a__03aprocess::__VnoInFunc_await\n"); );
    // Locals
    CData/*0:0*/ __Vtrigprevexpr_hd8bde081__0;
    __Vtrigprevexpr_hd8bde081__0 = 0;
    // Body
    VL_KEEP_THIS;
    IData/*31:0*/ __VlefCall_1__status;
    IData/*31:0*/ __VlefCall_0__status;
    this->__VnoInFunc_status(vlSymsp, __VlefCall_0__status);
    this->__VnoInFunc_status(vlSymsp, __VlefCall_1__status);
    if ((1U & (~ ((0U == __VlefCall_0__status) | (4U 
                                                  == __VlefCall_1__status))))) {
        CData/*0:0*/ __VdynTrigger_heac11d1f__0;
        __VdynTrigger_heac11d1f__0 = 0;
        __VdynTrigger_heac11d1f__0 = 0U;
        while ((1U & (~ (IData)(__VdynTrigger_heac11d1f__0)))) {
            co_await vlSymsp->TOP.__VdynSched.evaluation(
                                                         nullptr, 
                                                         "@([true] ((32'h0 == std::process.__VlefCall_0__status) | (32'h4 == std::process.__VlefCall_1__status)))", 
                                                         "D:\\FPGA_S2A_MSYS2_20261001\\env\\mingw64\\share\\verilator\\include\\verilated_std.sv", 
                                                         192);
            __Vtrigprevexpr_hd8bde081__0 = ((0U == __VlefCall_0__status) 
                                            | (4U == __VlefCall_1__status));
            __VdynTrigger_heac11d1f__0 = __Vtrigprevexpr_hd8bde081__0;
            vlSymsp->TOP.__VdynSched.anyTriggered(__VdynTrigger_heac11d1f__0);
        }
        co_await vlSymsp->TOP.__VdynSched.resumption(
                                                     nullptr, 
                                                     "@([true] ((32'h0 == std::process.__VlefCall_0__status) | (32'h4 == std::process.__VlefCall_1__status)))", 
                                                     "D:\\FPGA_S2A_MSYS2_20261001\\env\\mingw64\\share\\verilator\\include\\verilated_std.sv", 
                                                     192);
    }
    co_return;
}

void Vtb_s2a_conv_tile_unit_std__03a__03aprocess::__VnoInFunc_get_randstate(Vtb_s2a_conv_tile_unit__Syms* __restrict vlSymsp, std::string &get_randstate__Vfuncrtn) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtb_s2a_conv_tile_unit_std__03a__03aprocess::__VnoInFunc_get_randstate\n"); );
    // Body
    std::string s;
    s = VL_CVT_PACK_STR_NI(
// $c expression at D:\FPGA_S2A_MSYS2_20261001\env\mingw64\share\verilator\include\verilated_std.sv:234:26
0
    );

// $c statement at D:\FPGA_S2A_MSYS2_20261001\env\mingw64\share\verilator\include\verilated_std.sv:236:7
    s = this->m_process->randstate();
    get_randstate__Vfuncrtn = s;
}

void Vtb_s2a_conv_tile_unit_std__03a__03aprocess::__VnoInFunc_set_randstate(Vtb_s2a_conv_tile_unit__Syms* __restrict vlSymsp, std::string s) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtb_s2a_conv_tile_unit_std__03a__03aprocess::__VnoInFunc_set_randstate\n"); );
    // Body

// $c statement at D:\FPGA_S2A_MSYS2_20261001\env\mingw64\share\verilator\include\verilated_std.sv:241:7
    this->m_process->randstate(s);
}

void Vtb_s2a_conv_tile_unit_std__03a__03aprocess::init(Vtb_s2a_conv_tile_unit__Syms* __restrict vlSymsp) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtb_s2a_conv_tile_unit_std__03a__03aprocess::new\n"); );
    // Body
    _ctor_var_reset(vlSymsp);
}

void Vtb_s2a_conv_tile_unit_std__03a__03aprocess::_ctor_var_reset(Vtb_s2a_conv_tile_unit__Syms* __restrict vlSymsp) {
    VL_DEBUG_IF(VL_DBG_MSGF("+            Vtb_s2a_conv_tile_unit_std__03a__03aprocess::_ctor_var_reset\n"); );
    // Body
    (void)vlSymsp;  // Prevent unused variable warning
}
