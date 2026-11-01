// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vtb_s2a_backend_fault_recovery.h for the primary calling header

#include "Vtb_s2a_backend_fault_recovery__pch.h"

VlCoroutine Vtb_s2a_backend_fault_recovery___024root___eval_initial__TOP__Vtiming__0(Vtb_s2a_backend_fault_recovery___024root* vlSelf);
VlCoroutine Vtb_s2a_backend_fault_recovery___024root___eval_initial__TOP__Vtiming__1(Vtb_s2a_backend_fault_recovery___024root* vlSelf);
VlCoroutine Vtb_s2a_backend_fault_recovery___024root___eval_initial__TOP__Vtiming__2(Vtb_s2a_backend_fault_recovery___024root* vlSelf);

void Vtb_s2a_backend_fault_recovery___024root___eval_initial(Vtb_s2a_backend_fault_recovery___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root___eval_initial\n"); );
    Vtb_s2a_backend_fault_recovery__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    {
        // Inlined CFunc: _eval_initial__TOP
        IData/*31:0*/ __Vinline_0__eval_initial__TOP_tb_s2a_backend_fault_recovery__DOT____VlemExpr_0;
        __Vinline_0__eval_initial__TOP_tb_s2a_backend_fault_recovery__DOT____VlemExpr_0 
            = VL_VALUEPLUSARGS_INN(64, "WAVEFORM_PATH=%s"s, 
                                   vlSelfRef.tb_s2a_backend_fault_recovery__DOT__waveform_path);
        if (VL_UNLIKELY(((! __Vinline_0__eval_initial__TOP_tb_s2a_backend_fault_recovery__DOT____VlemExpr_0)))) {
            VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:76: Assertion failed in %m: \347\274\272\345\260\221\345\256\232\345\220\221\346\265\213\350\257\225\346\263\242\345\275\242\350\276\223\345\207\272\350\267\257\345\276\204\n",3, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery", 'T',-9
                         , '#',64,VL_TIME_UNITED_Q(1000));
            VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 76, "", false);
        }
        vlSymsp->_vm_contextp__->dumpfile(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__waveform_path);
        vlSymsp->_traceDumpOpen();
    }
    vlSelfRef.__Vm_traceActivity[2U] = 1U;
    Vtb_s2a_backend_fault_recovery___024root___eval_initial__TOP__Vtiming__0(vlSelf);
    Vtb_s2a_backend_fault_recovery___024root___eval_initial__TOP__Vtiming__1(vlSelf);
    Vtb_s2a_backend_fault_recovery___024root___eval_initial__TOP__Vtiming__2(vlSelf);
}

VlCoroutine Vtb_s2a_backend_fault_recovery___024root___eval_initial__TOP__Vtiming__0(Vtb_s2a_backend_fault_recovery___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root___eval_initial__TOP__Vtiming__0\n"); );
    Vtb_s2a_backend_fault_recovery__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    co_await vlSelfRef.__VdlySched.delay(0x000000012a05f200ULL, 
                                         nullptr, "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                         70);
    VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:71: Assertion failed in %m: \345\256\232\345\220\221 backend/CSR fault-recovery \350\207\252\346\243\200\350\266\205\346\227\266\n",3, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery", 'T',-9
                 , '#',64,VL_TIME_UNITED_Q(1000));
    VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 71, "", false);
    co_return;
}

void Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(Vtb_s2a_backend_fault_recovery___024root* vlSelf, const char* __VeventDescription);
void Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e288__0(Vtb_s2a_backend_fault_recovery___024root* vlSelf, const char* __VeventDescription);

