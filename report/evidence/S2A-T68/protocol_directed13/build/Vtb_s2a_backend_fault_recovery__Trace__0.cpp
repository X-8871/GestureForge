// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Tracing implementation internals

#include "verilated_vcd_c.h"
#include "Vtb_s2a_backend_fault_recovery__Syms.h"


void Vtb_s2a_backend_fault_recovery___024root__trace_chg_0_sub_0(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd::Buffer* bufp);

void Vtb_s2a_backend_fault_recovery___024root__trace_chg_0(void* voidSelf, VerilatedVcd::Buffer* bufp) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root__trace_chg_0\n"); );
    // Body
    Vtb_s2a_backend_fault_recovery___024root* const __restrict vlSelf VL_ATTR_UNUSED = static_cast<Vtb_s2a_backend_fault_recovery___024root*>(voidSelf);
    Vtb_s2a_backend_fault_recovery__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    if (VL_UNLIKELY(!vlSymsp->__Vm_activity)) return;
    Vtb_s2a_backend_fault_recovery___024root__trace_chg_0_sub_0((&vlSymsp->TOP), bufp);
}

void Vtb_s2a_backend_fault_recovery___024root__trace_chg_dtype____0(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd::Buffer* bufp, uint32_t offset, const VlUnpacked<IData/*31:0*/, 9>& __VdtypeVar);
void Vtb_s2a_backend_fault_recovery___024root__trace_chg_dtype____1(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd::Buffer* bufp, uint32_t offset, const VlUnpacked<IData/*31:0*/, 9>& __VdtypeVar);
void Vtb_s2a_backend_fault_recovery___024root__trace_chg_dtype____2(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd::Buffer* bufp, uint32_t offset, const VlUnpacked<QData/*63:0*/, 9>& __VdtypeVar);
void Vtb_s2a_backend_fault_recovery___024root__trace_chg_dtype____3(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd::Buffer* bufp, uint32_t offset, const VlUnpacked<QData/*63:0*/, 9>& __VdtypeVar);
void Vtb_s2a_backend_fault_recovery___024root__trace_chg_dtype____4(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd::Buffer* bufp, uint32_t offset, const VlUnpacked<IData/*31:0*/, 8>& __VdtypeVar);
void Vtb_s2a_backend_fault_recovery___024root__trace_chg_dtype____5(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd::Buffer* bufp, uint32_t offset, const VlUnpacked<CData/*7:0*/, 8>& __VdtypeVar);
void Vtb_s2a_backend_fault_recovery___024root__trace_chg_dtype____6(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd::Buffer* bufp, uint32_t offset, const VlUnpacked<VlWide<3>/*79:0*/, 8>& __VdtypeVar);
void Vtb_s2a_backend_fault_recovery___024root__trace_chg_dtype____7(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd::Buffer* bufp, uint32_t offset, const VlUnpacked<IData/*31:0*/, 8>& __VdtypeVar);
void Vtb_s2a_backend_fault_recovery___024root__trace_chg_dtype____8(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd::Buffer* bufp, uint32_t offset, const VlUnpacked<IData/*31:0*/, 4>& __VdtypeVar);

