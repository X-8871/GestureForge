// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design internal header
// See Vtb_s2a_conv_tile_unit.h for the primary calling header

#ifndef VERILATED_VTB_S2A_CONV_TILE_UNIT_STD__03A__03APROCESS__VCLPKG_H_
#define VERILATED_VTB_S2A_CONV_TILE_UNIT_STD__03A__03APROCESS__VCLPKG_H_  // guard

#include "verilated.h"
#include "verilated_timing.h"
class Vtb_s2a_conv_tile_unit_std__03a__03aprocess;


class Vtb_s2a_conv_tile_unit__Syms;

class alignas(VL_CACHE_LINE_BYTES) Vtb_s2a_conv_tile_unit_std__03a__03aprocess__Vclpkg final {
  public:

    // INTERNAL VARIABLES
    Vtb_s2a_conv_tile_unit__Syms* vlSymsp;
    const char* vlNamep;

    // CONSTRUCTORS
    Vtb_s2a_conv_tile_unit_std__03a__03aprocess__Vclpkg();
    ~Vtb_s2a_conv_tile_unit_std__03a__03aprocess__Vclpkg();
    void ctor(Vtb_s2a_conv_tile_unit__Syms* symsp, const char* namep);
    void dtor();
    VL_UNCOPYABLE(Vtb_s2a_conv_tile_unit_std__03a__03aprocess__Vclpkg);

    // INTERNAL METHODS
    void __Vconfigure(bool first);
    void __VnoInFunc_killQueue(Vtb_s2a_conv_tile_unit__Syms* __restrict vlSymsp, VlQueue<VlClassRef<Vtb_s2a_conv_tile_unit_std__03a__03aprocess>> &processQueue);
    void __VnoInFunc_self(VlProcessRef vlProcess, Vtb_s2a_conv_tile_unit__Syms* __restrict vlSymsp, VlClassRef<Vtb_s2a_conv_tile_unit_std__03a__03aprocess> &self__Vfuncrtn);
};


class Vtb_s2a_conv_tile_unit__Syms;

class Vtb_s2a_conv_tile_unit_std__03a__03aprocess : public virtual VlClass {
  public:

    // DESIGN SPECIFIC STATE
    VlProcessRef m_process;

    // INTERNAL METHODS
    virtual const char* typeName() const { return "std::process"; }
    VlClass* clone() const { return new Vtb_s2a_conv_tile_unit_std__03a__03aprocess(*this); }
    VlCoroutine __VnoInFunc_await(Vtb_s2a_conv_tile_unit__Syms* __restrict vlSymsp);
    void __VnoInFunc_get_randstate(Vtb_s2a_conv_tile_unit__Syms* __restrict vlSymsp, std::string &get_randstate__Vfuncrtn);
    void __VnoInFunc_kill(Vtb_s2a_conv_tile_unit__Syms* __restrict vlSymsp);
    void __VnoInFunc_resume(Vtb_s2a_conv_tile_unit__Syms* __restrict vlSymsp);
    void __VnoInFunc_set_randstate(Vtb_s2a_conv_tile_unit__Syms* __restrict vlSymsp, std::string s);
    void __VnoInFunc_set_status(Vtb_s2a_conv_tile_unit__Syms* __restrict vlSymsp, IData/*31:0*/ s);
    void __VnoInFunc_status(Vtb_s2a_conv_tile_unit__Syms* __restrict vlSymsp, IData/*31:0*/ &status__Vfuncrtn);
    void __VnoInFunc_suspend(Vtb_s2a_conv_tile_unit__Syms* __restrict vlSymsp);
  private:
    void _ctor_var_reset(Vtb_s2a_conv_tile_unit__Syms* __restrict vlSymsp);
  public:
    Vtb_s2a_conv_tile_unit_std__03a__03aprocess() = default;
    void init(Vtb_s2a_conv_tile_unit__Syms* __restrict vlSymsp);
    ~Vtb_s2a_conv_tile_unit_std__03a__03aprocess() {}
};



//*** Below code from `systemc in Verilog file
// From `systemc at D:\FPGA_S2A_MSYS2_20261001\env\mingw64\share\verilator\include\verilated_std.sv:211:21

template<> template<>
inline bool VlClassRef<Vtb_s2a_conv_tile_unit_std__03a__03aprocess>::operator==(const VlClassRef<Vtb_s2a_conv_tile_unit_std__03a__03aprocess>& rhs) const {
    if (!m_objp && !rhs.m_objp) return true;
    if (!m_objp || !rhs.m_objp) return false;
    return m_objp->m_process == rhs.m_objp->m_process;
};
template<> template<>
inline bool VlClassRef<Vtb_s2a_conv_tile_unit_std__03a__03aprocess>::operator!=(const VlClassRef<Vtb_s2a_conv_tile_unit_std__03a__03aprocess>& rhs) const {
    if (!m_objp && !rhs.m_objp) return false;
    if (!m_objp || !rhs.m_objp) return true;
    return m_objp->m_process != rhs.m_objp->m_process;
};
template<> template<>
inline bool VlClassRef<Vtb_s2a_conv_tile_unit_std__03a__03aprocess>::operator<(const VlClassRef<Vtb_s2a_conv_tile_unit_std__03a__03aprocess>& rhs) const {
    if (!m_objp && !rhs.m_objp) return false;
    if (!m_objp || !rhs.m_objp) return false;
    return m_objp->m_process < rhs.m_objp->m_process;
};
//*** Above code from `systemc in Verilog file


#endif  // guard