VlCoroutine Vtb_s2a_backend_fault_recovery___024root___eval_initial__TOP__Vtiming__1(Vtb_s2a_backend_fault_recovery___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root___eval_initial__TOP__Vtiming__1\n"); );
    Vtb_s2a_backend_fault_recovery__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__reset_design__2__tb_s2a_backend_fault_recovery__DOT__unnamedblk1_1__DOT____Vrepeat0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__reset_design__2__tb_s2a_backend_fault_recovery__DOT__unnamedblk1_1__DOT____Vrepeat0 = 0;
    CData/*3:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__3__expected_status;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__3__expected_status = 0;
    CData/*2:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__3__expected_error_code;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__3__expected_error_code = 0;
    CData/*0:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__3__expected_head_valid;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__3__expected_head_valid = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__3__status_value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__3__status_value = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__3__error_value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__3__error_value = 0;
    CData/*7:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__4__address;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__4__address = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__4__value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__4__value = 0;
    CData/*7:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__5__address;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__5__address = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__5__value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__5__value = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__start_transaction__6__timeout_value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__start_transaction__6__timeout_value = 0;
    CData/*7:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__7__address;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__7__address = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__7__value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__7__value = 0;
    CData/*7:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__8__address;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__8__address = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__8__value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__8__value = 0;
    CData/*2:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__inject_read_error__9__response_code;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__inject_read_error__9__response_code = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__inject_read_error__9__reads_before;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__inject_read_error__9__reads_before = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__inject_read_error__9__writes_before;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__inject_read_error__9__writes_before = 0;
    CData/*0:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_read_request__10____VlefCall_1__selected_byte_in_input_tensor;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_read_request__10____VlefCall_1__selected_byte_in_input_tensor = 0;
    CData/*0:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_read_request__10____VlefCall_0__is_onehot4;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_read_request__10____VlefCall_0__is_onehot4 = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_read_request__10__wait_index;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_read_request__10__wait_index = 0;
    CData/*0:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_read_request__10__request_found;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_read_request__10__request_found = 0;
    CData/*0:0*/ __Vfunc_tb_s2a_backend_fault_recovery__DOT__is_onehot4__11__Vfuncout;
    __Vfunc_tb_s2a_backend_fault_recovery__DOT__is_onehot4__11__Vfuncout = 0;
    CData/*3:0*/ __Vfunc_tb_s2a_backend_fault_recovery__DOT__is_onehot4__11__value;
    __Vfunc_tb_s2a_backend_fault_recovery__DOT__is_onehot4__11__value = 0;
    CData/*0:0*/ __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__12__Vfuncout;
    __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__12__Vfuncout = 0;
    CData/*0:0*/ __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__12__found;
    __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__12__found = 0;
    IData/*31:0*/ __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__12__selected_address;
    __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__12__selected_address = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_request__13__saved_address;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_request__13__saved_address = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_request__13__saved_wdata;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_request__13__saved_wdata = 0;
    CData/*3:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_request__13__saved_rstrb;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_request__13__saved_rstrb = 0;
    CData/*3:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_request__13__saved_wstrb;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_request__13__saved_wstrb = 0;
    CData/*0:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_request__13__saved_write;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_request__13__saved_write = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_request__13__stall_index;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_request__13__stall_index = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_memory_error__14__wait_index;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_memory_error__14__wait_index = 0;
    CData/*0:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_memory_error__14__error_found;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_memory_error__14__error_found = 0;
    CData/*3:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__15__expected_status;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__15__expected_status = 0;
    CData/*2:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__15__expected_error_code;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__15__expected_error_code = 0;
    CData/*0:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__15__expected_head_valid;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__15__expected_head_valid = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__15__status_value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__15__status_value = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__15__error_value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__15__error_value = 0;
    CData/*7:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__16__address;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__16__address = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__16__value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__16__value = 0;
    CData/*7:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__17__address;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__17__address = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__17__value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__17__value = 0;
    CData/*7:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__19__address;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__19__address = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__19__value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__19__value = 0;
    CData/*3:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__20__expected_status;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__20__expected_status = 0;
    CData/*2:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__20__expected_error_code;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__20__expected_error_code = 0;
    CData/*0:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__20__expected_head_valid;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__20__expected_head_valid = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__20__status_value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__20__status_value = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__20__error_value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__20__error_value = 0;
    CData/*7:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__21__address;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__21__address = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__21__value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__21__value = 0;
    CData/*7:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__22__address;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__22__address = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__22__value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__22__value = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__start_transaction__23__timeout_value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__start_transaction__23__timeout_value = 0;
    CData/*7:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__24__address;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__24__address = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__24__value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__24__value = 0;
    CData/*7:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__25__address;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__25__address = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__25__value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__25__value = 0;
    CData/*2:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__inject_read_error__26__response_code;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__inject_read_error__26__response_code = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__inject_read_error__26__reads_before;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__inject_read_error__26__reads_before = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__inject_read_error__26__writes_before;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__inject_read_error__26__writes_before = 0;
    CData/*0:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_read_request__27____VlefCall_1__selected_byte_in_input_tensor;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_read_request__27____VlefCall_1__selected_byte_in_input_tensor = 0;
    CData/*0:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_read_request__27____VlefCall_0__is_onehot4;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_read_request__27____VlefCall_0__is_onehot4 = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_read_request__27__wait_index;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_read_request__27__wait_index = 0;
    CData/*0:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_read_request__27__request_found;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_read_request__27__request_found = 0;
    CData/*0:0*/ __Vfunc_tb_s2a_backend_fault_recovery__DOT__is_onehot4__28__Vfuncout;
    __Vfunc_tb_s2a_backend_fault_recovery__DOT__is_onehot4__28__Vfuncout = 0;
    CData/*3:0*/ __Vfunc_tb_s2a_backend_fault_recovery__DOT__is_onehot4__28__value;
    __Vfunc_tb_s2a_backend_fault_recovery__DOT__is_onehot4__28__value = 0;
    CData/*0:0*/ __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__29__Vfuncout;
    __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__29__Vfuncout = 0;
    CData/*0:0*/ __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__29__found;
    __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__29__found = 0;
    IData/*31:0*/ __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__29__selected_address;
    __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__29__selected_address = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_request__30__saved_address;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_request__30__saved_address = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_request__30__saved_wdata;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_request__30__saved_wdata = 0;
    CData/*3:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_request__30__saved_rstrb;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_request__30__saved_rstrb = 0;
    CData/*3:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_request__30__saved_wstrb;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_request__30__saved_wstrb = 0;
    CData/*0:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_request__30__saved_write;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_request__30__saved_write = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_request__30__stall_index;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_request__30__stall_index = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_memory_error__31__wait_index;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_memory_error__31__wait_index = 0;
    CData/*0:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_memory_error__31__error_found;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_memory_error__31__error_found = 0;
    CData/*3:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__32__expected_status;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__32__expected_status = 0;
    CData/*2:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__32__expected_error_code;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__32__expected_error_code = 0;
    CData/*0:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__32__expected_head_valid;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__32__expected_head_valid = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__32__status_value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__32__status_value = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__32__error_value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__32__error_value = 0;
    CData/*7:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__33__address;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__33__address = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__33__value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__33__value = 0;
    CData/*7:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__34__address;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__34__address = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__34__value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__34__value = 0;
    CData/*7:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__36__address;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__36__address = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__36__value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__36__value = 0;
    CData/*3:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__37__expected_status;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__37__expected_status = 0;
    CData/*2:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__37__expected_error_code;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__37__expected_error_code = 0;
    CData/*0:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__37__expected_head_valid;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__37__expected_head_valid = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__37__status_value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__37__status_value = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__37__error_value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__37__error_value = 0;
    CData/*7:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__38__address;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__38__address = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__38__value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__38__value = 0;
    CData/*7:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__39__address;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__39__address = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__39__value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__39__value = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__cancel_output_write_with_soft_reset__40__reads_before;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__cancel_output_write_with_soft_reset__40__reads_before = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__cancel_output_write_with_soft_reset__40__writes_before;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__cancel_output_write_with_soft_reset__40__writes_before = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__prepare_unaccepted_output_write__41__reads_before;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__prepare_unaccepted_output_write__41__reads_before = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__prepare_unaccepted_output_write__41__writes_before;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__prepare_unaccepted_output_write__41__writes_before = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__start_transaction__42__timeout_value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__start_transaction__42__timeout_value = 0;
    CData/*7:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__43__address;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__43__address = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__43__value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__43__value = 0;
    CData/*7:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__44__address;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__44__address = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__44__value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__44__value = 0;
    CData/*0:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__45____VlefCall_1__selected_byte_in_layer0_output_tensor;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__45____VlefCall_1__selected_byte_in_layer0_output_tensor = 0;
    CData/*0:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__45____VlefCall_0__is_onehot4;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__45____VlefCall_0__is_onehot4 = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__45__wait_index;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__45__wait_index = 0;
    CData/*0:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__45__request_found;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__45__request_found = 0;
    CData/*0:0*/ __Vfunc_tb_s2a_backend_fault_recovery__DOT__is_onehot4__46__Vfuncout;
    __Vfunc_tb_s2a_backend_fault_recovery__DOT__is_onehot4__46__Vfuncout = 0;
    CData/*3:0*/ __Vfunc_tb_s2a_backend_fault_recovery__DOT__is_onehot4__46__value;
    __Vfunc_tb_s2a_backend_fault_recovery__DOT__is_onehot4__46__value = 0;
    CData/*0:0*/ __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__47__Vfuncout;
    __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__47__Vfuncout = 0;
    CData/*0:0*/ __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__47__found;
    __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__47__found = 0;
    IData/*31:0*/ __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__47__selected_address;
    __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__47__selected_address = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_output_write__48__saved_address;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_output_write__48__saved_address = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_output_write__48__saved_wdata;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_output_write__48__saved_wdata = 0;
    CData/*3:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_output_write__48__saved_wstrb;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_output_write__48__saved_wstrb = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_output_write__48__stall_index;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_output_write__48__stall_index = 0;
    CData/*7:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__49__address;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__49__address = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__49__value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__49__value = 0;
    CData/*3:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__50__expected_status;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__50__expected_status = 0;
    CData/*2:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__50__expected_error_code;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__50__expected_error_code = 0;
    CData/*0:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__50__expected_head_valid;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__50__expected_head_valid = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__50__status_value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__50__status_value = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__50__error_value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__50__error_value = 0;
    CData/*7:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__51__address;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__51__address = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__51__value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__51__value = 0;
    CData/*7:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__52__address;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__52__address = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__52__value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__52__value = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__check_no_late_effects__53__reads_before;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_no_late_effects__53__reads_before = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__check_no_late_effects__53__writes_before;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_no_late_effects__53__writes_before = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__check_no_late_effects__53__quiet_index;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_no_late_effects__53__quiet_index = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__cancel_output_write_with_hard_reset__54__tb_s2a_backend_fault_recovery__DOT__unnamedblk1_2__DOT____Vrepeat1;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__cancel_output_write_with_hard_reset__54__tb_s2a_backend_fault_recovery__DOT__unnamedblk1_2__DOT____Vrepeat1 = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__cancel_output_write_with_hard_reset__54__reads_before;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__cancel_output_write_with_hard_reset__54__reads_before = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__cancel_output_write_with_hard_reset__54__writes_before;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__cancel_output_write_with_hard_reset__54__writes_before = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__prepare_unaccepted_output_write__55__reads_before;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__prepare_unaccepted_output_write__55__reads_before = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__prepare_unaccepted_output_write__55__writes_before;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__prepare_unaccepted_output_write__55__writes_before = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__start_transaction__56__timeout_value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__start_transaction__56__timeout_value = 0;
    CData/*7:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__57__address;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__57__address = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__57__value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__57__value = 0;
    CData/*7:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__58__address;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__58__address = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__58__value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__58__value = 0;
    CData/*0:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__59____VlefCall_1__selected_byte_in_layer0_output_tensor;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__59____VlefCall_1__selected_byte_in_layer0_output_tensor = 0;
    CData/*0:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__59____VlefCall_0__is_onehot4;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__59____VlefCall_0__is_onehot4 = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__59__wait_index;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__59__wait_index = 0;
    CData/*0:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__59__request_found;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__59__request_found = 0;
    CData/*0:0*/ __Vfunc_tb_s2a_backend_fault_recovery__DOT__is_onehot4__60__Vfuncout;
    __Vfunc_tb_s2a_backend_fault_recovery__DOT__is_onehot4__60__Vfuncout = 0;
    CData/*3:0*/ __Vfunc_tb_s2a_backend_fault_recovery__DOT__is_onehot4__60__value;
    __Vfunc_tb_s2a_backend_fault_recovery__DOT__is_onehot4__60__value = 0;
    CData/*0:0*/ __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__61__Vfuncout;
    __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__61__Vfuncout = 0;
    CData/*0:0*/ __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__61__found;
    __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__61__found = 0;
    IData/*31:0*/ __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__61__selected_address;
    __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__61__selected_address = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_output_write__62__saved_address;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_output_write__62__saved_address = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_output_write__62__saved_wdata;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_output_write__62__saved_wdata = 0;
    CData/*3:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_output_write__62__saved_wstrb;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_output_write__62__saved_wstrb = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_output_write__62__stall_index;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_output_write__62__stall_index = 0;
    CData/*3:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__63__expected_status;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__63__expected_status = 0;
    CData/*2:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__63__expected_error_code;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__63__expected_error_code = 0;
    CData/*0:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__63__expected_head_valid;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__63__expected_head_valid = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__63__status_value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__63__status_value = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__63__error_value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__63__error_value = 0;
    CData/*7:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__64__address;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__64__address = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__64__value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__64__value = 0;
    CData/*7:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__65__address;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__65__address = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__65__value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__65__value = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__check_no_late_effects__66__reads_before;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_no_late_effects__66__reads_before = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__check_no_late_effects__66__writes_before;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_no_late_effects__66__writes_before = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__check_no_late_effects__66__quiet_index;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_no_late_effects__66__quiet_index = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__cancel_output_write_with_timeout__67__reads_before;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__cancel_output_write_with_timeout__67__reads_before = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__cancel_output_write_with_timeout__67__writes_before;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__cancel_output_write_with_timeout__67__writes_before = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__cancel_output_write_with_timeout__67__wait_index;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__cancel_output_write_with_timeout__67__wait_index = 0;
    CData/*0:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__cancel_output_write_with_timeout__67__timeout_found;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__cancel_output_write_with_timeout__67__timeout_found = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__prepare_unaccepted_output_write__68__reads_before;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__prepare_unaccepted_output_write__68__reads_before = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__prepare_unaccepted_output_write__68__writes_before;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__prepare_unaccepted_output_write__68__writes_before = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__start_transaction__69__timeout_value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__start_transaction__69__timeout_value = 0;
    CData/*7:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__70__address;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__70__address = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__70__value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__70__value = 0;
    CData/*7:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__71__address;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__71__address = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__71__value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__71__value = 0;
    CData/*0:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__72____VlefCall_1__selected_byte_in_layer0_output_tensor;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__72____VlefCall_1__selected_byte_in_layer0_output_tensor = 0;
    CData/*0:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__72____VlefCall_0__is_onehot4;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__72____VlefCall_0__is_onehot4 = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__72__wait_index;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__72__wait_index = 0;
    CData/*0:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__72__request_found;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__72__request_found = 0;
    CData/*0:0*/ __Vfunc_tb_s2a_backend_fault_recovery__DOT__is_onehot4__73__Vfuncout;
    __Vfunc_tb_s2a_backend_fault_recovery__DOT__is_onehot4__73__Vfuncout = 0;
    CData/*3:0*/ __Vfunc_tb_s2a_backend_fault_recovery__DOT__is_onehot4__73__value;
    __Vfunc_tb_s2a_backend_fault_recovery__DOT__is_onehot4__73__value = 0;
    CData/*0:0*/ __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__74__Vfuncout;
    __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__74__Vfuncout = 0;
    CData/*0:0*/ __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__74__found;
    __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__74__found = 0;
    IData/*31:0*/ __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__74__selected_address;
    __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__74__selected_address = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_output_write__75__saved_address;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_output_write__75__saved_address = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_output_write__75__saved_wdata;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_output_write__75__saved_wdata = 0;
    CData/*3:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_output_write__75__saved_wstrb;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_output_write__75__saved_wstrb = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_output_write__75__stall_index;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_output_write__75__stall_index = 0;
    CData/*3:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__76__expected_status;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__76__expected_status = 0;
    CData/*2:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__76__expected_error_code;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__76__expected_error_code = 0;
    CData/*0:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__76__expected_head_valid;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__76__expected_head_valid = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__76__status_value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__76__status_value = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__76__error_value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__76__error_value = 0;
    CData/*7:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__77__address;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__77__address = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__77__value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__77__value = 0;
    CData/*7:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__78__address;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__78__address = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__78__value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__78__value = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__check_no_late_effects__79__reads_before;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_no_late_effects__79__reads_before = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__check_no_late_effects__79__writes_before;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_no_late_effects__79__writes_before = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__check_no_late_effects__79__quiet_index;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_no_late_effects__79__quiet_index = 0;
    CData/*7:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__81__address;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__81__address = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__81__value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__81__value = 0;
    CData/*3:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__82__expected_status;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__82__expected_status = 0;
    CData/*2:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__82__expected_error_code;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__82__expected_error_code = 0;
    CData/*0:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__82__expected_head_valid;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__82__expected_head_valid = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__82__status_value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__82__status_value = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__82__error_value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__82__error_value = 0;
    CData/*7:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__83__address;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__83__address = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__83__value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__83__value = 0;
    CData/*7:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__84__address;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__84__address = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__84__value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__84__value = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__start_transaction__85__timeout_value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__start_transaction__85__timeout_value = 0;
    CData/*7:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__86__address;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__86__address = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__86__value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__86__value = 0;
    CData/*7:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__87__address;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__87__address = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__87__value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__87__value = 0;
    CData/*0:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_read_request__88____VlefCall_1__selected_byte_in_input_tensor;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_read_request__88____VlefCall_1__selected_byte_in_input_tensor = 0;
    CData/*0:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_read_request__88____VlefCall_0__is_onehot4;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_read_request__88____VlefCall_0__is_onehot4 = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_read_request__88__wait_index;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_read_request__88__wait_index = 0;
    CData/*0:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_read_request__88__request_found;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_read_request__88__request_found = 0;
    CData/*0:0*/ __Vfunc_tb_s2a_backend_fault_recovery__DOT__is_onehot4__89__Vfuncout;
    __Vfunc_tb_s2a_backend_fault_recovery__DOT__is_onehot4__89__Vfuncout = 0;
    CData/*3:0*/ __Vfunc_tb_s2a_backend_fault_recovery__DOT__is_onehot4__89__value;
    __Vfunc_tb_s2a_backend_fault_recovery__DOT__is_onehot4__89__value = 0;
    CData/*0:0*/ __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__90__Vfuncout;
    __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__90__Vfuncout = 0;
    CData/*0:0*/ __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__90__found;
    __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__90__found = 0;
    IData/*31:0*/ __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__90__selected_address;
    __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__90__selected_address = 0;
    CData/*7:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__91__address;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__91__address = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__91__value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__91__value = 0;
    CData/*3:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__92__expected_status;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__92__expected_status = 0;
    CData/*2:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__92__expected_error_code;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__92__expected_error_code = 0;
    CData/*0:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__92__expected_head_valid;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__92__expected_head_valid = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__92__status_value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__92__status_value = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__92__error_value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__92__error_value = 0;
    CData/*7:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__93__address;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__93__address = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__93__value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__93__value = 0;
    CData/*7:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__94__address;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__94__address = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__94__value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__94__value = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__check_no_late_effects__95__reads_before;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_no_late_effects__95__reads_before = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__check_no_late_effects__95__writes_before;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_no_late_effects__95__writes_before = 0;
    IData/*31:0*/ __Vtask_tb_s2a_backend_fault_recovery__DOT__check_no_late_effects__95__quiet_index;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_no_late_effects__95__quiet_index = 0;
    // Body
    __Vtask_tb_s2a_backend_fault_recovery__DOT__reset_design__2__tb_s2a_backend_fault_recovery__DOT__unnamedblk1_1__DOT____Vrepeat0 = 0U;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         271);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__hard_reset = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_write = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__manual_mem_ready = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__automatic_read_responses = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__manual_mem_error_code = 0U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__reset_design__2__tb_s2a_backend_fault_recovery__DOT__unnamedblk1_1__DOT____Vrepeat0 = 2U;
    while (VL_LTS_III(32, 0U, __Vtask_tb_s2a_backend_fault_recovery__DOT__reset_design__2__tb_s2a_backend_fault_recovery__DOT__unnamedblk1_1__DOT____Vrepeat0)) {
        Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e288__0(vlSelf, 
                                                                             "@(posedge tb_s2a_backend_fault_recovery.clk)");
        co_await vlSelfRef.__VtrigSched_h3193e288__0.trigger(0U, 
                                                             nullptr, 
                                                             "@(posedge tb_s2a_backend_fault_recovery.clk)", 
                                                             "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                             278);
        vlSelfRef.__Vm_traceActivity[3U] = 1U;
        __Vtask_tb_s2a_backend_fault_recovery__DOT__reset_design__2__tb_s2a_backend_fault_recovery__DOT__unnamedblk1_1__DOT____Vrepeat0 
            = (__Vtask_tb_s2a_backend_fault_recovery__DOT__reset_design__2__tb_s2a_backend_fault_recovery__DOT__unnamedblk1_1__DOT____Vrepeat0 
               - (IData)(1U));
    }
    co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                         nullptr, "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                         279);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    if (VL_UNLIKELY((((((((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid) 
                          | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__busy)) 
                         | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__done)) 
                        | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__error)) 
                       | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__buffer_owner_pl)) 
                      | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__head_output_valid))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:281: Assertion failed in %m: \347\241\254\345\244\215\344\275\215\346\234\237\351\227\264\347\212\266\346\200\201\346\210\226 memory request \346\234\252\346\270\205\351\231\244\n",3, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.reset_design", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 281, "", false);
    }
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         283);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__hard_reset = 0U;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e288__0(vlSelf, 
                                                                         "@(posedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e288__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(posedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         285);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                         nullptr, "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                         286);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__3__phase_name = "\345\210\235\345\247\213\345\244\215\344\275\215\345\220\216"s;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__3__expected_head_valid = 0U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__3__expected_error_code = 0U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__3__expected_status = 0U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__3__status_value = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__3__error_value = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__4__address = 4U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__4__value = 0;
    if (VL_UNLIKELY((((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__backend_abort) 
                      | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:287: Assertion failed in %m: \347\241\254\345\244\215\344\275\215\351\207\212\346\224\276\345\220\216 abort/request \346\234\252\346\270\205\351\231\244\n",3, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.reset_design", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 287, "", false);
    }
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         224);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_write = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__4__address;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_wdata = 0U;
    co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                         nullptr, "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                         229);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__4__value 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_rdata;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         231);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr = 0U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__3__status_value 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__4__value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__5__address = 8U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__5__value = 0;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         224);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_write = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__5__address;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_wdata = 0U;
    co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                         nullptr, "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                         229);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__5__value 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_rdata;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         231);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr = 0U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__3__error_value 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__5__value;
    if (VL_UNLIKELY((((0x0000000fU & __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__3__status_value) 
                      != (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__3__expected_status))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:249: Assertion failed in %m: %s STATUS \344\270\215\345\214\271\351\205\215\357\274\232\346\234\237\346\234\233=%b \345\256\236\351\231\205=%b\n",6, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.check_status", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , 'S',&(vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__3__phase_name)
                     , '#',4,(IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__3__expected_status)
                     , '#',4,(0x0000000fU & __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__3__status_value));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 249, "", false);
    }
    if (VL_UNLIKELY((((7U & __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__3__error_value) 
                      != (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__3__expected_error_code))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:253: Assertion failed in %m: %s ERROR_CODE \344\270\215\345\214\271\351\205\215\357\274\232\346\234\237\346\234\233=%0d \345\256\236\351\231\205=%0d\n",6, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.check_status", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , 'S',&(vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__3__phase_name)
                     , '#',3,(IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__3__expected_error_code)
                     , '#',3,(7U & __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__3__error_value));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 253, "", false);
    }
    if (VL_UNLIKELY((((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__head_output_valid) 
                      != (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__3__expected_head_valid))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:257: Assertion failed in %m: %s head_output_valid \344\270\215\345\214\271\351\205\215\357\274\232\346\234\237\346\234\233=%b \345\256\236\351\231\205=%b\n",6, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.check_status", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , 'S',&(vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__3__phase_name)
                     , '#',1,(IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__3__expected_head_valid)
                     , '#',1,vlSelfRef.tb_s2a_backend_fault_recovery__DOT__head_output_valid);
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 257, "", false);
    }
    if (VL_UNLIKELY(((((((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__busy) 
                         != (1U & (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__3__expected_status))) 
                        | ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__done) 
                           != (1U & ((IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__3__expected_status) 
                                     >> 1U)))) | ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__error) 
                                                  != 
                                                  (1U 
                                                   & ((IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__3__expected_status) 
                                                      >> 2U)))) 
                      | ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__buffer_owner_pl) 
                         != (1U & ((IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__3__expected_status) 
                                   >> 3U))))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:264: Assertion failed in %m: %s CSR/status \350\276\223\345\207\272\344\270\216\347\212\266\346\200\201\344\275\215\344\270\215\344\270\200\350\207\264\n",4, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.check_status", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , 'S',&(vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__3__phase_name));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 264, "", false);
    }
    __Vtask_tb_s2a_backend_fault_recovery__DOT__start_transaction__6__timeout_value = 0x00001388U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__7__value 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__start_transaction__6__timeout_value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__7__address = 0x28U;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         206);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_write = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__7__address;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_wdata 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__7__value;
    if (VL_UNLIKELY(((1U & (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__csr_ready)))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:207: Assertion failed in %m: CSR \345\206\231\345\205\245\346\234\252 ready\357\274\232addr=%02h\n",4, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.write_csr", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , '#',8,(IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__7__address));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 207, "", false);
    }
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e288__0(vlSelf, 
                                                                         "@(posedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e288__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(posedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         212);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                         nullptr, "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                         213);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         214);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_write = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_wdata = 0U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__8__value = 1U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__8__address = 0U;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         206);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_write = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__8__address;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_wdata 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__8__value;
    if (VL_UNLIKELY(((1U & (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__csr_ready)))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:207: Assertion failed in %m: CSR \345\206\231\345\205\245\346\234\252 ready\357\274\232addr=%02h\n",4, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.write_csr", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , '#',8,(IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__8__address));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 207, "", false);
    }
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e288__0(vlSelf, 
                                                                         "@(posedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e288__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(posedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         212);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                         nullptr, "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                         213);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         214);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_write = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_wdata = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__transaction_start_cycle 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__simulation_cycle_count;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__inject_read_error__9__response_code = 6U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__inject_read_error__9__reads_before = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__inject_read_error__9__writes_before = 0;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__automatic_read_responses = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__manual_mem_ready = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__manual_mem_error_code = 0U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_read_request__10__wait_index = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_read_request__10__request_found = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_read_request__10__request_found = 0U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_read_request__10__wait_index = 0U;
    if (VL_UNLIKELY(((1U & (((((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__backend_start)) 
                               | (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__busy))) 
                              | (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__buffer_owner_pl))) 
                             | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__done)) 
                            | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__error)))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:296: Assertion failed in %m: CSR \346\234\252\346\216\245\345\217\227\345\220\210\346\263\225 start\357\274\232start=%b busy=%b owner=%b\n",6, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.start_transaction", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , '#',1,(IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__backend_start)
                     , '#',1,vlSelfRef.tb_s2a_backend_fault_recovery__DOT__busy
                     , '#',1,(IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__buffer_owner_pl));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 296, "", false);
    }
    {
        while (VL_GTS_III(32, 0x00000080U, __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_read_request__10__wait_index)) {
            Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                                "@(negedge tb_s2a_backend_fault_recovery.clk)");
            co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                                 nullptr, 
                                                                 "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                                 "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                                 309);
            vlSelfRef.__Vm_traceActivity[3U] = 1U;
            if (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid) {
                __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_read_request__10__request_found = 1U;
                __Vfunc_tb_s2a_backend_fault_recovery__DOT__is_onehot4__11__value 
                    = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_rstrb;
                __Vfunc_tb_s2a_backend_fault_recovery__DOT__is_onehot4__11__Vfuncout = 0;
                __Vfunc_tb_s2a_backend_fault_recovery__DOT__is_onehot4__11__Vfuncout 
                    = ((0U != (IData)(__Vfunc_tb_s2a_backend_fault_recovery__DOT__is_onehot4__11__value)) 
                       & (0U == ((IData)(__Vfunc_tb_s2a_backend_fault_recovery__DOT__is_onehot4__11__value) 
                                 & ((IData)(__Vfunc_tb_s2a_backend_fault_recovery__DOT__is_onehot4__11__value) 
                                    - (IData)(1U)))));
                __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_read_request__10____VlefCall_0__is_onehot4 
                    = __Vfunc_tb_s2a_backend_fault_recovery__DOT__is_onehot4__11__Vfuncout;
                __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__12__Vfuncout = 0;
                __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__12__found = 0;
                __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__12__selected_address = 0;
                __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__12__Vfuncout = 0U;
                __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__12__found = 0U;
                __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__12__selected_address = 0U;
                if ((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_rstrb))) {
                    __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__12__selected_address 
                        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_addr;
                    __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__12__found 
                        = (0x0007ec00U > __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__12__selected_address);
                }
                if ((2U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_rstrb))) {
                    __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__12__selected_address 
                        = ((IData)(1U) + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_addr);
                    __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__12__found 
                        = (0x0007ec00U > __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__12__selected_address);
                }
                if ((4U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_rstrb))) {
                    __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__12__selected_address 
                        = ((IData)(2U) + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_addr);
                    __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__12__found 
                        = (0x0007ec00U > __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__12__selected_address);
                }
                if ((8U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_rstrb))) {
                    __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__12__selected_address 
                        = ((IData)(3U) + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_addr);
                    __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__12__found 
                        = (0x0007ec00U > __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__12__selected_address);
                }
                __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__12__Vfuncout 
                    = __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__12__found;
                __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_read_request__10____VlefCall_1__selected_byte_in_input_tensor 
                    = __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__12__Vfuncout;
                if (VL_UNLIKELY(((1U & (((((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_write) 
                                           | (~ (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_read_request__10____VlefCall_0__is_onehot4))) 
                                          | (0U != 
                                             (((4U 
                                                & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                                                ? (
                                                   ((1U 
                                                     & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                                                     ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_wstrb)
                                                     : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_wstrb)) 
                                                   & (- (IData)(
                                                                (1U 
                                                                 & (~ 
                                                                    ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                                                     >> 1U))))))
                                                : (
                                                   ((1U 
                                                     & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                                                     ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_wstrb)
                                                     : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_wstrb)) 
                                                   & (- (IData)(
                                                                (1U 
                                                                 & ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                                                    >> 1U)))))) 
                                              & (- (IData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid)))))) 
                                         | (0U != (3U 
                                                   & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_addr))) 
                                        | (~ (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_read_request__10____VlefCall_1__selected_byte_in_input_tensor))))))) {
                    VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:314: Assertion failed in %m: backend \351\246\226\344\270\252 feature \350\257\273\350\257\267\346\261\202\344\270\215\345\234\250\350\276\223\345\205\245 tensor \346\210\226 byte lane \351\235\236\346\263\225\357\274\232addr=%08h rstrb=%b\n",5, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.wait_for_read_request", 'T',-9
                                 , '#',64,VL_TIME_UNITED_Q(1000)
                                 , '#',32,vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_addr
                                 , '#',4,(IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_rstrb));
                    VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 314, "", false);
                }
                if (VL_UNLIKELY((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_ready))) {
                    VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:317: Assertion failed in %m: unaccepted request \350\247\202\346\265\213\345\211\215\346\204\217\345\244\226\346\217\241\346\211\213\n",3, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.wait_for_read_request", 'T',-9
                                 , '#',64,VL_TIME_UNITED_Q(1000));
                    VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 317, "", false);
                }
                goto __Vlabel0;
            }
            if (VL_UNLIKELY(((1U & ((((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__busy)) 
                                      | (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__buffer_owner_pl))) 
                                     | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__error)) 
                                    | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__done)))))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:321: Assertion failed in %m: \347\255\211\345\276\205\345\220\210\346\263\225 read request \346\227\266\344\273\273\345\212\241\346\217\220\345\211\215\347\246\273\345\274\200 busy\357\274\232busy=%b error=%b code=%0d\n",6, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.wait_for_read_request", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000)
                             , '#',1,(IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__busy)
                             , '#',1,vlSelfRef.tb_s2a_backend_fault_recovery__DOT__error
                             , '#',3,(IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__error_code));
                VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 321, "", false);
            }
            __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_read_request__10__wait_index 
                = ((IData)(1U) + __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_read_request__10__wait_index);
        }
        __Vlabel0: ;
    }
    if (VL_UNLIKELY(((1U & (~ (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_read_request__10__request_found)))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:325: Assertion failed in %m: backend \346\234\252\345\234\250\351\231\220\345\256\232\345\221\250\346\234\237\345\206\205\345\217\221\345\207\272\347\234\237\345\256\236 read request\n",3, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.wait_for_read_request", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 325, "", false);
    }
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_request__13__saved_address = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_request__13__saved_wdata = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_request__13__saved_rstrb = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_request__13__saved_wstrb = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_request__13__saved_write = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_request__13__stall_index = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_request__13__saved_address 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_addr;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_request__13__saved_wdata 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_wdata;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_request__13__saved_rstrb 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_rstrb;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_request__13__saved_wstrb 
        = (((4U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
             ? (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                  ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_wstrb)
                  : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_wstrb)) 
                & (- (IData)((1U & (~ ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                       >> 1U)))))) : 
            (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
               ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_wstrb)
               : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_wstrb)) 
             & (- (IData)((1U & ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                 >> 1U)))))) & (- (IData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid))));
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_request__13__saved_write 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_write;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_request__13__stall_index = 0U;
    while (VL_GTS_III(32, 3U, __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_request__13__stall_index)) {
        Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e288__0(vlSelf, 
                                                                             "@(posedge tb_s2a_backend_fault_recovery.clk)");
        co_await vlSelfRef.__VtrigSched_h3193e288__0.trigger(0U, 
                                                             nullptr, 
                                                             "@(posedge tb_s2a_backend_fault_recovery.clk)", 
                                                             "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                             343);
        vlSelfRef.__Vm_traceActivity[3U] = 1U;
        co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                             nullptr, 
                                             "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                             344);
        vlSelfRef.__Vm_traceActivity[3U] = 1U;
        if (VL_UNLIKELY(((1U & (((((((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid)) 
                                     | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_ready)) 
                                    | (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_addr 
                                       != __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_request__13__saved_address)) 
                                   | (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_wdata 
                                      != __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_request__13__saved_wdata)) 
                                  | ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_rstrb) 
                                     != (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_request__13__saved_rstrb))) 
                                 | ((((4U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                                       ? (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                                            ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_wstrb)
                                            : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_wstrb)) 
                                          & (- (IData)(
                                                       (1U 
                                                        & (~ 
                                                           ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                                            >> 1U))))))
                                       : (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                                            ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_wstrb)
                                            : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_wstrb)) 
                                          & (- (IData)(
                                                       (1U 
                                                        & ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                                           >> 1U)))))) 
                                     & (- (IData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid)))) 
                                    != (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_request__13__saved_wstrb))) 
                                | ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_write) 
                                   != (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_request__13__saved_write))))))) {
            VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:348: Assertion failed in %m: \346\234\252\346\217\241\346\211\213 memory request \345\255\227\346\256\265\346\234\252\344\277\235\346\214\201\347\250\263\345\256\232\n",3, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.hold_unaccepted_request", 'T',-9
                         , '#',64,VL_TIME_UNITED_Q(1000));
            VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 348, "", false);
        }
        __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_request__13__stall_index 
            = ((IData)(1U) + __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_request__13__stall_index);
    }
    __Vtask_tb_s2a_backend_fault_recovery__DOT__inject_read_error__9__reads_before 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__memory_read_handshakes;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__inject_read_error__9__writes_before 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__memory_write_side_effects;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         381);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__manual_mem_ready = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__manual_mem_error_code 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__inject_read_error__9__response_code;
    co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                         nullptr, "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                         384);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    if (VL_UNLIKELY(((1U & ((((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid)) 
                              | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_write)) 
                             | (~ ((0U != (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__backend_memory_error_code)) 
                                   & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__memory_handshake)))) 
                            | ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__backend_memory_error_code) 
                               != (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__inject_read_error__9__response_code))))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:387: Assertion failed in %m: memory response \346\234\252\347\273\217\347\234\237\345\256\236 backend handshake \344\272\247\347\224\237\351\224\231\350\257\257\344\272\213\344\273\266\357\274\232code=%0d valid=%b\n",5, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.inject_read_error", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , '#',3,(IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__inject_read_error__9__response_code)
                     , '#',1,((0U != (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__backend_memory_error_code)) 
                              & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__memory_handshake)));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 387, "", false);
    }
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e288__0(vlSelf, 
                                                                         "@(posedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e288__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(posedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         390);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                         nullptr, "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                         391);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__manual_mem_ready = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__manual_mem_error_code = 0U;
    if (VL_UNLIKELY(((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__memory_read_handshakes 
                      != ((IData)(1U) + __Vtask_tb_s2a_backend_fault_recovery__DOT__inject_read_error__9__reads_before))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:395: Assertion failed in %m: \346\263\250\345\205\245\351\224\231\350\257\257\350\257\273\346\234\252\346\201\260\345\245\275\346\217\241\346\211\213\344\270\200\346\254\241\357\274\232before=%0d after=%0d\n",5, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.inject_read_error", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , '~',32,__Vtask_tb_s2a_backend_fault_recovery__DOT__inject_read_error__9__reads_before
                     , '~',32,vlSelfRef.tb_s2a_backend_fault_recovery__DOT__memory_read_handshakes);
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 395, "", false);
    }
    if (VL_UNLIKELY(((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__memory_write_side_effects 
                      != __Vtask_tb_s2a_backend_fault_recovery__DOT__inject_read_error__9__writes_before)))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:399: Assertion failed in %m: \345\244\261\350\264\245 read response \344\272\247\347\224\237 output write \345\211\257\344\275\234\347\224\250\n",3, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.inject_read_error", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 399, "", false);
    }
    __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_memory_error__14__wait_index = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_memory_error__14__error_found = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_memory_error__14__error_found = 0U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_memory_error__14__wait_index = 0U;
    {
        while (VL_GTS_III(32, 8U, __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_memory_error__14__wait_index)) {
            Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                                "@(negedge tb_s2a_backend_fault_recovery.clk)");
            co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                                 nullptr, 
                                                                 "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                                 "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                                 360);
            vlSelfRef.__Vm_traceActivity[3U] = 1U;
            if (((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__error) 
                 & (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__busy)))) {
                __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_memory_error__14__error_found = 1U;
                goto __Vlabel1;
            }
            __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_memory_error__14__wait_index 
                = ((IData)(1U) + __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_memory_error__14__wait_index);
        }
        __Vlabel1: ;
    }
    if (VL_UNLIKELY(((1U & (~ (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_memory_error__14__error_found)))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:366: Assertion failed in %m: \347\234\237\345\256\236 memory error response \346\234\252\347\273\210\346\255\242 CSR \344\273\273\345\212\241\n",3, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.wait_for_memory_error", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 366, "", false);
    }
    vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__15__phase_name = "memory fault"s;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__15__expected_head_valid = 0U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__15__expected_error_code = 6U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__15__expected_status = 4U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__15__status_value = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__15__error_value = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__16__address = 4U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__16__value = 0;
    if (VL_UNLIKELY((((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid) 
                      | ((0U != (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__backend_memory_error_code)) 
                         & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__memory_handshake)))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:403: Assertion failed in %m: \345\244\261\350\264\245 response \345\220\216\344\273\215\346\234\211 memory request/error event\n",3, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.inject_read_error", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 403, "", false);
    }
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         224);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_write = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__16__address;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_wdata = 0U;
    co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                         nullptr, "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                         229);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__16__value 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_rdata;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         231);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr = 0U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__15__status_value 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__16__value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__17__address = 8U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__17__value = 0;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         224);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_write = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__17__address;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_wdata = 0U;
    co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                         nullptr, "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                         229);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__17__value 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_rdata;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         231);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr = 0U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__15__error_value 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__17__value;
    if (VL_UNLIKELY((((0x0000000fU & __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__15__status_value) 
                      != (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__15__expected_status))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:249: Assertion failed in %m: %s STATUS \344\270\215\345\214\271\351\205\215\357\274\232\346\234\237\346\234\233=%b \345\256\236\351\231\205=%b\n",6, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.check_status", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , 'S',&(vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__15__phase_name)
                     , '#',4,(IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__15__expected_status)
                     , '#',4,(0x0000000fU & __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__15__status_value));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 249, "", false);
    }
    if (VL_UNLIKELY((((7U & __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__15__error_value) 
                      != (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__15__expected_error_code))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:253: Assertion failed in %m: %s ERROR_CODE \344\270\215\345\214\271\351\205\215\357\274\232\346\234\237\346\234\233=%0d \345\256\236\351\231\205=%0d\n",6, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.check_status", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , 'S',&(vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__15__phase_name)
                     , '#',3,(IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__15__expected_error_code)
                     , '#',3,(7U & __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__15__error_value));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 253, "", false);
    }
    if (VL_UNLIKELY((((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__head_output_valid) 
                      != (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__15__expected_head_valid))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:257: Assertion failed in %m: %s head_output_valid \344\270\215\345\214\271\351\205\215\357\274\232\346\234\237\346\234\233=%b \345\256\236\351\231\205=%b\n",6, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.check_status", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , 'S',&(vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__15__phase_name)
                     , '#',1,(IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__15__expected_head_valid)
                     , '#',1,vlSelfRef.tb_s2a_backend_fault_recovery__DOT__head_output_valid);
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 257, "", false);
    }
    if (VL_UNLIKELY(((((((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__busy) 
                         != (1U & (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__15__expected_status))) 
                        | ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__done) 
                           != (1U & ((IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__15__expected_status) 
                                     >> 1U)))) | ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__error) 
                                                  != 
                                                  (1U 
                                                   & ((IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__15__expected_status) 
                                                      >> 2U)))) 
                      | ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__buffer_owner_pl) 
                         != (1U & ((IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__15__expected_status) 
                                   >> 3U))))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:264: Assertion failed in %m: %s CSR/status \350\276\223\345\207\272\344\270\216\347\212\266\346\200\201\344\275\215\344\270\215\344\270\200\350\207\264\n",4, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.check_status", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , 'S',&(vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__15__phase_name));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 264, "", false);
    }
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__19__value = 2U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__19__address = 0x3cU;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         206);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_write = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__19__address;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_wdata 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__19__value;
    if (VL_UNLIKELY(((1U & (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__csr_ready)))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:207: Assertion failed in %m: CSR \345\206\231\345\205\245\346\234\252 ready\357\274\232addr=%02h\n",4, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.write_csr", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , '#',8,(IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__19__address));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 207, "", false);
    }
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e288__0(vlSelf, 
                                                                         "@(posedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e288__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(posedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         212);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                         nullptr, "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                         213);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         214);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_write = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_wdata = 0U;
    vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__20__phase_name = "ACK \345\220\216"s;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__20__expected_head_valid = 0U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__20__expected_error_code = 0U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__20__expected_status = 0U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__20__status_value = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__20__error_value = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__21__address = 4U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__21__value = 0;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         224);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_write = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__21__address;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_wdata = 0U;
    co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                         nullptr, "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                         229);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__21__value 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_rdata;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         231);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr = 0U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__20__status_value 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__21__value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__22__address = 8U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__22__value = 0;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         224);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_write = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__22__address;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_wdata = 0U;
    co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                         nullptr, "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                         229);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__22__value 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_rdata;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         231);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr = 0U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__20__error_value 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__22__value;
    if (VL_UNLIKELY((((0x0000000fU & __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__20__status_value) 
                      != (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__20__expected_status))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:249: Assertion failed in %m: %s STATUS \344\270\215\345\214\271\351\205\215\357\274\232\346\234\237\346\234\233=%b \345\256\236\351\231\205=%b\n",6, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.check_status", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , 'S',&(vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__20__phase_name)
                     , '#',4,(IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__20__expected_status)
                     , '#',4,(0x0000000fU & __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__20__status_value));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 249, "", false);
    }
    if (VL_UNLIKELY((((7U & __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__20__error_value) 
                      != (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__20__expected_error_code))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:253: Assertion failed in %m: %s ERROR_CODE \344\270\215\345\214\271\351\205\215\357\274\232\346\234\237\346\234\233=%0d \345\256\236\351\231\205=%0d\n",6, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.check_status", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , 'S',&(vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__20__phase_name)
                     , '#',3,(IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__20__expected_error_code)
                     , '#',3,(7U & __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__20__error_value));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 253, "", false);
    }
    if (VL_UNLIKELY((((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__head_output_valid) 
                      != (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__20__expected_head_valid))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:257: Assertion failed in %m: %s head_output_valid \344\270\215\345\214\271\351\205\215\357\274\232\346\234\237\346\234\233=%b \345\256\236\351\231\205=%b\n",6, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.check_status", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , 'S',&(vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__20__phase_name)
                     , '#',1,(IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__20__expected_head_valid)
                     , '#',1,vlSelfRef.tb_s2a_backend_fault_recovery__DOT__head_output_valid);
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 257, "", false);
    }
    if (VL_UNLIKELY(((((((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__busy) 
                         != (1U & (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__20__expected_status))) 
                        | ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__done) 
                           != (1U & ((IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__20__expected_status) 
                                     >> 1U)))) | ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__error) 
                                                  != 
                                                  (1U 
                                                   & ((IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__20__expected_status) 
                                                      >> 2U)))) 
                      | ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__buffer_owner_pl) 
                         != (1U & ((IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__20__expected_status) 
                                   >> 3U))))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:264: Assertion failed in %m: %s CSR/status \350\276\223\345\207\272\344\270\216\347\212\266\346\200\201\344\275\215\344\270\215\344\270\200\350\207\264\n",4, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.check_status", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , 'S',&(vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__20__phase_name));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 264, "", false);
    }
    VL_WRITEF_NX("S2A_FAULT_CASE code=6 mapped=INTERNAL ack_restart=ready\n",0);
    __Vtask_tb_s2a_backend_fault_recovery__DOT__start_transaction__23__timeout_value = 0x00001388U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__24__value 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__start_transaction__23__timeout_value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__24__address = 0x28U;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         206);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_write = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__24__address;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_wdata 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__24__value;
    if (VL_UNLIKELY(((1U & (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__csr_ready)))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:207: Assertion failed in %m: CSR \345\206\231\345\205\245\346\234\252 ready\357\274\232addr=%02h\n",4, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.write_csr", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , '#',8,(IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__24__address));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 207, "", false);
    }
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e288__0(vlSelf, 
                                                                         "@(posedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e288__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(posedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         212);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                         nullptr, "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                         213);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         214);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_write = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_wdata = 0U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__25__value = 1U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__25__address = 0U;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         206);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_write = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__25__address;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_wdata 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__25__value;
    if (VL_UNLIKELY(((1U & (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__csr_ready)))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:207: Assertion failed in %m: CSR \345\206\231\345\205\245\346\234\252 ready\357\274\232addr=%02h\n",4, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.write_csr", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , '#',8,(IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__25__address));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 207, "", false);
    }
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e288__0(vlSelf, 
                                                                         "@(posedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e288__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(posedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         212);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                         nullptr, "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                         213);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         214);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_write = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_wdata = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__transaction_start_cycle 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__simulation_cycle_count;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__inject_read_error__26__response_code = 7U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__inject_read_error__26__reads_before = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__inject_read_error__26__writes_before = 0;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__automatic_read_responses = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__manual_mem_ready = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__manual_mem_error_code = 0U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_read_request__27__wait_index = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_read_request__27__request_found = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_read_request__27__request_found = 0U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_read_request__27__wait_index = 0U;
    if (VL_UNLIKELY(((1U & (((((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__backend_start)) 
                               | (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__busy))) 
                              | (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__buffer_owner_pl))) 
                             | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__done)) 
                            | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__error)))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:296: Assertion failed in %m: CSR \346\234\252\346\216\245\345\217\227\345\220\210\346\263\225 start\357\274\232start=%b busy=%b owner=%b\n",6, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.start_transaction", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , '#',1,(IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__backend_start)
                     , '#',1,vlSelfRef.tb_s2a_backend_fault_recovery__DOT__busy
                     , '#',1,(IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__buffer_owner_pl));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 296, "", false);
    }
    {
        while (VL_GTS_III(32, 0x00000080U, __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_read_request__27__wait_index)) {
            Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                                "@(negedge tb_s2a_backend_fault_recovery.clk)");
            co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                                 nullptr, 
                                                                 "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                                 "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                                 309);
            vlSelfRef.__Vm_traceActivity[3U] = 1U;
            if (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid) {
                __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_read_request__27__request_found = 1U;
                __Vfunc_tb_s2a_backend_fault_recovery__DOT__is_onehot4__28__value 
                    = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_rstrb;
                __Vfunc_tb_s2a_backend_fault_recovery__DOT__is_onehot4__28__Vfuncout = 0;
                __Vfunc_tb_s2a_backend_fault_recovery__DOT__is_onehot4__28__Vfuncout 
                    = ((0U != (IData)(__Vfunc_tb_s2a_backend_fault_recovery__DOT__is_onehot4__28__value)) 
                       & (0U == ((IData)(__Vfunc_tb_s2a_backend_fault_recovery__DOT__is_onehot4__28__value) 
                                 & ((IData)(__Vfunc_tb_s2a_backend_fault_recovery__DOT__is_onehot4__28__value) 
                                    - (IData)(1U)))));
                __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_read_request__27____VlefCall_0__is_onehot4 
                    = __Vfunc_tb_s2a_backend_fault_recovery__DOT__is_onehot4__28__Vfuncout;
                __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__29__Vfuncout = 0;
                __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__29__found = 0;
                __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__29__selected_address = 0;
                __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__29__Vfuncout = 0U;
                __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__29__found = 0U;
                __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__29__selected_address = 0U;
                if ((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_rstrb))) {
                    __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__29__selected_address 
                        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_addr;
                    __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__29__found 
                        = (0x0007ec00U > __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__29__selected_address);
                }
                if ((2U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_rstrb))) {
                    __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__29__selected_address 
                        = ((IData)(1U) + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_addr);
                    __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__29__found 
                        = (0x0007ec00U > __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__29__selected_address);
                }
                if ((4U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_rstrb))) {
                    __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__29__selected_address 
                        = ((IData)(2U) + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_addr);
                    __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__29__found 
                        = (0x0007ec00U > __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__29__selected_address);
                }
                if ((8U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_rstrb))) {
                    __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__29__selected_address 
                        = ((IData)(3U) + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_addr);
                    __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__29__found 
                        = (0x0007ec00U > __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__29__selected_address);
                }
                __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__29__Vfuncout 
                    = __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__29__found;
                __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_read_request__27____VlefCall_1__selected_byte_in_input_tensor 
                    = __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__29__Vfuncout;
                if (VL_UNLIKELY(((1U & (((((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_write) 
                                           | (~ (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_read_request__27____VlefCall_0__is_onehot4))) 
                                          | (0U != 
                                             (((4U 
                                                & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                                                ? (
                                                   ((1U 
                                                     & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                                                     ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_wstrb)
                                                     : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_wstrb)) 
                                                   & (- (IData)(
                                                                (1U 
                                                                 & (~ 
                                                                    ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                                                     >> 1U))))))
                                                : (
                                                   ((1U 
                                                     & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                                                     ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_wstrb)
                                                     : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_wstrb)) 
                                                   & (- (IData)(
                                                                (1U 
                                                                 & ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                                                    >> 1U)))))) 
                                              & (- (IData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid)))))) 
                                         | (0U != (3U 
                                                   & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_addr))) 
                                        | (~ (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_read_request__27____VlefCall_1__selected_byte_in_input_tensor))))))) {
                    VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:314: Assertion failed in %m: backend \351\246\226\344\270\252 feature \350\257\273\350\257\267\346\261\202\344\270\215\345\234\250\350\276\223\345\205\245 tensor \346\210\226 byte lane \351\235\236\346\263\225\357\274\232addr=%08h rstrb=%b\n",5, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.wait_for_read_request", 'T',-9
                                 , '#',64,VL_TIME_UNITED_Q(1000)
                                 , '#',32,vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_addr
                                 , '#',4,(IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_rstrb));
                    VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 314, "", false);
                }
                if (VL_UNLIKELY((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_ready))) {
                    VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:317: Assertion failed in %m: unaccepted request \350\247\202\346\265\213\345\211\215\346\204\217\345\244\226\346\217\241\346\211\213\n",3, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.wait_for_read_request", 'T',-9
                                 , '#',64,VL_TIME_UNITED_Q(1000));
                    VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 317, "", false);
                }
                goto __Vlabel2;
            }
            if (VL_UNLIKELY(((1U & ((((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__busy)) 
                                      | (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__buffer_owner_pl))) 
                                     | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__error)) 
                                    | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__done)))))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:321: Assertion failed in %m: \347\255\211\345\276\205\345\220\210\346\263\225 read request \346\227\266\344\273\273\345\212\241\346\217\220\345\211\215\347\246\273\345\274\200 busy\357\274\232busy=%b error=%b code=%0d\n",6, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.wait_for_read_request", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000)
                             , '#',1,(IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__busy)
                             , '#',1,vlSelfRef.tb_s2a_backend_fault_recovery__DOT__error
                             , '#',3,(IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__error_code));
                VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 321, "", false);
            }
            __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_read_request__27__wait_index 
                = ((IData)(1U) + __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_read_request__27__wait_index);
        }
        __Vlabel2: ;
    }
    if (VL_UNLIKELY(((1U & (~ (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_read_request__27__request_found)))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:325: Assertion failed in %m: backend \346\234\252\345\234\250\351\231\220\345\256\232\345\221\250\346\234\237\345\206\205\345\217\221\345\207\272\347\234\237\345\256\236 read request\n",3, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.wait_for_read_request", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 325, "", false);
    }
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_request__30__saved_address = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_request__30__saved_wdata = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_request__30__saved_rstrb = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_request__30__saved_wstrb = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_request__30__saved_write = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_request__30__stall_index = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_request__30__saved_address 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_addr;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_request__30__saved_wdata 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_wdata;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_request__30__saved_rstrb 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_rstrb;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_request__30__saved_wstrb 
        = (((4U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
             ? (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                  ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_wstrb)
                  : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_wstrb)) 
                & (- (IData)((1U & (~ ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                       >> 1U)))))) : 
            (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
               ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_wstrb)
               : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_wstrb)) 
             & (- (IData)((1U & ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                 >> 1U)))))) & (- (IData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid))));
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_request__30__saved_write 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_write;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_request__30__stall_index = 0U;
    while (VL_GTS_III(32, 3U, __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_request__30__stall_index)) {
        Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e288__0(vlSelf, 
                                                                             "@(posedge tb_s2a_backend_fault_recovery.clk)");
        co_await vlSelfRef.__VtrigSched_h3193e288__0.trigger(0U, 
                                                             nullptr, 
                                                             "@(posedge tb_s2a_backend_fault_recovery.clk)", 
                                                             "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                             343);
        vlSelfRef.__Vm_traceActivity[3U] = 1U;
        co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                             nullptr, 
                                             "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                             344);
        vlSelfRef.__Vm_traceActivity[3U] = 1U;
        if (VL_UNLIKELY(((1U & (((((((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid)) 
                                     | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_ready)) 
                                    | (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_addr 
                                       != __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_request__30__saved_address)) 
                                   | (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_wdata 
                                      != __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_request__30__saved_wdata)) 
                                  | ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_rstrb) 
                                     != (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_request__30__saved_rstrb))) 
                                 | ((((4U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                                       ? (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                                            ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_wstrb)
                                            : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_wstrb)) 
                                          & (- (IData)(
                                                       (1U 
                                                        & (~ 
                                                           ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                                            >> 1U))))))
                                       : (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                                            ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_wstrb)
                                            : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_wstrb)) 
                                          & (- (IData)(
                                                       (1U 
                                                        & ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                                           >> 1U)))))) 
                                     & (- (IData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid)))) 
                                    != (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_request__30__saved_wstrb))) 
                                | ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_write) 
                                   != (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_request__30__saved_write))))))) {
            VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:348: Assertion failed in %m: \346\234\252\346\217\241\346\211\213 memory request \345\255\227\346\256\265\346\234\252\344\277\235\346\214\201\347\250\263\345\256\232\n",3, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.hold_unaccepted_request", 'T',-9
                         , '#',64,VL_TIME_UNITED_Q(1000));
            VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 348, "", false);
        }
        __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_request__30__stall_index 
            = ((IData)(1U) + __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_request__30__stall_index);
    }
    __Vtask_tb_s2a_backend_fault_recovery__DOT__inject_read_error__26__reads_before 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__memory_read_handshakes;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__inject_read_error__26__writes_before 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__memory_write_side_effects;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         381);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__manual_mem_ready = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__manual_mem_error_code 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__inject_read_error__26__response_code;
    co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                         nullptr, "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                         384);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    if (VL_UNLIKELY(((1U & ((((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid)) 
                              | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_write)) 
                             | (~ ((0U != (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__backend_memory_error_code)) 
                                   & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__memory_handshake)))) 
                            | ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__backend_memory_error_code) 
                               != (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__inject_read_error__26__response_code))))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:387: Assertion failed in %m: memory response \346\234\252\347\273\217\347\234\237\345\256\236 backend handshake \344\272\247\347\224\237\351\224\231\350\257\257\344\272\213\344\273\266\357\274\232code=%0d valid=%b\n",5, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.inject_read_error", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , '#',3,(IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__inject_read_error__26__response_code)
                     , '#',1,((0U != (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__backend_memory_error_code)) 
                              & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__memory_handshake)));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 387, "", false);
    }
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e288__0(vlSelf, 
                                                                         "@(posedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e288__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(posedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         390);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                         nullptr, "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                         391);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__manual_mem_ready = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__manual_mem_error_code = 0U;
    if (VL_UNLIKELY(((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__memory_read_handshakes 
                      != ((IData)(1U) + __Vtask_tb_s2a_backend_fault_recovery__DOT__inject_read_error__26__reads_before))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:395: Assertion failed in %m: \346\263\250\345\205\245\351\224\231\350\257\257\350\257\273\346\234\252\346\201\260\345\245\275\346\217\241\346\211\213\344\270\200\346\254\241\357\274\232before=%0d after=%0d\n",5, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.inject_read_error", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , '~',32,__Vtask_tb_s2a_backend_fault_recovery__DOT__inject_read_error__26__reads_before
                     , '~',32,vlSelfRef.tb_s2a_backend_fault_recovery__DOT__memory_read_handshakes);
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 395, "", false);
    }
    if (VL_UNLIKELY(((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__memory_write_side_effects 
                      != __Vtask_tb_s2a_backend_fault_recovery__DOT__inject_read_error__26__writes_before)))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:399: Assertion failed in %m: \345\244\261\350\264\245 read response \344\272\247\347\224\237 output write \345\211\257\344\275\234\347\224\250\n",3, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.inject_read_error", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 399, "", false);
    }
    __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_memory_error__31__wait_index = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_memory_error__31__error_found = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_memory_error__31__error_found = 0U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_memory_error__31__wait_index = 0U;
    {
        while (VL_GTS_III(32, 8U, __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_memory_error__31__wait_index)) {
            Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                                "@(negedge tb_s2a_backend_fault_recovery.clk)");
            co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                                 nullptr, 
                                                                 "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                                 "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                                 360);
            vlSelfRef.__Vm_traceActivity[3U] = 1U;
            if (((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__error) 
                 & (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__busy)))) {
                __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_memory_error__31__error_found = 1U;
                goto __Vlabel3;
            }
            __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_memory_error__31__wait_index 
                = ((IData)(1U) + __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_memory_error__31__wait_index);
        }
        __Vlabel3: ;
    }
    if (VL_UNLIKELY(((1U & (~ (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_memory_error__31__error_found)))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:366: Assertion failed in %m: \347\234\237\345\256\236 memory error response \346\234\252\347\273\210\346\255\242 CSR \344\273\273\345\212\241\n",3, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.wait_for_memory_error", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 366, "", false);
    }
    if (VL_UNLIKELY((((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid) 
                      | ((0U != (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__backend_memory_error_code)) 
                         & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__memory_handshake)))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:403: Assertion failed in %m: \345\244\261\350\264\245 response \345\220\216\344\273\215\346\234\211 memory request/error event\n",3, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.inject_read_error", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 403, "", false);
    }
    vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__32__phase_name = "memory fault"s;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__32__expected_head_valid = 0U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__32__expected_error_code = 6U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__32__expected_status = 4U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__32__status_value = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__32__error_value = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__33__address = 4U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__33__value = 0;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         224);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_write = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__33__address;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_wdata = 0U;
    co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                         nullptr, "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                         229);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__33__value 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_rdata;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         231);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr = 0U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__32__status_value 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__33__value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__34__address = 8U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__34__value = 0;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         224);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_write = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__34__address;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_wdata = 0U;
    co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                         nullptr, "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                         229);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__34__value 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_rdata;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         231);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr = 0U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__32__error_value 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__34__value;
    if (VL_UNLIKELY((((0x0000000fU & __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__32__status_value) 
                      != (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__32__expected_status))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:249: Assertion failed in %m: %s STATUS \344\270\215\345\214\271\351\205\215\357\274\232\346\234\237\346\234\233=%b \345\256\236\351\231\205=%b\n",6, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.check_status", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , 'S',&(vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__32__phase_name)
                     , '#',4,(IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__32__expected_status)
                     , '#',4,(0x0000000fU & __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__32__status_value));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 249, "", false);
    }
    if (VL_UNLIKELY((((7U & __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__32__error_value) 
                      != (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__32__expected_error_code))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:253: Assertion failed in %m: %s ERROR_CODE \344\270\215\345\214\271\351\205\215\357\274\232\346\234\237\346\234\233=%0d \345\256\236\351\231\205=%0d\n",6, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.check_status", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , 'S',&(vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__32__phase_name)
                     , '#',3,(IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__32__expected_error_code)
                     , '#',3,(7U & __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__32__error_value));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 253, "", false);
    }
    if (VL_UNLIKELY((((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__head_output_valid) 
                      != (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__32__expected_head_valid))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:257: Assertion failed in %m: %s head_output_valid \344\270\215\345\214\271\351\205\215\357\274\232\346\234\237\346\234\233=%b \345\256\236\351\231\205=%b\n",6, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.check_status", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , 'S',&(vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__32__phase_name)
                     , '#',1,(IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__32__expected_head_valid)
                     , '#',1,vlSelfRef.tb_s2a_backend_fault_recovery__DOT__head_output_valid);
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 257, "", false);
    }
    if (VL_UNLIKELY(((((((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__busy) 
                         != (1U & (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__32__expected_status))) 
                        | ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__done) 
                           != (1U & ((IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__32__expected_status) 
                                     >> 1U)))) | ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__error) 
                                                  != 
                                                  (1U 
                                                   & ((IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__32__expected_status) 
                                                      >> 2U)))) 
                      | ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__buffer_owner_pl) 
                         != (1U & ((IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__32__expected_status) 
                                   >> 3U))))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:264: Assertion failed in %m: %s CSR/status \350\276\223\345\207\272\344\270\216\347\212\266\346\200\201\344\275\215\344\270\215\344\270\200\350\207\264\n",4, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.check_status", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , 'S',&(vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__32__phase_name));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 264, "", false);
    }
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__36__value = 2U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__36__address = 0x3cU;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         206);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_write = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__36__address;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_wdata 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__36__value;
    if (VL_UNLIKELY(((1U & (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__csr_ready)))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:207: Assertion failed in %m: CSR \345\206\231\345\205\245\346\234\252 ready\357\274\232addr=%02h\n",4, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.write_csr", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , '#',8,(IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__36__address));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 207, "", false);
    }
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e288__0(vlSelf, 
                                                                         "@(posedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e288__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(posedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         212);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                         nullptr, "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                         213);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         214);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_write = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_wdata = 0U;
    vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__37__phase_name = "ACK \345\220\216"s;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__37__expected_head_valid = 0U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__37__expected_error_code = 0U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__37__expected_status = 0U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__37__status_value = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__37__error_value = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__38__address = 4U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__38__value = 0;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         224);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_write = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__38__address;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_wdata = 0U;
    co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                         nullptr, "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                         229);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__38__value 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_rdata;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         231);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr = 0U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__37__status_value 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__38__value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__39__address = 8U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__39__value = 0;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         224);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_write = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__39__address;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_wdata = 0U;
    co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                         nullptr, "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                         229);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__39__value 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_rdata;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         231);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr = 0U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__37__error_value 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__39__value;
    if (VL_UNLIKELY((((0x0000000fU & __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__37__status_value) 
                      != (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__37__expected_status))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:249: Assertion failed in %m: %s STATUS \344\270\215\345\214\271\351\205\215\357\274\232\346\234\237\346\234\233=%b \345\256\236\351\231\205=%b\n",6, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.check_status", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , 'S',&(vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__37__phase_name)
                     , '#',4,(IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__37__expected_status)
                     , '#',4,(0x0000000fU & __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__37__status_value));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 249, "", false);
    }
    if (VL_UNLIKELY((((7U & __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__37__error_value) 
                      != (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__37__expected_error_code))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:253: Assertion failed in %m: %s ERROR_CODE \344\270\215\345\214\271\351\205\215\357\274\232\346\234\237\346\234\233=%0d \345\256\236\351\231\205=%0d\n",6, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.check_status", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , 'S',&(vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__37__phase_name)
                     , '#',3,(IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__37__expected_error_code)
                     , '#',3,(7U & __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__37__error_value));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 253, "", false);
    }
    if (VL_UNLIKELY((((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__head_output_valid) 
                      != (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__37__expected_head_valid))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:257: Assertion failed in %m: %s head_output_valid \344\270\215\345\214\271\351\205\215\357\274\232\346\234\237\346\234\233=%b \345\256\236\351\231\205=%b\n",6, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.check_status", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , 'S',&(vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__37__phase_name)
                     , '#',1,(IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__37__expected_head_valid)
                     , '#',1,vlSelfRef.tb_s2a_backend_fault_recovery__DOT__head_output_valid);
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 257, "", false);
    }
    if (VL_UNLIKELY(((((((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__busy) 
                         != (1U & (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__37__expected_status))) 
                        | ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__done) 
                           != (1U & ((IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__37__expected_status) 
                                     >> 1U)))) | ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__error) 
                                                  != 
                                                  (1U 
                                                   & ((IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__37__expected_status) 
                                                      >> 2U)))) 
                      | ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__buffer_owner_pl) 
                         != (1U & ((IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__37__expected_status) 
                                   >> 3U))))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:264: Assertion failed in %m: %s CSR/status \350\276\223\345\207\272\344\270\216\347\212\266\346\200\201\344\275\215\344\270\215\344\270\200\350\207\264\n",4, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.check_status", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , 'S',&(vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__37__phase_name));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 264, "", false);
    }
    VL_WRITEF_NX("S2A_FAULT_CASE code=7 mapped=INTERNAL ack_restart=ready\n",0);
    __Vtask_tb_s2a_backend_fault_recovery__DOT__cancel_output_write_with_soft_reset__40__reads_before = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__cancel_output_write_with_soft_reset__40__writes_before = 0;
    vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__prepare_unaccepted_output_write__41__case_name = "soft_reset"s;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__prepare_unaccepted_output_write__41__reads_before = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__prepare_unaccepted_output_write__41__writes_before = 0;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__manual_mem_ready = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__manual_mem_error_code = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__automatic_read_responses = 1U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__prepare_unaccepted_output_write__41__reads_before 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__memory_read_handshakes;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__prepare_unaccepted_output_write__41__writes_before 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__memory_write_side_effects;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__start_transaction__42__timeout_value = 0x000186a0U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__43__value 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__start_transaction__42__timeout_value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__43__address = 0x28U;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         206);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_write = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__43__address;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_wdata 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__43__value;
    if (VL_UNLIKELY(((1U & (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__csr_ready)))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:207: Assertion failed in %m: CSR \345\206\231\345\205\245\346\234\252 ready\357\274\232addr=%02h\n",4, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.write_csr", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , '#',8,(IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__43__address));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 207, "", false);
    }
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e288__0(vlSelf, 
                                                                         "@(posedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e288__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(posedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         212);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                         nullptr, "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                         213);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         214);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_write = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_wdata = 0U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__44__value = 1U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__44__address = 0U;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         206);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_write = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__44__address;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_wdata 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__44__value;
    if (VL_UNLIKELY(((1U & (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__csr_ready)))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:207: Assertion failed in %m: CSR \345\206\231\345\205\245\346\234\252 ready\357\274\232addr=%02h\n",4, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.write_csr", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , '#',8,(IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__44__address));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 207, "", false);
    }
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e288__0(vlSelf, 
                                                                         "@(posedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e288__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(posedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         212);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                         nullptr, "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                         213);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         214);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_write = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_wdata = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__transaction_start_cycle 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__simulation_cycle_count;
    vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__45__case_name 
        = vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__prepare_unaccepted_output_write__41__case_name;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__45__wait_index = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__45__request_found = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__45__request_found = 0U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__45__wait_index = 0U;
    if (VL_UNLIKELY(((1U & (((((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__backend_start)) 
                               | (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__busy))) 
                              | (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__buffer_owner_pl))) 
                             | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__done)) 
                            | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__error)))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:296: Assertion failed in %m: CSR \346\234\252\346\216\245\345\217\227\345\220\210\346\263\225 start\357\274\232start=%b busy=%b owner=%b\n",6, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.start_transaction", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , '#',1,(IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__backend_start)
                     , '#',1,vlSelfRef.tb_s2a_backend_fault_recovery__DOT__busy
                     , '#',1,(IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__buffer_owner_pl));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 296, "", false);
    }
    {
        while (VL_GTS_III(32, 0x00004e20U, __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__45__wait_index)) {
            Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                                "@(negedge tb_s2a_backend_fault_recovery.clk)");
            co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                                 nullptr, 
                                                                 "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                                 "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                                 445);
            vlSelfRef.__Vm_traceActivity[3U] = 1U;
            if (VL_UNLIKELY((((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid) 
                              & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_write))))) {
                __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__45__request_found = 1U;
                __Vfunc_tb_s2a_backend_fault_recovery__DOT__is_onehot4__46__value 
                    = (((4U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                         ? (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                              ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_wstrb)
                              : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_wstrb)) 
                            & (- (IData)((1U & (~ ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                                   >> 1U))))))
                         : (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                              ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_wstrb)
                              : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_wstrb)) 
                            & (- (IData)((1U & ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                                >> 1U)))))) 
                       & (- (IData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid))));
                __Vfunc_tb_s2a_backend_fault_recovery__DOT__is_onehot4__46__Vfuncout = 0;
                __Vfunc_tb_s2a_backend_fault_recovery__DOT__is_onehot4__46__Vfuncout 
                    = ((0U != (IData)(__Vfunc_tb_s2a_backend_fault_recovery__DOT__is_onehot4__46__value)) 
                       & (0U == ((IData)(__Vfunc_tb_s2a_backend_fault_recovery__DOT__is_onehot4__46__value) 
                                 & ((IData)(__Vfunc_tb_s2a_backend_fault_recovery__DOT__is_onehot4__46__value) 
                                    - (IData)(1U)))));
                __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__45____VlefCall_0__is_onehot4 
                    = __Vfunc_tb_s2a_backend_fault_recovery__DOT__is_onehot4__46__Vfuncout;
                __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__47__Vfuncout = 0;
                __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__47__found = 0;
                __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__47__selected_address = 0;
                __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__47__Vfuncout = 0U;
                __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__47__found = 0U;
                __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__47__selected_address = 0U;
                if ((((4U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                       ? (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                            ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_wstrb)
                            : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_wstrb)) 
                          & (- (IData)((1U & (~ ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                                 >> 1U))))))
                       : (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                            ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_wstrb)
                            : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_wstrb)) 
                          & (- (IData)((1U & ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                              >> 1U)))))) 
                     & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid))) {
                    __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__47__selected_address 
                        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_addr;
                    __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__47__found 
                        = ((0x01000000U <= __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__47__selected_address) 
                           & (0x01152000U > __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__47__selected_address));
                }
                if (((((4U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                        ? (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                             ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_wstrb)
                             : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_wstrb)) 
                           & (- (IData)((1U & (~ ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                                  >> 1U))))))
                        : (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                             ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_wstrb)
                             : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_wstrb)) 
                           & (- (IData)((1U & ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                               >> 1U)))))) 
                      >> 1U) & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid))) {
                    __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__47__selected_address 
                        = ((IData)(1U) + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_addr);
                    __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__47__found 
                        = ((0x01000000U <= __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__47__selected_address) 
                           & (0x01152000U > __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__47__selected_address));
                }
                if (((((4U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                        ? (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                             ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_wstrb)
                             : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_wstrb)) 
                           & (- (IData)((1U & (~ ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                                  >> 1U))))))
                        : (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                             ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_wstrb)
                             : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_wstrb)) 
                           & (- (IData)((1U & ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                               >> 1U)))))) 
                      >> 2U) & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid))) {
                    __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__47__selected_address 
                        = ((IData)(2U) + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_addr);
                    __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__47__found 
                        = ((0x01000000U <= __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__47__selected_address) 
                           & (0x01152000U > __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__47__selected_address));
                }
                if (((((4U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                        ? (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                             ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_wstrb)
                             : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_wstrb)) 
                           & (- (IData)((1U & (~ ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                                  >> 1U))))))
                        : (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                             ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_wstrb)
                             : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_wstrb)) 
                           & (- (IData)((1U & ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                               >> 1U)))))) 
                      >> 3U) & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid))) {
                    __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__47__selected_address 
                        = ((IData)(3U) + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_addr);
                    __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__47__found 
                        = ((0x01000000U <= __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__47__selected_address) 
                           & (0x01152000U > __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__47__selected_address));
                }
                __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__47__Vfuncout 
                    = __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__47__found;
                __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__45____VlefCall_1__selected_byte_in_layer0_output_tensor 
                    = __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__47__Vfuncout;
                if (VL_UNLIKELY(((1U & ((((((((((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_ready) 
                                                | (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__busy))) 
                                               | (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__buffer_owner_pl))) 
                                              | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__done)) 
                                             | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__error)) 
                                            | (0U != (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))) 
                                           | (~ (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__45____VlefCall_0__is_onehot4))) 
                                          | (0U != (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_rstrb))) 
                                         | (0U != (3U 
                                                   & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_addr))) 
                                        | (~ (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__45____VlefCall_1__selected_byte_in_layer0_output_tensor))))))) {
                    VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:452: Assertion failed in %m: layer0 \351\246\226\347\254\224 output write \350\257\267\346\261\202\344\270\215\345\220\210\346\263\225\357\274\232addr=%08h wstrb=%b ready=%b layer=%0d\n",7, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.wait_for_first_output_write", 'T',-9
                                 , '#',64,VL_TIME_UNITED_Q(1000)
                                 , '#',32,vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_addr
                                 , '#',4,(((4U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                                            ? (((1U 
                                                 & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                                                 ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_wstrb)
                                                 : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_wstrb)) 
                                               & (- (IData)(
                                                            (1U 
                                                             & (~ 
                                                                ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                                                 >> 1U))))))
                                            : (((1U 
                                                 & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                                                 ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_wstrb)
                                                 : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_wstrb)) 
                                               & (- (IData)(
                                                            (1U 
                                                             & ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                                                >> 1U)))))) 
                                          & (- (IData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid))))
                                 , '#',1,(IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_ready)
                                 , '#',6,vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor);
                    VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 452, "", false);
                }
                VL_WRITEF_NX("S2A_PENDING_OUTPUT_WRITE case=%s layer=0 cycles_from_start=%0d reads=%0d addr=%08h wstrb=%b\n",5
                             , 'S',&(vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__45__case_name)
                             , '#',32,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__simulation_cycle_count 
                                       - vlSelfRef.tb_s2a_backend_fault_recovery__DOT__transaction_start_cycle)
                             , '~',32,vlSelfRef.tb_s2a_backend_fault_recovery__DOT__memory_read_handshakes
                             , '#',32,vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_addr
                             , '#',4,(((4U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                                        ? (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                                             ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_wstrb)
                                             : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_wstrb)) 
                                           & (- (IData)(
                                                        (1U 
                                                         & (~ 
                                                            ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                                             >> 1U))))))
                                        : (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                                             ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_wstrb)
                                             : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_wstrb)) 
                                           & (- (IData)(
                                                        (1U 
                                                         & ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                                            >> 1U)))))) 
                                      & (- (IData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid)))));
                goto __Vlabel4;
            }
            if (VL_UNLIKELY(((1U & ((((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__busy)) 
                                      | (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__buffer_owner_pl))) 
                                     | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__error)) 
                                    | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__done)))))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:461: Assertion failed in %m: \347\255\211\345\276\205 layer0 output write \346\227\266\344\273\273\345\212\241\346\217\220\345\211\215\347\246\273\345\274\200 busy\357\274\232busy=%b error=%b code=%0d\n",6, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.wait_for_first_output_write", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000)
                             , '#',1,(IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__busy)
                             , '#',1,vlSelfRef.tb_s2a_backend_fault_recovery__DOT__error
                             , '#',3,(IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__error_code));
                VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 461, "", false);
            }
            __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__45__wait_index 
                = ((IData)(1U) + __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__45__wait_index);
        }
        __Vlabel4: ;
    }
    if (VL_UNLIKELY(((1U & (~ (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__45__request_found)))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:466: Assertion failed in %m: layer0 \346\234\252\345\234\250 20000 cycles \345\206\205\344\272\247\347\224\237\351\246\226\347\254\224 output write\n",3, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.wait_for_first_output_write", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 466, "", false);
    }
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_output_write__48__saved_address = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_output_write__48__saved_wdata = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_output_write__48__saved_wstrb = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_output_write__48__stall_index = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_output_write__48__saved_address 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_addr;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_output_write__48__saved_wdata 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_wdata;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_output_write__48__saved_wstrb 
        = (((4U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
             ? (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                  ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_wstrb)
                  : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_wstrb)) 
                & (- (IData)((1U & (~ ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                       >> 1U)))))) : 
            (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
               ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_wstrb)
               : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_wstrb)) 
             & (- (IData)((1U & ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                 >> 1U)))))) & (- (IData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid))));
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_output_write__48__stall_index = 0U;
    while (VL_GTS_III(32, 3U, __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_output_write__48__stall_index)) {
        Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e288__0(vlSelf, 
                                                                             "@(posedge tb_s2a_backend_fault_recovery.clk)");
        co_await vlSelfRef.__VtrigSched_h3193e288__0.trigger(0U, 
                                                             nullptr, 
                                                             "@(posedge tb_s2a_backend_fault_recovery.clk)", 
                                                             "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                             481);
        vlSelfRef.__Vm_traceActivity[3U] = 1U;
        co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                             nullptr, 
                                             "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                             482);
        vlSelfRef.__Vm_traceActivity[3U] = 1U;
        if (VL_UNLIKELY(((1U & (((((((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid)) 
                                     | (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_write))) 
                                    | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_ready)) 
                                   | (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_addr 
                                      != __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_output_write__48__saved_address)) 
                                  | (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_wdata 
                                     != __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_output_write__48__saved_wdata)) 
                                 | ((((4U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                                       ? (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                                            ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_wstrb)
                                            : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_wstrb)) 
                                          & (- (IData)(
                                                       (1U 
                                                        & (~ 
                                                           ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                                            >> 1U))))))
                                       : (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                                            ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_wstrb)
                                            : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_wstrb)) 
                                          & (- (IData)(
                                                       (1U 
                                                        & ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                                           >> 1U)))))) 
                                     & (- (IData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid)))) 
                                    != (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_output_write__48__saved_wstrb))) 
                                | (0U != (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_rstrb))))))) {
            VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:486: Assertion failed in %m: \346\234\252\346\217\241\346\211\213 layer0 output write \345\255\227\346\256\265\346\234\252\344\277\235\346\214\201\347\250\263\345\256\232\n",3, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.hold_unaccepted_output_write", 'T',-9
                         , '#',64,VL_TIME_UNITED_Q(1000));
            VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 486, "", false);
        }
        __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_output_write__48__stall_index 
            = ((IData)(1U) + __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_output_write__48__stall_index);
    }
    if (VL_UNLIKELY(((VL_LTES_III(32, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__memory_read_handshakes, __Vtask_tb_s2a_backend_fault_recovery__DOT__prepare_unaccepted_output_write__41__reads_before) 
                      | (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__memory_write_side_effects 
                         != __Vtask_tb_s2a_backend_fault_recovery__DOT__prepare_unaccepted_output_write__41__writes_before))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:506: Assertion failed in %m: \345\210\260\350\276\276\351\246\226\347\254\224\346\234\252\346\217\241\346\211\213 output write \345\211\215\345\220\216\350\257\273\345\206\231\350\256\241\346\225\260\345\274\202\345\270\270\n",3, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.prepare_unaccepted_output_write", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 506, "", false);
    }
    if (VL_UNLIKELY((("hard_reset"s == vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__prepare_unaccepted_output_write__41__case_name)))) {
        VL_WRITEF_NX("S2A_RETRY_CASE after=soft_reset request=pending_output_write next=hard_reset start_accepted=1\n",0);
    } else if (VL_UNLIKELY((("csr_timeout"s == vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__prepare_unaccepted_output_write__41__case_name)))) {
        VL_WRITEF_NX("S2A_RETRY_CASE after=hard_reset request=pending_output_write next=csr_timeout start_accepted=1\n",0);
    }
    __Vtask_tb_s2a_backend_fault_recovery__DOT__cancel_output_write_with_soft_reset__40__reads_before 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__memory_read_handshakes;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__cancel_output_write_with_soft_reset__40__writes_before 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__memory_write_side_effects;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__49__value = 2U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__49__address = 0U;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         206);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_write = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__49__address;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_wdata 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__49__value;
    if (VL_UNLIKELY(((1U & (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__csr_ready)))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:207: Assertion failed in %m: CSR \345\206\231\345\205\245\346\234\252 ready\357\274\232addr=%02h\n",4, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.write_csr", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , '#',8,(IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__49__address));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 207, "", false);
    }
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e288__0(vlSelf, 
                                                                         "@(posedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e288__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(posedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         212);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                         nullptr, "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                         213);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         214);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_write = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_wdata = 0U;
    if (VL_UNLIKELY(((1U & ((((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__backend_abort)) 
                              | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid)) 
                             | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__buffer_owner_pl)) 
                            | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__busy)))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:525: Assertion failed in %m: soft_reset \346\234\252\346\222\244\351\224\200\346\234\252\346\217\241\346\211\213 output write \346\210\226\351\207\212\346\224\276 ownership\n",3, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.cancel_output_write_with_soft_reset", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 525, "", false);
    }
    vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__50__phase_name = "soft_reset \345\220\216"s;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__50__expected_head_valid = 0U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__50__expected_error_code = 0U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__50__expected_status = 0U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__50__status_value = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__50__error_value = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__51__address = 4U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__51__value = 0;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         224);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_write = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__51__address;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_wdata = 0U;
    co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                         nullptr, "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                         229);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__51__value 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_rdata;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         231);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr = 0U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__50__status_value 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__51__value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__52__address = 8U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__52__value = 0;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         224);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_write = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__52__address;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_wdata = 0U;
    co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                         nullptr, "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                         229);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__52__value 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_rdata;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         231);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr = 0U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__50__error_value 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__52__value;
    if (VL_UNLIKELY((((0x0000000fU & __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__50__status_value) 
                      != (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__50__expected_status))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:249: Assertion failed in %m: %s STATUS \344\270\215\345\214\271\351\205\215\357\274\232\346\234\237\346\234\233=%b \345\256\236\351\231\205=%b\n",6, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.check_status", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , 'S',&(vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__50__phase_name)
                     , '#',4,(IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__50__expected_status)
                     , '#',4,(0x0000000fU & __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__50__status_value));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 249, "", false);
    }
    if (VL_UNLIKELY((((7U & __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__50__error_value) 
                      != (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__50__expected_error_code))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:253: Assertion failed in %m: %s ERROR_CODE \344\270\215\345\214\271\351\205\215\357\274\232\346\234\237\346\234\233=%0d \345\256\236\351\231\205=%0d\n",6, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.check_status", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , 'S',&(vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__50__phase_name)
                     , '#',3,(IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__50__expected_error_code)
                     , '#',3,(7U & __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__50__error_value));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 253, "", false);
    }
    if (VL_UNLIKELY((((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__head_output_valid) 
                      != (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__50__expected_head_valid))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:257: Assertion failed in %m: %s head_output_valid \344\270\215\345\214\271\351\205\215\357\274\232\346\234\237\346\234\233=%b \345\256\236\351\231\205=%b\n",6, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.check_status", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , 'S',&(vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__50__phase_name)
                     , '#',1,(IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__50__expected_head_valid)
                     , '#',1,vlSelfRef.tb_s2a_backend_fault_recovery__DOT__head_output_valid);
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 257, "", false);
    }
    if (VL_UNLIKELY(((((((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__busy) 
                         != (1U & (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__50__expected_status))) 
                        | ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__done) 
                           != (1U & ((IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__50__expected_status) 
                                     >> 1U)))) | ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__error) 
                                                  != 
                                                  (1U 
                                                   & ((IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__50__expected_status) 
                                                      >> 2U)))) 
                      | ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__buffer_owner_pl) 
                         != (1U & ((IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__50__expected_status) 
                                   >> 3U))))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:264: Assertion failed in %m: %s CSR/status \350\276\223\345\207\272\344\270\216\347\212\266\346\200\201\344\275\215\344\270\215\344\270\200\350\207\264\n",4, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.check_status", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , 'S',&(vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__50__phase_name));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 264, "", false);
    }
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_no_late_effects__53__writes_before 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__cancel_output_write_with_soft_reset__40__writes_before;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_no_late_effects__53__reads_before 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__cancel_output_write_with_soft_reset__40__reads_before;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_no_late_effects__53__quiet_index = 0;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         419);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__automatic_read_responses = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__manual_mem_error_code = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__manual_mem_ready = 1U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_no_late_effects__53__quiet_index = 0U;
    while (VL_GTS_III(32, 3U, __Vtask_tb_s2a_backend_fault_recovery__DOT__check_no_late_effects__53__quiet_index)) {
        Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e288__0(vlSelf, 
                                                                             "@(posedge tb_s2a_backend_fault_recovery.clk)");
        co_await vlSelfRef.__VtrigSched_h3193e288__0.trigger(0U, 
                                                             nullptr, 
                                                             "@(posedge tb_s2a_backend_fault_recovery.clk)", 
                                                             "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                             424);
        vlSelfRef.__Vm_traceActivity[3U] = 1U;
        co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                             nullptr, 
                                             "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                             425);
        vlSelfRef.__Vm_traceActivity[3U] = 1U;
        if (VL_UNLIKELY(((((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid) 
                           | ((0U != (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__backend_memory_error_code)) 
                              & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__memory_handshake))) 
                          | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_write))))) {
            VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:427: Assertion failed in %m: \345\217\226\346\266\210\345\220\216\345\207\272\347\216\260\350\277\237\345\210\260\350\257\267\346\261\202\346\210\226 memory error event\n",3, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.check_no_late_effects", 'T',-9
                         , '#',64,VL_TIME_UNITED_Q(1000));
            VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 427, "", false);
        }
        if (VL_UNLIKELY((((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__memory_read_handshakes 
                           != __Vtask_tb_s2a_backend_fault_recovery__DOT__check_no_late_effects__53__reads_before) 
                          | (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__memory_write_side_effects 
                             != __Vtask_tb_s2a_backend_fault_recovery__DOT__check_no_late_effects__53__writes_before))))) {
            VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:431: Assertion failed in %m: \345\217\226\346\266\210\345\220\216\345\207\272\347\216\260\350\277\237\345\210\260 read/write memory \345\211\257\344\275\234\347\224\250\n",3, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.check_no_late_effects", 'T',-9
                         , '#',64,VL_TIME_UNITED_Q(1000));
            VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 431, "", false);
        }
        __Vtask_tb_s2a_backend_fault_recovery__DOT__check_no_late_effects__53__quiet_index 
            = ((IData)(1U) + __Vtask_tb_s2a_backend_fault_recovery__DOT__check_no_late_effects__53__quiet_index);
    }
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         434);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__manual_mem_ready = 0U;
    if (VL_UNLIKELY(((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__memory_write_side_effects 
                      != __Vtask_tb_s2a_backend_fault_recovery__DOT__cancel_output_write_with_soft_reset__40__writes_before)))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:530: Assertion failed in %m: soft_reset \345\220\216\345\207\272\347\216\260\350\277\237\345\210\260 output write \345\211\257\344\275\234\347\224\250\n",3, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.cancel_output_write_with_soft_reset", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 530, "", false);
    }
    VL_WRITEF_NX("S2A_OUTPUT_WRITE_CANCEL kind=soft_reset layer=0 writes_before=%0d writes_after=%0d\nS2A_CANCEL_CASE kind=soft_reset request=pending_output_write cancelled=1 writes_before=%0d writes_after=%0d\n",4
                 , '~',32,__Vtask_tb_s2a_backend_fault_recovery__DOT__cancel_output_write_with_soft_reset__40__writes_before
                 , '~',32,vlSelfRef.tb_s2a_backend_fault_recovery__DOT__memory_write_side_effects
                 , '~',32,__Vtask_tb_s2a_backend_fault_recovery__DOT__cancel_output_write_with_soft_reset__40__writes_before
                 , '~',32,vlSelfRef.tb_s2a_backend_fault_recovery__DOT__memory_write_side_effects);
    __Vtask_tb_s2a_backend_fault_recovery__DOT__cancel_output_write_with_hard_reset__54__tb_s2a_backend_fault_recovery__DOT__unnamedblk1_2__DOT____Vrepeat1 = 0U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__cancel_output_write_with_hard_reset__54__reads_before = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__cancel_output_write_with_hard_reset__54__writes_before = 0;
    vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__prepare_unaccepted_output_write__55__case_name = "hard_reset"s;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__prepare_unaccepted_output_write__55__reads_before = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__prepare_unaccepted_output_write__55__writes_before = 0;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__manual_mem_ready = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__manual_mem_error_code = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__automatic_read_responses = 1U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__prepare_unaccepted_output_write__55__reads_before 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__memory_read_handshakes;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__prepare_unaccepted_output_write__55__writes_before 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__memory_write_side_effects;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__start_transaction__56__timeout_value = 0x000186a0U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__57__value 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__start_transaction__56__timeout_value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__57__address = 0x28U;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         206);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_write = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__57__address;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_wdata 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__57__value;
    if (VL_UNLIKELY(((1U & (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__csr_ready)))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:207: Assertion failed in %m: CSR \345\206\231\345\205\245\346\234\252 ready\357\274\232addr=%02h\n",4, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.write_csr", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , '#',8,(IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__57__address));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 207, "", false);
    }
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e288__0(vlSelf, 
                                                                         "@(posedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e288__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(posedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         212);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                         nullptr, "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                         213);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         214);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_write = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_wdata = 0U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__58__value = 1U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__58__address = 0U;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         206);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_write = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__58__address;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_wdata 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__58__value;
    if (VL_UNLIKELY(((1U & (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__csr_ready)))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:207: Assertion failed in %m: CSR \345\206\231\345\205\245\346\234\252 ready\357\274\232addr=%02h\n",4, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.write_csr", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , '#',8,(IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__58__address));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 207, "", false);
    }
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e288__0(vlSelf, 
                                                                         "@(posedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e288__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(posedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         212);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                         nullptr, "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                         213);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         214);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_write = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_wdata = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__transaction_start_cycle 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__simulation_cycle_count;
    vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__59__case_name 
        = vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__prepare_unaccepted_output_write__55__case_name;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__59__wait_index = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__59__request_found = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__59__request_found = 0U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__59__wait_index = 0U;
    if (VL_UNLIKELY(((1U & (((((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__backend_start)) 
                               | (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__busy))) 
                              | (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__buffer_owner_pl))) 
                             | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__done)) 
                            | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__error)))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:296: Assertion failed in %m: CSR \346\234\252\346\216\245\345\217\227\345\220\210\346\263\225 start\357\274\232start=%b busy=%b owner=%b\n",6, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.start_transaction", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , '#',1,(IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__backend_start)
                     , '#',1,vlSelfRef.tb_s2a_backend_fault_recovery__DOT__busy
                     , '#',1,(IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__buffer_owner_pl));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 296, "", false);
    }
    {
        while (VL_GTS_III(32, 0x00004e20U, __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__59__wait_index)) {
            Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                                "@(negedge tb_s2a_backend_fault_recovery.clk)");
            co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                                 nullptr, 
                                                                 "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                                 "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                                 445);
            vlSelfRef.__Vm_traceActivity[3U] = 1U;
            if (VL_UNLIKELY((((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid) 
                              & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_write))))) {
                __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__59__request_found = 1U;
                __Vfunc_tb_s2a_backend_fault_recovery__DOT__is_onehot4__60__value 
                    = (((4U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                         ? (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                              ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_wstrb)
                              : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_wstrb)) 
                            & (- (IData)((1U & (~ ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                                   >> 1U))))))
                         : (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                              ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_wstrb)
                              : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_wstrb)) 
                            & (- (IData)((1U & ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                                >> 1U)))))) 
                       & (- (IData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid))));
                __Vfunc_tb_s2a_backend_fault_recovery__DOT__is_onehot4__60__Vfuncout = 0;
                __Vfunc_tb_s2a_backend_fault_recovery__DOT__is_onehot4__60__Vfuncout 
                    = ((0U != (IData)(__Vfunc_tb_s2a_backend_fault_recovery__DOT__is_onehot4__60__value)) 
                       & (0U == ((IData)(__Vfunc_tb_s2a_backend_fault_recovery__DOT__is_onehot4__60__value) 
                                 & ((IData)(__Vfunc_tb_s2a_backend_fault_recovery__DOT__is_onehot4__60__value) 
                                    - (IData)(1U)))));
                __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__59____VlefCall_0__is_onehot4 
                    = __Vfunc_tb_s2a_backend_fault_recovery__DOT__is_onehot4__60__Vfuncout;
                __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__61__Vfuncout = 0;
                __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__61__found = 0;
                __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__61__selected_address = 0;
                __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__61__Vfuncout = 0U;
                __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__61__found = 0U;
                __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__61__selected_address = 0U;
                if ((((4U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                       ? (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                            ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_wstrb)
                            : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_wstrb)) 
                          & (- (IData)((1U & (~ ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                                 >> 1U))))))
                       : (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                            ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_wstrb)
                            : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_wstrb)) 
                          & (- (IData)((1U & ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                              >> 1U)))))) 
                     & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid))) {
                    __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__61__selected_address 
                        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_addr;
                    __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__61__found 
                        = ((0x01000000U <= __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__61__selected_address) 
                           & (0x01152000U > __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__61__selected_address));
                }
                if (((((4U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                        ? (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                             ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_wstrb)
                             : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_wstrb)) 
                           & (- (IData)((1U & (~ ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                                  >> 1U))))))
                        : (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                             ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_wstrb)
                             : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_wstrb)) 
                           & (- (IData)((1U & ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                               >> 1U)))))) 
                      >> 1U) & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid))) {
                    __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__61__selected_address 
                        = ((IData)(1U) + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_addr);
                    __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__61__found 
                        = ((0x01000000U <= __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__61__selected_address) 
                           & (0x01152000U > __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__61__selected_address));
                }
                if (((((4U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                        ? (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                             ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_wstrb)
                             : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_wstrb)) 
                           & (- (IData)((1U & (~ ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                                  >> 1U))))))
                        : (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                             ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_wstrb)
                             : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_wstrb)) 
                           & (- (IData)((1U & ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                               >> 1U)))))) 
                      >> 2U) & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid))) {
                    __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__61__selected_address 
                        = ((IData)(2U) + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_addr);
                    __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__61__found 
                        = ((0x01000000U <= __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__61__selected_address) 
                           & (0x01152000U > __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__61__selected_address));
                }
                if (((((4U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                        ? (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                             ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_wstrb)
                             : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_wstrb)) 
                           & (- (IData)((1U & (~ ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                                  >> 1U))))))
                        : (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                             ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_wstrb)
                             : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_wstrb)) 
                           & (- (IData)((1U & ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                               >> 1U)))))) 
                      >> 3U) & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid))) {
                    __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__61__selected_address 
                        = ((IData)(3U) + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_addr);
                    __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__61__found 
                        = ((0x01000000U <= __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__61__selected_address) 
                           & (0x01152000U > __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__61__selected_address));
                }
                __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__61__Vfuncout 
                    = __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__61__found;
                __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__59____VlefCall_1__selected_byte_in_layer0_output_tensor 
                    = __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__61__Vfuncout;
                if (VL_UNLIKELY(((1U & ((((((((((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_ready) 
                                                | (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__busy))) 
                                               | (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__buffer_owner_pl))) 
                                              | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__done)) 
                                             | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__error)) 
                                            | (0U != (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))) 
                                           | (~ (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__59____VlefCall_0__is_onehot4))) 
                                          | (0U != (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_rstrb))) 
                                         | (0U != (3U 
                                                   & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_addr))) 
                                        | (~ (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__59____VlefCall_1__selected_byte_in_layer0_output_tensor))))))) {
                    VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:452: Assertion failed in %m: layer0 \351\246\226\347\254\224 output write \350\257\267\346\261\202\344\270\215\345\220\210\346\263\225\357\274\232addr=%08h wstrb=%b ready=%b layer=%0d\n",7, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.wait_for_first_output_write", 'T',-9
                                 , '#',64,VL_TIME_UNITED_Q(1000)
                                 , '#',32,vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_addr
                                 , '#',4,(((4U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                                            ? (((1U 
                                                 & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                                                 ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_wstrb)
                                                 : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_wstrb)) 
                                               & (- (IData)(
                                                            (1U 
                                                             & (~ 
                                                                ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                                                 >> 1U))))))
                                            : (((1U 
                                                 & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                                                 ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_wstrb)
                                                 : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_wstrb)) 
                                               & (- (IData)(
                                                            (1U 
                                                             & ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                                                >> 1U)))))) 
                                          & (- (IData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid))))
                                 , '#',1,(IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_ready)
                                 , '#',6,vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor);
                    VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 452, "", false);
                }
                VL_WRITEF_NX("S2A_PENDING_OUTPUT_WRITE case=%s layer=0 cycles_from_start=%0d reads=%0d addr=%08h wstrb=%b\n",5
                             , 'S',&(vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__59__case_name)
                             , '#',32,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__simulation_cycle_count 
                                       - vlSelfRef.tb_s2a_backend_fault_recovery__DOT__transaction_start_cycle)
                             , '~',32,vlSelfRef.tb_s2a_backend_fault_recovery__DOT__memory_read_handshakes
                             , '#',32,vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_addr
                             , '#',4,(((4U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                                        ? (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                                             ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_wstrb)
                                             : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_wstrb)) 
                                           & (- (IData)(
                                                        (1U 
                                                         & (~ 
                                                            ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                                             >> 1U))))))
                                        : (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                                             ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_wstrb)
                                             : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_wstrb)) 
                                           & (- (IData)(
                                                        (1U 
                                                         & ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                                            >> 1U)))))) 
                                      & (- (IData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid)))));
                goto __Vlabel5;
            }
            if (VL_UNLIKELY(((1U & ((((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__busy)) 
                                      | (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__buffer_owner_pl))) 
                                     | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__error)) 
                                    | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__done)))))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:461: Assertion failed in %m: \347\255\211\345\276\205 layer0 output write \346\227\266\344\273\273\345\212\241\346\217\220\345\211\215\347\246\273\345\274\200 busy\357\274\232busy=%b error=%b code=%0d\n",6, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.wait_for_first_output_write", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000)
                             , '#',1,(IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__busy)
                             , '#',1,vlSelfRef.tb_s2a_backend_fault_recovery__DOT__error
                             , '#',3,(IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__error_code));
                VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 461, "", false);
            }
            __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__59__wait_index 
                = ((IData)(1U) + __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__59__wait_index);
        }
        __Vlabel5: ;
    }
    if (VL_UNLIKELY(((1U & (~ (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__59__request_found)))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:466: Assertion failed in %m: layer0 \346\234\252\345\234\250 20000 cycles \345\206\205\344\272\247\347\224\237\351\246\226\347\254\224 output write\n",3, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.wait_for_first_output_write", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 466, "", false);
    }
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_output_write__62__saved_address = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_output_write__62__saved_wdata = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_output_write__62__saved_wstrb = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_output_write__62__stall_index = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_output_write__62__saved_address 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_addr;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_output_write__62__saved_wdata 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_wdata;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_output_write__62__saved_wstrb 
        = (((4U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
             ? (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                  ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_wstrb)
                  : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_wstrb)) 
                & (- (IData)((1U & (~ ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                       >> 1U)))))) : 
            (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
               ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_wstrb)
               : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_wstrb)) 
             & (- (IData)((1U & ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                 >> 1U)))))) & (- (IData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid))));
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_output_write__62__stall_index = 0U;
    while (VL_GTS_III(32, 3U, __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_output_write__62__stall_index)) {
        Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e288__0(vlSelf, 
                                                                             "@(posedge tb_s2a_backend_fault_recovery.clk)");
        co_await vlSelfRef.__VtrigSched_h3193e288__0.trigger(0U, 
                                                             nullptr, 
                                                             "@(posedge tb_s2a_backend_fault_recovery.clk)", 
                                                             "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                             481);
        vlSelfRef.__Vm_traceActivity[3U] = 1U;
        co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                             nullptr, 
                                             "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                             482);
        vlSelfRef.__Vm_traceActivity[3U] = 1U;
        if (VL_UNLIKELY(((1U & (((((((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid)) 
                                     | (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_write))) 
                                    | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_ready)) 
                                   | (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_addr 
                                      != __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_output_write__62__saved_address)) 
                                  | (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_wdata 
                                     != __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_output_write__62__saved_wdata)) 
                                 | ((((4U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                                       ? (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                                            ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_wstrb)
                                            : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_wstrb)) 
                                          & (- (IData)(
                                                       (1U 
                                                        & (~ 
                                                           ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                                            >> 1U))))))
                                       : (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                                            ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_wstrb)
                                            : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_wstrb)) 
                                          & (- (IData)(
                                                       (1U 
                                                        & ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                                           >> 1U)))))) 
                                     & (- (IData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid)))) 
                                    != (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_output_write__62__saved_wstrb))) 
                                | (0U != (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_rstrb))))))) {
            VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:486: Assertion failed in %m: \346\234\252\346\217\241\346\211\213 layer0 output write \345\255\227\346\256\265\346\234\252\344\277\235\346\214\201\347\250\263\345\256\232\n",3, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.hold_unaccepted_output_write", 'T',-9
                         , '#',64,VL_TIME_UNITED_Q(1000));
            VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 486, "", false);
        }
        __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_output_write__62__stall_index 
            = ((IData)(1U) + __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_output_write__62__stall_index);
    }
    if (VL_UNLIKELY(((VL_LTES_III(32, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__memory_read_handshakes, __Vtask_tb_s2a_backend_fault_recovery__DOT__prepare_unaccepted_output_write__55__reads_before) 
                      | (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__memory_write_side_effects 
                         != __Vtask_tb_s2a_backend_fault_recovery__DOT__prepare_unaccepted_output_write__55__writes_before))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:506: Assertion failed in %m: \345\210\260\350\276\276\351\246\226\347\254\224\346\234\252\346\217\241\346\211\213 output write \345\211\215\345\220\216\350\257\273\345\206\231\350\256\241\346\225\260\345\274\202\345\270\270\n",3, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.prepare_unaccepted_output_write", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 506, "", false);
    }
    if (VL_UNLIKELY((("hard_reset"s == vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__prepare_unaccepted_output_write__55__case_name)))) {
        VL_WRITEF_NX("S2A_RETRY_CASE after=soft_reset request=pending_output_write next=hard_reset start_accepted=1\n",0);
    } else if (VL_UNLIKELY((("csr_timeout"s == vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__prepare_unaccepted_output_write__55__case_name)))) {
        VL_WRITEF_NX("S2A_RETRY_CASE after=hard_reset request=pending_output_write next=csr_timeout start_accepted=1\n",0);
    }
    __Vtask_tb_s2a_backend_fault_recovery__DOT__cancel_output_write_with_hard_reset__54__reads_before 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__memory_read_handshakes;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__cancel_output_write_with_hard_reset__54__writes_before 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__memory_write_side_effects;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         546);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__hard_reset = 1U;
    co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                         nullptr, "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                         548);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    if (VL_UNLIKELY((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:549: Assertion failed in %m: hard_reset \346\234\252\345\234\250 output write \346\217\241\346\211\213\345\211\215\346\222\244\351\224\200 mem_valid\n",3, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.cancel_output_write_with_hard_reset", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 549, "", false);
    }
    __Vtask_tb_s2a_backend_fault_recovery__DOT__cancel_output_write_with_hard_reset__54__tb_s2a_backend_fault_recovery__DOT__unnamedblk1_2__DOT____Vrepeat1 = 2U;
    while (VL_LTS_III(32, 0U, __Vtask_tb_s2a_backend_fault_recovery__DOT__cancel_output_write_with_hard_reset__54__tb_s2a_backend_fault_recovery__DOT__unnamedblk1_2__DOT____Vrepeat1)) {
        Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e288__0(vlSelf, 
                                                                             "@(posedge tb_s2a_backend_fault_recovery.clk)");
        co_await vlSelfRef.__VtrigSched_h3193e288__0.trigger(0U, 
                                                             nullptr, 
                                                             "@(posedge tb_s2a_backend_fault_recovery.clk)", 
                                                             "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                             550);
        vlSelfRef.__Vm_traceActivity[3U] = 1U;
        __Vtask_tb_s2a_backend_fault_recovery__DOT__cancel_output_write_with_hard_reset__54__tb_s2a_backend_fault_recovery__DOT__unnamedblk1_2__DOT____Vrepeat1 
            = (__Vtask_tb_s2a_backend_fault_recovery__DOT__cancel_output_write_with_hard_reset__54__tb_s2a_backend_fault_recovery__DOT__unnamedblk1_2__DOT____Vrepeat1 
               - (IData)(1U));
    }
    co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                         nullptr, "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                         551);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    if (VL_UNLIKELY(((((((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__busy) 
                         | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__done)) 
                        | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__error)) 
                       | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__buffer_owner_pl)) 
                      | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__head_output_valid))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:553: Assertion failed in %m: hard_reset \346\234\252\346\270\205\351\231\244 CSR \347\212\266\346\200\201/ownership/head-valid\n",3, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.cancel_output_write_with_hard_reset", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 553, "", false);
    }
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         555);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__hard_reset = 0U;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e288__0(vlSelf, 
                                                                         "@(posedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e288__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(posedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         557);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                         nullptr, "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                         558);
    if (VL_UNLIKELY((((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__backend_abort) 
                      | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:559: Assertion failed in %m: hard_reset \345\220\216\346\234\252\346\201\242\345\244\215 idle\n",3, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.cancel_output_write_with_hard_reset", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 559, "", false);
    }
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__63__phase_name = "hard_reset \345\220\216"s;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__63__expected_head_valid = 0U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__63__expected_error_code = 0U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__63__expected_status = 0U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__63__status_value = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__63__error_value = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__64__address = 4U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__64__value = 0;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         224);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_write = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__64__address;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_wdata = 0U;
    co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                         nullptr, "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                         229);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__64__value 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_rdata;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         231);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr = 0U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__63__status_value 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__64__value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__65__address = 8U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__65__value = 0;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         224);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_write = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__65__address;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_wdata = 0U;
    co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                         nullptr, "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                         229);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__65__value 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_rdata;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         231);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr = 0U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__63__error_value 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__65__value;
    if (VL_UNLIKELY((((0x0000000fU & __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__63__status_value) 
                      != (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__63__expected_status))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:249: Assertion failed in %m: %s STATUS \344\270\215\345\214\271\351\205\215\357\274\232\346\234\237\346\234\233=%b \345\256\236\351\231\205=%b\n",6, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.check_status", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , 'S',&(vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__63__phase_name)
                     , '#',4,(IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__63__expected_status)
                     , '#',4,(0x0000000fU & __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__63__status_value));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 249, "", false);
    }
    if (VL_UNLIKELY((((7U & __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__63__error_value) 
                      != (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__63__expected_error_code))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:253: Assertion failed in %m: %s ERROR_CODE \344\270\215\345\214\271\351\205\215\357\274\232\346\234\237\346\234\233=%0d \345\256\236\351\231\205=%0d\n",6, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.check_status", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , 'S',&(vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__63__phase_name)
                     , '#',3,(IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__63__expected_error_code)
                     , '#',3,(7U & __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__63__error_value));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 253, "", false);
    }
    if (VL_UNLIKELY((((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__head_output_valid) 
                      != (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__63__expected_head_valid))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:257: Assertion failed in %m: %s head_output_valid \344\270\215\345\214\271\351\205\215\357\274\232\346\234\237\346\234\233=%b \345\256\236\351\231\205=%b\n",6, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.check_status", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , 'S',&(vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__63__phase_name)
                     , '#',1,(IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__63__expected_head_valid)
                     , '#',1,vlSelfRef.tb_s2a_backend_fault_recovery__DOT__head_output_valid);
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 257, "", false);
    }
    if (VL_UNLIKELY(((((((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__busy) 
                         != (1U & (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__63__expected_status))) 
                        | ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__done) 
                           != (1U & ((IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__63__expected_status) 
                                     >> 1U)))) | ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__error) 
                                                  != 
                                                  (1U 
                                                   & ((IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__63__expected_status) 
                                                      >> 2U)))) 
                      | ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__buffer_owner_pl) 
                         != (1U & ((IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__63__expected_status) 
                                   >> 3U))))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:264: Assertion failed in %m: %s CSR/status \350\276\223\345\207\272\344\270\216\347\212\266\346\200\201\344\275\215\344\270\215\344\270\200\350\207\264\n",4, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.check_status", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , 'S',&(vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__63__phase_name));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 264, "", false);
    }
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_no_late_effects__66__writes_before 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__cancel_output_write_with_hard_reset__54__writes_before;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_no_late_effects__66__reads_before 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__cancel_output_write_with_hard_reset__54__reads_before;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_no_late_effects__66__quiet_index = 0;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         419);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__automatic_read_responses = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__manual_mem_error_code = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__manual_mem_ready = 1U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_no_late_effects__66__quiet_index = 0U;
    while (VL_GTS_III(32, 3U, __Vtask_tb_s2a_backend_fault_recovery__DOT__check_no_late_effects__66__quiet_index)) {
        Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e288__0(vlSelf, 
                                                                             "@(posedge tb_s2a_backend_fault_recovery.clk)");
        co_await vlSelfRef.__VtrigSched_h3193e288__0.trigger(0U, 
                                                             nullptr, 
                                                             "@(posedge tb_s2a_backend_fault_recovery.clk)", 
                                                             "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                             424);
        vlSelfRef.__Vm_traceActivity[3U] = 1U;
        co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                             nullptr, 
                                             "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                             425);
        vlSelfRef.__Vm_traceActivity[3U] = 1U;
        if (VL_UNLIKELY(((((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid) 
                           | ((0U != (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__backend_memory_error_code)) 
                              & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__memory_handshake))) 
                          | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_write))))) {
            VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:427: Assertion failed in %m: \345\217\226\346\266\210\345\220\216\345\207\272\347\216\260\350\277\237\345\210\260\350\257\267\346\261\202\346\210\226 memory error event\n",3, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.check_no_late_effects", 'T',-9
                         , '#',64,VL_TIME_UNITED_Q(1000));
            VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 427, "", false);
        }
        if (VL_UNLIKELY((((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__memory_read_handshakes 
                           != __Vtask_tb_s2a_backend_fault_recovery__DOT__check_no_late_effects__66__reads_before) 
                          | (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__memory_write_side_effects 
                             != __Vtask_tb_s2a_backend_fault_recovery__DOT__check_no_late_effects__66__writes_before))))) {
            VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:431: Assertion failed in %m: \345\217\226\346\266\210\345\220\216\345\207\272\347\216\260\350\277\237\345\210\260 read/write memory \345\211\257\344\275\234\347\224\250\n",3, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.check_no_late_effects", 'T',-9
                         , '#',64,VL_TIME_UNITED_Q(1000));
            VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 431, "", false);
        }
        __Vtask_tb_s2a_backend_fault_recovery__DOT__check_no_late_effects__66__quiet_index 
            = ((IData)(1U) + __Vtask_tb_s2a_backend_fault_recovery__DOT__check_no_late_effects__66__quiet_index);
    }
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         434);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__manual_mem_ready = 0U;
    if (VL_UNLIKELY(((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__memory_write_side_effects 
                      != __Vtask_tb_s2a_backend_fault_recovery__DOT__cancel_output_write_with_hard_reset__54__writes_before)))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:563: Assertion failed in %m: hard_reset \345\220\216\345\207\272\347\216\260\350\277\237\345\210\260 output write \345\211\257\344\275\234\347\224\250\n",3, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.cancel_output_write_with_hard_reset", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 563, "", false);
    }
    VL_WRITEF_NX("S2A_OUTPUT_WRITE_CANCEL kind=hard_reset layer=0 writes_before=%0d writes_after=%0d\nS2A_CANCEL_CASE kind=hard_reset request=pending_output_write cancelled=1 writes_before=%0d writes_after=%0d\n",4
                 , '~',32,__Vtask_tb_s2a_backend_fault_recovery__DOT__cancel_output_write_with_hard_reset__54__writes_before
                 , '~',32,vlSelfRef.tb_s2a_backend_fault_recovery__DOT__memory_write_side_effects
                 , '~',32,__Vtask_tb_s2a_backend_fault_recovery__DOT__cancel_output_write_with_hard_reset__54__writes_before
                 , '~',32,vlSelfRef.tb_s2a_backend_fault_recovery__DOT__memory_write_side_effects);
    __Vtask_tb_s2a_backend_fault_recovery__DOT__cancel_output_write_with_timeout__67__reads_before = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__cancel_output_write_with_timeout__67__writes_before = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__cancel_output_write_with_timeout__67__wait_index = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__cancel_output_write_with_timeout__67__timeout_found = 0;
    vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__prepare_unaccepted_output_write__68__case_name = "csr_timeout"s;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__prepare_unaccepted_output_write__68__reads_before = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__prepare_unaccepted_output_write__68__writes_before = 0;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__manual_mem_ready = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__manual_mem_error_code = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__automatic_read_responses = 1U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__prepare_unaccepted_output_write__68__reads_before 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__memory_read_handshakes;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__prepare_unaccepted_output_write__68__writes_before 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__memory_write_side_effects;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__start_transaction__69__timeout_value = 0x000186a0U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__70__value 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__start_transaction__69__timeout_value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__70__address = 0x28U;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         206);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_write = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__70__address;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_wdata 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__70__value;
    if (VL_UNLIKELY(((1U & (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__csr_ready)))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:207: Assertion failed in %m: CSR \345\206\231\345\205\245\346\234\252 ready\357\274\232addr=%02h\n",4, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.write_csr", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , '#',8,(IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__70__address));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 207, "", false);
    }
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e288__0(vlSelf, 
                                                                         "@(posedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e288__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(posedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         212);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                         nullptr, "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                         213);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         214);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_write = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_wdata = 0U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__71__value = 1U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__71__address = 0U;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         206);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_write = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__71__address;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_wdata 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__71__value;
    if (VL_UNLIKELY(((1U & (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__csr_ready)))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:207: Assertion failed in %m: CSR \345\206\231\345\205\245\346\234\252 ready\357\274\232addr=%02h\n",4, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.write_csr", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , '#',8,(IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__71__address));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 207, "", false);
    }
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e288__0(vlSelf, 
                                                                         "@(posedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e288__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(posedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         212);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                         nullptr, "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                         213);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         214);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_write = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_wdata = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__transaction_start_cycle 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__simulation_cycle_count;
    vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__72__case_name 
        = vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__prepare_unaccepted_output_write__68__case_name;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__72__wait_index = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__72__request_found = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__72__request_found = 0U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__72__wait_index = 0U;
    if (VL_UNLIKELY(((1U & (((((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__backend_start)) 
                               | (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__busy))) 
                              | (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__buffer_owner_pl))) 
                             | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__done)) 
                            | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__error)))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:296: Assertion failed in %m: CSR \346\234\252\346\216\245\345\217\227\345\220\210\346\263\225 start\357\274\232start=%b busy=%b owner=%b\n",6, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.start_transaction", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , '#',1,(IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__backend_start)
                     , '#',1,vlSelfRef.tb_s2a_backend_fault_recovery__DOT__busy
                     , '#',1,(IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__buffer_owner_pl));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 296, "", false);
    }
    {
        while (VL_GTS_III(32, 0x00004e20U, __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__72__wait_index)) {
            Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                                "@(negedge tb_s2a_backend_fault_recovery.clk)");
            co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                                 nullptr, 
                                                                 "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                                 "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                                 445);
            vlSelfRef.__Vm_traceActivity[3U] = 1U;
            if (VL_UNLIKELY((((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid) 
                              & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_write))))) {
                __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__72__request_found = 1U;
                __Vfunc_tb_s2a_backend_fault_recovery__DOT__is_onehot4__73__value 
                    = (((4U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                         ? (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                              ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_wstrb)
                              : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_wstrb)) 
                            & (- (IData)((1U & (~ ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                                   >> 1U))))))
                         : (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                              ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_wstrb)
                              : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_wstrb)) 
                            & (- (IData)((1U & ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                                >> 1U)))))) 
                       & (- (IData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid))));
                __Vfunc_tb_s2a_backend_fault_recovery__DOT__is_onehot4__73__Vfuncout = 0;
                __Vfunc_tb_s2a_backend_fault_recovery__DOT__is_onehot4__73__Vfuncout 
                    = ((0U != (IData)(__Vfunc_tb_s2a_backend_fault_recovery__DOT__is_onehot4__73__value)) 
                       & (0U == ((IData)(__Vfunc_tb_s2a_backend_fault_recovery__DOT__is_onehot4__73__value) 
                                 & ((IData)(__Vfunc_tb_s2a_backend_fault_recovery__DOT__is_onehot4__73__value) 
                                    - (IData)(1U)))));
                __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__72____VlefCall_0__is_onehot4 
                    = __Vfunc_tb_s2a_backend_fault_recovery__DOT__is_onehot4__73__Vfuncout;
                __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__74__Vfuncout = 0;
                __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__74__found = 0;
                __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__74__selected_address = 0;
                __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__74__Vfuncout = 0U;
                __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__74__found = 0U;
                __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__74__selected_address = 0U;
                if ((((4U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                       ? (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                            ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_wstrb)
                            : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_wstrb)) 
                          & (- (IData)((1U & (~ ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                                 >> 1U))))))
                       : (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                            ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_wstrb)
                            : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_wstrb)) 
                          & (- (IData)((1U & ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                              >> 1U)))))) 
                     & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid))) {
                    __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__74__selected_address 
                        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_addr;
                    __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__74__found 
                        = ((0x01000000U <= __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__74__selected_address) 
                           & (0x01152000U > __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__74__selected_address));
                }
                if (((((4U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                        ? (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                             ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_wstrb)
                             : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_wstrb)) 
                           & (- (IData)((1U & (~ ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                                  >> 1U))))))
                        : (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                             ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_wstrb)
                             : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_wstrb)) 
                           & (- (IData)((1U & ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                               >> 1U)))))) 
                      >> 1U) & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid))) {
                    __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__74__selected_address 
                        = ((IData)(1U) + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_addr);
                    __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__74__found 
                        = ((0x01000000U <= __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__74__selected_address) 
                           & (0x01152000U > __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__74__selected_address));
                }
                if (((((4U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                        ? (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                             ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_wstrb)
                             : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_wstrb)) 
                           & (- (IData)((1U & (~ ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                                  >> 1U))))))
                        : (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                             ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_wstrb)
                             : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_wstrb)) 
                           & (- (IData)((1U & ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                               >> 1U)))))) 
                      >> 2U) & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid))) {
                    __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__74__selected_address 
                        = ((IData)(2U) + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_addr);
                    __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__74__found 
                        = ((0x01000000U <= __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__74__selected_address) 
                           & (0x01152000U > __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__74__selected_address));
                }
                if (((((4U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                        ? (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                             ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_wstrb)
                             : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_wstrb)) 
                           & (- (IData)((1U & (~ ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                                  >> 1U))))))
                        : (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                             ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_wstrb)
                             : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_wstrb)) 
                           & (- (IData)((1U & ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                               >> 1U)))))) 
                      >> 3U) & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid))) {
                    __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__74__selected_address 
                        = ((IData)(3U) + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_addr);
                    __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__74__found 
                        = ((0x01000000U <= __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__74__selected_address) 
                           & (0x01152000U > __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__74__selected_address));
                }
                __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__74__Vfuncout 
                    = __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__74__found;
                __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__72____VlefCall_1__selected_byte_in_layer0_output_tensor 
                    = __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_layer0_output_tensor__74__Vfuncout;
                if (VL_UNLIKELY(((1U & ((((((((((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_ready) 
                                                | (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__busy))) 
                                               | (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__buffer_owner_pl))) 
                                              | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__done)) 
                                             | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__error)) 
                                            | (0U != (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))) 
                                           | (~ (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__72____VlefCall_0__is_onehot4))) 
                                          | (0U != (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_rstrb))) 
                                         | (0U != (3U 
                                                   & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_addr))) 
                                        | (~ (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__72____VlefCall_1__selected_byte_in_layer0_output_tensor))))))) {
                    VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:452: Assertion failed in %m: layer0 \351\246\226\347\254\224 output write \350\257\267\346\261\202\344\270\215\345\220\210\346\263\225\357\274\232addr=%08h wstrb=%b ready=%b layer=%0d\n",7, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.wait_for_first_output_write", 'T',-9
                                 , '#',64,VL_TIME_UNITED_Q(1000)
                                 , '#',32,vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_addr
                                 , '#',4,(((4U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                                            ? (((1U 
                                                 & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                                                 ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_wstrb)
                                                 : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_wstrb)) 
                                               & (- (IData)(
                                                            (1U 
                                                             & (~ 
                                                                ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                                                 >> 1U))))))
                                            : (((1U 
                                                 & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                                                 ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_wstrb)
                                                 : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_wstrb)) 
                                               & (- (IData)(
                                                            (1U 
                                                             & ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                                                >> 1U)))))) 
                                          & (- (IData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid))))
                                 , '#',1,(IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_ready)
                                 , '#',6,vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor);
                    VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 452, "", false);
                }
                VL_WRITEF_NX("S2A_PENDING_OUTPUT_WRITE case=%s layer=0 cycles_from_start=%0d reads=%0d addr=%08h wstrb=%b\n",5
                             , 'S',&(vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__72__case_name)
                             , '#',32,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__simulation_cycle_count 
                                       - vlSelfRef.tb_s2a_backend_fault_recovery__DOT__transaction_start_cycle)
                             , '~',32,vlSelfRef.tb_s2a_backend_fault_recovery__DOT__memory_read_handshakes
                             , '#',32,vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_addr
                             , '#',4,(((4U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                                        ? (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                                             ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_wstrb)
                                             : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_wstrb)) 
                                           & (- (IData)(
                                                        (1U 
                                                         & (~ 
                                                            ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                                             >> 1U))))))
                                        : (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                                             ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_wstrb)
                                             : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_wstrb)) 
                                           & (- (IData)(
                                                        (1U 
                                                         & ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                                            >> 1U)))))) 
                                      & (- (IData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid)))));
                goto __Vlabel6;
            }
            if (VL_UNLIKELY(((1U & ((((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__busy)) 
                                      | (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__buffer_owner_pl))) 
                                     | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__error)) 
                                    | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__done)))))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:461: Assertion failed in %m: \347\255\211\345\276\205 layer0 output write \346\227\266\344\273\273\345\212\241\346\217\220\345\211\215\347\246\273\345\274\200 busy\357\274\232busy=%b error=%b code=%0d\n",6, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.wait_for_first_output_write", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000)
                             , '#',1,(IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__busy)
                             , '#',1,vlSelfRef.tb_s2a_backend_fault_recovery__DOT__error
                             , '#',3,(IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__error_code));
                VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 461, "", false);
            }
            __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__72__wait_index 
                = ((IData)(1U) + __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__72__wait_index);
        }
        __Vlabel6: ;
    }
    if (VL_UNLIKELY(((1U & (~ (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_first_output_write__72__request_found)))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:466: Assertion failed in %m: layer0 \346\234\252\345\234\250 20000 cycles \345\206\205\344\272\247\347\224\237\351\246\226\347\254\224 output write\n",3, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.wait_for_first_output_write", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 466, "", false);
    }
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_output_write__75__saved_address = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_output_write__75__saved_wdata = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_output_write__75__saved_wstrb = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_output_write__75__stall_index = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_output_write__75__saved_address 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_addr;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_output_write__75__saved_wdata 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_wdata;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_output_write__75__saved_wstrb 
        = (((4U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
             ? (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                  ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_wstrb)
                  : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_wstrb)) 
                & (- (IData)((1U & (~ ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                       >> 1U)))))) : 
            (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
               ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_wstrb)
               : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_wstrb)) 
             & (- (IData)((1U & ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                 >> 1U)))))) & (- (IData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid))));
    __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_output_write__75__stall_index = 0U;
    while (VL_GTS_III(32, 3U, __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_output_write__75__stall_index)) {
        Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e288__0(vlSelf, 
                                                                             "@(posedge tb_s2a_backend_fault_recovery.clk)");
        co_await vlSelfRef.__VtrigSched_h3193e288__0.trigger(0U, 
                                                             nullptr, 
                                                             "@(posedge tb_s2a_backend_fault_recovery.clk)", 
                                                             "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                             481);
        vlSelfRef.__Vm_traceActivity[3U] = 1U;
        co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                             nullptr, 
                                             "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                             482);
        vlSelfRef.__Vm_traceActivity[3U] = 1U;
        if (VL_UNLIKELY(((1U & (((((((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid)) 
                                     | (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_write))) 
                                    | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_ready)) 
                                   | (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_addr 
                                      != __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_output_write__75__saved_address)) 
                                  | (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_wdata 
                                     != __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_output_write__75__saved_wdata)) 
                                 | ((((4U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                                       ? (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                                            ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_wstrb)
                                            : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_wstrb)) 
                                          & (- (IData)(
                                                       (1U 
                                                        & (~ 
                                                           ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                                            >> 1U))))))
                                       : (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                                            ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_wstrb)
                                            : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_wstrb)) 
                                          & (- (IData)(
                                                       (1U 
                                                        & ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                                           >> 1U)))))) 
                                     & (- (IData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid)))) 
                                    != (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_output_write__75__saved_wstrb))) 
                                | (0U != (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_rstrb))))))) {
            VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:486: Assertion failed in %m: \346\234\252\346\217\241\346\211\213 layer0 output write \345\255\227\346\256\265\346\234\252\344\277\235\346\214\201\347\250\263\345\256\232\n",3, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.hold_unaccepted_output_write", 'T',-9
                         , '#',64,VL_TIME_UNITED_Q(1000));
            VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 486, "", false);
        }
        __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_output_write__75__stall_index 
            = ((IData)(1U) + __Vtask_tb_s2a_backend_fault_recovery__DOT__hold_unaccepted_output_write__75__stall_index);
    }
    if (VL_UNLIKELY(((VL_LTES_III(32, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__memory_read_handshakes, __Vtask_tb_s2a_backend_fault_recovery__DOT__prepare_unaccepted_output_write__68__reads_before) 
                      | (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__memory_write_side_effects 
                         != __Vtask_tb_s2a_backend_fault_recovery__DOT__prepare_unaccepted_output_write__68__writes_before))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:506: Assertion failed in %m: \345\210\260\350\276\276\351\246\226\347\254\224\346\234\252\346\217\241\346\211\213 output write \345\211\215\345\220\216\350\257\273\345\206\231\350\256\241\346\225\260\345\274\202\345\270\270\n",3, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.prepare_unaccepted_output_write", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 506, "", false);
    }
    if (VL_UNLIKELY((("hard_reset"s == vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__prepare_unaccepted_output_write__68__case_name)))) {
        VL_WRITEF_NX("S2A_RETRY_CASE after=soft_reset request=pending_output_write next=hard_reset start_accepted=1\n",0);
    } else if (VL_UNLIKELY((("csr_timeout"s == vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__prepare_unaccepted_output_write__68__case_name)))) {
        VL_WRITEF_NX("S2A_RETRY_CASE after=hard_reset request=pending_output_write next=csr_timeout start_accepted=1\n",0);
    }
    __Vtask_tb_s2a_backend_fault_recovery__DOT__cancel_output_write_with_timeout__67__reads_before 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__memory_read_handshakes;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__cancel_output_write_with_timeout__67__writes_before 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__memory_write_side_effects;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__cancel_output_write_with_timeout__67__timeout_found = 0U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__cancel_output_write_with_timeout__67__wait_index = 0U;
    {
        while ((0x000186a8U > __Vtask_tb_s2a_backend_fault_recovery__DOT__cancel_output_write_with_timeout__67__wait_index)) {
            Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                                "@(negedge tb_s2a_backend_fault_recovery.clk)");
            co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                                 nullptr, 
                                                                 "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                                 "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                                 583);
            vlSelfRef.__Vm_traceActivity[3U] = 1U;
            if (((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__error) 
                 & (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__busy)))) {
                __Vtask_tb_s2a_backend_fault_recovery__DOT__cancel_output_write_with_timeout__67__timeout_found = 1U;
                goto __Vlabel7;
            }
            if (VL_UNLIKELY(((1U & ((((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid)) 
                                      | (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_write))) 
                                     | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_ready)) 
                                    | (0U != (3U & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_addr))))))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:589: Assertion failed in %m: CSR timeout \345\211\215 layer0 output write \346\234\252\344\277\235\346\214\201\344\270\272\346\234\252\346\217\241\346\211\213\350\257\267\346\261\202\n",3, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.cancel_output_write_with_timeout", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 589, "", false);
            }
            __Vtask_tb_s2a_backend_fault_recovery__DOT__cancel_output_write_with_timeout__67__wait_index 
                = ((IData)(1U) + __Vtask_tb_s2a_backend_fault_recovery__DOT__cancel_output_write_with_timeout__67__wait_index);
        }
        __Vlabel7: ;
    }
    if (VL_UNLIKELY(((1U & (~ (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__cancel_output_write_with_timeout__67__timeout_found)))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:592: Assertion failed in %m: \346\234\252\346\217\241\346\211\213 output write \346\234\252\345\234\250\351\205\215\347\275\256 timeout \345\221\250\346\234\237\346\222\244\351\224\200\n",3, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.cancel_output_write_with_timeout", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 592, "", false);
    }
    if (VL_UNLIKELY((((((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid) 
                        | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__buffer_owner_pl)) 
                       | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__done)) 
                      | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__head_output_valid))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:594: Assertion failed in %m: timeout \345\220\216 output write/ownership/done/head-valid \347\212\266\346\200\201\351\224\231\350\257\257\n",3, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.cancel_output_write_with_timeout", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 594, "", false);
    }
    vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__76__phase_name = "output write timeout \345\220\216"s;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__76__expected_head_valid = 0U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__76__expected_error_code = 5U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__76__expected_status = 4U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__76__status_value = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__76__error_value = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__77__address = 4U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__77__value = 0;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         224);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_write = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__77__address;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_wdata = 0U;
    co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                         nullptr, "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                         229);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__77__value 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_rdata;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         231);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr = 0U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__76__status_value 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__77__value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__78__address = 8U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__78__value = 0;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         224);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_write = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__78__address;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_wdata = 0U;
    co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                         nullptr, "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                         229);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__78__value 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_rdata;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         231);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr = 0U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__76__error_value 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__78__value;
    if (VL_UNLIKELY((((0x0000000fU & __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__76__status_value) 
                      != (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__76__expected_status))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:249: Assertion failed in %m: %s STATUS \344\270\215\345\214\271\351\205\215\357\274\232\346\234\237\346\234\233=%b \345\256\236\351\231\205=%b\n",6, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.check_status", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , 'S',&(vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__76__phase_name)
                     , '#',4,(IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__76__expected_status)
                     , '#',4,(0x0000000fU & __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__76__status_value));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 249, "", false);
    }
    if (VL_UNLIKELY((((7U & __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__76__error_value) 
                      != (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__76__expected_error_code))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:253: Assertion failed in %m: %s ERROR_CODE \344\270\215\345\214\271\351\205\215\357\274\232\346\234\237\346\234\233=%0d \345\256\236\351\231\205=%0d\n",6, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.check_status", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , 'S',&(vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__76__phase_name)
                     , '#',3,(IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__76__expected_error_code)
                     , '#',3,(7U & __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__76__error_value));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 253, "", false);
    }
    if (VL_UNLIKELY((((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__head_output_valid) 
                      != (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__76__expected_head_valid))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:257: Assertion failed in %m: %s head_output_valid \344\270\215\345\214\271\351\205\215\357\274\232\346\234\237\346\234\233=%b \345\256\236\351\231\205=%b\n",6, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.check_status", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , 'S',&(vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__76__phase_name)
                     , '#',1,(IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__76__expected_head_valid)
                     , '#',1,vlSelfRef.tb_s2a_backend_fault_recovery__DOT__head_output_valid);
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 257, "", false);
    }
    if (VL_UNLIKELY(((((((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__busy) 
                         != (1U & (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__76__expected_status))) 
                        | ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__done) 
                           != (1U & ((IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__76__expected_status) 
                                     >> 1U)))) | ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__error) 
                                                  != 
                                                  (1U 
                                                   & ((IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__76__expected_status) 
                                                      >> 2U)))) 
                      | ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__buffer_owner_pl) 
                         != (1U & ((IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__76__expected_status) 
                                   >> 3U))))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:264: Assertion failed in %m: %s CSR/status \350\276\223\345\207\272\344\270\216\347\212\266\346\200\201\344\275\215\344\270\215\344\270\200\350\207\264\n",4, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.check_status", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , 'S',&(vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__76__phase_name));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 264, "", false);
    }
    if (VL_UNLIKELY((((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__memory_read_handshakes 
                       != __Vtask_tb_s2a_backend_fault_recovery__DOT__cancel_output_write_with_timeout__67__reads_before) 
                      | (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__memory_write_side_effects 
                         != __Vtask_tb_s2a_backend_fault_recovery__DOT__cancel_output_write_with_timeout__67__writes_before))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:599: Assertion failed in %m: timeout \345\211\215\346\234\252\346\217\241\346\211\213 output write \344\270\215\345\272\224\344\272\247\347\224\237 memory \345\211\257\344\275\234\347\224\250\n",3, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.cancel_output_write_with_timeout", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 599, "", false);
    }
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_no_late_effects__79__writes_before 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__cancel_output_write_with_timeout__67__writes_before;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_no_late_effects__79__reads_before 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__cancel_output_write_with_timeout__67__reads_before;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_no_late_effects__79__quiet_index = 0;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         419);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__automatic_read_responses = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__manual_mem_error_code = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__manual_mem_ready = 1U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_no_late_effects__79__quiet_index = 0U;
    while (VL_GTS_III(32, 3U, __Vtask_tb_s2a_backend_fault_recovery__DOT__check_no_late_effects__79__quiet_index)) {
        Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e288__0(vlSelf, 
                                                                             "@(posedge tb_s2a_backend_fault_recovery.clk)");
        co_await vlSelfRef.__VtrigSched_h3193e288__0.trigger(0U, 
                                                             nullptr, 
                                                             "@(posedge tb_s2a_backend_fault_recovery.clk)", 
                                                             "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                             424);
        vlSelfRef.__Vm_traceActivity[3U] = 1U;
        co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                             nullptr, 
                                             "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                             425);
        vlSelfRef.__Vm_traceActivity[3U] = 1U;
        if (VL_UNLIKELY(((((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid) 
                           | ((0U != (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__backend_memory_error_code)) 
                              & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__memory_handshake))) 
                          | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_write))))) {
            VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:427: Assertion failed in %m: \345\217\226\346\266\210\345\220\216\345\207\272\347\216\260\350\277\237\345\210\260\350\257\267\346\261\202\346\210\226 memory error event\n",3, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.check_no_late_effects", 'T',-9
                         , '#',64,VL_TIME_UNITED_Q(1000));
            VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 427, "", false);
        }
        if (VL_UNLIKELY((((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__memory_read_handshakes 
                           != __Vtask_tb_s2a_backend_fault_recovery__DOT__check_no_late_effects__79__reads_before) 
                          | (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__memory_write_side_effects 
                             != __Vtask_tb_s2a_backend_fault_recovery__DOT__check_no_late_effects__79__writes_before))))) {
            VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:431: Assertion failed in %m: \345\217\226\346\266\210\345\220\216\345\207\272\347\216\260\350\277\237\345\210\260 read/write memory \345\211\257\344\275\234\347\224\250\n",3, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.check_no_late_effects", 'T',-9
                         , '#',64,VL_TIME_UNITED_Q(1000));
            VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 431, "", false);
        }
        __Vtask_tb_s2a_backend_fault_recovery__DOT__check_no_late_effects__79__quiet_index 
            = ((IData)(1U) + __Vtask_tb_s2a_backend_fault_recovery__DOT__check_no_late_effects__79__quiet_index);
    }
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         434);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__manual_mem_ready = 0U;
    if (VL_UNLIKELY(((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__memory_write_side_effects 
                      != __Vtask_tb_s2a_backend_fault_recovery__DOT__cancel_output_write_with_timeout__67__writes_before)))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:603: Assertion failed in %m: timeout \345\220\216\345\207\272\347\216\260\350\277\237\345\210\260 output write \345\211\257\344\275\234\347\224\250\n",3, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.cancel_output_write_with_timeout", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 603, "", false);
    }
    VL_WRITEF_NX("S2A_OUTPUT_WRITE_CANCEL kind=csr_timeout layer=0 writes_before=%0d writes_after=%0d\nS2A_CANCEL_CASE kind=csr_timeout request=pending_output_write cancelled=1 writes_before=%0d writes_after=%0d\n",4
                 , '~',32,__Vtask_tb_s2a_backend_fault_recovery__DOT__cancel_output_write_with_timeout__67__writes_before
                 , '~',32,vlSelfRef.tb_s2a_backend_fault_recovery__DOT__memory_write_side_effects
                 , '~',32,__Vtask_tb_s2a_backend_fault_recovery__DOT__cancel_output_write_with_timeout__67__writes_before
                 , '~',32,vlSelfRef.tb_s2a_backend_fault_recovery__DOT__memory_write_side_effects);
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__81__value = 2U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__81__address = 0x3cU;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         206);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_write = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__81__address;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_wdata 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__81__value;
    if (VL_UNLIKELY(((1U & (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__csr_ready)))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:207: Assertion failed in %m: CSR \345\206\231\345\205\245\346\234\252 ready\357\274\232addr=%02h\n",4, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.write_csr", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , '#',8,(IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__81__address));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 207, "", false);
    }
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e288__0(vlSelf, 
                                                                         "@(posedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e288__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(posedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         212);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                         nullptr, "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                         213);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         214);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_write = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_wdata = 0U;
    vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__82__phase_name = "ACK \345\220\216"s;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__82__expected_head_valid = 0U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__82__expected_error_code = 0U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__82__expected_status = 0U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__82__status_value = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__82__error_value = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__83__address = 4U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__83__value = 0;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         224);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_write = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__83__address;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_wdata = 0U;
    co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                         nullptr, "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                         229);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__83__value 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_rdata;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         231);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr = 0U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__82__status_value 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__83__value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__84__address = 8U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__84__value = 0;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         224);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_write = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__84__address;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_wdata = 0U;
    co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                         nullptr, "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                         229);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__84__value 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_rdata;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         231);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr = 0U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__82__error_value 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__84__value;
    if (VL_UNLIKELY((((0x0000000fU & __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__82__status_value) 
                      != (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__82__expected_status))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:249: Assertion failed in %m: %s STATUS \344\270\215\345\214\271\351\205\215\357\274\232\346\234\237\346\234\233=%b \345\256\236\351\231\205=%b\n",6, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.check_status", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , 'S',&(vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__82__phase_name)
                     , '#',4,(IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__82__expected_status)
                     , '#',4,(0x0000000fU & __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__82__status_value));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 249, "", false);
    }
    if (VL_UNLIKELY((((7U & __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__82__error_value) 
                      != (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__82__expected_error_code))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:253: Assertion failed in %m: %s ERROR_CODE \344\270\215\345\214\271\351\205\215\357\274\232\346\234\237\346\234\233=%0d \345\256\236\351\231\205=%0d\n",6, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.check_status", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , 'S',&(vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__82__phase_name)
                     , '#',3,(IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__82__expected_error_code)
                     , '#',3,(7U & __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__82__error_value));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 253, "", false);
    }
    if (VL_UNLIKELY((((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__head_output_valid) 
                      != (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__82__expected_head_valid))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:257: Assertion failed in %m: %s head_output_valid \344\270\215\345\214\271\351\205\215\357\274\232\346\234\237\346\234\233=%b \345\256\236\351\231\205=%b\n",6, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.check_status", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , 'S',&(vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__82__phase_name)
                     , '#',1,(IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__82__expected_head_valid)
                     , '#',1,vlSelfRef.tb_s2a_backend_fault_recovery__DOT__head_output_valid);
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 257, "", false);
    }
    if (VL_UNLIKELY(((((((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__busy) 
                         != (1U & (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__82__expected_status))) 
                        | ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__done) 
                           != (1U & ((IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__82__expected_status) 
                                     >> 1U)))) | ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__error) 
                                                  != 
                                                  (1U 
                                                   & ((IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__82__expected_status) 
                                                      >> 2U)))) 
                      | ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__buffer_owner_pl) 
                         != (1U & ((IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__82__expected_status) 
                                   >> 3U))))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:264: Assertion failed in %m: %s CSR/status \350\276\223\345\207\272\344\270\216\347\212\266\346\200\201\344\275\215\344\270\215\344\270\200\350\207\264\n",4, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.check_status", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , 'S',&(vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__82__phase_name));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 264, "", false);
    }
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__automatic_read_responses = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__manual_mem_ready = 0U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__start_transaction__85__timeout_value = 0x00001388U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__86__value 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__start_transaction__85__timeout_value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__86__address = 0x28U;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         206);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_write = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__86__address;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_wdata 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__86__value;
    if (VL_UNLIKELY(((1U & (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__csr_ready)))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:207: Assertion failed in %m: CSR \345\206\231\345\205\245\346\234\252 ready\357\274\232addr=%02h\n",4, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.write_csr", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , '#',8,(IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__86__address));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 207, "", false);
    }
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e288__0(vlSelf, 
                                                                         "@(posedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e288__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(posedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         212);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                         nullptr, "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                         213);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         214);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_write = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_wdata = 0U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__87__value = 1U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__87__address = 0U;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         206);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_write = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__87__address;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_wdata 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__87__value;
    if (VL_UNLIKELY(((1U & (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__csr_ready)))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:207: Assertion failed in %m: CSR \345\206\231\345\205\245\346\234\252 ready\357\274\232addr=%02h\n",4, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.write_csr", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , '#',8,(IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__87__address));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 207, "", false);
    }
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e288__0(vlSelf, 
                                                                         "@(posedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e288__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(posedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         212);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                         nullptr, "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                         213);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         214);
    if (VL_UNLIKELY(((1U & (((((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__backend_start)) 
                               | (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__busy))) 
                              | (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__buffer_owner_pl))) 
                             | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__done)) 
                            | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__error)))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:296: Assertion failed in %m: CSR \346\234\252\346\216\245\345\217\227\345\220\210\346\263\225 start\357\274\232start=%b busy=%b owner=%b\n",6, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.start_transaction", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , '#',1,(IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__backend_start)
                     , '#',1,vlSelfRef.tb_s2a_backend_fault_recovery__DOT__busy
                     , '#',1,(IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__buffer_owner_pl));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 296, "", false);
    }
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_write = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_wdata = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__transaction_start_cycle 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__simulation_cycle_count;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_read_request__88__wait_index = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_read_request__88__request_found = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_read_request__88__request_found = 0U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_read_request__88__wait_index = 0U;
    {
        while (VL_GTS_III(32, 0x00000080U, __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_read_request__88__wait_index)) {
            Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                                "@(negedge tb_s2a_backend_fault_recovery.clk)");
            co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                                 nullptr, 
                                                                 "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                                 "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                                 309);
            vlSelfRef.__Vm_traceActivity[3U] = 1U;
            if (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid) {
                __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_read_request__88__request_found = 1U;
                __Vfunc_tb_s2a_backend_fault_recovery__DOT__is_onehot4__89__value 
                    = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_rstrb;
                __Vfunc_tb_s2a_backend_fault_recovery__DOT__is_onehot4__89__Vfuncout = 0;
                __Vfunc_tb_s2a_backend_fault_recovery__DOT__is_onehot4__89__Vfuncout 
                    = ((0U != (IData)(__Vfunc_tb_s2a_backend_fault_recovery__DOT__is_onehot4__89__value)) 
                       & (0U == ((IData)(__Vfunc_tb_s2a_backend_fault_recovery__DOT__is_onehot4__89__value) 
                                 & ((IData)(__Vfunc_tb_s2a_backend_fault_recovery__DOT__is_onehot4__89__value) 
                                    - (IData)(1U)))));
                __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_read_request__88____VlefCall_0__is_onehot4 
                    = __Vfunc_tb_s2a_backend_fault_recovery__DOT__is_onehot4__89__Vfuncout;
                __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__90__Vfuncout = 0;
                __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__90__found = 0;
                __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__90__selected_address = 0;
                __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__90__Vfuncout = 0U;
                __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__90__found = 0U;
                __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__90__selected_address = 0U;
                if ((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_rstrb))) {
                    __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__90__selected_address 
                        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_addr;
                    __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__90__found 
                        = (0x0007ec00U > __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__90__selected_address);
                }
                if ((2U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_rstrb))) {
                    __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__90__selected_address 
                        = ((IData)(1U) + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_addr);
                    __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__90__found 
                        = (0x0007ec00U > __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__90__selected_address);
                }
                if ((4U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_rstrb))) {
                    __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__90__selected_address 
                        = ((IData)(2U) + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_addr);
                    __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__90__found 
                        = (0x0007ec00U > __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__90__selected_address);
                }
                if ((8U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_rstrb))) {
                    __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__90__selected_address 
                        = ((IData)(3U) + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_addr);
                    __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__90__found 
                        = (0x0007ec00U > __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__90__selected_address);
                }
                __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__90__Vfuncout 
                    = __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__90__found;
                __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_read_request__88____VlefCall_1__selected_byte_in_input_tensor 
                    = __Vfunc_tb_s2a_backend_fault_recovery__DOT__selected_byte_in_input_tensor__90__Vfuncout;
                if (VL_UNLIKELY(((1U & (((((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_write) 
                                           | (~ (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_read_request__88____VlefCall_0__is_onehot4))) 
                                          | (0U != 
                                             (((4U 
                                                & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                                                ? (
                                                   ((1U 
                                                     & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                                                     ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_wstrb)
                                                     : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_wstrb)) 
                                                   & (- (IData)(
                                                                (1U 
                                                                 & (~ 
                                                                    ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                                                     >> 1U))))))
                                                : (
                                                   ((1U 
                                                     & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                                                     ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_wstrb)
                                                     : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_wstrb)) 
                                                   & (- (IData)(
                                                                (1U 
                                                                 & ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                                                    >> 1U)))))) 
                                              & (- (IData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid)))))) 
                                         | (0U != (3U 
                                                   & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_addr))) 
                                        | (~ (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_read_request__88____VlefCall_1__selected_byte_in_input_tensor))))))) {
                    VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:314: Assertion failed in %m: backend \351\246\226\344\270\252 feature \350\257\273\350\257\267\346\261\202\344\270\215\345\234\250\350\276\223\345\205\245 tensor \346\210\226 byte lane \351\235\236\346\263\225\357\274\232addr=%08h rstrb=%b\n",5, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.wait_for_read_request", 'T',-9
                                 , '#',64,VL_TIME_UNITED_Q(1000)
                                 , '#',32,vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_addr
                                 , '#',4,(IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_rstrb));
                    VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 314, "", false);
                }
                if (VL_UNLIKELY((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_ready))) {
                    VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:317: Assertion failed in %m: unaccepted request \350\247\202\346\265\213\345\211\215\346\204\217\345\244\226\346\217\241\346\211\213\n",3, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.wait_for_read_request", 'T',-9
                                 , '#',64,VL_TIME_UNITED_Q(1000));
                    VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 317, "", false);
                }
                goto __Vlabel8;
            }
            if (VL_UNLIKELY(((1U & ((((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__busy)) 
                                      | (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__buffer_owner_pl))) 
                                     | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__error)) 
                                    | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__done)))))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:321: Assertion failed in %m: \347\255\211\345\276\205\345\220\210\346\263\225 read request \346\227\266\344\273\273\345\212\241\346\217\220\345\211\215\347\246\273\345\274\200 busy\357\274\232busy=%b error=%b code=%0d\n",6, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.wait_for_read_request", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000)
                             , '#',1,(IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__busy)
                             , '#',1,vlSelfRef.tb_s2a_backend_fault_recovery__DOT__error
                             , '#',3,(IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__error_code));
                VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 321, "", false);
            }
            __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_read_request__88__wait_index 
                = ((IData)(1U) + __Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_read_request__88__wait_index);
        }
        __Vlabel8: ;
    }
    if (VL_UNLIKELY(((1U & (~ (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__wait_for_read_request__88__request_found)))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:325: Assertion failed in %m: backend \346\234\252\345\234\250\351\231\220\345\256\232\345\221\250\346\234\237\345\206\205\345\217\221\345\207\272\347\234\237\345\256\236 read request\n",3, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.wait_for_read_request", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 325, "", false);
    }
    VL_WRITEF_NX("S2A_RETRY_CASE after=csr_timeout_ack request=pending_read next=soft_reset start_accepted=1\n",0);
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__unnamedblk1__DOT__reads_before 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__memory_read_handshakes;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__unnamedblk1__DOT__writes_before 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__memory_write_side_effects;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__91__value = 2U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__91__address = 0U;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         206);
    if (VL_UNLIKELY(((1U & (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__csr_ready)))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:207: Assertion failed in %m: CSR \345\206\231\345\205\245\346\234\252 ready\357\274\232addr=%02h\n",4, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.write_csr", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , '#',8,(IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__91__address));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 207, "", false);
    }
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_write = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__91__address;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_wdata 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__write_csr__91__value;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e288__0(vlSelf, 
                                                                         "@(posedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e288__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(posedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         212);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                         nullptr, "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                         213);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         214);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_write = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_wdata = 0U;
    vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__92__phase_name = "timeout ACK \345\220\216\351\207\215\345\220\257\345\206\215 soft_reset"s;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__92__expected_head_valid = 0U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__92__expected_error_code = 0U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__92__expected_status = 0U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__92__status_value = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__92__error_value = 0;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__93__address = 4U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__93__value = 0;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         224);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_write = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__93__address;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_wdata = 0U;
    co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                         nullptr, "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                         229);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__93__value 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_rdata;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         231);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr = 0U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__92__status_value 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__93__value;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__94__address = 8U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__94__value = 0;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         224);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_write = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__94__address;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_wdata = 0U;
    co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                         nullptr, "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                         229);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__94__value 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_rdata;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         231);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr = 0U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__92__error_value 
        = __Vtask_tb_s2a_backend_fault_recovery__DOT__read_csr__94__value;
    if (VL_UNLIKELY((((0x0000000fU & __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__92__status_value) 
                      != (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__92__expected_status))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:249: Assertion failed in %m: %s STATUS \344\270\215\345\214\271\351\205\215\357\274\232\346\234\237\346\234\233=%b \345\256\236\351\231\205=%b\n",6, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.check_status", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , 'S',&(vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__92__phase_name)
                     , '#',4,(IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__92__expected_status)
                     , '#',4,(0x0000000fU & __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__92__status_value));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 249, "", false);
    }
    if (VL_UNLIKELY((((7U & __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__92__error_value) 
                      != (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__92__expected_error_code))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:253: Assertion failed in %m: %s ERROR_CODE \344\270\215\345\214\271\351\205\215\357\274\232\346\234\237\346\234\233=%0d \345\256\236\351\231\205=%0d\n",6, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.check_status", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , 'S',&(vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__92__phase_name)
                     , '#',3,(IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__92__expected_error_code)
                     , '#',3,(7U & __Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__92__error_value));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 253, "", false);
    }
    if (VL_UNLIKELY((((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__head_output_valid) 
                      != (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__92__expected_head_valid))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:257: Assertion failed in %m: %s head_output_valid \344\270\215\345\214\271\351\205\215\357\274\232\346\234\237\346\234\233=%b \345\256\236\351\231\205=%b\n",6, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.check_status", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , 'S',&(vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__92__phase_name)
                     , '#',1,(IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__92__expected_head_valid)
                     , '#',1,vlSelfRef.tb_s2a_backend_fault_recovery__DOT__head_output_valid);
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 257, "", false);
    }
    if (VL_UNLIKELY(((((((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__busy) 
                         != (1U & (IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__92__expected_status))) 
                        | ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__done) 
                           != (1U & ((IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__92__expected_status) 
                                     >> 1U)))) | ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__error) 
                                                  != 
                                                  (1U 
                                                   & ((IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__92__expected_status) 
                                                      >> 2U)))) 
                      | ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__buffer_owner_pl) 
                         != (1U & ((IData)(__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__92__expected_status) 
                                   >> 3U))))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:264: Assertion failed in %m: %s CSR/status \350\276\223\345\207\272\344\270\216\347\212\266\346\200\201\344\275\215\344\270\215\344\270\200\350\207\264\n",4, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.check_status", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , 'S',&(vlSelfRef.__Vtask_tb_s2a_backend_fault_recovery__DOT__check_status__92__phase_name));
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 264, "", false);
    }
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_no_late_effects__95__writes_before 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__unnamedblk1__DOT__writes_before;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_no_late_effects__95__reads_before 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__unnamedblk1__DOT__reads_before;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_no_late_effects__95__quiet_index = 0;
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         419);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__automatic_read_responses = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__manual_mem_error_code = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__manual_mem_ready = 1U;
    __Vtask_tb_s2a_backend_fault_recovery__DOT__check_no_late_effects__95__quiet_index = 0U;
    while (VL_GTS_III(32, 3U, __Vtask_tb_s2a_backend_fault_recovery__DOT__check_no_late_effects__95__quiet_index)) {
        Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e288__0(vlSelf, 
                                                                             "@(posedge tb_s2a_backend_fault_recovery.clk)");
        co_await vlSelfRef.__VtrigSched_h3193e288__0.trigger(0U, 
                                                             nullptr, 
                                                             "@(posedge tb_s2a_backend_fault_recovery.clk)", 
                                                             "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                             424);
        vlSelfRef.__Vm_traceActivity[3U] = 1U;
        co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                             nullptr, 
                                             "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                             425);
        vlSelfRef.__Vm_traceActivity[3U] = 1U;
        if (VL_UNLIKELY(((((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid) 
                           | ((0U != (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__backend_memory_error_code)) 
                              & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__memory_handshake))) 
                          | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_write))))) {
            VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:427: Assertion failed in %m: \345\217\226\346\266\210\345\220\216\345\207\272\347\216\260\350\277\237\345\210\260\350\257\267\346\261\202\346\210\226 memory error event\n",3, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.check_no_late_effects", 'T',-9
                         , '#',64,VL_TIME_UNITED_Q(1000));
            VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 427, "", false);
        }
        if (VL_UNLIKELY((((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__memory_read_handshakes 
                           != __Vtask_tb_s2a_backend_fault_recovery__DOT__check_no_late_effects__95__reads_before) 
                          | (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__memory_write_side_effects 
                             != __Vtask_tb_s2a_backend_fault_recovery__DOT__check_no_late_effects__95__writes_before))))) {
            VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:431: Assertion failed in %m: \345\217\226\346\266\210\345\220\216\345\207\272\347\216\260\350\277\237\345\210\260 read/write memory \345\211\257\344\275\234\347\224\250\n",3, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery.check_no_late_effects", 'T',-9
                         , '#',64,VL_TIME_UNITED_Q(1000));
            VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 431, "", false);
        }
        __Vtask_tb_s2a_backend_fault_recovery__DOT__check_no_late_effects__95__quiet_index 
            = ((IData)(1U) + __Vtask_tb_s2a_backend_fault_recovery__DOT__check_no_late_effects__95__quiet_index);
    }
    Vtb_s2a_backend_fault_recovery___024root____VbeforeTrig_h3193e339__0(vlSelf, 
                                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)");
    co_await vlSelfRef.__VtrigSched_h3193e339__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_backend_fault_recovery.clk)", 
                                                         "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                                         434);
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__manual_mem_ready = 0U;
    VL_WRITEF_NX("S2A_CANCEL_CASE kind=soft_reset request=pending_read cancelled=1 ack_restart=ready\n",0);
    if (VL_UNLIKELY(((0U != vlSelfRef.tb_s2a_backend_fault_recovery__DOT__memory_write_side_effects)))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_backend_fault_recovery.sv:649: Assertion failed in %m: \345\256\232\345\220\221\351\224\231\350\257\257/\345\217\226\346\266\210\346\265\213\350\257\225\344\270\215\345\272\224\346\217\220\344\272\244 output writes\357\274\232%0d\n",4, 'M',vlSymsp->name(),"tb_s2a_backend_fault_recovery", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , '~',32,vlSelfRef.tb_s2a_backend_fault_recovery__DOT__memory_write_side_effects);
        VL_STOP_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 649, "", false);
    }
    VL_WRITEF_NX("PASS_S2A_BACKEND_FAULT_CANCEL_RECOVERY reads=%0d writes=%0d\n",2
                 , '~',32,vlSelfRef.tb_s2a_backend_fault_recovery__DOT__memory_read_handshakes
                 , '~',32,vlSelfRef.tb_s2a_backend_fault_recovery__DOT__memory_write_side_effects);
    VL_FINISH_MT("D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 653, "");
    vlSelfRef.__Vm_traceActivity[3U] = 1U;
    co_return;
}