void Vtb_s2a_backend_fault_recovery___024root__trace_chg_0_sub_0(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd::Buffer* bufp) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root__trace_chg_0_sub_0\n"); );
    Vtb_s2a_backend_fault_recovery__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    VlWide<4>/*127:0*/ __Vtemp_2;
    VlWide<3>/*95:0*/ __Vtemp_5;
    VlWide<3>/*95:0*/ __Vtemp_6;
    VlWide<3>/*95:0*/ __Vtemp_7;
    VlWide<3>/*95:0*/ __Vtemp_8;
    VlWide<3>/*95:0*/ __Vtemp_9;
    VlWide<3>/*95:0*/ __Vtemp_11;
    VlWide<3>/*95:0*/ __Vtemp_12;
    VlWide<3>/*95:0*/ __Vtemp_13;
    VlWide<3>/*95:0*/ __Vtemp_14;
    // Body
    uint32_t* const oldp VL_ATTR_UNUSED = bufp->oldp(vlSymsp->__Vm_baseCode + 0);
    if (VL_UNLIKELY((((vlSelfRef.__Vm_traceActivity[1U] 
                       | vlSelfRef.__Vm_traceActivity[2U]) 
                      | vlSelfRef.__Vm_traceActivity[3U])))) {
        bufp->chgBit(oldp+0,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__hard_reset));
        bufp->chgBit(oldp+1,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid));
        bufp->chgBit(oldp+2,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_write));
        bufp->chgCData(oldp+3,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr),8);
        bufp->chgIData(oldp+4,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_wdata),32);
        bufp->chgBit(oldp+5,((1U & (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__hard_reset)))));
        bufp->chgBit(oldp+6,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__manual_mem_ready));
        bufp->chgBit(oldp+7,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__automatic_read_responses));
        bufp->chgCData(oldp+8,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__manual_mem_error_code),3);
        bufp->chgIData(oldp+9,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__transaction_start_cycle),32);
        bufp->chgIData(oldp+10,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__unnamedblk1__DOT__reads_before),32);
        bufp->chgIData(oldp+11,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__unnamedblk1__DOT__writes_before),32);
    }
    if (VL_UNLIKELY(((vlSelfRef.__Vm_traceActivity[4U] 
                      | vlSelfRef.__Vm_traceActivity[6U])))) {
        bufp->chgIData(oldp+12,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_rdata),32);
        bufp->chgBit(oldp+13,(((0U != (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__backend_memory_error_code)) 
                               & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__memory_handshake))));
        bufp->chgCData(oldp+14,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__backend_memory_error_code),3);
        bufp->chgBit(oldp+15,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__operator_result_valid));
        bufp->chgCData(oldp+16,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__operator_error_code),3);
        bufp->chgBit(oldp+17,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid));
        bufp->chgBit(oldp+18,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_write));
        bufp->chgIData(oldp+19,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_addr),32);
        bufp->chgIData(oldp+20,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_wdata),32);
        bufp->chgCData(oldp+21,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_rstrb),4);
        bufp->chgBit(oldp+22,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_ready));
        bufp->chgCData(oldp+23,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_op),3);
        bufp->chgCData(oldp+24,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_input_count),2);
        bufp->chgIData(oldp+25,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_base[0]),32);
        bufp->chgIData(oldp+26,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_base[1]),32);
        bufp->chgIData(oldp+27,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_length[0]),32);
        bufp->chgIData(oldp+28,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_length[1]),32);
        bufp->chgSData(oldp+29,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_n[0]),16);
        bufp->chgSData(oldp+30,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_n[1]),16);
        bufp->chgSData(oldp+31,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_c[0]),16);
        bufp->chgSData(oldp+32,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_c[1]),16);
        bufp->chgSData(oldp+33,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0]),16);
        bufp->chgSData(oldp+34,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[1]),16);
        bufp->chgSData(oldp+35,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0]),16);
        bufp->chgSData(oldp+36,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[1]),16);
        bufp->chgSData(oldp+37,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_route_start[0]),16);
        bufp->chgSData(oldp+38,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_route_start[1]),16);
        bufp->chgSData(oldp+39,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_route_end[0]),16);
        bufp->chgSData(oldp+40,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_route_end[1]),16);
        bufp->chgIData(oldp+41,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_base),32);
        bufp->chgIData(oldp+42,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_length),32);
        bufp->chgSData(oldp+43,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_n),16);
        bufp->chgSData(oldp+44,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_c),16);
        bufp->chgSData(oldp+45,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_h),16);
        bufp->chgSData(oldp+46,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_w),16);
        bufp->chgQData(oldp+47,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_plane_elements),64);
        bufp->chgQData(oldp+49,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_batch_elements),64);
        bufp->chgQData(oldp+51,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_element_count),64);
        bufp->chgIData(oldp+53,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel),32);
        bufp->chgIData(oldp+54,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_y),32);
        bufp->chgIData(oldp+55,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_x),32);
        bufp->chgIData(oldp+56,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mq_index),32);
        bufp->chgBit(oldp+57,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__descriptor_valid));
        bufp->chgBit(oldp+58,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_valid));
        bufp->chgBit(oldp+59,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__descriptor_fault));
        bufp->chgBit(oldp+60,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__is_alias_row));
        bufp->chgCData(oldp+61,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index),6);
        bufp->chgQData(oldp+62,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_output_plane_elements),64);
        bufp->chgQData(oldp+64,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_output_element_count),64);
        bufp->chgBit(oldp+66,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_start_valid));
        bufp->chgBit(oldp+67,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__start_ready));
        bufp->chgBit(oldp+68,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_start_valid));
        bufp->chgBit(oldp+69,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__start_ready));
        bufp->chgBit(oldp+70,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_start_valid));
        bufp->chgBit(oldp+71,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__start_ready));
        bufp->chgBit(oldp+72,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_start_valid));
        bufp->chgBit(oldp+73,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__start_ready));
        bufp->chgBit(oldp+74,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_valid));
        bufp->chgBit(oldp+75,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__backend_req_ready));
        bufp->chgBit(oldp+76,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_write));
        bufp->chgCData(oldp+77,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_rstrb),4);
        bufp->chgCData(oldp+78,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_wstrb),4);
        bufp->chgBit(oldp+79,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_valid));
        bufp->chgBit(oldp+80,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__backend_req_ready));
        bufp->chgBit(oldp+81,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_write));
        bufp->chgIData(oldp+82,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_addr),32);
        bufp->chgIData(oldp+83,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_wdata),32);
        bufp->chgCData(oldp+84,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_rstrb),4);
        bufp->chgCData(oldp+85,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_wstrb),4);
        bufp->chgBit(oldp+86,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_valid));
        bufp->chgBit(oldp+87,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__backend_req_ready));
        bufp->chgBit(oldp+88,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_write));
        bufp->chgIData(oldp+89,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_addr),32);
        bufp->chgIData(oldp+90,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_wdata),32);
        bufp->chgCData(oldp+91,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_rstrb),4);
        bufp->chgCData(oldp+92,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_wstrb),4);
        bufp->chgBit(oldp+93,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_valid));
        bufp->chgBit(oldp+94,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__backend_req_ready));
        bufp->chgBit(oldp+95,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_write));
        bufp->chgIData(oldp+96,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_addr),32);
        bufp->chgIData(oldp+97,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_wdata),32);
        bufp->chgCData(oldp+98,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_rstrb),4);
        bufp->chgCData(oldp+99,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_wstrb),4);
        bufp->chgBit(oldp+100,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__backend_rsp_valid));
        bufp->chgBit(oldp+101,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__backend_rsp_valid));
        bufp->chgBit(oldp+102,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__backend_rsp_valid));
        bufp->chgBit(oldp+103,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__backend_rsp_valid));
        bufp->chgBit(oldp+104,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_result_ready));
        bufp->chgBit(oldp+105,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_result_ready));
        bufp->chgBit(oldp+106,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_result_ready));
        bufp->chgBit(oldp+107,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_result_ready));
        bufp->chgIData(oldp+108,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_addr),32);
        bufp->chgIData(oldp+109,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_wdata),32);
        bufp->chgBit(oldp+110,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_result_valid));
        bufp->chgBit(oldp+111,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__memory_handshake));
        bufp->chgBit(oldp+112,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_start_ready));
        bufp->chgIData(oldp+113,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_base[0U]),32);
        bufp->chgIData(oldp+114,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_length[0U]),32);
        bufp->chgIData(oldp+115,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_n[0U]),32);
        bufp->chgIData(oldp+116,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_c[0U]),32);
        bufp->chgIData(oldp+117,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U]),32);
        bufp->chgIData(oldp+118,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U]),32);
        bufp->chgIData(oldp+119,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_n),32);
        bufp->chgIData(oldp+120,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_c),32);
        bufp->chgIData(oldp+121,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_h),32);
        bufp->chgIData(oldp+122,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_w),32);
        bufp->chgQData(oldp+123,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__patch_plane_bytes),64);
        bufp->chgBit(oldp+125,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_advance));
        bufp->chgQData(oldp+126,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_input_y),64);
        bufp->chgQData(oldp+128,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_input_x),64);
        bufp->chgBit(oldp+130,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_in_bounds));
        bufp->chgQData(oldp+131,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_source_offset),64);
        bufp->chgQData(oldp+133,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_source_address_wide),64);
        bufp->chgIData(oldp+135,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_area),32);
        bufp->chgIData(oldp+136,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_y),32);
        bufp->chgIData(oldp+137,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_x),32);
        bufp->chgIData(oldp+138,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_next_input_channel),32);
        bufp->chgIData(oldp+139,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_next_kernel_y),32);
        bufp->chgIData(oldp+140,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_next_kernel_x),32);
        bufp->chgIData(oldp+141,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_next_reduction_index),32);
        bufp->chgIData(oldp+142,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_point_y),32);
        bufp->chgIData(oldp+143,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_point_x),32);
        bufp->chgIData(oldp+144,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_input_channel),32);
        bufp->chgIData(oldp+145,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_kernel_y),32);
        bufp->chgIData(oldp+146,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_kernel_x),32);
        bufp->chgIData(oldp+147,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_reduction_index),32);
        bufp->chgQData(oldp+148,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_input_y),64);
        bufp->chgQData(oldp+150,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_input_x),64);
        bufp->chgBit(oldp+152,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_tap_in_bounds));
        bufp->chgQData(oldp+153,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index_wide),64);
        bufp->chgIData(oldp+155,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index),32);
        bufp->chgQData(oldp+156,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_input_y),64);
        bufp->chgQData(oldp+158,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_input_x),64);
        bufp->chgBit(oldp+160,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_tap_in_bounds));
        bufp->chgQData(oldp+161,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_feature_index_wide),64);
        bufp->chgIData(oldp+163,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_feature_index),32);
        bufp->chgBit(oldp+164,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_enable));
        bufp->chgCData(oldp+165,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[0]),8);
        bufp->chgCData(oldp+166,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[1]),8);
        bufp->chgCData(oldp+167,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[2]),8);
        bufp->chgCData(oldp+168,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[3]),8);
        bufp->chgCData(oldp+169,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[4]),8);
        bufp->chgCData(oldp+170,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[5]),8);
        bufp->chgCData(oldp+171,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[6]),8);
        bufp->chgCData(oldp+172,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[7]),8);
        bufp->chgCData(oldp+173,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[0]),8);
        bufp->chgCData(oldp+174,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[1]),8);
        bufp->chgCData(oldp+175,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[2]),8);
        bufp->chgCData(oldp+176,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[3]),8);
        bufp->chgCData(oldp+177,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[4]),8);
        bufp->chgCData(oldp+178,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[5]),8);
        bufp->chgCData(oldp+179,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[6]),8);
        bufp->chgCData(oldp+180,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[7]),8);
        bufp->chgSData(oldp+181,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[0]),16);
        bufp->chgSData(oldp+182,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[1]),16);
        bufp->chgSData(oldp+183,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[2]),16);
        bufp->chgSData(oldp+184,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[3]),16);
        bufp->chgSData(oldp+185,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[4]),16);
        bufp->chgSData(oldp+186,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[5]),16);
        bufp->chgSData(oldp+187,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[6]),16);
        bufp->chgSData(oldp+188,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[7]),16);
        bufp->chgQData(oldp+189,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[0]),33);
        bufp->chgQData(oldp+191,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[1]),33);
        bufp->chgQData(oldp+193,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[2]),33);
        bufp->chgQData(oldp+195,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[3]),33);
        bufp->chgQData(oldp+197,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[4]),33);
        bufp->chgQData(oldp+199,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[5]),33);
        bufp->chgQData(oldp+201,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[6]),33);
        bufp->chgQData(oldp+203,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[7]),33);
        bufp->chgBit(oldp+205,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_bad_argument));
        bufp->chgBit(oldp+206,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_overflow));
        bufp->chgBit(oldp+207,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_whitebox_resync));
        bufp->chgIData(oldp+208,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_whitebox_point_y),32);
        bufp->chgIData(oldp+209,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_whitebox_point_x),32);
        bufp->chgCData(oldp+210,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mapped_response_error),3);
        bufp->chgQData(oldp+211,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_output_height),33);
        bufp->chgQData(oldp+213,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_output_width),33);
        bufp->chgCData(oldp+215,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_count),4);
        bufp->chgSData(oldp+216,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask),9);
        Vtb_s2a_backend_fault_recovery___024root__trace_chg_dtype____0(vlSelf, bufp, 217, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address);
        Vtb_s2a_backend_fault_recovery___024root__trace_chg_dtype____1(vlSelf, bufp, 226, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel);
        Vtb_s2a_backend_fault_recovery___024root__trace_chg_dtype____2(vlSelf, bufp, 235, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y);
        Vtb_s2a_backend_fault_recovery___024root__trace_chg_dtype____3(vlSelf, bufp, 253, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x);
        bufp->chgCData(oldp+271,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_error_code),3);
        bufp->chgBit(oldp+272,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_inputs_valid));
        bufp->chgBit(oldp+273,(((0U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_error_code)) 
                                & ((4U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_count)) 
                                   & ((0x0fU == (0x0000000fU 
                                                 & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask))) 
                                      & ((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_output_height 
                                          == (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_h))) 
                                         & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_output_width 
                                            == (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_w)))))))));
        bufp->chgQData(oldp+274,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_offset_work),64);
        bufp->chgWData(oldp+276,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_address_work),65);
        bufp->chgIData(oldp+279,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__selected_input_word_address),32);
        bufp->chgCData(oldp+280,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__selected_input_lane),4);
        bufp->chgQData(oldp+281,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__extent_y),33);
        bufp->chgQData(oldp+283,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__extent_x),33);
        bufp->chgQData(oldp+285,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_height_work),33);
        bufp->chgQData(oldp+287,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_width_work),33);
        bufp->chgQData(oldp+289,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__origin_y),64);
        bufp->chgQData(oldp+291,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__origin_x),64);
        bufp->chgQData(oldp+293,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_y_step),64);
        bufp->chgQData(oldp+295,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_x_step),64);
        bufp->chgQData(oldp+297,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_y_work),64);
        bufp->chgQData(oldp+299,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_x_work),64);
        bufp->chgWData(oldp+301,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work),96);
        bufp->chgWData(oldp+304,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work),96);
        bufp->chgWData(oldp+307,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work),96);
        bufp->chgWData(oldp+310,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work),97);
        bufp->chgIData(oldp+314,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__tap_index),32);
        bufp->chgIData(oldp+315,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work),32);
        bufp->chgIData(oldp+316,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work),32);
        bufp->chgBit(oldp+317,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__tap_range_error));
        bufp->chgIData(oldp+318,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_input_count),32);
        bufp->chgIData(oldp+319,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_route_start[0U]),32);
        bufp->chgIData(oldp+320,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_route_end[0U]),32);
        bufp->chgIData(oldp+321,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_base[1U]),32);
        bufp->chgIData(oldp+322,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_length[1U]),32);
        bufp->chgIData(oldp+323,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_c[1U]),32);
        bufp->chgIData(oldp+324,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[1U]),32);
        bufp->chgIData(oldp+325,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[1U]),32);
        bufp->chgIData(oldp+326,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_route_start[1U]),32);
        bufp->chgIData(oldp+327,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_route_end[1U]),32);
        bufp->chgIData(oldp+328,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__selected_word_address),32);
        bufp->chgCData(oldp+329,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__selected_read_lane),4);
        bufp->chgQData(oldp+330,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_output_height),64);
        bufp->chgQData(oldp+332,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_output_width),64);
        bufp->chgIData(oldp+334,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_channel),32);
        bufp->chgIData(oldp+335,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_y),32);
        bufp->chgIData(oldp+336,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_x),32);
        bufp->chgIData(oldp+337,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_address),32);
        bufp->chgCData(oldp+338,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_unused_value),8);
        bufp->chgCData(oldp+339,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_error_code),3);
        bufp->chgQData(oldp+340,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__output_offset_work),64);
        bufp->chgWData(oldp+342,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__output_address_work),65);
        bufp->chgQData(oldp+345,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__output_height_work),64);
        bufp->chgQData(oldp+347,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__output_width_work),64);
        bufp->chgCData(oldp+349,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__plane_elements_work),8);
        bufp->chgCData(oldp+350,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__plane_index_work),8);
        bufp->chgQData(oldp+351,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__byte_offset_work),40);
        bufp->chgQData(oldp+353,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__address_work),41);
        bufp->chgCData(oldp+355,((((1U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__backend_memory_error_code)) 
                                   | ((2U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__backend_memory_error_code)) 
                                      | (6U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__backend_memory_error_code))))
                                   ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__backend_memory_error_code)
                                   : 6U)),3);
    }
    if (VL_UNLIKELY((vlSelfRef.__Vm_traceActivity[5U]))) {
        bufp->chgBit(oldp+356,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__backend_start));
        bufp->chgBit(oldp+357,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__backend_abort));
        bufp->chgBit(oldp+358,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__busy));
        bufp->chgBit(oldp+359,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__done));
        bufp->chgBit(oldp+360,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__error));
        bufp->chgBit(oldp+361,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__buffer_owner_pl));
        bufp->chgBit(oldp+362,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__head_output_valid));
        bufp->chgCData(oldp+363,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state),3);
        bufp->chgCData(oldp+364,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor),6);
        bufp->chgIData(oldp+365,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_element_index),32);
        bufp->chgBit(oldp+366,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_pending));
        bufp->chgIData(oldp+367,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_data_latched),32);
        bufp->chgCData(oldp+368,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_error_latched),3);
        bufp->chgCData(oldp+369,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_target_latched),3);
        bufp->chgIData(oldp+370,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__request_address_latched),32);
        bufp->chgIData(oldp+371,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__request_wdata_latched),32);
        bufp->chgBit(oldp+372,((0x13U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__state))));
        bufp->chgCData(oldp+373,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__result_error_latched),3);
        bufp->chgBit(oldp+374,((6U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__state))));
        __Vtemp_2[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched[0U];
        __Vtemp_2[1U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched[1U];
        __Vtemp_2[2U] = (IData)((((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched[3U])) 
                                  << 0x00000020U) | (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched[2U]))));
        __Vtemp_2[3U] = (IData)(((((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched[3U])) 
                                   << 0x00000020U) 
                                  | (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched[2U]))) 
                                 >> 0x00000020U));
        bufp->chgWData(oldp+375,(__Vtemp_2),128);
        bufp->chgIData(oldp+379,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_address_latched),32);
        bufp->chgCData(oldp+380,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__result_value_latched),8);
        bufp->chgCData(oldp+381,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__result_error_latched),3);
        bufp->chgBit(oldp+382,((7U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__state))));
        bufp->chgIData(oldp+383,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source_index_latched),32);
        bufp->chgIData(oldp+384,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source_address_latched),32);
        bufp->chgIData(oldp+385,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_address_latched),32);
        bufp->chgCData(oldp+386,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__result_value_latched),8);
        bufp->chgCData(oldp+387,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__result_error_latched),3);
        bufp->chgBit(oldp+388,((5U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__state))));
        bufp->chgIData(oldp+389,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__source_address_latched),32);
        bufp->chgIData(oldp+390,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__output_address_latched),32);
        bufp->chgCData(oldp+391,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__copied_value_latched),8);
        bufp->chgCData(oldp+392,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__result_error_latched),3);
        bufp->chgCData(oldp+393,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_result_error),3);
        bufp->chgIData(oldp+394,(((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
                                   ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_LAYER_INDEX
                                  [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor]
                                   : 0U)),32);
        bufp->chgIData(oldp+395,(((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
                                   ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_WEIGHT_LAYER_INDEX
                                  [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor]
                                   : 0U)),32);
        bufp->chgIData(oldp+396,(((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
                                   ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_KERNEL_H
                                  [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor]
                                   : 0U)),32);
        bufp->chgIData(oldp+397,(((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
                                   ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_KERNEL_W
                                  [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor]
                                   : 0U)),32);
        bufp->chgIData(oldp+398,(((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
                                   ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_STRIDE_H
                                  [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor]
                                   : 0U)),32);
        bufp->chgIData(oldp+399,(((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
                                   ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_STRIDE_W
                                  [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor]
                                   : 0U)),32);
        bufp->chgIData(oldp+400,(((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
                                   ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_PADDING_LEFT
                                  [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor]
                                   : 0U)),32);
        bufp->chgIData(oldp+401,(((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
                                   ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_PADDING_RIGHT
                                  [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor]
                                   : 0U)),32);
        bufp->chgIData(oldp+402,(((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
                                   ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_PADDING_TOP
                                  [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor]
                                   : 0U)),32);
        bufp->chgIData(oldp+403,(((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
                                   ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_PADDING_BOTTOM
                                  [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor]
                                   : 0U)),32);
        bufp->chgIData(oldp+404,(((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
                                   ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_GROUP_COUNT
                                  [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor]
                                   : 0U)),32);
        bufp->chgIData(oldp+405,((((- (IData)((1U & 
                                               (((0x25U 
                                                  >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
                                                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_PADDING_VALUE_INT8
                                                 [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor]
                                                  : 0U) 
                                                >> 7U)))) 
                                   << 8U) | ((0x25U 
                                              >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
                                              ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_PADDING_VALUE_INT8
                                             [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor]
                                              : 0U))),32);
        bufp->chgIData(oldp+406,(((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
                                   ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_GF8_WEIGHT_OFFSET
                                  [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor]
                                   : 0U)),32);
        bufp->chgIData(oldp+407,(((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
                                   ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_GF8_WEIGHT_BYTES
                                  [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor]
                                   : 0U)),32);
        bufp->chgCData(oldp+408,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_conv_engine__activation_mode),2);
        bufp->chgBit(oldp+409,((0U != (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__state))));
        bufp->chgCData(oldp+410,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__state),5);
        bufp->chgIData(oldp+411,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched),32);
        bufp->chgIData(oldp+412,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_layer_index_latched),32);
        bufp->chgIData(oldp+413,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_base_latched),32);
        bufp->chgIData(oldp+414,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_length_latched),32);
        bufp->chgIData(oldp+415,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_batch_count_latched),32);
        bufp->chgIData(oldp+416,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_channels_latched),32);
        bufp->chgIData(oldp+417,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_height_latched),32);
        bufp->chgIData(oldp+418,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_width_latched),32);
        bufp->chgIData(oldp+419,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_base_latched),32);
        bufp->chgIData(oldp+420,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_length_latched),32);
        bufp->chgIData(oldp+421,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_batch_count_latched),32);
        bufp->chgIData(oldp+422,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_channels_latched),32);
        bufp->chgIData(oldp+423,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_latched),32);
        bufp->chgIData(oldp+424,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_latched),32);
        bufp->chgIData(oldp+425,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_height_latched),32);
        bufp->chgIData(oldp+426,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_width_latched),32);
        bufp->chgIData(oldp+427,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__stride_y_latched),32);
        bufp->chgIData(oldp+428,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__stride_x_latched),32);
        bufp->chgIData(oldp+429,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__pad_left_latched),32);
        bufp->chgIData(oldp+430,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__pad_right_latched),32);
        bufp->chgIData(oldp+431,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__pad_top_latched),32);
        bufp->chgIData(oldp+432,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__pad_bottom_latched),32);
        bufp->chgIData(oldp+433,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__groups_latched),32);
        bufp->chgIData(oldp+434,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__padding_latched),32);
        bufp->chgIData(oldp+435,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_package_base_latched),32);
        bufp->chgIData(oldp+436,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_package_length_latched),32);
        bufp->chgIData(oldp+437,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__quantized_weight_offset_latched),32);
        bufp->chgIData(oldp+438,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__quantized_weight_bytes_latched),32);
        bufp->chgIData(oldp+439,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_batch_latched),32);
        bufp->chgCData(oldp+440,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__activation_mode_latched),2);
        Vtb_s2a_backend_fault_recovery___024root__trace_chg_dtype____4(vlSelf, bufp, 441, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator);
        bufp->chgCData(oldp+449,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_read_data),8);
        bufp->chgBit(oldp+450,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_read_in_bounds));
        Vtb_s2a_backend_fault_recovery___024root__trace_chg_dtype____5(vlSelf, bufp, 451, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_read_byte);
        bufp->chgCData(oldp+459,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_lane_bank_valid),8);
        bufp->chgIData(oldp+460,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_latched),32);
        bufp->chgIData(oldp+461,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base),32);
        bufp->chgIData(oldp+462,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_y),32);
        bufp->chgIData(oldp+463,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_x),32);
        bufp->chgIData(oldp+464,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__tile_height),32);
        bufp->chgIData(oldp+465,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__tile_width),32);
        bufp->chgIData(oldp+466,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__patch_height),32);
        bufp->chgIData(oldp+467,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__patch_width),32);
        bufp->chgIData(oldp+468,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__patch_byte_count),32);
        bufp->chgIData(oldp+469,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__tile_point_count),32);
        bufp->chgIData(oldp+470,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count),32);
        bufp->chgIData(oldp+471,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_index),32);
        bufp->chgIData(oldp+472,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_lane_index),32);
        bufp->chgIData(oldp+473,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_reduction_index),32);
        bufp->chgIData(oldp+474,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_index),32);
        bufp->chgIData(oldp+475,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_scan_y),32);
        bufp->chgIData(oldp+476,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_scan_x),32);
        bufp->chgIData(oldp+477,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_reduction_index),32);
        bufp->chgIData(oldp+478,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_lane_index),32);
        bufp->chgIData(oldp+479,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_point_index),32);
        bufp->chgCData(oldp+480,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__request_strobe_latched),4);
        bufp->chgBit(oldp+481,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__request_write_latched));
        bufp->chgIData(oldp+482,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_address_latched),32);
        bufp->chgCData(oldp+483,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_value_latched),8);
        bufp->chgWData(oldp+484,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_elements_wide),128);
        bufp->chgWData(oldp+488,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_elements_wide),128);
        bufp->chgWData(oldp+492,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__expected_weight_bytes_wide),128);
        bufp->chgWData(oldp+496,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_wide),128);
        bufp->chgWData(oldp+500,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_end_wide),128);
        bufp->chgWData(oldp+504,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_end_wide),128);
        bufp->chgWData(oldp+508,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_package_end_wide),128);
        bufp->chgWData(oldp+512,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__quantized_weight_end_wide),128);
        bufp->chgQData(oldp+516,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_numerator),64);
        bufp->chgQData(oldp+518,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_numerator),64);
        bufp->chgQData(oldp+520,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_shape_span),64);
        bufp->chgQData(oldp+522,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_shape_span),64);
        bufp->chgQData(oldp+524,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_shape_product),64);
        bufp->chgQData(oldp+526,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_shape_product),64);
        bufp->chgQData(oldp+528,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_span_plus_stride),64);
        bufp->chgQData(oldp+530,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_span_plus_stride),64);
        bufp->chgWData(oldp+532,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_height_wide),128);
        bufp->chgWData(oldp+536,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_width_wide),128);
        bufp->chgWData(oldp+540,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_bytes_wide),128);
        bufp->chgWData(oldp+544,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__full_weight_group_bytes_wide),128);
        bufp->chgBit(oldp+548,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__validation_ok));
        bufp->chgCData(oldp+549,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__validation_error),3);
        bufp->chgIData(oldp+550,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_channel),32);
        bufp->chgIData(oldp+551,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_y),32);
        bufp->chgIData(oldp+552,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_x),32);
        bufp->chgIData(oldp+553,((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base 
                                  + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_lane_index)),32);
        bufp->chgQData(oldp+554,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_source_address_wide),64);
        bufp->chgIData(oldp+556,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_input_channel),32);
        bufp->chgIData(oldp+557,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_y),32);
        bufp->chgIData(oldp+558,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_x),32);
        bufp->chgIData(oldp+559,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_lane),32);
        bufp->chgIData(oldp+560,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_index),32);
        bufp->chgWData(oldp+561,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_parameter),80);
        bufp->chgIData(oldp+564,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_bias),32);
        bufp->chgBit(oldp+565,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_invalid));
        Vtb_s2a_backend_fault_recovery___024root__trace_chg_dtype____6(vlSelf, bufp, 566, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_mq_parameter);
        Vtb_s2a_backend_fault_recovery___024root__trace_chg_dtype____7(vlSelf, bufp, 590, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_bias);
        bufp->chgIData(oldp+598,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_lane_index),32);
        bufp->chgWData(oldp+599,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_parameter),80);
        bufp->chgIData(oldp+602,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_accumulator),32);
        bufp->chgIData(oldp+603,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier),32);
        bufp->chgIData(oldp+604,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift),32);
        bufp->chgIData(oldp+605,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude),32);
        bufp->chgQData(oldp+606,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product),64);
        bufp->chgQData(oldp+608,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add),64);
        bufp->chgQData(oldp+610,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude),64);
        bufp->chgQData(oldp+612,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value),64);
        bufp->chgCData(oldp+614,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requantized_value),8);
        bufp->chgIData(oldp+615,((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_y 
                                  + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_point_scan_y)),32);
        bufp->chgIData(oldp+616,((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_x 
                                  + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_point_scan_x)),32);
        bufp->chgIData(oldp+617,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_point_scan_y),32);
        bufp->chgIData(oldp+618,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_point_scan_x),32);
        bufp->chgIData(oldp+619,((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base 
                                  + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_lane_index)),32);
        bufp->chgQData(oldp+620,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_byte_offset_wide),64);
        bufp->chgQData(oldp+622,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_address_wide),64);
        bufp->chgCData(oldp+624,((3U & (0x00030210U 
                                        >> ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__request_strobe_latched) 
                                            << 1U)))),2);
        bufp->chgIData(oldp+625,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__seq_lane),32);
        bufp->chgIData(oldp+626,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__layer_index),32);
        bufp->chgIData(oldp+627,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_height),32);
        bufp->chgIData(oldp+628,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width),32);
        bufp->chgIData(oldp+629,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_y),32);
        bufp->chgIData(oldp+630,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_x),32);
        bufp->chgIData(oldp+631,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__darknet_padding_parameter),32);
        bufp->chgCData(oldp+632,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__state),4);
        Vtb_s2a_backend_fault_recovery___024root__trace_chg_dtype____8(vlSelf, bufp, 633, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched);
        bufp->chgWData(oldp+637,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__candidate_values_latched),72);
        bufp->chgCData(oldp+640,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__read_tap_index),3);
        bufp->chgIData(oldp+641,((0x00000018U & ((- (IData)(
                                                            (4U 
                                                             > (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__read_tap_index)))) 
                                                 & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched
                                                    [
                                                    (3U 
                                                     & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__read_tap_index))] 
                                                    << 3U)))),32);
        bufp->chgCData(oldp+642,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__mapped_response_error),3);
        bufp->chgCData(oldp+643,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__window_max_value),8);
        bufp->chgCData(oldp+644,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__window_error_code),3);
        bufp->chgIData(oldp+645,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_index),32);
        bufp->chgCData(oldp+646,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__candidate_value),8);
        bufp->chgCData(oldp+647,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__current_maximum),8);
        bufp->chgIData(oldp+648,(((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
                                   ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_ROUTE_GROUP_ID
                                  [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor]
                                   : 0U)),32);
        bufp->chgIData(oldp+649,(vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_ROUTE_SOURCE_MULTIPLIER_Q31
                                 [((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
                                    ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor)
                                    : 0U)][0U]),32);
        bufp->chgIData(oldp+650,(vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_ROUTE_SOURCE_MULTIPLIER_Q31
                                 [((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
                                    ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor)
                                    : 0U)][1U]),32);
        bufp->chgCData(oldp+651,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__state),4);
        bufp->chgIData(oldp+652,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source_count_latched),32);
        bufp->chgIData(oldp+653,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__groups_latched),32);
        bufp->chgIData(oldp+654,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__group_id_latched),32);
        bufp->chgIData(oldp+655,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_channel_latched),32);
        bufp->chgIData(oldp+656,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_y_latched),32);
        bufp->chgIData(oldp+657,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_x_latched),32);
        bufp->chgIData(oldp+658,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_base_latched),32);
        bufp->chgIData(oldp+659,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_length_latched),32);
        bufp->chgIData(oldp+660,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_channels_latched),32);
        bufp->chgIData(oldp+661,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_height_latched),32);
        bufp->chgIData(oldp+662,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_width_latched),32);
        bufp->chgIData(oldp+663,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_start_latched),32);
        bufp->chgIData(oldp+664,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_end_latched),32);
        bufp->chgIData(oldp+665,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_multiplier_latched),32);
        bufp->chgCData(oldp+666,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_value_latched),8);
        bufp->chgIData(oldp+667,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_base_latched),32);
        bufp->chgIData(oldp+668,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_length_latched),32);
        bufp->chgIData(oldp+669,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_channels_latched),32);
        bufp->chgIData(oldp+670,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_height_latched),32);
        bufp->chgIData(oldp+671,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_width_latched),32);
        bufp->chgIData(oldp+672,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_start_latched),32);
        bufp->chgIData(oldp+673,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_end_latched),32);
        bufp->chgIData(oldp+674,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_multiplier_latched),32);
        bufp->chgCData(oldp+675,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_value_latched),8);
        bufp->chgIData(oldp+676,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_base_latched),32);
        bufp->chgIData(oldp+677,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_length_latched),32);
        bufp->chgIData(oldp+678,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_channels_latched),32);
        bufp->chgIData(oldp+679,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_height_latched),32);
        bufp->chgIData(oldp+680,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_width_latched),32);
        bufp->chgIData(oldp+681,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__query_output_channels),32);
        bufp->chgIData(oldp+682,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__query_output_height),32);
        bufp->chgIData(oldp+683,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__query_output_width),32);
        bufp->chgIData(oldp+684,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__query_source_index),32);
        bufp->chgIData(oldp+685,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__query_source_channel),32);
        bufp->chgIData(oldp+686,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__query_source_address),32);
        bufp->chgCData(oldp+687,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__query_output_value),8);
        bufp->chgCData(oldp+688,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__query_error_code),3);
        __Vtemp_5[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_channels_latched;
        __Vtemp_5[1U] = 0U;
        __Vtemp_5[2U] = 0U;
        VL_MUL_W(3, __Vtemp_6, __Vtemp_5, vlSelfRef.__VdfgRegularize_h6e95ff9d_0_7);
        __Vtemp_7[0U] = __Vtemp_6[0U];
        __Vtemp_7[1U] = __Vtemp_6[1U];
        __Vtemp_7[2U] = (1U & __Vtemp_6[2U]);
        VL_MUL_W(3, __Vtemp_8, vlSelfRef.__VdfgRegularize_h6e95ff9d_0_8, __Vtemp_7);
        __Vtemp_9[0U] = __Vtemp_8[0U];
        __Vtemp_9[1U] = __Vtemp_8[1U];
        __Vtemp_9[2U] = (1U & __Vtemp_8[2U]);
        bufp->chgWData(oldp+689,(__Vtemp_9),65);
        bufp->chgWData(oldp+692,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_offset_work),65);
        __Vtemp_11[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_length_latched;
        __Vtemp_11[1U] = 0U;
        __Vtemp_11[2U] = 0U;
        __Vtemp_12[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_base_latched;
        __Vtemp_12[1U] = 0U;
        __Vtemp_12[2U] = 0U;
        VL_ADD_W(3, __Vtemp_13, __Vtemp_11, __Vtemp_12);
        __Vtemp_14[0U] = __Vtemp_13[0U];
        __Vtemp_14[1U] = __Vtemp_13[1U];
        __Vtemp_14[2U] = (1U & __Vtemp_13[2U]);
        bufp->chgWData(oldp+695,(__Vtemp_14),65);
        bufp->chgIData(oldp+698,((0x00000018U & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source_address_latched 
                                                 << 3U))),32);
        bufp->chgCData(oldp+699,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__mapped_response_error),3);
        bufp->chgBit(oldp+700,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_argument));
        bufp->chgBit(oldp+701,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_range));
        bufp->chgQData(oldp+702,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source0_shape_bytes),64);
        bufp->chgQData(oldp+704,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_shape_bytes),64);
        bufp->chgQData(oldp+706,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source0_plane_elements),64);
        bufp->chgQData(oldp+708,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_plane_elements),64);
        bufp->chgQData(oldp+710,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source0_object_end),64);
        bufp->chgQData(oldp+712,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_object_end),64);
        bufp->chgQData(oldp+714,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__output_channels_wide),64);
        bufp->chgQData(oldp+716,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__expected_group_start),64);
        bufp->chgQData(oldp+718,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__expected_group_end),64);
        bufp->chgQData(oldp+720,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_offset),64);
        bufp->chgQData(oldp+722,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_address_wide),64);
        bufp->chgIData(oldp+724,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source0_selected_count),32);
        bufp->chgIData(oldp+725,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_selected_count),32);
        bufp->chgIData(oldp+726,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_multiplier),32);
        bufp->chgIData(oldp+727,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_base_address),32);
        bufp->chgIData(oldp+728,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_length_bytes),32);
        bufp->chgCData(oldp+729,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_value),8);
        bufp->chgCData(oldp+730,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_magnitude),7);
        bufp->chgQData(oldp+731,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__scaled_product),39);
        bufp->chgQData(oldp+733,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__rounded_product),40);
        bufp->chgSData(oldp+735,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__rounded_magnitude),9);
        bufp->chgSData(oldp+736,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__scaled_signed),9);
        bufp->chgIData(oldp+737,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_source_index),32);
        bufp->chgIData(oldp+738,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_source_channel),32);
        bufp->chgIData(oldp+739,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_upsample_engine__stride),32);
        bufp->chgCData(oldp+740,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__state),3);
        bufp->chgIData(oldp+741,((0x00000018U & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__source_address_latched 
                                                 << 3U))),32);
        bufp->chgCData(oldp+742,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__mapped_response_error),3);
        bufp->chgCData(oldp+743,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__error_code),3);
        bufp->chgIData(oldp+744,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__frame_id),32);
        bufp->chgIData(oldp+745,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__active_frame_id),32);
        bufp->chgIData(oldp+746,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__input_addr),32);
        bufp->chgIData(oldp+747,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__input_bytes),32);
        bufp->chgIData(oldp+748,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__weight_addr),32);
        bufp->chgIData(oldp+749,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__weight_bytes),32);
        bufp->chgIData(oldp+750,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__timeout_cycles),32);
        bufp->chgIData(oldp+751,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__elapsed_cycles),32);
        bufp->chgBit(oldp+752,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__config_idle));
    }
    bufp->chgBit(oldp+753,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__clk));
    bufp->chgCData(oldp+754,((((4U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                                ? (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                                     ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_wstrb)
                                     : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_wstrb)) 
                                   & (- (IData)((1U 
                                                 & (~ 
                                                    ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                                     >> 1U))))))
                                : (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                                     ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_wstrb)
                                     : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_wstrb)) 
                                   & (- (IData)((1U 
                                                 & ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                                    >> 1U)))))) 
                              & (- (IData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid))))),4);
    bufp->chgIData(oldp+755,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__simulation_cycle_count),32);
    bufp->chgIData(oldp+756,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__memory_read_handshakes),32);
    bufp->chgIData(oldp+757,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__memory_write_side_effects),32);
    bufp->chgBit(oldp+758,(((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__hard_reset) 
                            | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__backend_abort))));
    bufp->chgBit(oldp+759,(((4U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                             ? ((~ ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                    >> 1U)) & ((1U 
                                                & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                                                ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_valid)
                                                : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_valid)))
                             : (((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                 >> 1U) & ((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                                            ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_valid)
                                            : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_valid))))));
    bufp->chgBit(oldp+760,(((4U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                             ? ((~ ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                    >> 1U)) & ((1U 
                                                & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                                                ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_write)
                                                : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_write)))
                             : (((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                 >> 1U) & ((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                                            ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_write)
                                            : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_write))))));
    bufp->chgCData(oldp+761,(((4U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                               ? (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                                    ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_rstrb)
                                    : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_rstrb)) 
                                  & (- (IData)((1U 
                                                & (~ 
                                                   ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                                    >> 1U))))))
                               : (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                                    ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_rstrb)
                                    : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_rstrb)) 
                                  & (- (IData)((1U 
                                                & ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                                   >> 1U))))))),4);
    bufp->chgCData(oldp+762,(((4U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                               ? (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                                    ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_wstrb)
                                    : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_wstrb)) 
                                  & (- (IData)((1U 
                                                & (~ 
                                                   ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                                    >> 1U))))))
                               : (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                                    ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_wstrb)
                                    : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_wstrb)) 
                                  & (- (IData)((1U 
                                                & ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                                   >> 1U))))))),4);
}

void Vtb_s2a_backend_fault_recovery___024root__trace_chg_dtype____0(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd::Buffer* bufp, uint32_t offset, const VlUnpacked<IData/*31:0*/, 9>& __VdtypeVar) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root__trace_chg_dtype____0\n"); );
    Vtb_s2a_backend_fault_recovery__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    uint32_t* const oldp VL_ATTR_UNUSED = bufp->oldp(vlSymsp->__Vm_baseCode +  offset);
    bufp->chgIData(oldp+0,(__VdtypeVar[0]),32);
    bufp->chgIData(oldp+1,(__VdtypeVar[1]),32);
    bufp->chgIData(oldp+2,(__VdtypeVar[2]),32);
    bufp->chgIData(oldp+3,(__VdtypeVar[3]),32);
    bufp->chgIData(oldp+4,(__VdtypeVar[4]),32);
    bufp->chgIData(oldp+5,(__VdtypeVar[5]),32);
    bufp->chgIData(oldp+6,(__VdtypeVar[6]),32);
    bufp->chgIData(oldp+7,(__VdtypeVar[7]),32);
    bufp->chgIData(oldp+8,(__VdtypeVar[8]),32);
}

void Vtb_s2a_backend_fault_recovery___024root__trace_chg_dtype____1(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd::Buffer* bufp, uint32_t offset, const VlUnpacked<IData/*31:0*/, 9>& __VdtypeVar) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root__trace_chg_dtype____1\n"); );
    Vtb_s2a_backend_fault_recovery__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    uint32_t* const oldp VL_ATTR_UNUSED = bufp->oldp(vlSymsp->__Vm_baseCode +  offset);
    bufp->chgIData(oldp+0,(__VdtypeVar[0]),32);
    bufp->chgIData(oldp+1,(__VdtypeVar[1]),32);
    bufp->chgIData(oldp+2,(__VdtypeVar[2]),32);
    bufp->chgIData(oldp+3,(__VdtypeVar[3]),32);
    bufp->chgIData(oldp+4,(__VdtypeVar[4]),32);
    bufp->chgIData(oldp+5,(__VdtypeVar[5]),32);
    bufp->chgIData(oldp+6,(__VdtypeVar[6]),32);
    bufp->chgIData(oldp+7,(__VdtypeVar[7]),32);
    bufp->chgIData(oldp+8,(__VdtypeVar[8]),32);
}