VlCoroutine Vtb_s2a_backend_fault_recovery___024root___eval_initial__TOP__Vtiming__2(Vtb_s2a_backend_fault_recovery___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root___eval_initial__TOP__Vtiming__2\n"); );
    Vtb_s2a_backend_fault_recovery__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    while (VL_LIKELY(!vlSymsp->_vm_contextp__->gotFinish())) {
        co_await vlSelfRef.__VdlySched.delay(0x0000000000001388ULL, 
                                             nullptr, 
                                             "D:\\FPGA_Competition\\sim\\tb_s2a_backend_fault_recovery.sv", 
                                             57);
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__clk 
            = (1U & (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__clk)));
    }
    co_return;
}

bool Vtb_s2a_backend_fault_recovery___024root___trigger_anySet__act(const VlUnpacked<QData/*63:0*/, 1> &in) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root___trigger_anySet__act\n"); );
    // Locals
    IData/*31:0*/ n;
    // Body
    n = 0U;
    do {
        if (in[n]) {
            return (1U);
        }
        n = ((IData)(1U) + n);
    } while ((1U > n));
    return (0U);
}

extern const VlWide<43>/*1375:0*/ Vtb_s2a_backend_fault_recovery__ConstPool__CONST_h3efedef1_0;

void Vtb_s2a_backend_fault_recovery___024root___act_comb__TOP__0(Vtb_s2a_backend_fault_recovery___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root___act_comb__TOP__0\n"); );
    Vtb_s2a_backend_fault_recovery__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_5;
    __VdfgRegularize_h6e95ff9d_0_5 = 0;
    VlWide<3>/*64:0*/ __VdfgRegularize_h6e95ff9d_0_6;
    VL_ZERO_W(65, __VdfgRegularize_h6e95ff9d_0_6);
    VlWide<3>/*95:0*/ __Vtemp_4;
    VlWide<3>/*95:0*/ __Vtemp_5;
    VlWide<3>/*95:0*/ __Vtemp_6;
    VlWide<3>/*95:0*/ __Vtemp_7;
    VlWide<3>/*95:0*/ __Vtemp_8;
    VlWide<3>/*95:0*/ __Vtemp_9;
    VlWide<3>/*95:0*/ __Vtemp_10;
    VlWide<3>/*95:0*/ __Vtemp_11;
    VlWide<3>/*95:0*/ __Vtemp_12;
    VlWide<3>/*95:0*/ __Vtemp_13;
    VlWide<3>/*95:0*/ __Vtemp_14;
    VlWide<3>/*95:0*/ __Vtemp_15;
    VlWide<4>/*127:0*/ __Vtemp_17;
    VlWide<4>/*127:0*/ __Vtemp_18;
    VlWide<4>/*127:0*/ __Vtemp_19;
    VlWide<3>/*95:0*/ __Vtemp_24;
    VlWide<3>/*95:0*/ __Vtemp_25;
    VlWide<3>/*95:0*/ __Vtemp_26;
    VlWide<4>/*127:0*/ __Vtemp_28;
    VlWide<4>/*127:0*/ __Vtemp_29;
    VlWide<4>/*127:0*/ __Vtemp_30;
    VlWide<3>/*95:0*/ __Vtemp_35;
    VlWide<3>/*95:0*/ __Vtemp_36;
    VlWide<3>/*95:0*/ __Vtemp_37;
    VlWide<4>/*127:0*/ __Vtemp_39;
    VlWide<4>/*127:0*/ __Vtemp_40;
    VlWide<4>/*127:0*/ __Vtemp_41;
    VlWide<3>/*95:0*/ __Vtemp_46;
    VlWide<3>/*95:0*/ __Vtemp_47;
    VlWide<3>/*95:0*/ __Vtemp_48;
    VlWide<4>/*127:0*/ __Vtemp_50;
    VlWide<4>/*127:0*/ __Vtemp_51;
    VlWide<4>/*127:0*/ __Vtemp_52;
    VlWide<3>/*95:0*/ __Vtemp_57;
    VlWide<3>/*95:0*/ __Vtemp_58;
    VlWide<3>/*95:0*/ __Vtemp_59;
    VlWide<4>/*127:0*/ __Vtemp_61;
    VlWide<4>/*127:0*/ __Vtemp_62;
    VlWide<4>/*127:0*/ __Vtemp_63;
    VlWide<3>/*95:0*/ __Vtemp_68;
    VlWide<3>/*95:0*/ __Vtemp_69;
    VlWide<3>/*95:0*/ __Vtemp_70;
    VlWide<4>/*127:0*/ __Vtemp_72;
    VlWide<4>/*127:0*/ __Vtemp_73;
    VlWide<4>/*127:0*/ __Vtemp_74;
    VlWide<3>/*95:0*/ __Vtemp_79;
    VlWide<3>/*95:0*/ __Vtemp_80;
    VlWide<3>/*95:0*/ __Vtemp_81;
    VlWide<4>/*127:0*/ __Vtemp_83;
    VlWide<4>/*127:0*/ __Vtemp_84;
    VlWide<4>/*127:0*/ __Vtemp_85;
    VlWide<3>/*95:0*/ __Vtemp_90;
    VlWide<3>/*95:0*/ __Vtemp_91;
    VlWide<3>/*95:0*/ __Vtemp_92;
    VlWide<4>/*127:0*/ __Vtemp_94;
    VlWide<4>/*127:0*/ __Vtemp_95;
    VlWide<4>/*127:0*/ __Vtemp_96;
    VlWide<3>/*95:0*/ __Vtemp_101;
    VlWide<3>/*95:0*/ __Vtemp_102;
    VlWide<3>/*95:0*/ __Vtemp_103;
    VlWide<4>/*127:0*/ __Vtemp_105;
    VlWide<4>/*127:0*/ __Vtemp_106;
    VlWide<4>/*127:0*/ __Vtemp_107;
    VlWide<3>/*95:0*/ __Vtemp_113;
    VlWide<3>/*95:0*/ __Vtemp_114;
    VlWide<3>/*95:0*/ __Vtemp_116;
    VlWide<3>/*95:0*/ __Vtemp_117;
    // Body
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__csr_ready 
        = (1U & (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__hard_reset)));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_wstrb = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_wstrb = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_wstrb = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_wstrb = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__backend_rsp_valid 
        = ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_pending) 
           & ((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__hard_reset)) 
              & ((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__backend_abort)) 
                 & (1U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_target_latched)))));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__backend_rsp_valid 
        = ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_pending) 
           & ((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__hard_reset)) 
              & ((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__backend_abort)) 
                 & (3U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_target_latched)))));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__backend_rsp_valid 
        = ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_pending) 
           & ((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__hard_reset)) 
              & ((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__backend_abort)) 
                 & (2U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_target_latched)))));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_rstrb = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_rstrb = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_wdata = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_addr = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_wdata = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__selected_read_lane 
        = (0x0000000fU & ((IData)(1U) << (3U & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source_address_latched)));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_rstrb = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_wdata = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_rdata = 0U;
    if (((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid) 
         & (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_write)))) {
        if ((0U == (3U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr)))) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_rdata 
                = ((0x00000080U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                    ? 0U : ((0x00000040U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                             ? 0U : ((0x00000020U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                      ? ((0x00000010U 
                                          & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                          ? ((8U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                              ? ((4U 
                                                  & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                  ? 0U
                                                  : 
                                                 ((2U 
                                                   & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                   ? 0U
                                                   : 
                                                  ((1U 
                                                    & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                    ? 0U
                                                    : 0x00004f38U)))
                                              : ((4U 
                                                  & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                  ? 
                                                 ((2U 
                                                   & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                   ? 0U
                                                   : 
                                                  ((1U 
                                                    & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                    ? 0U
                                                    : 0x01ad5e80U))
                                                  : 
                                                 ((2U 
                                                   & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                   ? 0U
                                                   : 
                                                  ((1U 
                                                    & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                    ? 0U
                                                    : 0x000013ceU))))
                                          : ((8U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                              ? ((4U 
                                                  & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                  ? 
                                                 ((2U 
                                                   & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                   ? 0U
                                                   : 
                                                  ((1U 
                                                    & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                    ? 0U
                                                    : 0x01a46100U))
                                                  : 
                                                 ((2U 
                                                   & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                   ? 0U
                                                   : 
                                                  ((1U 
                                                    & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                    ? 0U
                                                    : vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__timeout_cycles)))
                                              : ((4U 
                                                  & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                  ? 
                                                 ((2U 
                                                   & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                   ? 0U
                                                   : 
                                                  ((1U 
                                                    & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                    ? 0U
                                                    : 0x01adadb8U))
                                                  : 
                                                 ((2U 
                                                   & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                   ? 0U
                                                   : 
                                                  ((1U 
                                                    & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                    ? 0U
                                                    : 0x01000000U)))))
                                      : ((0x00000010U 
                                          & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                          ? ((8U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                              ? ((4U 
                                                  & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                  ? 
                                                 ((2U 
                                                   & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                   ? 0U
                                                   : 
                                                  ((1U 
                                                    & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                    ? 0U
                                                    : vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__weight_bytes))
                                                  : 
                                                 ((2U 
                                                   & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                   ? 0U
                                                   : 
                                                  ((1U 
                                                    & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                    ? 0U
                                                    : vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__weight_addr)))
                                              : ((4U 
                                                  & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                  ? 
                                                 ((2U 
                                                   & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                   ? 0U
                                                   : 
                                                  ((1U 
                                                    & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                    ? 0U
                                                    : vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__input_bytes))
                                                  : 
                                                 ((2U 
                                                   & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                   ? 0U
                                                   : 
                                                  ((1U 
                                                    & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                    ? 0U
                                                    : vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__input_addr))))
                                          : ((8U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                              ? ((4U 
                                                  & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                  ? 
                                                 ((2U 
                                                   & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                   ? 0U
                                                   : 
                                                  ((1U 
                                                    & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                    ? 0U
                                                    : vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__frame_id))
                                                  : 
                                                 ((2U 
                                                   & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                   ? 0U
                                                   : 
                                                  ((1U 
                                                    & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                    ? 0U
                                                    : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__error_code))))
                                              : ((4U 
                                                  & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                  ? 
                                                 ((2U 
                                                   & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                   ? 0U
                                                   : 
                                                  ((1U 
                                                    & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr))
                                                    ? 0U
                                                    : 
                                                   ((((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__buffer_owner_pl) 
                                                      << 3U) 
                                                     | ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__error) 
                                                        << 2U)) 
                                                    | (((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__done) 
                                                        << 1U) 
                                                       | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__busy)))))
                                                  : 0U))))));
        }
    }
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_rstrb = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__selected_input_lane = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__selected_word_address 
        = (0xfffffffcU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source_address_latched);
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_addr = 0U;
    if ((4U > (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__read_tap_index))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__selected_input_lane 
            = (0x0000000fU & ((IData)(1U) << (3U & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched
                                              [(3U 
                                                & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__read_tap_index))])));
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_addr = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__selected_input_word_address = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__selected_input_word_address 
            = (0xfffffffcU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched
               [(3U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__read_tap_index))]);
    } else {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_addr = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__selected_input_word_address = 0U;
    }
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_result_valid = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_result_ready 
        = (((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__hard_reset)) 
            & (2U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))) 
           & (0x13U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__state)));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_result_ready 
        = (((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__hard_reset)) 
            & (3U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))) 
           & (6U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__state)));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_result_ready 
        = (((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__hard_reset)) 
            & (4U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))) 
           & (7U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__state)));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_result_ready 
        = (((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__hard_reset)) 
            & (5U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))) 
           & (5U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__state)));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_write = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_write = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_write = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_write = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__backend_rsp_valid 
        = ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_pending) 
           & ((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__hard_reset)) 
              & ((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__backend_abort)) 
                 & (0U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_target_latched)))));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_valid = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_valid = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_valid = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_valid = 0U;
    if ((1U & ((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__hard_reset)) 
               & (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__backend_abort))))) {
        if ((1U != (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__state))) {
            if ((4U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__state))) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_wstrb 
                    = (0x0000000fU & ((IData)(1U) << 
                                      (3U & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_address_latched)));
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_wdata 
                    = VL_SHIFTL_III(32,32,32, (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__result_value_latched), 
                                    (0x00000018U & 
                                     (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_address_latched 
                                      << 3U)));
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_write = 1U;
            }
        }
        if ((1U != (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__state))) {
            if ((3U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__state))) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_wstrb 
                    = (0x0000000fU & ((IData)(1U) << 
                                      (3U & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__output_address_latched)));
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_wdata 
                    = VL_SHIFTL_III(32,32,32, (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__copied_value_latched), 
                                    (0x00000018U & 
                                     (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__output_address_latched 
                                      << 3U)));
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_write = 1U;
            }
        }
        if ((2U != (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__state))) {
            if ((5U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__state))) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_wstrb 
                    = (0x0000000fU & ((IData)(1U) << 
                                      (3U & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_address_latched)));
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_wdata 
                    = VL_SHIFTL_III(32,32,32, (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__result_value_latched), 
                                    (0x00000018U & 
                                     (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_address_latched 
                                      << 3U)));
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_write = 1U;
            }
        }
        if ((1U & (~ ((4U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__state)) 
                      || (8U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__state)))))) {
            if ((0x10U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__state))) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_wstrb 
                    = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__request_strobe_latched;
            }
        }
        if ((1U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__state))) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_rstrb 
                = (0x0000000fU & ((IData)(1U) << (3U 
                                                  & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__source_address_latched)));
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_addr 
                = (0xfffffffcU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__source_address_latched);
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_valid = 1U;
        } else if ((3U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__state))) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_addr 
                = (0xfffffffcU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__output_address_latched);
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_valid = 1U;
        }
        if (((4U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__state)) 
             || (8U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__state)))) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_rstrb 
                = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__request_strobe_latched;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_write = 0U;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_valid = 1U;
        } else if ((0x10U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__state))) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_write = 1U;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_valid = 1U;
        }
        if ((2U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__state))) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_rstrb 
                = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__selected_read_lane;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_addr 
                = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__selected_word_address;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_valid = 1U;
        } else if ((5U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__state))) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_addr 
                = (0xfffffffcU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_address_latched);
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_valid = 1U;
        }
        if ((1U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__state))) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_rstrb 
                = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__selected_input_lane;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_addr 
                = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__selected_input_word_address;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_valid = 1U;
        } else if ((4U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__state))) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_addr 
                = (0xfffffffcU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_address_latched);
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_valid = 1U;
        }
    }
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__start_ready 
        = ((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__hard_reset)) 
           & ((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__backend_abort)) 
              & (0U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__state))));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__start_ready 
        = ((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__hard_reset)) 
           & ((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__backend_abort)) 
              & (0U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__state))));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__start_ready 
        = ((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__hard_reset)) 
           & ((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__backend_abort)) 
              & (0U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__state))));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__start_ready 
        = ((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__hard_reset)) 
           & ((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__backend_abort)) 
              & (0U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__state))));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_wdata = 0U;
    if ((4U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))) {
        if ((1U & (~ ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                      >> 1U)))) {
            if ((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_result_valid 
                    = ((5U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__state)) 
                       & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_result_ready));
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_wdata 
                    = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_wdata;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_wdata 
                    = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_wdata;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_addr = 0U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_addr 
                    = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_addr;
            } else {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_result_valid 
                    = ((7U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__state)) 
                       & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_result_ready));
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_wdata 
                    = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_wdata;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_wdata 
                    = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_wdata;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_addr = 0U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_addr 
                    = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_addr;
            }
        } else {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_wdata 
                = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_wdata;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_addr = 0U;
        }
    } else if ((2U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))) {
        if ((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_result_valid 
                = ((6U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__state)) 
                   & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_result_ready));
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_wdata 
                = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_wdata;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_wdata 
                = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_wdata;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_addr = 0U;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_addr 
                = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_addr;
        } else {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_result_valid 
                = ((0x13U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__state)) 
                   & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_result_ready));
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_wdata 
                = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__request_wdata_latched;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_wdata 
                = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_wdata;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_addr = 0U;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_addr 
                = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__request_address_latched;
        }
    } else {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_wdata 
            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_wdata;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_addr = 0U;
    }
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_addr 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_addr;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__patch_plane_bytes 
        = ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__patch_height)) 
           * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__patch_width)));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_input_y = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_input_x = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_in_bounds = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_advance = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_source_offset = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_source_address_wide = 0ULL;
    if (((0ULL != vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__patch_plane_bytes) 
         & (0U != vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__patch_width))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_input_y 
            = ((((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_y)) 
                 * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__stride_y_latched))) 
                + (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_y))) 
               - (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__pad_top_latched)));
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_input_x 
            = ((((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_x)) 
                 * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__stride_x_latched))) 
                + (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_x))) 
               - (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__pad_left_latched)));
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_in_bounds 
            = (((VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_input_y) 
                 & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_input_y, (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_height_latched)))) 
                & VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_input_x)) 
               & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_input_x, (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_width_latched))));
        if (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_in_bounds) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_source_offset 
                = (((((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_channel)) 
                      * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_height_latched))) 
                     + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_input_y) 
                    * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_width_latched))) 
                   + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_input_x);
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_source_address_wide 
                = ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_base_latched)) 
                   + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_source_offset);
        }
    }
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_area 
        = (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_height_latched 
           * vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_width_latched);
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_next_input_channel 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_input_channel;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_next_kernel_y 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_y;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_next_reduction_index 
        = ((IData)(1U) + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_reduction_index);
    if ((((IData)(1U) + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_x) 
         >= vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_width_latched)) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_next_kernel_x = 0U;
        if ((((IData)(1U) + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_y) 
             >= vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_height_latched)) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_next_kernel_y = 0U;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_next_input_channel 
                = ((IData)(1U) + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_input_channel);
        } else {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_next_kernel_y 
                = ((IData)(1U) + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_y);
        }
    } else {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_next_kernel_x 
            = ((IData)(1U) + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_x);
    }
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_point_y 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_scan_y;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_point_x 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_scan_x;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_input_channel 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_input_channel;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_kernel_y 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_y;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_kernel_x 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_x;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_reduction_index 
        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_reduction_index;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_input_y = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_input_x = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_tap_in_bounds = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_feature_index_wide = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_feature_index = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_enable = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_bad_argument = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_overflow = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[0U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[0U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[0U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[0U] = 0ULL;
    if ((0U < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[0U] 
            = ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[0U] 
            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_read_byte[0U];
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[0U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[0U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[0U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[0U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[0U])));
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[0U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[0U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[0U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[0U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[0U])))));
        if (((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[0U]) 
                | (0x80U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[0U])))) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[0U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[0U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_overflow = 1U;
        }
    }
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[1U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[1U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[1U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[1U] = 0ULL;
    if ((1U < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[1U] 
            = ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[1U] 
            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_read_byte[1U];
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[1U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[1U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[1U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[1U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[1U])));
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[1U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[1U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[1U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[1U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[1U])))));
        if (((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[1U]) 
                | (0x80U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[1U])))) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[1U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[1U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_overflow = 1U;
        }
    }
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[2U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[2U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[2U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[2U] = 0ULL;
    if ((2U < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[2U] 
            = ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[2U] 
            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_read_byte[2U];
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[2U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[2U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[2U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[2U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[2U])));
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[2U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[2U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[2U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[2U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[2U])))));
        if (((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[2U]) 
                | (0x80U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[2U])))) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[2U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[2U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_overflow = 1U;
        }
    }
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[3U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[3U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[3U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[3U] = 0ULL;
    if ((3U < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[3U] 
            = ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[3U] 
            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_read_byte[3U];
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[3U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[3U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[3U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[3U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[3U])));
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[3U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[3U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[3U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[3U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[3U])))));
        if (((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[3U]) 
                | (0x80U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[3U])))) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[3U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[3U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_overflow = 1U;
        }
    }
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[4U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[4U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[4U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[4U] = 0ULL;
    if ((4U < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[4U] 
            = ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[4U] 
            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_read_byte[4U];
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[4U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[4U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[4U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[4U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[4U])));
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[4U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[4U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[4U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[4U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[4U])))));
        if (((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[4U]) 
                | (0x80U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[4U])))) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[4U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[4U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_overflow = 1U;
        }
    }
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[5U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[5U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[5U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[5U] = 0ULL;
    if ((5U < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[5U] 
            = ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[5U] 
            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_read_byte[5U];
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[5U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[5U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[5U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[5U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[5U])));
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[5U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[5U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[5U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[5U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[5U])))));
        if (((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[5U]) 
                | (0x80U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[5U])))) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[5U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[5U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_overflow = 1U;
        }
    }
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[6U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[6U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[6U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[6U] = 0ULL;
    if ((6U < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[6U] 
            = ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[6U] 
            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_read_byte[6U];
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[6U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[6U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[6U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[6U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[6U])));
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[6U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[6U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[6U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[6U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[6U])))));
        if (((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[6U]) 
                | (0x80U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[6U])))) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[6U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[6U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_overflow = 1U;
        }
    }
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[7U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[7U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[7U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[7U] = 0ULL;
    if ((7U < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count)) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[7U] 
            = ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[7U] 
            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_read_byte[7U];
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[7U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[7U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[7U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[7U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[7U])));
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[7U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[7U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[7U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[7U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[7U])))));
        if (((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[7U]) 
                | (0x80U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[7U])))) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[7U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[7U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_overflow = 1U;
        }
    }
    if (((0x0bU == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__state)) 
         | (0x0cU == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__state)))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_point_y 
            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_scan_y;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_point_x 
            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_scan_x;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_input_channel = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_kernel_y = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_kernel_x = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_reduction_index = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_enable = 1U;
    } else if ((0x0dU == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__state))) {
        if ((((((IData)(1U) + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_reduction_index) 
               < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_latched) 
              & (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_bad_argument))) 
             & (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_overflow)))) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_point_y 
                = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_scan_y;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_point_x 
                = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_scan_x;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_input_channel 
                = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_next_input_channel;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_kernel_y 
                = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_next_kernel_y;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_kernel_x 
                = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_next_kernel_x;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_reduction_index 
                = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_next_reduction_index;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_enable = 1U;
        }
    }
    if (((0U != vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_area) 
         & (0U != vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__tile_width))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_input_y 
            = (((((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_y)) 
                  * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__stride_y_latched))) 
                 + ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_point_y)) 
                    * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__stride_y_latched)))) 
                + (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_kernel_y))) 
               - (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__pad_top_latched)));
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_input_x 
            = (((((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_x)) 
                  * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__stride_x_latched))) 
                 + ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_point_x)) 
                    * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__stride_x_latched)))) 
                + (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_kernel_x))) 
               - (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__pad_left_latched)));
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_tap_in_bounds 
            = (((VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_input_y) 
                 & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_input_y, (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_height_latched)))) 
                & VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_input_x)) 
               & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_input_x, (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_width_latched))));
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_feature_index_wide 
            = (((((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_input_channel)) 
                  * vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__patch_plane_bytes) 
                 + ((((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_point_y)) 
                      * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__stride_y_latched))) 
                     + (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_kernel_y))) 
                    * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__patch_width)))) 
                + ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_point_x)) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__stride_x_latched)))) 
               + (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_kernel_x)));
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_feature_index 
            = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_read_feature_index_wide);
    }
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mapped_response_error = 6U;
    if ((0U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_error_latched))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mapped_response_error = 0U;
    } else if ((((1U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_error_latched)) 
                 | (2U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_error_latched))) 
                | (6U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_error_latched)))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mapped_response_error 
            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_error_latched;
    }
    if ((((3U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__state)) 
          & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_index 
             < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__patch_byte_count)) 
         & (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_in_bounds)))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_advance = 1U;
    } else if ((((5U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__state)) 
                 & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__backend_rsp_valid)) 
                & (0U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mapped_response_error)))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_advance = 1U;
    }
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid 
        = (((4U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
             ? ((~ ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                    >> 1U)) & ((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                                ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_valid)
                                : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_valid)))
             : (((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                 >> 1U) & ((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                            ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_valid)
                            : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_valid)))) 
           & ((~ ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_pending) 
                  | ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__hard_reset) 
                     | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__backend_abort)))) 
              & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__buffer_owner_pl)));
    if ((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_op 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OP
            [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor];
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_input_count 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_COUNT
            [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor];
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_base 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_ADDRESS
            [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor];
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_length 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_LENGTH_BYTES
            [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor];
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_n 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_N
            [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor];
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_c 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_C
            [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor];
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_h 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_H
            [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor];
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_w 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_W
            [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor];
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_ALIAS_LAYER_INDEX
            [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor];
    } else {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_op = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_input_count = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_base = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_length = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_n = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_c = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_h = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_w = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index = 0U;
    }
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_plane_elements 
        = ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_h)) 
           * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_w)));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_batch_elements 
        = ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_c)) 
           * vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_plane_elements);
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_element_count 
        = ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_n)) 
           * vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_batch_elements);
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_y = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_x = 0U;
    if ((((0ULL != vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_plane_elements) 
          & (0ULL != vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_batch_elements)) 
         & (0U != (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_w)))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel 
            = (IData)(VL_MODDIV_QQQ(64, VL_DIV_QQQ(64, (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_element_index)), vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_plane_elements), (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_c))));
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_y 
            = (IData)(VL_MODDIV_QQQ(64, VL_DIV_QQQ(64, (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_element_index)), (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_w))), (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_h))));
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_x 
            = VL_MODDIV_III(32, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_element_index, (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_w));
    }
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_base[0U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_length[0U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_n[0U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_c[0U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_route_start[0U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_route_end[0U] = 0U;
    if ((0U < (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_input_count))) {
        if (((0U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor)) 
             & (~ (IData)(vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_KIND
                          [((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
                             ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor)
                             : 0U)][0U])))) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_base[0U] = 0U;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_length[0U] = 0x0007ec00U;
        } else {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_base[0U] 
                = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_ADDRESS
                [((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
                   ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor)
                   : 0U)][0U];
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_length[0U] 
                = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_LENGTH_BYTES
                [((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
                   ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor)
                   : 0U)][0U];
        }
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_n[0U] 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_N
            [((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
               ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor)
               : 0U)][0U];
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_c[0U] 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_C
            [((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
               ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor)
               : 0U)][0U];
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U] 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_H
            [((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
               ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor)
               : 0U)][0U];
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U] 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_W
            [((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
               ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor)
               : 0U)][0U];
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_route_start[0U] 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_ROUTE_CHANNEL_START
            [((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
               ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor)
               : 0U)][0U];
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_route_end[0U] 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_ROUTE_CHANNEL_END
            [((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
               ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor)
               : 0U)][0U];
    }
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_base[1U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_length[1U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_n[1U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_c[1U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[1U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[1U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_route_start[1U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_route_end[1U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mq_index 
        = (((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
             ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
            [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor]
             : 0U) + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel);
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__is_alias_row 
        = (4U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_op));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_valid = 0U;
    if (((((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__is_alias_row) 
           & (~ ((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor)) 
                 && vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_MEMORY_WRITE_REQUIRED
                 [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor]))) 
          & ((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor)) 
             && vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_ALLOCATION_KIND
             [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor])) 
         & (0x26U > (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index)))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_output_plane_elements 
            = ((QData)((IData)(((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index))
                                 ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_H
                                [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index]
                                 : 0U))) * (QData)((IData)(
                                                           ((0x25U 
                                                             >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index))
                                                             ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_W
                                                            [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index]
                                                             : 0U))));
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_output_element_count 
            = (((QData)((IData)(((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index))
                                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_N
                                 [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index]
                                  : 0U))) * (QData)((IData)(
                                                            ((0x25U 
                                                              >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index))
                                                              ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_C
                                                             [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index]
                                                              : 0U)))) 
               * vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_output_plane_elements);
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_valid 
            = ((((((((((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index))
                        ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_TENSOR_INDEX
                       [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index]
                        : 0U) == ((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
                                   ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_TENSOR_INDEX
                                  [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor]
                                   : 0U)) & (((0x25U 
                                               >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index))
                                               ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_ADDRESS
                                              [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index]
                                               : 0U) 
                                             == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_base)) 
                    & (((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index))
                         ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_LENGTH_BYTES
                        [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index]
                         : 0U) == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_length)) 
                   & (((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index))
                        ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_N
                       [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index]
                        : 0U) == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_n))) 
                  & (((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index))
                       ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_C
                      [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index]
                       : 0U) == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_c))) 
                 & (((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index))
                      ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_H
                     [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index]
                      : 0U) == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_h))) 
                & (((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index))
                     ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_W
                    [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index]
                     : 0U) == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_w))) 
               & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_output_element_count 
                  == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_element_count));
    } else {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_output_plane_elements = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_output_element_count = 0ULL;
    }
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__descriptor_valid = 1U;
    if ((((((((((((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
                   ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_LAYER_INDEX
                  [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor]
                   : 0U) != (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor)) 
                | (0U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_input_count))) 
               | (2U < (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_input_count))) 
              | (1U != (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_n))) 
             | (0U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_c))) 
            | (0U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_h))) 
           | (0U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_w))) 
          | (0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_length)) 
         | (0ULL == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_element_count))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__descriptor_valid = 0U;
    }
    if ((1U < (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_input_count))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_base[1U] 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_ADDRESS
            [((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
               ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor)
               : 0U)][1U];
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_length[1U] 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_LENGTH_BYTES
            [((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
               ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor)
               : 0U)][1U];
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_n[1U] 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_N
            [((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
               ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor)
               : 0U)][1U];
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_c[1U] 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_C
            [((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
               ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor)
               : 0U)][1U];
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[1U] 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_H
            [((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
               ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor)
               : 0U)][1U];
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[1U] 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_W
            [((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
               ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor)
               : 0U)][1U];
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_route_start[1U] 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_ROUTE_CHANNEL_START
            [((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
               ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor)
               : 0U)][1U];
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_route_end[1U] 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_ROUTE_CHANNEL_END
            [((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
               ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor)
               : 0U)][1U];
    }
    if ((0U < (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_input_count))) {
        if ((((((1U != vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_n[0U]) 
                | (0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_c[0U])) 
               | (0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U])) 
              | (0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U])) 
             | (0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_length[0U]))) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__descriptor_valid = 0U;
        }
        if (((~ (IData)(vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_KIND
                        [((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
                           ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor)
                           : 0U)][0U])) & (0U != (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor)))) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__descriptor_valid = 0U;
        }
    }
    if ((1U < (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_input_count))) {
        if ((((((1U != vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_n[1U]) 
                | (0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_c[1U])) 
               | (0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[1U])) 
              | (0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[1U])) 
             | (0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_length[1U]))) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__descriptor_valid = 0U;
        }
        if ((1U & (~ (IData)(vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_KIND
                             [((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
                                ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor)
                                : 0U)][1U])))) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__descriptor_valid = 0U;
        }
    }
    if (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__is_alias_row) {
        if ((1U & (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_valid)))) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__descriptor_valid = 0U;
        }
    } else if ((1U & ((~ ((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor)) 
                          && vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_MEMORY_WRITE_REQUIRED
                          [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor])) 
                      | ((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor)) 
                         && vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_ALLOCATION_KIND
                         [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor])))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__descriptor_valid = 0U;
    }
    if ((0U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_op))) {
        vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__map_conv_activation__96__descriptor_activation 
            = ((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_ACTIVATION
               [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor]
                : 0U);
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____VlemCall_0__map_conv_activation 
            = (3U & (0xd0U >> ((IData)(vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__map_conv_activation__96__descriptor_activation) 
                               << 1U)));
        if (((((((1U != (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_input_count)) 
                 | (((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
                      ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                     [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor]
                      : 0U) != (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_c))) 
                | (0x00000c5cU <= vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mq_index)) 
               | (0x00000c5cU < (((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
                                   ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                  [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor]
                                   : 0U) + ((0x25U 
                                             >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
                                             ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                                            [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor]
                                             : 0U)))) 
              | (3U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____VlemCall_0__map_conv_activation))) 
             | (((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_WEIGHT_LAYER_INDEX
                 [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor]
                  : 0U) != ((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
                             ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_LAYER_INDEX
                            [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor]
                             : 0U)))) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__descriptor_valid = 0U;
        }
    } else if (((1U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_op)) 
                | (3U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_op)))) {
        if ((1U != (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_input_count))) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__descriptor_valid = 0U;
        }
    } else if ((2U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_op))) {
        if (((1U != (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_input_count)) 
             & (2U != (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_input_count)))) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__descriptor_valid = 0U;
        }
    } else if ((1U & (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__is_alias_row)))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__descriptor_valid = 0U;
    }
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__descriptor_fault 
        = (1U & (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__descriptor_valid)));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_start_valid 
        = ((((1U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state)) 
             & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__buffer_owner_pl)) 
            & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__descriptor_valid)) 
           & (0U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_op)));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_start_valid 
        = ((((1U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state)) 
             & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__buffer_owner_pl)) 
            & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__descriptor_valid)) 
           & (1U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_op)));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_start_valid 
        = ((((1U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state)) 
             & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__buffer_owner_pl)) 
            & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__descriptor_valid)) 
           & (2U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_op)));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_start_valid 
        = ((((1U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state)) 
             & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__buffer_owner_pl)) 
            & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__descriptor_valid)) 
           & (3U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_op)));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_start_ready 
        = ((1U & (~ ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_op) 
                     >> 2U))) && ((2U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_op))
                                   ? ((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_op))
                                       ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__start_ready)
                                       : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__start_ready))
                                   : ((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_op))
                                       ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__start_ready)
                                       : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__start_ready))));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_rstrb 
        = (((4U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
             ? (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                  ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_rstrb)
                  : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_rstrb)) 
                & (- (IData)((1U & (~ ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                       >> 1U)))))) : 
            (((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
               ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_rstrb)
               : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_rstrb)) 
             & (- (IData)((1U & ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                 >> 1U)))))) & (- (IData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid))));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_write 
        = (((4U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
             ? ((~ ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                    >> 1U)) & ((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                                ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_write)
                                : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_write)))
             : (((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                 >> 1U) & ((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                            ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_write)
                            : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_write)))) 
           & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid));
    __VdfgRegularize_h6e95ff9d_0_6[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_base;
    __VdfgRegularize_h6e95ff9d_0_6[1U] = 0U;
    __VdfgRegularize_h6e95ff9d_0_6[2U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__operator_result_valid = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__operator_error_code = 0U;
    if ((((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__hard_reset)) 
          & (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__backend_abort))) 
         & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__buffer_owner_pl))) {
        if ((4U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))) {
            if ((2U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__operator_result_valid = 1U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__operator_error_code = 6U;
            } else {
                vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__97__code 
                    = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_result_error;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____VlemCall_1__normalize_engine_error 
                    = ((4U & (IData)(vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__97__code))
                        ? (IData)(vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__97__code)
                        : ((2U & (IData)(vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__97__code))
                            ? (IData)(vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__97__code)
                            : ((1U & (IData)(vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__97__code))
                                ? (IData)(vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__97__code)
                                : 0U)));
                if (((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_result_valid) 
                     & (0U != (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____VlemCall_1__normalize_engine_error)))) {
                    vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__98__code 
                        = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_result_error;
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__operator_result_valid = 1U;
                    vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__98__Vfuncout 
                        = ((4U & (IData)(vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__98__code))
                            ? (IData)(vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__98__code)
                            : ((2U & (IData)(vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__98__code))
                                ? (IData)(vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__98__code)
                                : ((1U & (IData)(vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__98__code))
                                    ? (IData)(vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__98__code)
                                    : 0U)));
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__operator_error_code 
                        = vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__98__Vfuncout;
                } else if ((((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_result_valid) 
                             & ((0U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_op)) 
                                | ((1ULL + (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_element_index))) 
                                   >= vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_element_count))) 
                            & (0x00000026U <= ((IData)(1U) 
                                               + (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))))) {
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__operator_result_valid = 1U;
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__operator_error_code = 0U;
                }
            }
        } else if ((2U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))) {
            vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__99__code 
                = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_result_error;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____VlemCall_1__normalize_engine_error 
                = ((4U & (IData)(vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__99__code))
                    ? (IData)(vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__99__code)
                    : ((2U & (IData)(vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__99__code))
                        ? (IData)(vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__99__code)
                        : ((1U & (IData)(vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__99__code))
                            ? (IData)(vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__99__code)
                            : 0U)));
            if (((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_result_valid) 
                 & (0U != (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____VlemCall_1__normalize_engine_error)))) {
                vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__100__code 
                    = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_result_error;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__operator_result_valid = 1U;
                vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__100__Vfuncout 
                    = ((4U & (IData)(vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__100__code))
                        ? (IData)(vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__100__code)
                        : ((2U & (IData)(vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__100__code))
                            ? (IData)(vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__100__code)
                            : ((1U & (IData)(vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__100__code))
                                ? (IData)(vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__100__code)
                                : 0U)));
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__operator_error_code 
                    = vlSelfRef.__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__100__Vfuncout;
            } else if ((((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_result_valid) 
                         & ((0U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_op)) 
                            | ((1ULL + (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_element_index))) 
                               >= vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_element_count))) 
                        & (0x00000026U <= ((IData)(1U) 
                                           + (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))))) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__operator_result_valid = 1U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__operator_error_code = 0U;
            }
        } else if ((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))) {
            if ((1U & ((((0x26U <= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor)) 
                         | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__descriptor_fault)) 
                        | ((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__is_alias_row)) 
                           & (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_start_ready)))) 
                       | ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__is_alias_row) 
                          & (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_valid)))))) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__operator_result_valid = 1U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__operator_error_code = 6U;
            } else if (((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__is_alias_row) 
                        & (0x00000026U <= ((IData)(1U) 
                                           + (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))))) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__operator_result_valid = 1U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__operator_error_code = 0U;
            }
        }
    }
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_inputs_valid 
        = ((9U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__layer_index)
            ? ((2U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_height) 
               & ((2U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width) 
                  & ((2U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_y) 
                     & ((2U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_x) 
                        & ((1U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__darknet_padding_parameter) 
                           & ((0x0080U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_c[0U]) 
                              & ((0x0068U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U]) 
                                 & ((0x0068U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U]) 
                                    & ((0x0080U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_c)) 
                                       & ((0x0034U 
                                           == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_h)) 
                                          & (0x0034U 
                                             == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_w))))))))))))
            : ((0x00000011U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__layer_index)
                ? ((2U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_height) 
                   & ((2U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width) 
                      & ((2U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_y) 
                         & ((2U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_x) 
                            & ((1U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__darknet_padding_parameter) 
                               & ((0x0100U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_c[0U]) 
                                  & ((0x0034U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U]) 
                                     & ((0x0034U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U]) 
                                        & ((0x0100U 
                                            == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_c)) 
                                           & ((0x001aU 
                                               == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_h)) 
                                              & (0x001aU 
                                                 == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_w))))))))))))
                : ((2U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_height) 
                   & ((2U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width) 
                      & ((2U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_y) 
                         & ((2U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_x) 
                            & ((1U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__darknet_padding_parameter) 
                               & ((0x00000019U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__layer_index) 
                                  & ((0x0200U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_c[0U]) 
                                     & ((0x001aU == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U]) 
                                        & ((0x001aU 
                                            == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U]) 
                                           & ((0x0200U 
                                               == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_c)) 
                                              & ((0x000dU 
                                                  == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_h)) 
                                                 & (0x000dU 
                                                    == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_w)))))))))))))));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__output_offset_work 
        = ((0x000000000000001aULL * ((0x000000000000001aULL 
                                      * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel))) 
                                     + (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_y)))) 
           + (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_x)));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_offset_work 
        = ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_x)) 
           + (((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_y)) 
               + ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel)) 
                  * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_h)))) 
              * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_w))));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__output_height_work = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__output_width_work = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__plane_elements_work = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__plane_index_work = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__byte_offset_work = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__address_work = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_output_height = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_output_width = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_channel = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_y = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_x = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_address = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_unused_value = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_error_code = 0U;
    if (((((((0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_c[0U]) 
             | (0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U])) 
            | (0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U])) 
           | (0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_upsample_engine__stride)) 
          | (0x000dU < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U])) 
         | (0x000dU < vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U]))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_error_code = 1U;
    } else {
        if ((2U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_upsample_engine__stride)) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__output_height_work 
                = ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U])) 
                   << 1U);
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__output_width_work 
                = ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U])) 
                   << 1U);
        } else {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__output_height_work 
                = ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U])) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_upsample_engine__stride)));
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__output_width_work 
                = ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U])) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_upsample_engine__stride)));
        }
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_output_height 
            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__output_height_work;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_output_width 
            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__output_width_work;
        if ((((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel 
               >= vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_c[0U]) 
              | ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_y)) 
                 >= vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__output_height_work)) 
             | ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_x)) 
                >= vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__output_width_work))) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_error_code = 1U;
        } else {
            if ((2U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_upsample_engine__stride)) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_y 
                    = (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_y 
                       >> 1U);
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_x 
                    = (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_x 
                       >> 1U);
            } else {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_y 
                    = VL_DIV_III(32, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_y, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_upsample_engine__stride);
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_x 
                    = VL_DIV_III(32, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_x, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_upsample_engine__stride);
            }
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_channel 
                = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__plane_elements_work 
                = (0x000000ffU & ((0x0000000fU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U]) 
                                  * (0x0000000fU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U])));
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__plane_index_work 
                = (0x000000ffU & (((0x0000000fU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_y) 
                                   * (0x0000000fU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U])) 
                                  + (0x0000000fU & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_x)));
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__byte_offset_work 
                = (0x000000ffffffffffULL & (((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel)) 
                                             * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__plane_elements_work))) 
                                            + (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__plane_index_work))));
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__address_work 
                = (0x000001ffffffffffULL & ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_base[0U])) 
                                            + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__byte_offset_work));
            if ((0U != (0x000001ffU & (IData)((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__address_work 
                                               >> 0x20U))))) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_error_code = 2U;
            } else {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_address 
                    = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__address_work);
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_unused_value 
                    = ((0x0547U >= ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__plane_index_work) 
                                    << 3U)) ? (0x000000ffU 
                                               & (((0U 
                                                    == 
                                                    (0x0000001fU 
                                                     & ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__plane_index_work) 
                                                        << 3U)))
                                                    ? 0U
                                                    : 
                                                   (Vtb_s2a_backend_fault_recovery__ConstPool__CONST_h3efedef1_0
                                                    [
                                                    (((IData)(7U) 
                                                      + 
                                                      ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__plane_index_work) 
                                                       << 3U)) 
                                                     >> 5U)] 
                                                    << 
                                                    ((IData)(0x00000020U) 
                                                     - 
                                                     (0x0000001fU 
                                                      & ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__plane_index_work) 
                                                         << 3U))))) 
                                                  | (Vtb_s2a_backend_fault_recovery__ConstPool__CONST_h3efedef1_0
                                                     [
                                                     (0x07ffffffU 
                                                      & ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__plane_index_work) 
                                                         >> 2U))] 
                                                     >> 
                                                     (0x0000001fU 
                                                      & ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__plane_index_work) 
                                                         << 3U)))))
                        : 0U);
            }
        }
    }
    if ((0U != (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_error_code))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_output_height = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_output_width = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_channel = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_y = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_x = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_address = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_unused_value = 0U;
    }
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__extent_y 
        = (0x00000001ffffffffULL & ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U])) 
                                    + (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__darknet_padding_parameter))));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__extent_x 
        = (0x00000001ffffffffULL & ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U])) 
                                    + (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__darknet_padding_parameter))));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_height_work = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_width_work = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_y_step = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_x_step = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_y_work = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_x_work = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__tap_range_error = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_output_height = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_output_width = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_count = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_error_code = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__origin_y = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__origin_x = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_y_work[0U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_index_work[0U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[0U][0U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[0U][1U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[0U][2U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_y_work[1U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_index_work[1U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[1U][0U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[1U][1U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[1U][2U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_y_work[2U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_index_work[2U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[2U][0U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[2U][1U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[2U][2U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_index = 3U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[0U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[0U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[0U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[0U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[1U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[1U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[1U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[1U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[2U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[2U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[2U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[2U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[3U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[3U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[3U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[3U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[4U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[4U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[4U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[4U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[5U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[5U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[5U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[5U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[6U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[6U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[6U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[6U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[7U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[7U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[7U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[7U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[8U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[8U] = 0U;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[8U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[8U] = 0ULL;
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__tap_index = 9U;
    if ((1U & ((((((~ (((2U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_height) 
                        & (2U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width)) 
                       | ((3U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_height) 
                          & (3U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width)))) 
                   | (0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_y)) 
                  | (0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_x)) 
                 | (0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_c[0U])) 
                | (0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U])) 
               | (0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U])))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_error_code = 1U;
    } else if (((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__extent_y 
                 < (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_height))) 
                | (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__extent_x 
                   < (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width))))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_error_code = 1U;
    } else {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_height_work 
            = (0x00000001ffffffffULL & ((2U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_y)
                                         ? (1ULL + 
                                            (0x00000000ffffffffULL 
                                             & ((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__extent_y 
                                                 - (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_height))) 
                                                >> 1U)))
                                         : (1ULL + 
                                            VL_DIV_QQQ(33, 
                                                       (0x00000001ffffffffULL 
                                                        & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__extent_y 
                                                           - (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_height)))), (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_y))))));
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_width_work 
            = (0x00000001ffffffffULL & ((2U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_x)
                                         ? (1ULL + 
                                            (0x00000000ffffffffULL 
                                             & ((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__extent_x 
                                                 - (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width))) 
                                                >> 1U)))
                                         : (1ULL + 
                                            VL_DIV_QQQ(33, 
                                                       (0x00000001ffffffffULL 
                                                        & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__extent_x 
                                                           - (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width)))), (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_x))))));
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_output_height 
            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_height_work;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_output_width 
            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_width_work;
        if ((((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel 
               >= vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_c[0U]) 
              | ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_y)) 
                 >= vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_height_work)) 
             | ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_x)) 
                >= vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_width_work))) {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_error_code = 1U;
        } else {
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_count 
                = ((2U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_height)
                    ? 4U : 9U);
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_index = 3U;
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__origin_y 
                = (- VL_EXTENDS_QQ(64,63, (QData)((IData)(
                                                          (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__darknet_padding_parameter 
                                                           >> 1U)))));
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__origin_x 
                = (- VL_EXTENDS_QQ(64,63, (QData)((IData)(
                                                          (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__darknet_padding_parameter 
                                                           >> 1U)))));
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_y_step 
                = (0x00000001ffffffffULL & ((2U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_y)
                                             ? ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_y)) 
                                                << 1U)
                                             : ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_y)) 
                                                * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_y)))));
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_x_step 
                = (0x00000001ffffffffULL & ((2U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_x)
                                             ? ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_x)) 
                                                << 1U)
                                             : ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_x)) 
                                                * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_x)))));
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_y_work 
                = (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__origin_y 
                   + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_y_step);
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_x_work 
                = (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__origin_x 
                   + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_x_step);
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work 
                = ((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel)) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U])));
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_y_work[0U] 
                = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_y_work;
            if ((VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_y_work[0U]) 
                 & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_y_work[0U], (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U]))))) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_index_work[0U] 
                    = (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work 
                       + (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_y_work[0U])));
                __Vtemp_4[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_index_work[0U]);
                __Vtemp_4[1U] = (IData)((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_index_work[0U] 
                                         >> 0x00000020U));
                __Vtemp_4[2U] = 0U;
                __Vtemp_5[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U];
                __Vtemp_5[1U] = 0U;
                __Vtemp_5[2U] = 0U;
                VL_MUL_W(3, __Vtemp_6, __Vtemp_4, __Vtemp_5);
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[0U][0U] 
                    = __Vtemp_6[0U];
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[0U][1U] 
                    = __Vtemp_6[1U];
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[0U][2U] 
                    = __Vtemp_6[2U];
            }
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_y_work[1U] 
                = (1ULL + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_y_work);
            if ((VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_y_work[1U]) 
                 & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_y_work[1U], (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U]))))) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_index_work[1U] 
                    = (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work 
                       + (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_y_work[1U])));
                __Vtemp_7[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_index_work[1U]);
                __Vtemp_7[1U] = (IData)((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_index_work[1U] 
                                         >> 0x00000020U));
                __Vtemp_7[2U] = 0U;
                __Vtemp_8[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U];
                __Vtemp_8[1U] = 0U;
                __Vtemp_8[2U] = 0U;
                VL_MUL_W(3, __Vtemp_9, __Vtemp_7, __Vtemp_8);
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[1U][0U] 
                    = __Vtemp_9[0U];
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[1U][1U] 
                    = __Vtemp_9[1U];
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[1U][2U] 
                    = __Vtemp_9[2U];
            }
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_y_work[2U] 
                = (2ULL + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_y_work);
            if ((VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_y_work[2U]) 
                 & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_y_work[2U], (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U]))))) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_index_work[2U] 
                    = (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work 
                       + (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_y_work[2U])));
                __Vtemp_10[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_index_work[2U]);
                __Vtemp_10[1U] = (IData)((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_index_work[2U] 
                                          >> 0x00000020U));
                __Vtemp_10[2U] = 0U;
                __Vtemp_11[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U];
                __Vtemp_11[1U] = 0U;
                __Vtemp_11[2U] = 0U;
                VL_MUL_W(3, __Vtemp_12, __Vtemp_10, __Vtemp_11);
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[2U][0U] 
                    = __Vtemp_12[0U];
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[2U][1U] 
                    = __Vtemp_12[1U];
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[2U][2U] 
                    = __Vtemp_12[2U];
            }
            if ((0U < (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_count))) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work = 0U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work = 0U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[0U] 
                    = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[0U] 
                    = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_y_work;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[0U] 
                    = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_x_work;
                if ((((VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[0U]) 
                       & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[0U], (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U])))) 
                      & VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[0U])) 
                     & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[0U], (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U]))))) {
                    if ((0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work)) {
                        __Vtemp_13[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[0U]);
                        __Vtemp_13[1U] = 0U;
                        __Vtemp_13[2U] = 0U;
                        VL_ADD_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[0U], __Vtemp_13);
                    } else if ((1U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work)) {
                        __Vtemp_14[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[0U]);
                        __Vtemp_14[1U] = 0U;
                        __Vtemp_14[2U] = 0U;
                        VL_ADD_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[1U], __Vtemp_14);
                    } else if ((2U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work)) {
                        __Vtemp_15[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[0U]);
                        __Vtemp_15[1U] = 0U;
                        __Vtemp_15[2U] = 0U;
                        VL_ADD_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[2U], __Vtemp_15);
                    } else {
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U] = 0U;
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U] = 0U;
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U] = 0U;
                    }
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask 
                        = (1U | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask));
                    __Vtemp_17[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_base[0U];
                    __Vtemp_17[1U] = 0U;
                    __Vtemp_17[2U] = 0U;
                    __Vtemp_17[3U] = 0U;
                    __Vtemp_18[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U];
                    __Vtemp_18[1U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U];
                    __Vtemp_18[2U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U];
                    __Vtemp_18[3U] = 0U;
                    VL_ADD_W(4, __Vtemp_19, __Vtemp_17, __Vtemp_18);
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U] 
                        = __Vtemp_19[0U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                        = __Vtemp_19[1U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U] 
                        = __Vtemp_19[2U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U] 
                        = (1U & __Vtemp_19[3U]);
                    if ((0U != ((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                                 | vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U]) 
                                | (1U & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U])))) {
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__tap_range_error = 1U;
                    } else {
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[0U] 
                            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U];
                    }
                }
            }
            if ((1U < (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_count))) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work = 0U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work = 1U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[1U] 
                    = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[1U] 
                    = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_y_work;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[1U] 
                    = (1ULL + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_x_work);
                if ((((VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[1U]) 
                       & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[1U], (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U])))) 
                      & VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[1U])) 
                     & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[1U], (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U]))))) {
                    if ((0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work)) {
                        __Vtemp_24[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[1U]);
                        __Vtemp_24[1U] = 0U;
                        __Vtemp_24[2U] = 0U;
                        VL_ADD_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[0U], __Vtemp_24);
                    } else if ((1U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work)) {
                        __Vtemp_25[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[1U]);
                        __Vtemp_25[1U] = 0U;
                        __Vtemp_25[2U] = 0U;
                        VL_ADD_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[1U], __Vtemp_25);
                    } else if ((2U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work)) {
                        __Vtemp_26[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[1U]);
                        __Vtemp_26[1U] = 0U;
                        __Vtemp_26[2U] = 0U;
                        VL_ADD_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[2U], __Vtemp_26);
                    } else {
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U] = 0U;
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U] = 0U;
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U] = 0U;
                    }
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask 
                        = (2U | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask));
                    __Vtemp_28[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_base[0U];
                    __Vtemp_28[1U] = 0U;
                    __Vtemp_28[2U] = 0U;
                    __Vtemp_28[3U] = 0U;
                    __Vtemp_29[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U];
                    __Vtemp_29[1U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U];
                    __Vtemp_29[2U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U];
                    __Vtemp_29[3U] = 0U;
                    VL_ADD_W(4, __Vtemp_30, __Vtemp_28, __Vtemp_29);
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U] 
                        = __Vtemp_30[0U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                        = __Vtemp_30[1U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U] 
                        = __Vtemp_30[2U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U] 
                        = (1U & __Vtemp_30[3U]);
                    if ((0U != ((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                                 | vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U]) 
                                | (1U & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U])))) {
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__tap_range_error = 1U;
                    } else {
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[1U] 
                            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U];
                    }
                }
            }
            if ((2U < (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_count))) {
                if ((2U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width)) {
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work = 1U;
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work = 0U;
                } else {
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work = 0U;
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work = 2U;
                }
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[2U] 
                    = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[2U] 
                    = (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_y_work 
                       + VL_EXTENDS_QI(64,32, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work));
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[2U] 
                    = (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_x_work 
                       + VL_EXTENDS_QI(64,32, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work));
                if ((((VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[2U]) 
                       & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[2U], (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U])))) 
                      & VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[2U])) 
                     & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[2U], (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U]))))) {
                    if ((0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work)) {
                        __Vtemp_35[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[2U]);
                        __Vtemp_35[1U] = 0U;
                        __Vtemp_35[2U] = 0U;
                        VL_ADD_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[0U], __Vtemp_35);
                    } else if ((1U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work)) {
                        __Vtemp_36[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[2U]);
                        __Vtemp_36[1U] = 0U;
                        __Vtemp_36[2U] = 0U;
                        VL_ADD_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[1U], __Vtemp_36);
                    } else if ((2U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work)) {
                        __Vtemp_37[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[2U]);
                        __Vtemp_37[1U] = 0U;
                        __Vtemp_37[2U] = 0U;
                        VL_ADD_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[2U], __Vtemp_37);
                    } else {
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U] = 0U;
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U] = 0U;
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U] = 0U;
                    }
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask 
                        = (4U | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask));
                    __Vtemp_39[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_base[0U];
                    __Vtemp_39[1U] = 0U;
                    __Vtemp_39[2U] = 0U;
                    __Vtemp_39[3U] = 0U;
                    __Vtemp_40[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U];
                    __Vtemp_40[1U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U];
                    __Vtemp_40[2U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U];
                    __Vtemp_40[3U] = 0U;
                    VL_ADD_W(4, __Vtemp_41, __Vtemp_39, __Vtemp_40);
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U] 
                        = __Vtemp_41[0U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                        = __Vtemp_41[1U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U] 
                        = __Vtemp_41[2U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U] 
                        = (1U & __Vtemp_41[3U]);
                    if ((0U != ((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                                 | vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U]) 
                                | (1U & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U])))) {
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__tap_range_error = 1U;
                    } else {
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[2U] 
                            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U];
                    }
                }
            }
            if ((3U < (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_count))) {
                if ((2U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width)) {
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work = 1U;
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work = 1U;
                } else {
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work = 1U;
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work = 0U;
                }
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[3U] 
                    = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[3U] 
                    = (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_y_work 
                       + VL_EXTENDS_QI(64,32, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work));
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[3U] 
                    = (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_x_work 
                       + VL_EXTENDS_QI(64,32, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work));
                if ((((VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[3U]) 
                       & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[3U], (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U])))) 
                      & VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[3U])) 
                     & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[3U], (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U]))))) {
                    if ((0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work)) {
                        __Vtemp_46[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[3U]);
                        __Vtemp_46[1U] = 0U;
                        __Vtemp_46[2U] = 0U;
                        VL_ADD_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[0U], __Vtemp_46);
                    } else if ((1U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work)) {
                        __Vtemp_47[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[3U]);
                        __Vtemp_47[1U] = 0U;
                        __Vtemp_47[2U] = 0U;
                        VL_ADD_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[1U], __Vtemp_47);
                    } else if ((2U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work)) {
                        __Vtemp_48[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[3U]);
                        __Vtemp_48[1U] = 0U;
                        __Vtemp_48[2U] = 0U;
                        VL_ADD_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[2U], __Vtemp_48);
                    } else {
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U] = 0U;
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U] = 0U;
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U] = 0U;
                    }
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask 
                        = (8U | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask));
                    __Vtemp_50[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_base[0U];
                    __Vtemp_50[1U] = 0U;
                    __Vtemp_50[2U] = 0U;
                    __Vtemp_50[3U] = 0U;
                    __Vtemp_51[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U];
                    __Vtemp_51[1U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U];
                    __Vtemp_51[2U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U];
                    __Vtemp_51[3U] = 0U;
                    VL_ADD_W(4, __Vtemp_52, __Vtemp_50, __Vtemp_51);
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U] 
                        = __Vtemp_52[0U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                        = __Vtemp_52[1U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U] 
                        = __Vtemp_52[2U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U] 
                        = (1U & __Vtemp_52[3U]);
                    if ((0U != ((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                                 | vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U]) 
                                | (1U & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U])))) {
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__tap_range_error = 1U;
                    } else {
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[3U] 
                            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U];
                    }
                }
            }
            if ((4U < (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_count))) {
                if ((2U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width)) {
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work = 0U;
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work = 0U;
                } else {
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work = 1U;
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work = 1U;
                }
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[4U] 
                    = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[4U] 
                    = (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_y_work 
                       + VL_EXTENDS_QI(64,32, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work));
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[4U] 
                    = (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_x_work 
                       + VL_EXTENDS_QI(64,32, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work));
                if ((((VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[4U]) 
                       & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[4U], (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U])))) 
                      & VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[4U])) 
                     & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[4U], (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U]))))) {
                    if ((0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work)) {
                        __Vtemp_57[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[4U]);
                        __Vtemp_57[1U] = 0U;
                        __Vtemp_57[2U] = 0U;
                        VL_ADD_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[0U], __Vtemp_57);
                    } else if ((1U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work)) {
                        __Vtemp_58[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[4U]);
                        __Vtemp_58[1U] = 0U;
                        __Vtemp_58[2U] = 0U;
                        VL_ADD_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[1U], __Vtemp_58);
                    } else if ((2U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work)) {
                        __Vtemp_59[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[4U]);
                        __Vtemp_59[1U] = 0U;
                        __Vtemp_59[2U] = 0U;
                        VL_ADD_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[2U], __Vtemp_59);
                    } else {
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U] = 0U;
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U] = 0U;
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U] = 0U;
                    }
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask 
                        = (0x00000010U | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask));
                    __Vtemp_61[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_base[0U];
                    __Vtemp_61[1U] = 0U;
                    __Vtemp_61[2U] = 0U;
                    __Vtemp_61[3U] = 0U;
                    __Vtemp_62[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U];
                    __Vtemp_62[1U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U];
                    __Vtemp_62[2U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U];
                    __Vtemp_62[3U] = 0U;
                    VL_ADD_W(4, __Vtemp_63, __Vtemp_61, __Vtemp_62);
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U] 
                        = __Vtemp_63[0U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                        = __Vtemp_63[1U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U] 
                        = __Vtemp_63[2U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U] 
                        = (1U & __Vtemp_63[3U]);
                    if ((0U != ((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                                 | vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U]) 
                                | (1U & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U])))) {
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__tap_range_error = 1U;
                    } else {
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[4U] 
                            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U];
                    }
                }
            }
            if ((5U < (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_count))) {
                if ((2U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width)) {
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work = 0U;
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work = 0U;
                } else {
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work = 1U;
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work = 2U;
                }
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[5U] 
                    = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[5U] 
                    = (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_y_work 
                       + VL_EXTENDS_QI(64,32, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work));
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[5U] 
                    = (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_x_work 
                       + VL_EXTENDS_QI(64,32, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work));
                if ((((VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[5U]) 
                       & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[5U], (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U])))) 
                      & VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[5U])) 
                     & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[5U], (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U]))))) {
                    if ((0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work)) {
                        __Vtemp_68[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[5U]);
                        __Vtemp_68[1U] = 0U;
                        __Vtemp_68[2U] = 0U;
                        VL_ADD_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[0U], __Vtemp_68);
                    } else if ((1U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work)) {
                        __Vtemp_69[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[5U]);
                        __Vtemp_69[1U] = 0U;
                        __Vtemp_69[2U] = 0U;
                        VL_ADD_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[1U], __Vtemp_69);
                    } else if ((2U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work)) {
                        __Vtemp_70[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[5U]);
                        __Vtemp_70[1U] = 0U;
                        __Vtemp_70[2U] = 0U;
                        VL_ADD_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[2U], __Vtemp_70);
                    } else {
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U] = 0U;
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U] = 0U;
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U] = 0U;
                    }
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask 
                        = (0x00000020U | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask));
                    __Vtemp_72[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_base[0U];
                    __Vtemp_72[1U] = 0U;
                    __Vtemp_72[2U] = 0U;
                    __Vtemp_72[3U] = 0U;
                    __Vtemp_73[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U];
                    __Vtemp_73[1U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U];
                    __Vtemp_73[2U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U];
                    __Vtemp_73[3U] = 0U;
                    VL_ADD_W(4, __Vtemp_74, __Vtemp_72, __Vtemp_73);
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U] 
                        = __Vtemp_74[0U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                        = __Vtemp_74[1U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U] 
                        = __Vtemp_74[2U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U] 
                        = (1U & __Vtemp_74[3U]);
                    if ((0U != ((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                                 | vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U]) 
                                | (1U & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U])))) {
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__tap_range_error = 1U;
                    } else {
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[5U] 
                            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U];
                    }
                }
            }
            if ((6U < (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_count))) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work 
                    = ((2U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width)
                        ? 0U : 2U);
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work = 0U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[6U] 
                    = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[6U] 
                    = (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_y_work 
                       + VL_EXTENDS_QI(64,32, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work));
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[6U] 
                    = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_x_work;
                if ((((VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[6U]) 
                       & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[6U], (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U])))) 
                      & VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[6U])) 
                     & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[6U], (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U]))))) {
                    if ((0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work)) {
                        __Vtemp_79[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[6U]);
                        __Vtemp_79[1U] = 0U;
                        __Vtemp_79[2U] = 0U;
                        VL_ADD_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[0U], __Vtemp_79);
                    } else if ((1U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work)) {
                        __Vtemp_80[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[6U]);
                        __Vtemp_80[1U] = 0U;
                        __Vtemp_80[2U] = 0U;
                        VL_ADD_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[1U], __Vtemp_80);
                    } else if ((2U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work)) {
                        __Vtemp_81[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[6U]);
                        __Vtemp_81[1U] = 0U;
                        __Vtemp_81[2U] = 0U;
                        VL_ADD_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[2U], __Vtemp_81);
                    } else {
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U] = 0U;
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U] = 0U;
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U] = 0U;
                    }
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask 
                        = (0x00000040U | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask));
                    __Vtemp_83[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_base[0U];
                    __Vtemp_83[1U] = 0U;
                    __Vtemp_83[2U] = 0U;
                    __Vtemp_83[3U] = 0U;
                    __Vtemp_84[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U];
                    __Vtemp_84[1U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U];
                    __Vtemp_84[2U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U];
                    __Vtemp_84[3U] = 0U;
                    VL_ADD_W(4, __Vtemp_85, __Vtemp_83, __Vtemp_84);
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U] 
                        = __Vtemp_85[0U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                        = __Vtemp_85[1U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U] 
                        = __Vtemp_85[2U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U] 
                        = (1U & __Vtemp_85[3U]);
                    if ((0U != ((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                                 | vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U]) 
                                | (1U & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U])))) {
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__tap_range_error = 1U;
                    } else {
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[6U] 
                            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U];
                    }
                }
            }
            if ((7U < (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_count))) {
                if ((2U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width)) {
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work = 0U;
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work = 0U;
                } else {
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work = 2U;
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work = 1U;
                }
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[7U] 
                    = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[7U] 
                    = (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_y_work 
                       + VL_EXTENDS_QI(64,32, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work));
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[7U] 
                    = (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_x_work 
                       + VL_EXTENDS_QI(64,32, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work));
                if ((((VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[7U]) 
                       & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[7U], (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U])))) 
                      & VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[7U])) 
                     & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[7U], (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U]))))) {
                    if ((0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work)) {
                        __Vtemp_90[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[7U]);
                        __Vtemp_90[1U] = 0U;
                        __Vtemp_90[2U] = 0U;
                        VL_ADD_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[0U], __Vtemp_90);
                    } else if ((1U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work)) {
                        __Vtemp_91[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[7U]);
                        __Vtemp_91[1U] = 0U;
                        __Vtemp_91[2U] = 0U;
                        VL_ADD_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[1U], __Vtemp_91);
                    } else if ((2U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work)) {
                        __Vtemp_92[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[7U]);
                        __Vtemp_92[1U] = 0U;
                        __Vtemp_92[2U] = 0U;
                        VL_ADD_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[2U], __Vtemp_92);
                    } else {
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U] = 0U;
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U] = 0U;
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U] = 0U;
                    }
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask 
                        = (0x00000080U | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask));
                    __Vtemp_94[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_base[0U];
                    __Vtemp_94[1U] = 0U;
                    __Vtemp_94[2U] = 0U;
                    __Vtemp_94[3U] = 0U;
                    __Vtemp_95[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U];
                    __Vtemp_95[1U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U];
                    __Vtemp_95[2U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U];
                    __Vtemp_95[3U] = 0U;
                    VL_ADD_W(4, __Vtemp_96, __Vtemp_94, __Vtemp_95);
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U] 
                        = __Vtemp_96[0U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                        = __Vtemp_96[1U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U] 
                        = __Vtemp_96[2U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U] 
                        = (1U & __Vtemp_96[3U]);
                    if ((0U != ((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                                 | vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U]) 
                                | (1U & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U])))) {
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__tap_range_error = 1U;
                    } else {
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[7U] 
                            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U];
                    }
                }
            }
            if ((8U < (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_count))) {
                if ((2U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width)) {
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work = 0U;
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work = 0U;
                } else {
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work = 2U;
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work = 2U;
                }
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[8U] 
                    = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[8U] 
                    = (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_y_work 
                       + VL_EXTENDS_QI(64,32, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work));
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[8U] 
                    = (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_x_work 
                       + VL_EXTENDS_QI(64,32, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work));
                if ((((VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[8U]) 
                       & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[8U], (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U])))) 
                      & VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[8U])) 
                     & VL_LTS_IQQ(64, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[8U], (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U]))))) {
                    if ((0U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work)) {
                        __Vtemp_101[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[8U]);
                        __Vtemp_101[1U] = 0U;
                        __Vtemp_101[2U] = 0U;
                        VL_ADD_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[0U], __Vtemp_101);
                    } else if ((1U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work)) {
                        __Vtemp_102[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[8U]);
                        __Vtemp_102[1U] = 0U;
                        __Vtemp_102[2U] = 0U;
                        VL_ADD_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[1U], __Vtemp_102);
                    } else if ((2U == vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work)) {
                        __Vtemp_103[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[8U]);
                        __Vtemp_103[1U] = 0U;
                        __Vtemp_103[2U] = 0U;
                        VL_ADD_W(3, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_offset_work[2U], __Vtemp_103);
                    } else {
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U] = 0U;
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U] = 0U;
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U] = 0U;
                    }
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask 
                        = (0x00000100U | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask));
                    __Vtemp_105[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_base[0U];
                    __Vtemp_105[1U] = 0U;
                    __Vtemp_105[2U] = 0U;
                    __Vtemp_105[3U] = 0U;
                    __Vtemp_106[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[0U];
                    __Vtemp_106[1U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[1U];
                    __Vtemp_106[2U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work[2U];
                    __Vtemp_106[3U] = 0U;
                    VL_ADD_W(4, __Vtemp_107, __Vtemp_105, __Vtemp_106);
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U] 
                        = __Vtemp_107[0U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                        = __Vtemp_107[1U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U] 
                        = __Vtemp_107[2U];
                    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U] 
                        = (1U & __Vtemp_107[3U]);
                    if ((0U != ((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[1U] 
                                 | vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[2U]) 
                                | (1U & vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[3U])))) {
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__tap_range_error = 1U;
                    } else {
                        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[8U] 
                            = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work[0U];
                    }
                }
            }
            vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__tap_index = 9U;
            if (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__tap_range_error) {
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_error_code = 2U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_output_height = 0ULL;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_output_width = 0ULL;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_count = 0U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask = 0U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[0U] = 0U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[0U] = 0U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[0U] = 0ULL;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[0U] = 0ULL;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__tap_index = 9U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[1U] = 0U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[1U] = 0U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[1U] = 0ULL;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[1U] = 0ULL;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[2U] = 0U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[2U] = 0U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[2U] = 0ULL;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[2U] = 0ULL;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[3U] = 0U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[3U] = 0U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[3U] = 0ULL;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[3U] = 0ULL;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[4U] = 0U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[4U] = 0U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[4U] = 0ULL;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[4U] = 0ULL;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[5U] = 0U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[5U] = 0U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[5U] = 0ULL;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[5U] = 0ULL;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[6U] = 0U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[6U] = 0U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[6U] = 0ULL;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[6U] = 0ULL;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[7U] = 0U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[7U] = 0U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[7U] = 0ULL;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[7U] = 0ULL;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[8U] = 0U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[8U] = 0U;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[8U] = 0ULL;
                vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[8U] = 0ULL;
            }
        }
    }
    if ((1U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_error_code))) {
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_output_height = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_output_width = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_count = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[0U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[0U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[0U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[0U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__tap_index = 9U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[1U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[1U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[1U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[1U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[2U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[2U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[2U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[2U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[3U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[3U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[3U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[3U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[4U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[4U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[4U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[4U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[5U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[5U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[5U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[5U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[6U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[6U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[6U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[6U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[7U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[7U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[7U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[7U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[8U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel[8U] = 0U;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[8U] = 0ULL;
        vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[8U] = 0ULL;
    }
    __VdfgRegularize_h6e95ff9d_0_5 = ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__automatic_read_responses) 
                                      & ((~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_write)) 
                                         & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid)));
    __Vtemp_113[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__output_offset_work);
    __Vtemp_113[1U] = (IData)((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__output_offset_work 
                               >> 0x00000020U));
    __Vtemp_113[2U] = 0U;
    VL_ADD_W(3, __Vtemp_114, __Vtemp_113, __VdfgRegularize_h6e95ff9d_0_6);
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__output_address_work[0U] 
        = __Vtemp_114[0U];
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__output_address_work[1U] 
        = __Vtemp_114[1U];
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__output_address_work[2U] 
        = (1U & __Vtemp_114[2U]);
    __Vtemp_116[0U] = (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_offset_work);
    __Vtemp_116[1U] = (IData)((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_offset_work 
                               >> 0x00000020U));
    __Vtemp_116[2U] = 0U;
    VL_ADD_W(3, __Vtemp_117, __Vtemp_116, __VdfgRegularize_h6e95ff9d_0_6);
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_address_work[0U] 
        = __Vtemp_117[0U];
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_address_work[1U] 
        = __Vtemp_117[1U];
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_address_work[2U] 
        = (1U & __Vtemp_117[2U]);
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__backend_memory_error_code 
        = ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__manual_mem_error_code) 
           & (- (IData)((1U & (~ (IData)(__VdfgRegularize_h6e95ff9d_0_5))))));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_ready 
        = ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__manual_mem_ready) 
           | (IData)(__VdfgRegularize_h6e95ff9d_0_5));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__memory_handshake 
        = ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_ready) 
           & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__backend_req_ready 
        = ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid) 
           & ((3U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state)) 
              & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_ready)));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__backend_req_ready 
        = ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid) 
           & ((5U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state)) 
              & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_ready)));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__backend_req_ready 
        = ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid) 
           & ((4U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state)) 
              & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_ready)));
    vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__backend_req_ready 
        = ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid) 
           & ((2U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state)) 
              & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_ready)));
}