void Vtb_s2a_backend_fault_recovery___024root__trace_chg_dtype____2(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd::Buffer* bufp, uint32_t offset, const VlUnpacked<QData/*63:0*/, 9>& __VdtypeVar) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root__trace_chg_dtype____2\n"); );
    Vtb_s2a_backend_fault_recovery__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    uint32_t* const oldp VL_ATTR_UNUSED = bufp->oldp(vlSymsp->__Vm_baseCode +  offset);
    bufp->chgQData(oldp+0,(__VdtypeVar[0]),64);
    bufp->chgQData(oldp+2,(__VdtypeVar[1]),64);
    bufp->chgQData(oldp+4,(__VdtypeVar[2]),64);
    bufp->chgQData(oldp+6,(__VdtypeVar[3]),64);
    bufp->chgQData(oldp+8,(__VdtypeVar[4]),64);
    bufp->chgQData(oldp+10,(__VdtypeVar[5]),64);
    bufp->chgQData(oldp+12,(__VdtypeVar[6]),64);
    bufp->chgQData(oldp+14,(__VdtypeVar[7]),64);
    bufp->chgQData(oldp+16,(__VdtypeVar[8]),64);
}

void Vtb_s2a_backend_fault_recovery___024root__trace_chg_dtype____3(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd::Buffer* bufp, uint32_t offset, const VlUnpacked<QData/*63:0*/, 9>& __VdtypeVar) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root__trace_chg_dtype____3\n"); );
    Vtb_s2a_backend_fault_recovery__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    uint32_t* const oldp VL_ATTR_UNUSED = bufp->oldp(vlSymsp->__Vm_baseCode +  offset);
    bufp->chgQData(oldp+0,(__VdtypeVar[0]),64);
    bufp->chgQData(oldp+2,(__VdtypeVar[1]),64);
    bufp->chgQData(oldp+4,(__VdtypeVar[2]),64);
    bufp->chgQData(oldp+6,(__VdtypeVar[3]),64);
    bufp->chgQData(oldp+8,(__VdtypeVar[4]),64);
    bufp->chgQData(oldp+10,(__VdtypeVar[5]),64);
    bufp->chgQData(oldp+12,(__VdtypeVar[6]),64);
    bufp->chgQData(oldp+14,(__VdtypeVar[7]),64);
    bufp->chgQData(oldp+16,(__VdtypeVar[8]),64);
}

void Vtb_s2a_backend_fault_recovery___024root__trace_chg_dtype____4(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd::Buffer* bufp, uint32_t offset, const VlUnpacked<IData/*31:0*/, 8>& __VdtypeVar) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root__trace_chg_dtype____4\n"); );
    Vtb_s2a_backend_fault_recovery__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    uint32_t* const oldp VL_ATTR_UNUSED = bufp->oldp(vlSymsp->__Vm_baseCode +  offset);
    bufp->chgIData(oldp+0,(__VdtypeVar[0]),32);
    bufp->chgIData(oldp+1,(__VdtypeVar[1]),32);
    bufp->chgIData(oldp+2,(__VdtypeVar[2]),32);
    bufp->chgIData(oldp+3,(__VdtypeVar[3]),32);
    bufp->chgIData(oldp+4,(__VdtypeVar[4]),32);
    bufp->chgIData(oldp+5,(__VdtypeVar[5]),32);
    bufp->chgIData(oldp+6,(__VdtypeVar[6]),32);
    bufp->chgIData(oldp+7,(__VdtypeVar[7]),32);
}

void Vtb_s2a_backend_fault_recovery___024root__trace_chg_dtype____5(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd::Buffer* bufp, uint32_t offset, const VlUnpacked<CData/*7:0*/, 8>& __VdtypeVar) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root__trace_chg_dtype____5\n"); );
    Vtb_s2a_backend_fault_recovery__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    uint32_t* const oldp VL_ATTR_UNUSED = bufp->oldp(vlSymsp->__Vm_baseCode +  offset);
    bufp->chgCData(oldp+0,(__VdtypeVar[0]),8);
    bufp->chgCData(oldp+1,(__VdtypeVar[1]),8);
    bufp->chgCData(oldp+2,(__VdtypeVar[2]),8);
    bufp->chgCData(oldp+3,(__VdtypeVar[3]),8);
    bufp->chgCData(oldp+4,(__VdtypeVar[4]),8);
    bufp->chgCData(oldp+5,(__VdtypeVar[5]),8);
    bufp->chgCData(oldp+6,(__VdtypeVar[6]),8);
    bufp->chgCData(oldp+7,(__VdtypeVar[7]),8);
}

void Vtb_s2a_backend_fault_recovery___024root__trace_chg_dtype____6(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd::Buffer* bufp, uint32_t offset, const VlUnpacked<VlWide<3>/*79:0*/, 8>& __VdtypeVar) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root__trace_chg_dtype____6\n"); );
    Vtb_s2a_backend_fault_recovery__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    uint32_t* const oldp VL_ATTR_UNUSED = bufp->oldp(vlSymsp->__Vm_baseCode +  offset);
    bufp->chgWData(oldp+0,(__VdtypeVar[0]),80);
    bufp->chgWData(oldp+3,(__VdtypeVar[1]),80);
    bufp->chgWData(oldp+6,(__VdtypeVar[2]),80);
    bufp->chgWData(oldp+9,(__VdtypeVar[3]),80);
    bufp->chgWData(oldp+12,(__VdtypeVar[4]),80);
    bufp->chgWData(oldp+15,(__VdtypeVar[5]),80);
    bufp->chgWData(oldp+18,(__VdtypeVar[6]),80);
    bufp->chgWData(oldp+21,(__VdtypeVar[7]),80);
}

void Vtb_s2a_backend_fault_recovery___024root__trace_chg_dtype____7(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd::Buffer* bufp, uint32_t offset, const VlUnpacked<IData/*31:0*/, 8>& __VdtypeVar) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root__trace_chg_dtype____7\n"); );
    Vtb_s2a_backend_fault_recovery__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    uint32_t* const oldp VL_ATTR_UNUSED = bufp->oldp(vlSymsp->__Vm_baseCode +  offset);
    bufp->chgIData(oldp+0,(__VdtypeVar[0]),32);
    bufp->chgIData(oldp+1,(__VdtypeVar[1]),32);
    bufp->chgIData(oldp+2,(__VdtypeVar[2]),32);
    bufp->chgIData(oldp+3,(__VdtypeVar[3]),32);
    bufp->chgIData(oldp+4,(__VdtypeVar[4]),32);
    bufp->chgIData(oldp+5,(__VdtypeVar[5]),32);
    bufp->chgIData(oldp+6,(__VdtypeVar[6]),32);
    bufp->chgIData(oldp+7,(__VdtypeVar[7]),32);
}

void Vtb_s2a_backend_fault_recovery___024root__trace_chg_dtype____8(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd::Buffer* bufp, uint32_t offset, const VlUnpacked<IData/*31:0*/, 4>& __VdtypeVar) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root__trace_chg_dtype____8\n"); );
    Vtb_s2a_backend_fault_recovery__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    uint32_t* const oldp VL_ATTR_UNUSED = bufp->oldp(vlSymsp->__Vm_baseCode +  offset);
    bufp->chgIData(oldp+0,(__VdtypeVar[0]),32);
    bufp->chgIData(oldp+1,(__VdtypeVar[1]),32);
    bufp->chgIData(oldp+2,(__VdtypeVar[2]),32);
    bufp->chgIData(oldp+3,(__VdtypeVar[3]),32);
}

void Vtb_s2a_backend_fault_recovery___024root__trace_cleanup(void* voidSelf, VerilatedVcd* /*unused*/) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root__trace_cleanup\n"); );
    // Body
    Vtb_s2a_backend_fault_recovery___024root* const __restrict vlSelf VL_ATTR_UNUSED = static_cast<Vtb_s2a_backend_fault_recovery___024root*>(voidSelf);
    Vtb_s2a_backend_fault_recovery__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    vlSymsp->__Vm_activity = false;
    vlSymsp->TOP.__Vm_traceActivity[0U] = 0U;
    vlSymsp->TOP.__Vm_traceActivity[1U] = 0U;
    vlSymsp->TOP.__Vm_traceActivity[2U] = 0U;
    vlSymsp->TOP.__Vm_traceActivity[3U] = 0U;
    vlSymsp->TOP.__Vm_traceActivity[4U] = 0U;
    vlSymsp->TOP.__Vm_traceActivity[5U] = 0U;
    vlSymsp->TOP.__Vm_traceActivity[6U] = 0U;
}
