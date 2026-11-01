// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Tracing implementation internals

#include "verilated_vcd_c.h"
#include "Vtb_s2a_backend_fault_recovery__Syms.h"


VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root__trace_init_sub__TOP__s2a_network_descriptor_pkg__0(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd* tracep);
VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root__trace_init_dtype____8(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd* tracep, const char* name, uint32_t fidx, uint32_t c, VerilatedTraceSigDirection direction);
VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root__trace_init_dtype____13(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd* tracep, const char* name, uint32_t fidx, uint32_t c, VerilatedTraceSigDirection direction);
VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root__trace_init_dtype____14(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd* tracep, const char* name, uint32_t fidx, uint32_t c, VerilatedTraceSigDirection direction);
VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root__trace_init_dtype____15(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd* tracep, const char* name, uint32_t fidx, uint32_t c, VerilatedTraceSigDirection direction);
VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root__trace_init_dtype____16(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd* tracep, const char* name, uint32_t fidx, uint32_t c, VerilatedTraceSigDirection direction);
VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root__trace_init_dtype____17(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd* tracep, const char* name, uint32_t fidx, uint32_t c, VerilatedTraceSigDirection direction);
VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root__trace_init_dtype____18(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd* tracep, const char* name, uint32_t fidx, uint32_t c, VerilatedTraceSigDirection direction);
VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root__trace_init_dtype____19(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd* tracep, const char* name, uint32_t fidx, uint32_t c, VerilatedTraceSigDirection direction);

VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root__trace_init_sub__TOP__0(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd* tracep) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root__trace_init_sub__TOP__0\n"); );
    Vtb_s2a_backend_fault_recovery__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    const int c = vlSymsp->__Vm_baseCode;
    VL_TRACE_PUSH_PREFIX(tracep, "s2a_network_descriptor_pkg", VerilatedTracePrefixType::SCOPE_MODULE, 0, 0);
    Vtb_s2a_backend_fault_recovery___024root__trace_init_sub__TOP__s2a_network_descriptor_pkg__0(vlSelf, tracep);
    VL_TRACE_POP_PREFIX(tracep);
    VL_TRACE_PUSH_PREFIX(tracep, "tb_s2a_backend_fault_recovery", VerilatedTracePrefixType::SCOPE_MODULE, 0, 0);
    VL_TRACE_DECL_BUS(tracep,c+733,0,"REG_CMD",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 7,0);
    VL_TRACE_DECL_BUS(tracep,c+734,0,"REG_STATUS",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 7,0);
    VL_TRACE_DECL_BUS(tracep,c+735,0,"REG_ERROR_CODE",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 7,0);
    VL_TRACE_DECL_BUS(tracep,c+736,0,"REG_TIMEOUT",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 7,0);
    VL_TRACE_DECL_BUS(tracep,c+737,0,"REG_ACK",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 7,0);
    VL_TRACE_DECL_BUS(tracep,c+738,0,"NONE",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+739,0,"INTERNAL",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+740,0,"TIMEOUT_ERROR",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+741,0,"INPUT_BASE",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+742,0,"INPUT_BYTES",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+743,0,"WEIGHT_BASE",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+744,0,"WEIGHT_BYTES",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+745,0,"OUTPUT_CANCEL_TIMEOUT",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+746,0,"REQUEST_WAIT_LIMIT",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::INTEGER, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+747,0,"OUTPUT_WRITE_WAIT_LIMIT",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::INTEGER, 31,0);
    VL_TRACE_DECL_BIT(tracep,c+723,0,"clk",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+0,0,"hard_reset",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+1,0,"csr_valid",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+2,0,"csr_write",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BUS(tracep,c+3,0,"csr_addr",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 7,0);
    VL_TRACE_DECL_BUS(tracep,c+4,0,"csr_wdata",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BIT(tracep,c+5,0,"csr_ready",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BUS(tracep,c+12,0,"csr_rdata",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BIT(tracep,c+13,0,"backend_memory_error_valid",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BUS(tracep,c+14,0,"backend_memory_error_code",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BIT(tracep,c+15,0,"operator_result_valid",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BUS(tracep,c+16,0,"operator_error_code",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BIT(tracep,c+339,0,"backend_start",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+340,0,"backend_abort",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+341,0,"busy",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+342,0,"done",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+343,0,"error",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+344,0,"buffer_owner_pl",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+345,0,"head_output_valid",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+17,0,"mem_valid",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+18,0,"mem_write",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BUS(tracep,c+19,0,"mem_addr",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+20,0,"mem_wdata",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+21,0,"mem_rstrb",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 3,0);
    VL_TRACE_DECL_BUS(tracep,c+724,0,"mem_wstrb",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 3,0);
    VL_TRACE_DECL_BIT(tracep,c+6,0,"manual_mem_ready",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+7,0,"automatic_read_responses",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+22,0,"mem_ready",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BUS(tracep,c+748,0,"mem_rdata",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+8,0,"manual_mem_error_code",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+14,0,"mem_error_code",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+725,0,"simulation_cycle_count",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+9,0,"transaction_start_cycle",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+726,0,"memory_read_handshakes",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::INTEGER, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+727,0,"memory_write_side_effects",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::INTEGER, 31,0);
    VL_TRACE_PUSH_PREFIX(tracep, "u_backend", VerilatedTracePrefixType::SCOPE_MODULE, 0, 0);
    VL_TRACE_DECL_BIT(tracep,c+723,0,"clk",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+0,0,"hard_reset",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+340,0,"abort",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+339,0,"backend_start",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+344,0,"buffer_owner_pl",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BUS(tracep,c+741,0,"input_base_address",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+742,0,"input_length_bytes",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+743,0,"weight_package_base_address",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+744,0,"weight_package_length_bytes",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BIT(tracep,c+17,0,"mem_valid",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+18,0,"mem_write",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BUS(tracep,c+19,0,"mem_addr",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+20,0,"mem_wdata",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+21,0,"mem_rstrb",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 3,0);
    VL_TRACE_DECL_BUS(tracep,c+724,0,"mem_wstrb",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 3,0);
    VL_TRACE_DECL_BIT(tracep,c+22,0,"mem_ready",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BUS(tracep,c+748,0,"mem_rdata",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+14,0,"mem_error_code",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BIT(tracep,c+13,0,"backend_memory_error_valid",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BUS(tracep,c+14,0,"backend_memory_error_code",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BIT(tracep,c+15,0,"operator_result_valid",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BUS(tracep,c+16,0,"operator_error_code",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+738,0,"NONE",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+739,0,"INTERNAL",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+346,0,"state",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+347,0,"layer_cursor",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 5,0);
    VL_TRACE_DECL_BUS(tracep,c+348,0,"output_element_index",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BIT(tracep,c+349,0,"response_pending",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BUS(tracep,c+350,0,"response_data_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+351,0,"response_error_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+352,0,"response_target_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+23,0,"current_op",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+24,0,"current_input_count",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 1,0);
    VL_TRACE_PUSH_PREFIX(tracep, "source_base", VerilatedTracePrefixType::ARRAY_UNPACKED, 0, 1);
    for (int i = 0; i < 2; ++i) {
        VL_TRACE_DECL_BUS_ARRAY(tracep,c+25+i*1,0,"",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, (i + 0), 31,0);
    }
    VL_TRACE_POP_PREFIX(tracep);
    VL_TRACE_PUSH_PREFIX(tracep, "source_length", VerilatedTracePrefixType::ARRAY_UNPACKED, 0, 1);
    for (int i = 0; i < 2; ++i) {
        VL_TRACE_DECL_BUS_ARRAY(tracep,c+27+i*1,0,"",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, (i + 0), 31,0);
    }
    VL_TRACE_POP_PREFIX(tracep);
    VL_TRACE_PUSH_PREFIX(tracep, "source_n", VerilatedTracePrefixType::ARRAY_UNPACKED, 0, 1);
    for (int i = 0; i < 2; ++i) {
        VL_TRACE_DECL_BUS_ARRAY(tracep,c+29+i*1,0,"",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, (i + 0), 15,0);
    }
    VL_TRACE_POP_PREFIX(tracep);
    VL_TRACE_PUSH_PREFIX(tracep, "source_c", VerilatedTracePrefixType::ARRAY_UNPACKED, 0, 1);
    for (int i = 0; i < 2; ++i) {
        VL_TRACE_DECL_BUS_ARRAY(tracep,c+31+i*1,0,"",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, (i + 0), 15,0);
    }
    VL_TRACE_POP_PREFIX(tracep);
    VL_TRACE_PUSH_PREFIX(tracep, "source_h", VerilatedTracePrefixType::ARRAY_UNPACKED, 0, 1);
    for (int i = 0; i < 2; ++i) {
        VL_TRACE_DECL_BUS_ARRAY(tracep,c+33+i*1,0,"",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, (i + 0), 15,0);
    }
    VL_TRACE_POP_PREFIX(tracep);
    VL_TRACE_PUSH_PREFIX(tracep, "source_w", VerilatedTracePrefixType::ARRAY_UNPACKED, 0, 1);
    for (int i = 0; i < 2; ++i) {
        VL_TRACE_DECL_BUS_ARRAY(tracep,c+35+i*1,0,"",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, (i + 0), 15,0);
    }
    VL_TRACE_POP_PREFIX(tracep);
    VL_TRACE_PUSH_PREFIX(tracep, "source_route_start", VerilatedTracePrefixType::ARRAY_UNPACKED, 0, 1);
    for (int i = 0; i < 2; ++i) {
        VL_TRACE_DECL_BUS_ARRAY(tracep,c+37+i*1,0,"",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, (i + 0), 15,0);
    }
    VL_TRACE_POP_PREFIX(tracep);
    VL_TRACE_PUSH_PREFIX(tracep, "source_route_end", VerilatedTracePrefixType::ARRAY_UNPACKED, 0, 1);
    for (int i = 0; i < 2; ++i) {
        VL_TRACE_DECL_BUS_ARRAY(tracep,c+39+i*1,0,"",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, (i + 0), 15,0);
    }
    VL_TRACE_POP_PREFIX(tracep);
    VL_TRACE_DECL_BUS(tracep,c+41,0,"output_base",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+42,0,"output_length",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+43,0,"output_n",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 15,0);
    VL_TRACE_DECL_BUS(tracep,c+44,0,"output_c",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 15,0);
    VL_TRACE_DECL_BUS(tracep,c+45,0,"output_h",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 15,0);
    VL_TRACE_DECL_BUS(tracep,c+46,0,"output_w",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 15,0);
    VL_TRACE_DECL_QUAD(tracep,c+47,0,"output_plane_elements",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 63,0);
    VL_TRACE_DECL_QUAD(tracep,c+49,0,"output_batch_elements",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 63,0);
    VL_TRACE_DECL_QUAD(tracep,c+51,0,"output_element_count",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 63,0);
    VL_TRACE_DECL_BUS(tracep,c+53,0,"decoded_channel",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+54,0,"decoded_y",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+55,0,"decoded_x",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+56,0,"mq_index",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BIT(tracep,c+57,0,"descriptor_valid",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+58,0,"alias_valid",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+59,0,"descriptor_fault",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+60,0,"is_alias_row",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BUS(tracep,c+61,0,"alias_layer_index",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 5,0);
    VL_TRACE_DECL_QUAD(tracep,c+62,0,"alias_output_plane_elements",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 63,0);
    VL_TRACE_DECL_QUAD(tracep,c+64,0,"alias_output_element_count",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 63,0);
    VL_TRACE_DECL_BIT(tracep,c+66,0,"conv_start_valid",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+67,0,"conv_start_ready",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+68,0,"maxpool_start_valid",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+69,0,"maxpool_start_ready",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+70,0,"route_start_valid",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+71,0,"route_start_ready",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+72,0,"upsample_start_valid",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+73,0,"upsample_start_ready",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+728,0,"maxpool_cancel",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+728,0,"route_cancel",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+728,0,"upsample_cancel",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+74,0,"conv_req_valid",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+75,0,"conv_req_ready",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+76,0,"conv_req_write",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BUS(tracep,c+353,0,"conv_req_addr",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+354,0,"conv_req_wdata",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+77,0,"conv_req_rstrb",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 3,0);
    VL_TRACE_DECL_BUS(tracep,c+78,0,"conv_req_wstrb",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 3,0);
    VL_TRACE_DECL_BIT(tracep,c+79,0,"maxpool_req_valid",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+80,0,"maxpool_req_ready",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+81,0,"maxpool_req_write",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BUS(tracep,c+82,0,"maxpool_req_addr",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+83,0,"maxpool_req_wdata",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+84,0,"maxpool_req_rstrb",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 3,0);
    VL_TRACE_DECL_BUS(tracep,c+85,0,"maxpool_req_wstrb",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 3,0);
    VL_TRACE_DECL_BIT(tracep,c+86,0,"route_req_valid",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+87,0,"route_req_ready",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+88,0,"route_req_write",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BUS(tracep,c+89,0,"route_req_addr",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+90,0,"route_req_wdata",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+91,0,"route_req_rstrb",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 3,0);
    VL_TRACE_DECL_BUS(tracep,c+92,0,"route_req_wstrb",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 3,0);
    VL_TRACE_DECL_BIT(tracep,c+93,0,"upsample_req_valid",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+94,0,"upsample_req_ready",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+95,0,"upsample_req_write",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BUS(tracep,c+96,0,"upsample_req_addr",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+97,0,"upsample_req_wdata",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+98,0,"upsample_req_rstrb",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 3,0);
    VL_TRACE_DECL_BUS(tracep,c+99,0,"upsample_req_wstrb",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 3,0);
    VL_TRACE_DECL_BIT(tracep,c+100,0,"conv_rsp_valid",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+101,0,"maxpool_rsp_valid",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+102,0,"route_rsp_valid",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+103,0,"upsample_rsp_valid",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BUS(tracep,c+350,0,"conv_rsp_data",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+350,0,"maxpool_rsp_data",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+350,0,"route_rsp_data",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+350,0,"upsample_rsp_data",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+351,0,"conv_rsp_error",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+351,0,"maxpool_rsp_error",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+351,0,"route_rsp_error",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+351,0,"upsample_rsp_error",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BIT(tracep,c+355,0,"conv_result_valid",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+104,0,"conv_result_ready",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BUS(tracep,c+356,0,"conv_result_error",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BIT(tracep,c+357,0,"maxpool_result_valid",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+105,0,"maxpool_result_ready",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_WIDE(tracep,c+358,0,"maxpool_tap_addresses",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 127,0);
    VL_TRACE_DECL_BUS(tracep,c+362,0,"maxpool_result_address",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+363,0,"maxpool_result_value",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 7,0);
    VL_TRACE_DECL_BUS(tracep,c+364,0,"maxpool_result_error",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BIT(tracep,c+365,0,"route_result_valid",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+106,0,"route_result_ready",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BUS(tracep,c+366,0,"route_result_source_index",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+367,0,"route_result_source_address",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+368,0,"route_result_address",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+369,0,"route_result_value",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 7,0);
    VL_TRACE_DECL_BUS(tracep,c+370,0,"route_result_error",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BIT(tracep,c+371,0,"upsample_result_valid",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+107,0,"upsample_result_ready",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BUS(tracep,c+372,0,"upsample_result_source_address",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+373,0,"upsample_result_address",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+374,0,"upsample_result_value",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 7,0);
    VL_TRACE_DECL_BUS(tracep,c+375,0,"upsample_result_error",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BIT(tracep,c+729,0,"selected_req_valid",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+730,0,"selected_req_write",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BUS(tracep,c+108,0,"selected_req_addr",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+109,0,"selected_req_wdata",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+731,0,"selected_req_rstrb",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 3,0);
    VL_TRACE_DECL_BUS(tracep,c+732,0,"selected_req_wstrb",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 3,0);
    VL_TRACE_DECL_BIT(tracep,c+110,0,"selected_result_valid",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BUS(tracep,c+376,0,"selected_result_error",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BIT(tracep,c+111,0,"memory_handshake",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+112,0,"selected_start_ready",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_PUSH_PREFIX(tracep, "u_conv_engine", VerilatedTracePrefixType::SCOPE_MODULE, 0, 0);
    VL_TRACE_DECL_BIT(tracep,c+723,0,"clk",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+0,0,"hard_reset",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+340,0,"abort",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+344,0,"buffer_owner_pl",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+66,0,"start_valid",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+67,0,"start_ready",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BUS(tracep,c+377,0,"layer_index",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+378,0,"weight_layer_index",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+113,0,"input_base_address",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+114,0,"input_length_bytes",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+115,0,"input_batch_count",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+116,0,"input_channels",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+117,0,"input_height",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+118,0,"input_width",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+41,0,"output_base_address",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+42,0,"output_length_bytes",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+119,0,"output_batch_count",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+120,0,"output_channels",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+121,0,"output_height",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+122,0,"output_width",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+379,0,"kernel_height",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+380,0,"kernel_width",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+381,0,"stride_y",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+382,0,"stride_x",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+383,0,"pad_left",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+384,0,"pad_right",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+385,0,"pad_top",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+386,0,"pad_bottom",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+387,0,"groups",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+388,0,"padding_value_int8",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+749,0,"weight_package_base_address",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+750,0,"weight_package_length_bytes",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+389,0,"quantized_weight_offset",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+390,0,"quantized_weight_bytes",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+748,0,"output_batch",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+391,0,"activation_mode",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 1,0);
    VL_TRACE_DECL_BIT(tracep,c+728,0,"backend_cancel",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+74,0,"backend_req_valid",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+75,0,"backend_req_ready",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+76,0,"backend_req_write",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BUS(tracep,c+353,0,"backend_req_addr",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+354,0,"backend_req_wdata",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+77,0,"backend_req_rstrb",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 3,0);
    VL_TRACE_DECL_BUS(tracep,c+78,0,"backend_req_wstrb",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 3,0);
    VL_TRACE_DECL_BIT(tracep,c+100,0,"backend_rsp_valid",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BUS(tracep,c+350,0,"backend_rsp_rdata",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+351,0,"backend_rsp_error",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BIT(tracep,c+392,0,"busy",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+355,0,"result_valid",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+104,0,"result_ready",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BUS(tracep,c+356,0,"result_error_code",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+738,0,"NONE",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+751,0,"BAD_ARGUMENT",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+752,0,"BAD_RANGE",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+753,0,"BAD_LENGTH",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+739,0,"INTERNAL",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+754,0,"ACCUMULATOR_OVERFLOW",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+755,0,"TILE_EDGE",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::INTEGER, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+755,0,"LANE_COUNT",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::INTEGER, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+756,0,"MAX_FEATURE_PATCH_BYTES",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::INTEGER, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+757,0,"MAX_WEIGHT_GROUP_BYTES",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::INTEGER, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+758,0,"OUTPUT_BLOCK_BYTES",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::INTEGER, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+393,0,"state",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 4,0);
    VL_TRACE_DECL_BUS(tracep,c+394,0,"layer_index_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+395,0,"weight_layer_index_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+396,0,"input_base_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+397,0,"input_length_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+398,0,"input_batch_count_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+399,0,"input_channels_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+400,0,"input_height_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+401,0,"input_width_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+402,0,"output_base_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+403,0,"output_length_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+404,0,"output_batch_count_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+405,0,"output_channels_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+406,0,"output_height_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+407,0,"output_width_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+408,0,"kernel_height_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+409,0,"kernel_width_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+410,0,"stride_y_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+411,0,"stride_x_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+412,0,"pad_left_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+413,0,"pad_right_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+414,0,"pad_top_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+415,0,"pad_bottom_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+416,0,"groups_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+417,0,"padding_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+418,0,"weight_package_base_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+419,0,"weight_package_length_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+420,0,"quantized_weight_offset_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+421,0,"quantized_weight_bytes_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+422,0,"output_batch_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+423,0,"activation_mode_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 1,0);

    Vtb_s2a_backend_fault_recovery___024root__trace_init_dtype____8(vlSelf, tracep, "lane_accumulator", 0, c+424, VerilatedTraceSigDirection::NONE);
    VL_TRACE_DECL_BUS(tracep,c+432,0,"reduction_count_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+433,0,"output_group_base",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+434,0,"tile_start_y",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+435,0,"tile_start_x",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+436,0,"tile_height",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+437,0,"tile_width",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+438,0,"patch_height",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+439,0,"patch_width",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+440,0,"patch_byte_count",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+441,0,"tile_point_count",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+442,0,"group_lane_count",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+443,0,"feature_scan_index",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+444,0,"weight_lane_index",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+445,0,"weight_reduction_index",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+446,0,"compute_point_index",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+447,0,"compute_reduction_index",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+448,0,"output_lane_index",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+449,0,"output_point_index",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+353,0,"request_address_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+450,0,"request_strobe_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 3,0);
    VL_TRACE_DECL_BIT(tracep,c+451,0,"request_write_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BUS(tracep,c+354,0,"request_wdata_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+452,0,"output_address_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+453,0,"output_value_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 7,0);
    VL_TRACE_DECL_BUS(tracep,c+356,0,"result_error_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_WIDE(tracep,c+454,0,"input_elements_wide",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 127,0);
    VL_TRACE_DECL_WIDE(tracep,c+458,0,"output_elements_wide",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 127,0);
    VL_TRACE_DECL_WIDE(tracep,c+462,0,"expected_weight_bytes_wide",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 127,0);
    VL_TRACE_DECL_WIDE(tracep,c+466,0,"reduction_count_wide",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 127,0);
    VL_TRACE_DECL_WIDE(tracep,c+470,0,"input_end_wide",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 127,0);
    VL_TRACE_DECL_WIDE(tracep,c+474,0,"output_end_wide",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 127,0);
    VL_TRACE_DECL_WIDE(tracep,c+478,0,"weight_package_end_wide",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 127,0);
    VL_TRACE_DECL_WIDE(tracep,c+482,0,"quantized_weight_end_wide",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 127,0);
    VL_TRACE_DECL_QUAD(tracep,c+486,0,"output_height_numerator",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 63,0);
    VL_TRACE_DECL_QUAD(tracep,c+488,0,"output_width_numerator",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 63,0);
    VL_TRACE_DECL_QUAD(tracep,c+490,0,"output_height_shape_span",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 63,0);
    VL_TRACE_DECL_QUAD(tracep,c+492,0,"output_width_shape_span",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 63,0);
    VL_TRACE_DECL_QUAD(tracep,c+494,0,"output_height_shape_product",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 63,0);
    VL_TRACE_DECL_QUAD(tracep,c+496,0,"output_width_shape_product",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 63,0);
    VL_TRACE_DECL_QUAD(tracep,c+498,0,"output_height_span_plus_stride",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 63,0);
    VL_TRACE_DECL_QUAD(tracep,c+500,0,"output_width_span_plus_stride",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 63,0);
    VL_TRACE_DECL_WIDE(tracep,c+502,0,"full_tile_patch_height_wide",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 127,0);
    VL_TRACE_DECL_WIDE(tracep,c+506,0,"full_tile_patch_width_wide",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 127,0);
    VL_TRACE_DECL_WIDE(tracep,c+510,0,"full_tile_patch_bytes_wide",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 127,0);
    VL_TRACE_DECL_WIDE(tracep,c+514,0,"full_weight_group_bytes_wide",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 127,0);
    VL_TRACE_DECL_BIT(tracep,c+518,0,"validation_ok",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BUS(tracep,c+519,0,"validation_error",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_QUAD(tracep,c+123,0,"patch_plane_bytes",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 63,0);
    VL_TRACE_DECL_BUS(tracep,c+520,0,"feature_scan_channel",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+521,0,"feature_scan_y",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+522,0,"feature_scan_x",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BIT(tracep,c+125,0,"feature_scan_advance",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_QUAD(tracep,c+126,0,"feature_input_y",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 63,0);
    VL_TRACE_DECL_QUAD(tracep,c+128,0,"feature_input_x",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 63,0);
    VL_TRACE_DECL_BIT(tracep,c+130,0,"feature_scan_in_bounds",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_QUAD(tracep,c+131,0,"feature_source_offset",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 63,0);
    VL_TRACE_DECL_QUAD(tracep,c+133,0,"feature_source_address_wide",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 63,0);
    VL_TRACE_DECL_BUS(tracep,c+523,0,"current_weight_output_channel",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_QUAD(tracep,c+524,0,"weight_source_address_wide",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 63,0);
    VL_TRACE_DECL_BUS(tracep,c+135,0,"compute_kernel_area",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+526,0,"compute_input_channel",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+527,0,"compute_kernel_y",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+528,0,"compute_kernel_x",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+136,0,"compute_point_y",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+137,0,"compute_point_x",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_QUAD(tracep,c+138,0,"compute_input_y",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 63,0);
    VL_TRACE_DECL_QUAD(tracep,c+140,0,"compute_input_x",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 63,0);
    VL_TRACE_DECL_BIT(tracep,c+142,0,"compute_tap_in_bounds",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_QUAD(tracep,c+143,0,"compute_feature_index_wide",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 63,0);
    VL_TRACE_DECL_BUS(tracep,c+145,0,"compute_feature_index",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_PUSH_PREFIX(tracep, "compute_feature_byte", VerilatedTracePrefixType::ARRAY_UNPACKED, 0, 7);
    for (int i = 0; i < 8; ++i) {
        VL_TRACE_DECL_BUS_ARRAY(tracep,c+146+i*1,0,"",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, (i + 0), 7,0);
    }
    VL_TRACE_POP_PREFIX(tracep);
    VL_TRACE_PUSH_PREFIX(tracep, "compute_weight_byte", VerilatedTracePrefixType::ARRAY_UNPACKED, 0, 7);
    for (int i = 0; i < 8; ++i) {
        VL_TRACE_DECL_BUS_ARRAY(tracep,c+154+i*1,0,"",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, (i + 0), 7,0);
    }
    VL_TRACE_POP_PREFIX(tracep);
    VL_TRACE_PUSH_PREFIX(tracep, "compute_product", VerilatedTracePrefixType::ARRAY_UNPACKED, 0, 7);
    for (int i = 0; i < 8; ++i) {
        VL_TRACE_DECL_BUS_ARRAY(tracep,c+162+i*1,0,"",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, (i + 0), 15,0);
    }
    VL_TRACE_POP_PREFIX(tracep);
    VL_TRACE_PUSH_PREFIX(tracep, "compute_sum", VerilatedTracePrefixType::ARRAY_UNPACKED, 0, 7);
    for (int i = 0; i < 8; ++i) {
        VL_TRACE_DECL_QUAD_ARRAY(tracep,c+170+i*2,0,"",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, (i + 0), 32,0);
    }
    VL_TRACE_POP_PREFIX(tracep);
    VL_TRACE_DECL_BIT(tracep,c+186,0,"compute_bad_argument",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+187,0,"compute_overflow",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BUS(tracep,c+529,0,"mq_prefetch_lane",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+530,0,"mq_prefetch_index",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_WIDE(tracep,c+531,0,"mq_prefetch_parameter",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 79,0);
    VL_TRACE_DECL_BUS(tracep,c+534,0,"mq_prefetch_bias",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BIT(tracep,c+535,0,"mq_prefetch_invalid",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);

    Vtb_s2a_backend_fault_recovery___024root__trace_init_dtype____13(vlSelf, tracep, "lane_mq_parameter", 0, c+536, VerilatedTraceSigDirection::NONE);

    Vtb_s2a_backend_fault_recovery___024root__trace_init_dtype____14(vlSelf, tracep, "lane_bias", 0, c+560, VerilatedTraceSigDirection::NONE);
    VL_TRACE_DECL_BUS(tracep,c+568,0,"requant_lane_index",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_WIDE(tracep,c+569,0,"requant_parameter",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 79,0);
    VL_TRACE_DECL_BUS(tracep,c+572,0,"requant_accumulator",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+573,0,"requant_multiplier",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+574,0,"requant_q_shift",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+575,0,"requant_magnitude",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_QUAD(tracep,c+576,0,"requant_product",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 63,0);
    VL_TRACE_DECL_QUAD(tracep,c+578,0,"requant_rounding_add",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 63,0);
    VL_TRACE_DECL_QUAD(tracep,c+580,0,"requant_rounded_magnitude",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 63,0);
    VL_TRACE_DECL_QUAD(tracep,c+582,0,"requant_signed_value",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 63,0);
    VL_TRACE_DECL_BUS(tracep,c+584,0,"requantized_value",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 7,0);
    VL_TRACE_DECL_BUS(tracep,c+585,0,"output_global_y",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+586,0,"output_global_x",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+587,0,"output_point_scan_y",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+588,0,"output_point_scan_x",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+589,0,"output_channel_current",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_QUAD(tracep,c+590,0,"output_byte_offset_wide",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 63,0);
    VL_TRACE_DECL_QUAD(tracep,c+592,0,"output_address_wide",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 63,0);
    VL_TRACE_DECL_BUS(tracep,c+188,0,"mapped_response_error",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+594,0,"request_byte_lane",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 1,0);
    VL_TRACE_DECL_BUS(tracep,c+189,0,"comb_lane",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::INTEGER, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+595,0,"seq_lane",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::INTEGER, 31,0);
    VL_TRACE_POP_PREFIX(tracep);
    VL_TRACE_PUSH_PREFIX(tracep, "u_maxpool_engine", VerilatedTracePrefixType::SCOPE_MODULE, 0, 0);
    VL_TRACE_DECL_BIT(tracep,c+723,0,"clk",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+0,0,"hard_reset",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+340,0,"abort",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+68,0,"start_valid",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+69,0,"start_ready",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BUS(tracep,c+596,0,"layer_index",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+113,0,"input_base_address",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+114,0,"input_length_bytes",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+116,0,"input_channels",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+117,0,"input_height",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+118,0,"input_width",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+41,0,"output_base_address",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+42,0,"output_length_bytes",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+120,0,"output_channels",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+121,0,"output_height",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+122,0,"output_width",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+597,0,"kernel_height",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+598,0,"kernel_width",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+599,0,"stride_y",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+600,0,"stride_x",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+601,0,"darknet_padding_parameter",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+53,0,"output_channel",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+54,0,"output_y",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+55,0,"output_x",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BIT(tracep,c+728,0,"backend_cancel",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+79,0,"backend_req_valid",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+80,0,"backend_req_ready",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+81,0,"backend_req_write",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BUS(tracep,c+82,0,"backend_req_addr",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+83,0,"backend_req_wdata",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+84,0,"backend_req_rstrb",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 3,0);
    VL_TRACE_DECL_BUS(tracep,c+85,0,"backend_req_wstrb",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 3,0);
    VL_TRACE_DECL_BIT(tracep,c+101,0,"backend_rsp_valid",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BUS(tracep,c+350,0,"backend_rsp_rdata",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+351,0,"backend_rsp_error",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BIT(tracep,c+357,0,"result_valid",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+105,0,"result_ready",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_WIDE(tracep,c+358,0,"result_tap_addresses",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 127,0);
    VL_TRACE_DECL_BUS(tracep,c+362,0,"result_output_address",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+363,0,"result_value",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 7,0);
    VL_TRACE_DECL_BUS(tracep,c+364,0,"result_error_code",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+738,0,"NONE",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+751,0,"BAD_ARGUMENT",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+752,0,"BAD_RANGE",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+753,0,"BAD_LENGTH",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+739,0,"INTERNAL",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+759,0,"L9_INPUT_BASE",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+760,0,"L9_INPUT_LENGTH",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+761,0,"L9_OUTPUT_BASE",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+762,0,"L9_OUTPUT_LENGTH",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+763,0,"L17_INPUT_BASE",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+764,0,"L17_INPUT_LENGTH",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+765,0,"L17_OUTPUT_BASE",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+766,0,"L17_OUTPUT_LENGTH",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+767,0,"L25_INPUT_BASE",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+762,0,"L25_INPUT_LENGTH",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+768,0,"L25_OUTPUT_BASE",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+769,0,"L25_OUTPUT_LENGTH",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+602,0,"state",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 3,0);

    Vtb_s2a_backend_fault_recovery___024root__trace_init_dtype____15(vlSelf, tracep, "tap_address_latched", 0, c+603, VerilatedTraceSigDirection::NONE);
    VL_TRACE_DECL_BUS(tracep,c+362,0,"output_address_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_WIDE(tracep,c+607,0,"candidate_values_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 71,0);
    VL_TRACE_DECL_BUS(tracep,c+610,0,"read_tap_index",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+363,0,"result_value_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 7,0);
    VL_TRACE_DECL_BUS(tracep,c+364,0,"result_error_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_QUAD(tracep,c+190,0,"query_output_height",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 32,0);
    VL_TRACE_DECL_QUAD(tracep,c+192,0,"query_output_width",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 32,0);
    VL_TRACE_DECL_BUS(tracep,c+194,0,"query_tap_count",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 3,0);
    VL_TRACE_DECL_BUS(tracep,c+195,0,"query_tap_valid_mask",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 8,0);

    Vtb_s2a_backend_fault_recovery___024root__trace_init_dtype____16(vlSelf, tracep, "query_tap_address", 0, c+196, VerilatedTraceSigDirection::NONE);

    Vtb_s2a_backend_fault_recovery___024root__trace_init_dtype____17(vlSelf, tracep, "query_tap_source_channel", 0, c+205, VerilatedTraceSigDirection::NONE);

    Vtb_s2a_backend_fault_recovery___024root__trace_init_dtype____18(vlSelf, tracep, "query_tap_source_y", 0, c+214, VerilatedTraceSigDirection::NONE);

    Vtb_s2a_backend_fault_recovery___024root__trace_init_dtype____19(vlSelf, tracep, "query_tap_source_x", 0, c+232, VerilatedTraceSigDirection::NONE);
    VL_TRACE_DECL_BUS(tracep,c+250,0,"query_error_code",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BIT(tracep,c+251,0,"query_inputs_valid",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+252,0,"query_outputs_valid",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_QUAD(tracep,c+253,0,"output_offset_work",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 63,0);
    VL_TRACE_DECL_WIDE(tracep,c+255,0,"output_address_work",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 64,0);
    VL_TRACE_DECL_BUS(tracep,c+611,0,"selected_byte_shift",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+258,0,"selected_input_word_address",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+259,0,"selected_input_lane",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 3,0);
    VL_TRACE_DECL_BUS(tracep,c+612,0,"mapped_response_error",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+613,0,"window_max_value",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 7,0);
    VL_TRACE_DECL_BUS(tracep,c+614,0,"window_error_code",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+615,0,"tap_index",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::INTEGER, 31,0);
    VL_TRACE_PUSH_PREFIX(tracep, "u_geometry", VerilatedTracePrefixType::SCOPE_MODULE, 0, 0);
    VL_TRACE_DECL_BUS(tracep,c+113,0,"input_base_address",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+116,0,"input_channels",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+117,0,"input_height",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+118,0,"input_width",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+597,0,"kernel_height",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+598,0,"kernel_width",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+599,0,"stride_y",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+600,0,"stride_x",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+601,0,"darknet_padding_parameter",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+53,0,"input_channel",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+54,0,"output_y",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+55,0,"output_x",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_QUAD(tracep,c+190,0,"output_height",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 32,0);
    VL_TRACE_DECL_QUAD(tracep,c+192,0,"output_width",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 32,0);
    VL_TRACE_DECL_BUS(tracep,c+194,0,"tap_count",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 3,0);
    VL_TRACE_DECL_BUS(tracep,c+195,0,"tap_valid_mask",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 8,0);
    VL_TRACE_PUSH_PREFIX(tracep, "tap_address", VerilatedTracePrefixType::ARRAY_UNPACKED, 0, 8);
    for (int i = 0; i < 9; ++i) {
        VL_TRACE_DECL_BUS_ARRAY(tracep,c+196+i*1,0,"",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, (i + 0), 31,0);
    }
    VL_TRACE_POP_PREFIX(tracep);
    VL_TRACE_PUSH_PREFIX(tracep, "tap_source_channel", VerilatedTracePrefixType::ARRAY_UNPACKED, 0, 8);
    for (int i = 0; i < 9; ++i) {
        VL_TRACE_DECL_BUS_ARRAY(tracep,c+205+i*1,0,"",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, (i + 0), 31,0);
    }
    VL_TRACE_POP_PREFIX(tracep);
    VL_TRACE_PUSH_PREFIX(tracep, "tap_source_y", VerilatedTracePrefixType::ARRAY_UNPACKED, 0, 8);
    for (int i = 0; i < 9; ++i) {
        VL_TRACE_DECL_QUAD_ARRAY(tracep,c+214+i*2,0,"",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, (i + 0), 63,0);
    }
    VL_TRACE_POP_PREFIX(tracep);
    VL_TRACE_PUSH_PREFIX(tracep, "tap_source_x", VerilatedTracePrefixType::ARRAY_UNPACKED, 0, 8);
    for (int i = 0; i < 9; ++i) {
        VL_TRACE_DECL_QUAD_ARRAY(tracep,c+232+i*2,0,"",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, (i + 0), 63,0);
    }
    VL_TRACE_POP_PREFIX(tracep);
    VL_TRACE_DECL_BUS(tracep,c+250,0,"error_code",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+751,0,"BAD_ARGUMENT",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+752,0,"BAD_RANGE",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_QUAD(tracep,c+260,0,"extent_y",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 32,0);
    VL_TRACE_DECL_QUAD(tracep,c+262,0,"extent_x",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 32,0);
    VL_TRACE_DECL_QUAD(tracep,c+264,0,"output_height_work",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 32,0);
    VL_TRACE_DECL_QUAD(tracep,c+266,0,"output_width_work",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 32,0);
    VL_TRACE_DECL_QUAD(tracep,c+268,0,"origin_y",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 63,0);
    VL_TRACE_DECL_QUAD(tracep,c+270,0,"origin_x",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 63,0);
    VL_TRACE_DECL_QUAD(tracep,c+272,0,"output_y_step",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 63,0);
    VL_TRACE_DECL_QUAD(tracep,c+274,0,"output_x_step",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 63,0);
    VL_TRACE_DECL_QUAD(tracep,c+276,0,"source_y_work",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 63,0);
    VL_TRACE_DECL_QUAD(tracep,c+278,0,"source_x_work",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 63,0);
    VL_TRACE_DECL_WIDE(tracep,c+280,0,"channel_row_work",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 95,0);
    VL_TRACE_DECL_WIDE(tracep,c+283,0,"row_work",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 95,0);
    VL_TRACE_DECL_WIDE(tracep,c+286,0,"logical_offset_work",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 95,0);
    VL_TRACE_DECL_WIDE(tracep,c+289,0,"address_work",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 96,0);
    VL_TRACE_DECL_BUS(tracep,c+293,0,"tap_index",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::INTEGER, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+294,0,"kernel_y_work",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::INTEGER, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+295,0,"kernel_x_work",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::INTEGER, 31,0);
    VL_TRACE_DECL_BIT(tracep,c+296,0,"tap_range_error",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_POP_PREFIX(tracep);
    VL_TRACE_PUSH_PREFIX(tracep, "u_window", VerilatedTracePrefixType::SCOPE_MODULE, 0, 0);
    VL_TRACE_DECL_BUS(tracep,c+770,0,"candidate_count",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 3,0);
    VL_TRACE_DECL_WIDE(tracep,c+607,0,"candidates",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 71,0);
    VL_TRACE_DECL_BUS(tracep,c+613,0,"max_value",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 7,0);
    VL_TRACE_DECL_BUS(tracep,c+614,0,"error_code",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+751,0,"BAD_ARGUMENT",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+771,0,"tap_index",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::INTEGER, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+616,0,"candidate_value",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 7,0);
    VL_TRACE_DECL_BUS(tracep,c+617,0,"current_maximum",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 7,0);
    VL_TRACE_POP_PREFIX(tracep);
    VL_TRACE_POP_PREFIX(tracep);
    VL_TRACE_PUSH_PREFIX(tracep, "u_route_engine", VerilatedTracePrefixType::SCOPE_MODULE, 0, 0);
    VL_TRACE_DECL_BIT(tracep,c+723,0,"clk",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+0,0,"hard_reset",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+340,0,"abort",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+70,0,"start_valid",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+71,0,"start_ready",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BUS(tracep,c+297,0,"source_count",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+387,0,"groups",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+618,0,"group_id",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+53,0,"output_channel",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+54,0,"output_y",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+55,0,"output_x",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+113,0,"source0_base_address",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+114,0,"source0_length_bytes",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+116,0,"source0_channels",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+117,0,"source0_height",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+118,0,"source0_width",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+298,0,"source0_channel_start",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+299,0,"source0_channel_end",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+619,0,"source0_multiplier_q31",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+300,0,"source1_base_address",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+301,0,"source1_length_bytes",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+302,0,"source1_channels",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+303,0,"source1_height",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+304,0,"source1_width",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+305,0,"source1_channel_start",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+306,0,"source1_channel_end",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+620,0,"source1_multiplier_q31",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+41,0,"output_base_address",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+42,0,"output_length_bytes",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+120,0,"output_channels",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+121,0,"output_height",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+122,0,"output_width",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BIT(tracep,c+728,0,"backend_cancel",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+86,0,"backend_req_valid",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+87,0,"backend_req_ready",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+88,0,"backend_req_write",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BUS(tracep,c+89,0,"backend_req_addr",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+90,0,"backend_req_wdata",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+91,0,"backend_req_rstrb",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 3,0);
    VL_TRACE_DECL_BUS(tracep,c+92,0,"backend_req_wstrb",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 3,0);
    VL_TRACE_DECL_BIT(tracep,c+102,0,"backend_rsp_valid",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BUS(tracep,c+350,0,"backend_rsp_rdata",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+351,0,"backend_rsp_error",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BIT(tracep,c+365,0,"result_valid",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+106,0,"result_ready",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BUS(tracep,c+366,0,"result_source_index",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+367,0,"result_source_address",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+368,0,"result_output_address",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+369,0,"result_value",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 7,0);
    VL_TRACE_DECL_BUS(tracep,c+370,0,"result_error_code",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+738,0,"NONE",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+751,0,"BAD_ARGUMENT",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+752,0,"BAD_RANGE",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+753,0,"BAD_LENGTH",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+739,0,"INTERNAL",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+621,0,"state",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 3,0);
    VL_TRACE_DECL_BUS(tracep,c+622,0,"source_count_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+623,0,"groups_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+624,0,"group_id_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+625,0,"output_channel_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+626,0,"output_y_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+627,0,"output_x_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+628,0,"source0_base_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+629,0,"source0_length_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+630,0,"source0_channels_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+631,0,"source0_height_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+632,0,"source0_width_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+633,0,"source0_start_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+634,0,"source0_end_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+635,0,"source0_multiplier_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+636,0,"source0_value_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 7,0);
    VL_TRACE_DECL_BUS(tracep,c+637,0,"source1_base_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+638,0,"source1_length_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+639,0,"source1_channels_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+640,0,"source1_height_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+641,0,"source1_width_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+642,0,"source1_start_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+643,0,"source1_end_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+644,0,"source1_multiplier_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+645,0,"source1_value_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 7,0);
    VL_TRACE_DECL_BUS(tracep,c+646,0,"output_base_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+647,0,"output_length_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+648,0,"output_channels_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+649,0,"output_height_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+650,0,"output_width_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+366,0,"source_index_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+367,0,"source_address_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+368,0,"output_address_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+369,0,"result_value_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 7,0);
    VL_TRACE_DECL_BUS(tracep,c+370,0,"result_error_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+651,0,"query_output_channels",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+652,0,"query_output_height",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+653,0,"query_output_width",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+654,0,"query_source_index",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+655,0,"query_source_channel",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+656,0,"query_source_address",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+657,0,"query_output_value",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 7,0);
    VL_TRACE_DECL_BUS(tracep,c+658,0,"query_error_code",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_WIDE(tracep,c+659,0,"output_elements_work",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 64,0);
    VL_TRACE_DECL_WIDE(tracep,c+662,0,"output_offset_work",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 64,0);
    VL_TRACE_DECL_WIDE(tracep,c+665,0,"output_end_work",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 64,0);
    VL_TRACE_DECL_BUS(tracep,c+307,0,"selected_word_address",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+308,0,"selected_read_lane",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 3,0);
    VL_TRACE_DECL_BUS(tracep,c+668,0,"selected_byte_shift",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+669,0,"mapped_response_error",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_PUSH_PREFIX(tracep, "u_query", VerilatedTracePrefixType::SCOPE_MODULE, 0, 0);
    VL_TRACE_DECL_BUS(tracep,c+622,0,"source_count",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+623,0,"groups",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+624,0,"group_id",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+625,0,"output_channel",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+626,0,"output_y",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+627,0,"output_x",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+628,0,"source0_base_address",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+629,0,"source0_length_bytes",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+630,0,"source0_channels",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+631,0,"source0_height",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+632,0,"source0_width",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+633,0,"source0_channel_start",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+634,0,"source0_channel_end",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+635,0,"source0_multiplier_q31",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+636,0,"source0_value",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 7,0);
    VL_TRACE_DECL_BUS(tracep,c+637,0,"source1_base_address",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+638,0,"source1_length_bytes",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+639,0,"source1_channels",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+640,0,"source1_height",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+641,0,"source1_width",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+642,0,"source1_channel_start",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+643,0,"source1_channel_end",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+644,0,"source1_multiplier_q31",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+645,0,"source1_value",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 7,0);
    VL_TRACE_DECL_BUS(tracep,c+651,0,"output_channels",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+652,0,"output_height",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+653,0,"output_width",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+654,0,"source_index",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+655,0,"source_channel",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+656,0,"source_address",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+657,0,"output_value",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 7,0);
    VL_TRACE_DECL_BUS(tracep,c+658,0,"error_code",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+738,0,"OK",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+751,0,"BAD_ARGUMENT",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+752,0,"BAD_RANGE",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BIT(tracep,c+670,0,"bad_argument",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+671,0,"bad_range",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_QUAD(tracep,c+672,0,"source0_shape_bytes",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 63,0);
    VL_TRACE_DECL_QUAD(tracep,c+674,0,"source1_shape_bytes",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 63,0);
    VL_TRACE_DECL_QUAD(tracep,c+676,0,"source0_plane_elements",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 63,0);
    VL_TRACE_DECL_QUAD(tracep,c+678,0,"source1_plane_elements",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 63,0);
    VL_TRACE_DECL_QUAD(tracep,c+680,0,"source0_object_end",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 63,0);
    VL_TRACE_DECL_QUAD(tracep,c+682,0,"source1_object_end",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 63,0);
    VL_TRACE_DECL_QUAD(tracep,c+684,0,"output_channels_wide",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 63,0);
    VL_TRACE_DECL_QUAD(tracep,c+686,0,"expected_group_start",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 63,0);
    VL_TRACE_DECL_QUAD(tracep,c+688,0,"expected_group_end",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 63,0);
    VL_TRACE_DECL_QUAD(tracep,c+690,0,"selected_offset",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 63,0);
    VL_TRACE_DECL_QUAD(tracep,c+692,0,"selected_address_wide",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 63,0);
    VL_TRACE_DECL_BUS(tracep,c+694,0,"source0_selected_count",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+695,0,"source1_selected_count",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+696,0,"selected_multiplier",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+697,0,"selected_base_address",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+698,0,"selected_length_bytes",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+699,0,"selected_value",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 7,0);
    VL_TRACE_DECL_BUS(tracep,c+700,0,"selected_magnitude",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 7,0);
    VL_TRACE_DECL_QUAD(tracep,c+701,0,"scaled_product",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 63,0);
    VL_TRACE_DECL_QUAD(tracep,c+703,0,"rounded_magnitude",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 63,0);
    VL_TRACE_DECL_QUAD(tracep,c+705,0,"scaled_signed",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 63,0);
    VL_TRACE_DECL_BUS(tracep,c+707,0,"selected_source_index",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+708,0,"selected_source_channel",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_POP_PREFIX(tracep);
    VL_TRACE_POP_PREFIX(tracep);
    VL_TRACE_PUSH_PREFIX(tracep, "u_upsample_engine", VerilatedTracePrefixType::SCOPE_MODULE, 0, 0);
    VL_TRACE_DECL_BIT(tracep,c+723,0,"clk",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+0,0,"hard_reset",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+340,0,"abort",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+72,0,"start_valid",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+73,0,"start_ready",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BUS(tracep,c+113,0,"input_base_address",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+114,0,"input_length_bytes",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+41,0,"output_base_address",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+42,0,"output_length_bytes",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+116,0,"input_channels",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+117,0,"input_height",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+118,0,"input_width",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+709,0,"stride",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+53,0,"output_channel",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+54,0,"output_y",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+55,0,"output_x",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BIT(tracep,c+728,0,"backend_cancel",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+93,0,"backend_req_valid",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+94,0,"backend_req_ready",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+95,0,"backend_req_write",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BUS(tracep,c+96,0,"backend_req_addr",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+97,0,"backend_req_wdata",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+98,0,"backend_req_rstrb",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 3,0);
    VL_TRACE_DECL_BUS(tracep,c+99,0,"backend_req_wstrb",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 3,0);
    VL_TRACE_DECL_BIT(tracep,c+103,0,"backend_rsp_valid",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BUS(tracep,c+350,0,"backend_rsp_rdata",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+351,0,"backend_rsp_error",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BIT(tracep,c+371,0,"result_valid",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+107,0,"result_ready",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BUS(tracep,c+372,0,"result_source_address",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+373,0,"result_output_address",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+374,0,"result_value",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 7,0);
    VL_TRACE_DECL_BUS(tracep,c+375,0,"result_error_code",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+738,0,"NONE",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+751,0,"BAD_ARGUMENT",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+752,0,"BAD_RANGE",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+753,0,"BAD_LENGTH",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+739,0,"INTERNAL",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+772,0,"INPUT_BASE",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+773,0,"INPUT_LENGTH",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+774,0,"OUTPUT_BASE",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+769,0,"OUTPUT_LENGTH",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+775,0,"CHANNELS",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+776,0,"INPUT_DIMENSION",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+777,0,"UPSAMPLE_STRIDE",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+710,0,"state",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+372,0,"source_address_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+373,0,"output_address_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+374,0,"copied_value_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 7,0);
    VL_TRACE_DECL_BUS(tracep,c+375,0,"result_error_latched",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_QUAD(tracep,c+309,0,"query_output_height",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 63,0);
    VL_TRACE_DECL_QUAD(tracep,c+311,0,"query_output_width",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 63,0);
    VL_TRACE_DECL_BUS(tracep,c+313,0,"query_source_channel",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+314,0,"query_source_y",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+315,0,"query_source_x",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+316,0,"query_source_address",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+317,0,"query_unused_value",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 7,0);
    VL_TRACE_DECL_BUS(tracep,c+318,0,"query_error_code",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_WIDE(tracep,c+778,0,"query_unused_plane",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 1351,0);
    VL_TRACE_DECL_QUAD(tracep,c+319,0,"output_offset_work",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 63,0);
    VL_TRACE_DECL_WIDE(tracep,c+321,0,"output_address_work",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 64,0);
    VL_TRACE_DECL_BUS(tracep,c+711,0,"selected_byte_shift",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+712,0,"mapped_response_error",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_PUSH_PREFIX(tracep, "u_query", VerilatedTracePrefixType::SCOPE_MODULE, 0, 0);
    VL_TRACE_DECL_BUS(tracep,c+113,0,"input_base_address",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+116,0,"input_channels",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+117,0,"input_height",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+118,0,"input_width",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+709,0,"stride",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+53,0,"input_channel",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+54,0,"output_y",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+55,0,"output_x",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_WIDE(tracep,c+821,0,"source_plane",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 1351,0);
    VL_TRACE_DECL_QUAD(tracep,c+309,0,"output_height",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 63,0);
    VL_TRACE_DECL_QUAD(tracep,c+311,0,"output_width",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 63,0);
    VL_TRACE_DECL_BUS(tracep,c+313,0,"source_channel",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+314,0,"source_y",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+315,0,"source_x",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+316,0,"source_address",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+317,0,"output_value",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 7,0);
    VL_TRACE_DECL_BUS(tracep,c+318,0,"error_code",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+751,0,"BAD_ARGUMENT",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+752,0,"BAD_RANGE",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+776,0,"MAX_PLANE_DIMENSION",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_QUAD(tracep,c+324,0,"output_height_work",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 63,0);
    VL_TRACE_DECL_QUAD(tracep,c+326,0,"output_width_work",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 63,0);
    VL_TRACE_DECL_QUAD(tracep,c+328,0,"channel_row_work",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 63,0);
    VL_TRACE_DECL_QUAD(tracep,c+330,0,"row_work",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 63,0);
    VL_TRACE_DECL_QUAD(tracep,c+332,0,"byte_offset_work",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 63,0);
    VL_TRACE_DECL_BUS(tracep,c+334,0,"plane_index_work",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_WIDE(tracep,c+335,0,"address_work",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 64,0);
    VL_TRACE_POP_PREFIX(tracep);
    VL_TRACE_POP_PREFIX(tracep);
    VL_TRACE_POP_PREFIX(tracep);
    VL_TRACE_PUSH_PREFIX(tracep, "u_csr", VerilatedTracePrefixType::SCOPE_MODULE, 0, 0);
    VL_TRACE_DECL_BIT(tracep,c+723,0,"clk",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+0,0,"hard_reset",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+1,0,"csr_valid",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+5,0,"csr_ready",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+2,0,"csr_write",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BUS(tracep,c+3,0,"csr_addr",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 7,0);
    VL_TRACE_DECL_BUS(tracep,c+4,0,"csr_wdata",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+12,0,"csr_rdata",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BIT(tracep,c+13,0,"backend_memory_error_valid",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BUS(tracep,c+14,0,"backend_memory_error_code",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BIT(tracep,c+15,0,"operator_result_valid",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BUS(tracep,c+16,0,"operator_error_code",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BIT(tracep,c+339,0,"backend_start",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+340,0,"backend_abort",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+341,0,"busy",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+342,0,"done",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+343,0,"error",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+344,0,"pl_owns_buffers",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+345,0,"head_output_valid",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BUS(tracep,c+733,0,"REG_CMD",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 7,0);
    VL_TRACE_DECL_BUS(tracep,c+734,0,"REG_STATUS",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 7,0);
    VL_TRACE_DECL_BUS(tracep,c+735,0,"REG_ERROR_CODE",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 7,0);
    VL_TRACE_DECL_BUS(tracep,c+864,0,"REG_FRAME_ID",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 7,0);
    VL_TRACE_DECL_BUS(tracep,c+865,0,"REG_INPUT_ADDR",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 7,0);
    VL_TRACE_DECL_BUS(tracep,c+866,0,"REG_INPUT_BYTES",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 7,0);
    VL_TRACE_DECL_BUS(tracep,c+867,0,"REG_WEIGHT_ADDR",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 7,0);
    VL_TRACE_DECL_BUS(tracep,c+868,0,"REG_WEIGHT_BYTES",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 7,0);
    VL_TRACE_DECL_BUS(tracep,c+869,0,"REG_FEATURE_BASE",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 7,0);
    VL_TRACE_DECL_BUS(tracep,c+870,0,"REG_FEATURE_LIMIT",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 7,0);
    VL_TRACE_DECL_BUS(tracep,c+736,0,"REG_TIMEOUT",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 7,0);
    VL_TRACE_DECL_BUS(tracep,c+871,0,"REG_HEAD13_ADDR",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 7,0);
    VL_TRACE_DECL_BUS(tracep,c+872,0,"REG_HEAD13_BYTES",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 7,0);
    VL_TRACE_DECL_BUS(tracep,c+873,0,"REG_HEAD26_ADDR",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 7,0);
    VL_TRACE_DECL_BUS(tracep,c+874,0,"REG_HEAD26_BYTES",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 7,0);
    VL_TRACE_DECL_BUS(tracep,c+737,0,"REG_ACK",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 7,0);
    VL_TRACE_DECL_BUS(tracep,c+741,0,"DEFAULT_INPUT_ADDR",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+742,0,"DEFAULT_INPUT_BYTES",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+743,0,"DEFAULT_WEIGHT_ADDR",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+744,0,"DEFAULT_WEIGHT_BYTES",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+875,0,"DEFAULT_FEATURE_BASE",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+876,0,"DEFAULT_FEATURE_LIMIT",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+877,0,"DEFAULT_HEAD13_ADDR",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+878,0,"DEFAULT_HEAD13_BYTES",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+879,0,"DEFAULT_HEAD26_ADDR",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+880,0,"DEFAULT_HEAD26_BYTES",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+738,0,"NONE",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+751,0,"BAD_ARGUMENT",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+752,0,"BAD_RANGE",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+753,0,"BAD_LENGTH",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+740,0,"TIMEOUT_ERROR",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+739,0,"INTERNAL",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+713,0,"error_code",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+714,0,"frame_id",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+715,0,"active_frame_id",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+716,0,"input_addr",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+717,0,"input_bytes",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+718,0,"weight_addr",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+719,0,"weight_bytes",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+720,0,"timeout_cycles",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+721,0,"elapsed_cycles",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 31,0);
    VL_TRACE_DECL_BIT(tracep,c+722,0,"config_idle",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BUS(tracep,c+338,0,"mapped_memory_error",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_POP_PREFIX(tracep);
    VL_TRACE_PUSH_PREFIX(tracep, "unnamedblk1", VerilatedTracePrefixType::SCOPE_MODULE, 0, 0);
    VL_TRACE_DECL_BUS(tracep,c+10,0,"reads_before",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::INTEGER, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+11,0,"writes_before",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::INTEGER, 31,0);
    VL_TRACE_POP_PREFIX(tracep);
    VL_TRACE_POP_PREFIX(tracep);
}

VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root__trace_init_dtype_sub____8(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd* tracep, const char* name, uint32_t fidx, uint32_t c, VerilatedTraceSigDirection direction);

VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root__trace_init_dtype____8(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd* tracep, const char* name, uint32_t fidx, uint32_t c, VerilatedTraceSigDirection direction) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root__trace_init_dtype____8\n"); );
    Vtb_s2a_backend_fault_recovery__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    Vtb_s2a_backend_fault_recovery___024root__trace_init_dtype_sub____8(vlSelf, tracep, name, fidx, c, direction);
}

VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root__trace_init_dtype_sub____8(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd* tracep, const char* name, uint32_t fidx, uint32_t c, VerilatedTraceSigDirection direction) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root__trace_init_dtype_sub____8\n"); );
    Vtb_s2a_backend_fault_recovery__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    VL_TRACE_PUSH_PREFIX(tracep, name, VerilatedTracePrefixType::ARRAY_UNPACKED, 0, 7);
    for (int i = 0; i < 8; ++i) {
        VL_TRACE_DECL_BUS_ARRAY(tracep,c+0+i*1,fidx,"",-1, direction, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, (i + 0), 31,0);
    }
    VL_TRACE_POP_PREFIX(tracep);
}

VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root__trace_init_dtype_sub____13(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd* tracep, const char* name, uint32_t fidx, uint32_t c, VerilatedTraceSigDirection direction);

VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root__trace_init_dtype____13(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd* tracep, const char* name, uint32_t fidx, uint32_t c, VerilatedTraceSigDirection direction) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root__trace_init_dtype____13\n"); );
    Vtb_s2a_backend_fault_recovery__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    Vtb_s2a_backend_fault_recovery___024root__trace_init_dtype_sub____13(vlSelf, tracep, name, fidx, c, direction);
}

VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root__trace_init_dtype_sub____13(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd* tracep, const char* name, uint32_t fidx, uint32_t c, VerilatedTraceSigDirection direction) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root__trace_init_dtype_sub____13\n"); );
    Vtb_s2a_backend_fault_recovery__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    VL_TRACE_PUSH_PREFIX(tracep, name, VerilatedTracePrefixType::ARRAY_UNPACKED, 0, 7);
    for (int i = 0; i < 8; ++i) {
        VL_TRACE_DECL_WIDE_ARRAY(tracep,c+0+i*3,fidx,"",-1, direction, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, (i + 0), 79,0);
    }
    VL_TRACE_POP_PREFIX(tracep);
}

VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root__trace_init_dtype_sub____14(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd* tracep, const char* name, uint32_t fidx, uint32_t c, VerilatedTraceSigDirection direction);

VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root__trace_init_dtype____14(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd* tracep, const char* name, uint32_t fidx, uint32_t c, VerilatedTraceSigDirection direction) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root__trace_init_dtype____14\n"); );
    Vtb_s2a_backend_fault_recovery__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    Vtb_s2a_backend_fault_recovery___024root__trace_init_dtype_sub____14(vlSelf, tracep, name, fidx, c, direction);
}

VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root__trace_init_dtype_sub____14(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd* tracep, const char* name, uint32_t fidx, uint32_t c, VerilatedTraceSigDirection direction) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root__trace_init_dtype_sub____14\n"); );
    Vtb_s2a_backend_fault_recovery__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    VL_TRACE_PUSH_PREFIX(tracep, name, VerilatedTracePrefixType::ARRAY_UNPACKED, 0, 7);
    for (int i = 0; i < 8; ++i) {
        VL_TRACE_DECL_BUS_ARRAY(tracep,c+0+i*1,fidx,"",-1, direction, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, (i + 0), 31,0);
    }
    VL_TRACE_POP_PREFIX(tracep);
}

VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root__trace_init_dtype_sub____15(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd* tracep, const char* name, uint32_t fidx, uint32_t c, VerilatedTraceSigDirection direction);

VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root__trace_init_dtype____15(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd* tracep, const char* name, uint32_t fidx, uint32_t c, VerilatedTraceSigDirection direction) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root__trace_init_dtype____15\n"); );
    Vtb_s2a_backend_fault_recovery__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    Vtb_s2a_backend_fault_recovery___024root__trace_init_dtype_sub____15(vlSelf, tracep, name, fidx, c, direction);
}

VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root__trace_init_dtype_sub____15(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd* tracep, const char* name, uint32_t fidx, uint32_t c, VerilatedTraceSigDirection direction) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root__trace_init_dtype_sub____15\n"); );
    Vtb_s2a_backend_fault_recovery__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    VL_TRACE_PUSH_PREFIX(tracep, name, VerilatedTracePrefixType::ARRAY_UNPACKED, 0, 3);
    for (int i = 0; i < 4; ++i) {
        VL_TRACE_DECL_BUS_ARRAY(tracep,c+0+i*1,fidx,"",-1, direction, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, (i + 0), 31,0);
    }
    VL_TRACE_POP_PREFIX(tracep);
}

VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root__trace_init_dtype_sub____16(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd* tracep, const char* name, uint32_t fidx, uint32_t c, VerilatedTraceSigDirection direction);

VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root__trace_init_dtype____16(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd* tracep, const char* name, uint32_t fidx, uint32_t c, VerilatedTraceSigDirection direction) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root__trace_init_dtype____16\n"); );
    Vtb_s2a_backend_fault_recovery__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    Vtb_s2a_backend_fault_recovery___024root__trace_init_dtype_sub____16(vlSelf, tracep, name, fidx, c, direction);
}

VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root__trace_init_dtype_sub____16(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd* tracep, const char* name, uint32_t fidx, uint32_t c, VerilatedTraceSigDirection direction) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root__trace_init_dtype_sub____16\n"); );
    Vtb_s2a_backend_fault_recovery__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    VL_TRACE_PUSH_PREFIX(tracep, name, VerilatedTracePrefixType::ARRAY_UNPACKED, 0, 8);
    for (int i = 0; i < 9; ++i) {
        VL_TRACE_DECL_BUS_ARRAY(tracep,c+0+i*1,fidx,"",-1, direction, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, (i + 0), 31,0);
    }
    VL_TRACE_POP_PREFIX(tracep);
}

VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root__trace_init_dtype_sub____17(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd* tracep, const char* name, uint32_t fidx, uint32_t c, VerilatedTraceSigDirection direction);

VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root__trace_init_dtype____17(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd* tracep, const char* name, uint32_t fidx, uint32_t c, VerilatedTraceSigDirection direction) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root__trace_init_dtype____17\n"); );
    Vtb_s2a_backend_fault_recovery__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    Vtb_s2a_backend_fault_recovery___024root__trace_init_dtype_sub____17(vlSelf, tracep, name, fidx, c, direction);
}

VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root__trace_init_dtype_sub____17(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd* tracep, const char* name, uint32_t fidx, uint32_t c, VerilatedTraceSigDirection direction) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root__trace_init_dtype_sub____17\n"); );
    Vtb_s2a_backend_fault_recovery__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    VL_TRACE_PUSH_PREFIX(tracep, name, VerilatedTracePrefixType::ARRAY_UNPACKED, 0, 8);
    for (int i = 0; i < 9; ++i) {
        VL_TRACE_DECL_BUS_ARRAY(tracep,c+0+i*1,fidx,"",-1, direction, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, (i + 0), 31,0);
    }
    VL_TRACE_POP_PREFIX(tracep);
}

VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root__trace_init_dtype_sub____18(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd* tracep, const char* name, uint32_t fidx, uint32_t c, VerilatedTraceSigDirection direction);

VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root__trace_init_dtype____18(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd* tracep, const char* name, uint32_t fidx, uint32_t c, VerilatedTraceSigDirection direction) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root__trace_init_dtype____18\n"); );
    Vtb_s2a_backend_fault_recovery__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    Vtb_s2a_backend_fault_recovery___024root__trace_init_dtype_sub____18(vlSelf, tracep, name, fidx, c, direction);
}

VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root__trace_init_dtype_sub____18(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd* tracep, const char* name, uint32_t fidx, uint32_t c, VerilatedTraceSigDirection direction) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root__trace_init_dtype_sub____18\n"); );
    Vtb_s2a_backend_fault_recovery__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    VL_TRACE_PUSH_PREFIX(tracep, name, VerilatedTracePrefixType::ARRAY_UNPACKED, 0, 8);
    for (int i = 0; i < 9; ++i) {
        VL_TRACE_DECL_QUAD_ARRAY(tracep,c+0+i*2,fidx,"",-1, direction, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, (i + 0), 63,0);
    }
    VL_TRACE_POP_PREFIX(tracep);
}

VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root__trace_init_dtype_sub____19(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd* tracep, const char* name, uint32_t fidx, uint32_t c, VerilatedTraceSigDirection direction);

VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root__trace_init_dtype____19(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd* tracep, const char* name, uint32_t fidx, uint32_t c, VerilatedTraceSigDirection direction) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root__trace_init_dtype____19\n"); );
    Vtb_s2a_backend_fault_recovery__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    Vtb_s2a_backend_fault_recovery___024root__trace_init_dtype_sub____19(vlSelf, tracep, name, fidx, c, direction);
}

VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root__trace_init_dtype_sub____19(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd* tracep, const char* name, uint32_t fidx, uint32_t c, VerilatedTraceSigDirection direction) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root__trace_init_dtype_sub____19\n"); );
    Vtb_s2a_backend_fault_recovery__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    VL_TRACE_PUSH_PREFIX(tracep, name, VerilatedTracePrefixType::ARRAY_UNPACKED, 0, 8);
    for (int i = 0; i < 9; ++i) {
        VL_TRACE_DECL_QUAD_ARRAY(tracep,c+0+i*2,fidx,"",-1, direction, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, (i + 0), 63,0);
    }
    VL_TRACE_POP_PREFIX(tracep);
}

VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root__trace_init_sub__TOP__s2a_network_descriptor_pkg__0(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd* tracep) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root__trace_init_sub__TOP__s2a_network_descriptor_pkg__0\n"); );
    Vtb_s2a_backend_fault_recovery__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    const int c = vlSymsp->__Vm_baseCode;
    VL_TRACE_DECL_BUS(tracep,c+881,0,"S2A_LAYER_COUNT",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::INT, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+882,0,"S2A_CONV_CHANNEL_COUNT",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::INT, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+883,0,"S2A_MAX_INPUTS",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::INT, 31,0);
    VL_TRACE_DECL_BIT(tracep,c+884,0,"S2A_SERIAL_DISPATCH",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+884,0,"S2A_TIMEOUT_SCOPE_GLOBAL",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+885,0,"S2A_PER_LAYER_TIMEOUT_RESTART",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+885,0,"S2A_PS_VISIBLE_CSR_CHANGED",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BUS(tracep,c+886,0,"S2A_MEMORY_OUTSTANDING_LIMIT",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 7,0);
    VL_TRACE_DECL_WIDE(tracep,c+887,0,"S2A_G0_SPEC_SHA256",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 255,0);
    VL_TRACE_DECL_WIDE(tracep,c+895,0,"S2A_MANIFEST_SHA256",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 255,0);
    VL_TRACE_DECL_WIDE(tracep,c+903,0,"S2A_T22_SHA256",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 255,0);
    VL_TRACE_DECL_WIDE(tracep,c+911,0,"S2A_T23_SHA256",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 255,0);
    VL_TRACE_DECL_BUS(tracep,c+738,0,"S2A_OP_CONV",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+751,0,"S2A_OP_MAXPOOL",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+752,0,"S2A_OP_ROUTE",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+753,0,"S2A_OP_UPSAMPLE",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+919,0,"S2A_OP_YOLO",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 2,0);
    VL_TRACE_DECL_BUS(tracep,c+920,0,"S2A_INPUT_NETWORK",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 1,0);
    VL_TRACE_DECL_BUS(tracep,c+921,0,"S2A_INPUT_LAYER_OUTPUT",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 1,0);
    VL_TRACE_DECL_BIT(tracep,c+885,0,"S2A_OUTPUT_OWNED",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BIT(tracep,c+884,0,"S2A_OUTPUT_HEAD_ALIAS",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC);
    VL_TRACE_DECL_BUS(tracep,c+920,0,"S2A_ACT_NONE",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 1,0);
    VL_TRACE_DECL_BUS(tracep,c+921,0,"S2A_ACT_LINEAR",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 1,0);
    VL_TRACE_DECL_BUS(tracep,c+922,0,"S2A_ACT_LEAKY",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 1,0);
    VL_TRACE_DECL_BUS(tracep,c+920,0,"S2A_ROUTE_REQUANT_NONE",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 1,0);
    VL_TRACE_DECL_BUS(tracep,c+921,0,"S2A_ROUTE_REQUANT_TO_OUTPUT_SCALE",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 1,0);
    VL_TRACE_DECL_BUS(tracep,c+920,0,"S2A_ROUTE_ORDER_NONE",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 1,0);
    VL_TRACE_DECL_BUS(tracep,c+921,0,"S2A_ROUTE_ORDER_SLICE_THEN_CFG_CONCAT",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 1,0);
    VL_TRACE_DECL_BUS(tracep,c+923,0,"S2A_ROUTE_Q31_FRACTIONAL_BITS",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::INT, 31,0);
    VL_TRACE_DECL_BUS(tracep,c+920,0,"S2A_MAXPOOL_FORMULA_NONE",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 1,0);
    VL_TRACE_DECL_BUS(tracep,c+921,0,"S2A_MAXPOOL_FORMULA_DARKNET",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 1,0);
    VL_TRACE_DECL_BUS(tracep,c+920,0,"S2A_UPSAMPLE_NONE",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 1,0);
    VL_TRACE_DECL_BUS(tracep,c+921,0,"S2A_UPSAMPLE_NEAREST_REPEAT",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, 1,0);
}

VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root__trace_init_top(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd* tracep) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root__trace_init_top\n"); );
    Vtb_s2a_backend_fault_recovery__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    Vtb_s2a_backend_fault_recovery___024root__trace_init_sub__TOP__0(vlSelf, tracep);
}

VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root__trace_const_0(void* voidSelf, VerilatedVcd::Buffer* bufp);
VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root__trace_full_0(void* voidSelf, VerilatedVcd::Buffer* bufp);
void Vtb_s2a_backend_fault_recovery___024root__trace_chg_0(void* voidSelf, VerilatedVcd::Buffer* bufp);
void Vtb_s2a_backend_fault_recovery___024root__trace_cleanup(void* voidSelf, VerilatedVcd* /*unused*/);

VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root__trace_register(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd* tracep) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root__trace_register\n"); );
    Vtb_s2a_backend_fault_recovery__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    tracep->addConstCb(&Vtb_s2a_backend_fault_recovery___024root__trace_const_0, 0, vlSelf);
    tracep->addFullCb(&Vtb_s2a_backend_fault_recovery___024root__trace_full_0, 0, vlSelf);
    tracep->addChgCb(&Vtb_s2a_backend_fault_recovery___024root__trace_chg_0, 0, vlSelf);
    tracep->addCleanupCb(&Vtb_s2a_backend_fault_recovery___024root__trace_cleanup, vlSelf);
}

VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root__trace_const_0_sub_0(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd::Buffer* bufp);

VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root__trace_const_0(void* voidSelf, VerilatedVcd::Buffer* bufp) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root__trace_const_0\n"); );
    // Body
    Vtb_s2a_backend_fault_recovery___024root* const __restrict vlSelf VL_ATTR_UNUSED = static_cast<Vtb_s2a_backend_fault_recovery___024root*>(voidSelf);
    Vtb_s2a_backend_fault_recovery__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    Vtb_s2a_backend_fault_recovery___024root__trace_const_0_sub_0((&vlSymsp->TOP), bufp);
}

extern const VlWide<43>/*1375:0*/ Vtb_s2a_backend_fault_recovery__ConstPool__CONST_h3efedef1_0;
extern const VlWide<8>/*255:0*/ Vtb_s2a_backend_fault_recovery__ConstPool__CONST_h90a38f9a_0;
extern const VlWide<8>/*255:0*/ Vtb_s2a_backend_fault_recovery__ConstPool__CONST_ha68405d2_0;
extern const VlWide<8>/*255:0*/ Vtb_s2a_backend_fault_recovery__ConstPool__CONST_ha2435ec0_0;
extern const VlWide<8>/*255:0*/ Vtb_s2a_backend_fault_recovery__ConstPool__CONST_hf49351ff_0;

VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root__trace_const_0_sub_0(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd::Buffer* bufp) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root__trace_const_0_sub_0\n"); );
    Vtb_s2a_backend_fault_recovery__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    uint32_t* const oldp VL_ATTR_UNUSED = bufp->oldp(vlSymsp->__Vm_baseCode);
    bufp->fullCData(oldp+733,(0U),8);
    bufp->fullCData(oldp+734,(4U),8);
    bufp->fullCData(oldp+735,(8U),8);
    bufp->fullCData(oldp+736,(0x28U),8);
    bufp->fullCData(oldp+737,(0x3cU),8);
    bufp->fullCData(oldp+738,(0U),3);
    bufp->fullCData(oldp+739,(6U),3);
    bufp->fullCData(oldp+740,(5U),3);
    bufp->fullIData(oldp+741,(0U),32);
    bufp->fullIData(oldp+742,(0x0007ec00U),32);
    bufp->fullIData(oldp+743,(0x00100000U),32);
    bufp->fullIData(oldp+744,(0x005a12fcU),32);
    bufp->fullIData(oldp+745,(0x000186a0U),32);
    bufp->fullIData(oldp+746,(0x00000080U),32);
    bufp->fullIData(oldp+747,(0x00004e20U),32);
    bufp->fullIData(oldp+748,(0U),32);
    bufp->fullIData(oldp+749,(0x00100000U),32);
    bufp->fullIData(oldp+750,(0x005a12fcU),32);
    bufp->fullCData(oldp+751,(1U),3);
    bufp->fullCData(oldp+752,(2U),3);
    bufp->fullCData(oldp+753,(3U),3);
    bufp->fullCData(oldp+754,(7U),3);
    bufp->fullIData(oldp+755,(8U),32);
    bufp->fullIData(oldp+756,(0x0000c800U),32);
    bufp->fullIData(oldp+757,(0x00009000U),32);
    bufp->fullIData(oldp+758,(0x00000200U),32);
    bufp->fullIData(oldp+759,(0x014f3800U),32);
    bufp->fullIData(oldp+760,(0x00152000U),32);
    bufp->fullIData(oldp+761,(0x01645800U),32);
    bufp->fullIData(oldp+762,(0x00054800U),32);
    bufp->fullIData(oldp+763,(0x01816400U),32);
    bufp->fullIData(oldp+764,(0x000a9000U),32);
    bufp->fullIData(oldp+765,(0x018bf400U),32);
    bufp->fullIData(oldp+766,(0x0002a400U),32);
    bufp->fullIData(oldp+767,(0x019a7a00U),32);
    bufp->fullIData(oldp+768,(0x019fc200U),32);
    bufp->fullIData(oldp+769,(0x00015200U),32);
    bufp->fullCData(oldp+770,(4U),4);
    bufp->fullIData(oldp+771,(9U),32);
    bufp->fullIData(oldp+772,(0x01a51e00U),32);
    bufp->fullIData(oldp+773,(0x00005480U),32);
    bufp->fullIData(oldp+774,(0x01a57280U),32);
    bufp->fullIData(oldp+775,(0x00000080U),32);
    bufp->fullIData(oldp+776,(0x0000000dU),32);
    bufp->fullIData(oldp+777,(2U),32);
    bufp->fullWData(oldp+778,(Vtb_s2a_backend_fault_recovery__ConstPool__CONST_h3efedef1_0),1352);
    bufp->fullWData(oldp+821,(Vtb_s2a_backend_fault_recovery__ConstPool__CONST_h3efedef1_0),1352);
    bufp->fullCData(oldp+864,(0x0cU),8);
    bufp->fullCData(oldp+865,(0x10U),8);
    bufp->fullCData(oldp+866,(0x14U),8);
    bufp->fullCData(oldp+867,(0x18U),8);
    bufp->fullCData(oldp+868,(0x1cU),8);
    bufp->fullCData(oldp+869,(0x20U),8);
    bufp->fullCData(oldp+870,(0x24U),8);
    bufp->fullCData(oldp+871,(0x2cU),8);
    bufp->fullCData(oldp+872,(0x30U),8);
    bufp->fullCData(oldp+873,(0x34U),8);
    bufp->fullCData(oldp+874,(0x38U),8);
    bufp->fullIData(oldp+875,(0x01000000U),32);
    bufp->fullIData(oldp+876,(0x01adadb8U),32);
    bufp->fullIData(oldp+877,(0x01a46100U),32);
    bufp->fullIData(oldp+878,(0x000013ceU),32);
    bufp->fullIData(oldp+879,(0x01ad5e80U),32);
    bufp->fullIData(oldp+880,(0x00004f38U),32);
    bufp->fullIData(oldp+881,(0x00000026U),32);
    bufp->fullIData(oldp+882,(0x00000c5cU),32);
    bufp->fullIData(oldp+883,(2U),32);
    bufp->fullBit(oldp+884,(1U));
    bufp->fullBit(oldp+885,(0U));
    bufp->fullCData(oldp+886,(1U),8);
    bufp->fullWData(oldp+887,(Vtb_s2a_backend_fault_recovery__ConstPool__CONST_h90a38f9a_0),256);
    bufp->fullWData(oldp+895,(Vtb_s2a_backend_fault_recovery__ConstPool__CONST_ha68405d2_0),256);
    bufp->fullWData(oldp+903,(Vtb_s2a_backend_fault_recovery__ConstPool__CONST_ha2435ec0_0),256);
    bufp->fullWData(oldp+911,(Vtb_s2a_backend_fault_recovery__ConstPool__CONST_hf49351ff_0),256);
    bufp->fullCData(oldp+919,(4U),3);
    bufp->fullCData(oldp+920,(0U),2);
    bufp->fullCData(oldp+921,(1U),2);
    bufp->fullCData(oldp+922,(2U),2);
    bufp->fullIData(oldp+923,(0x0000001fU),32);
}

VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root__trace_full_0_sub_0(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd::Buffer* bufp);

VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root__trace_full_0(void* voidSelf, VerilatedVcd::Buffer* bufp) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root__trace_full_0\n"); );
    // Body
    Vtb_s2a_backend_fault_recovery___024root* const __restrict vlSelf VL_ATTR_UNUSED = static_cast<Vtb_s2a_backend_fault_recovery___024root*>(voidSelf);
    Vtb_s2a_backend_fault_recovery__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    Vtb_s2a_backend_fault_recovery___024root__trace_full_0_sub_0((&vlSymsp->TOP), bufp);
}

VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root__trace_full_dtype____0(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd::Buffer* bufp, uint32_t offset, const VlUnpacked<IData/*31:0*/, 9>& __VdtypeVar);
VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root__trace_full_dtype____1(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd::Buffer* bufp, uint32_t offset, const VlUnpacked<IData/*31:0*/, 9>& __VdtypeVar);
VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root__trace_full_dtype____2(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd::Buffer* bufp, uint32_t offset, const VlUnpacked<QData/*63:0*/, 9>& __VdtypeVar);
VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root__trace_full_dtype____3(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd::Buffer* bufp, uint32_t offset, const VlUnpacked<QData/*63:0*/, 9>& __VdtypeVar);
VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root__trace_full_dtype____4(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd::Buffer* bufp, uint32_t offset, const VlUnpacked<IData/*31:0*/, 8>& __VdtypeVar);
VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root__trace_full_dtype____5(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd::Buffer* bufp, uint32_t offset, const VlUnpacked<VlWide<3>/*79:0*/, 8>& __VdtypeVar);
VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root__trace_full_dtype____6(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd::Buffer* bufp, uint32_t offset, const VlUnpacked<IData/*31:0*/, 8>& __VdtypeVar);
VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root__trace_full_dtype____7(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd::Buffer* bufp, uint32_t offset, const VlUnpacked<IData/*31:0*/, 4>& __VdtypeVar);

VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root__trace_full_0_sub_0(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd::Buffer* bufp) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root__trace_full_0_sub_0\n"); );
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
    uint32_t* const oldp VL_ATTR_UNUSED = bufp->oldp(vlSymsp->__Vm_baseCode);
    bufp->fullBit(oldp+0,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__hard_reset));
    bufp->fullBit(oldp+1,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_valid));
    bufp->fullBit(oldp+2,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_write));
    bufp->fullCData(oldp+3,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_addr),8);
    bufp->fullIData(oldp+4,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_wdata),32);
    bufp->fullBit(oldp+5,((1U & (~ (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__hard_reset)))));
    bufp->fullBit(oldp+6,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__manual_mem_ready));
    bufp->fullBit(oldp+7,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__automatic_read_responses));
    bufp->fullCData(oldp+8,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__manual_mem_error_code),3);
    bufp->fullIData(oldp+9,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__transaction_start_cycle),32);
    bufp->fullIData(oldp+10,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__unnamedblk1__DOT__reads_before),32);
    bufp->fullIData(oldp+11,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__unnamedblk1__DOT__writes_before),32);
    bufp->fullIData(oldp+12,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__csr_rdata),32);
    bufp->fullBit(oldp+13,(((0U != (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__backend_memory_error_code)) 
                            & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__memory_handshake))));
    bufp->fullCData(oldp+14,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__backend_memory_error_code),3);
    bufp->fullBit(oldp+15,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__operator_result_valid));
    bufp->fullCData(oldp+16,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__operator_error_code),3);
    bufp->fullBit(oldp+17,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_valid));
    bufp->fullBit(oldp+18,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_write));
    bufp->fullIData(oldp+19,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_addr),32);
    bufp->fullIData(oldp+20,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__mem_wdata),32);
    bufp->fullCData(oldp+21,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_rstrb),4);
    bufp->fullBit(oldp+22,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mem_ready));
    bufp->fullCData(oldp+23,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_op),3);
    bufp->fullCData(oldp+24,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_input_count),2);
    bufp->fullIData(oldp+25,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_base[0]),32);
    bufp->fullIData(oldp+26,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_base[1]),32);
    bufp->fullIData(oldp+27,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_length[0]),32);
    bufp->fullIData(oldp+28,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_length[1]),32);
    bufp->fullSData(oldp+29,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_n[0]),16);
    bufp->fullSData(oldp+30,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_n[1]),16);
    bufp->fullSData(oldp+31,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_c[0]),16);
    bufp->fullSData(oldp+32,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_c[1]),16);
    bufp->fullSData(oldp+33,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0]),16);
    bufp->fullSData(oldp+34,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[1]),16);
    bufp->fullSData(oldp+35,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0]),16);
    bufp->fullSData(oldp+36,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[1]),16);
    bufp->fullSData(oldp+37,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_route_start[0]),16);
    bufp->fullSData(oldp+38,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_route_start[1]),16);
    bufp->fullSData(oldp+39,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_route_end[0]),16);
    bufp->fullSData(oldp+40,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_route_end[1]),16);
    bufp->fullIData(oldp+41,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_base),32);
    bufp->fullIData(oldp+42,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_length),32);
    bufp->fullSData(oldp+43,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_n),16);
    bufp->fullSData(oldp+44,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_c),16);
    bufp->fullSData(oldp+45,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_h),16);
    bufp->fullSData(oldp+46,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_w),16);
    bufp->fullQData(oldp+47,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_plane_elements),64);
    bufp->fullQData(oldp+49,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_batch_elements),64);
    bufp->fullQData(oldp+51,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_element_count),64);
    bufp->fullIData(oldp+53,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel),32);
    bufp->fullIData(oldp+54,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_y),32);
    bufp->fullIData(oldp+55,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_x),32);
    bufp->fullIData(oldp+56,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__mq_index),32);
    bufp->fullBit(oldp+57,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__descriptor_valid));
    bufp->fullBit(oldp+58,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_valid));
    bufp->fullBit(oldp+59,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__descriptor_fault));
    bufp->fullBit(oldp+60,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__is_alias_row));
    bufp->fullCData(oldp+61,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_layer_index),6);
    bufp->fullQData(oldp+62,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_output_plane_elements),64);
    bufp->fullQData(oldp+64,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_output_element_count),64);
    bufp->fullBit(oldp+66,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_start_valid));
    bufp->fullBit(oldp+67,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__start_ready));
    bufp->fullBit(oldp+68,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_start_valid));
    bufp->fullBit(oldp+69,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__start_ready));
    bufp->fullBit(oldp+70,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_start_valid));
    bufp->fullBit(oldp+71,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__start_ready));
    bufp->fullBit(oldp+72,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_start_valid));
    bufp->fullBit(oldp+73,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__start_ready));
    bufp->fullBit(oldp+74,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_valid));
    bufp->fullBit(oldp+75,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__backend_req_ready));
    bufp->fullBit(oldp+76,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_write));
    bufp->fullCData(oldp+77,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_rstrb),4);
    bufp->fullCData(oldp+78,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_wstrb),4);
    bufp->fullBit(oldp+79,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_valid));
    bufp->fullBit(oldp+80,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__backend_req_ready));
    bufp->fullBit(oldp+81,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_write));
    bufp->fullIData(oldp+82,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_addr),32);
    bufp->fullIData(oldp+83,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_wdata),32);
    bufp->fullCData(oldp+84,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_rstrb),4);
    bufp->fullCData(oldp+85,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_wstrb),4);
    bufp->fullBit(oldp+86,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_valid));
    bufp->fullBit(oldp+87,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__backend_req_ready));
    bufp->fullBit(oldp+88,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_write));
    bufp->fullIData(oldp+89,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_addr),32);
    bufp->fullIData(oldp+90,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_wdata),32);
    bufp->fullCData(oldp+91,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_rstrb),4);
    bufp->fullCData(oldp+92,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_wstrb),4);
    bufp->fullBit(oldp+93,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_valid));
    bufp->fullBit(oldp+94,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__backend_req_ready));
    bufp->fullBit(oldp+95,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_write));
    bufp->fullIData(oldp+96,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_addr),32);
    bufp->fullIData(oldp+97,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_wdata),32);
    bufp->fullCData(oldp+98,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_rstrb),4);
    bufp->fullCData(oldp+99,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_wstrb),4);
    bufp->fullBit(oldp+100,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__backend_rsp_valid));
    bufp->fullBit(oldp+101,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__backend_rsp_valid));
    bufp->fullBit(oldp+102,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__backend_rsp_valid));
    bufp->fullBit(oldp+103,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__backend_rsp_valid));
    bufp->fullBit(oldp+104,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_result_ready));
    bufp->fullBit(oldp+105,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_result_ready));
    bufp->fullBit(oldp+106,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_result_ready));
    bufp->fullBit(oldp+107,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_result_ready));
    bufp->fullIData(oldp+108,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_addr),32);
    bufp->fullIData(oldp+109,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_req_wdata),32);
    bufp->fullBit(oldp+110,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_result_valid));
    bufp->fullBit(oldp+111,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__memory_handshake));
    bufp->fullBit(oldp+112,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_start_ready));
    bufp->fullIData(oldp+113,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_base[0U]),32);
    bufp->fullIData(oldp+114,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_length[0U]),32);
    bufp->fullIData(oldp+115,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_n[0U]),32);
    bufp->fullIData(oldp+116,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_c[0U]),32);
    bufp->fullIData(oldp+117,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[0U]),32);
    bufp->fullIData(oldp+118,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[0U]),32);
    bufp->fullIData(oldp+119,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_n),32);
    bufp->fullIData(oldp+120,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_c),32);
    bufp->fullIData(oldp+121,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_h),32);
    bufp->fullIData(oldp+122,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_w),32);
    bufp->fullQData(oldp+123,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__patch_plane_bytes),64);
    bufp->fullBit(oldp+125,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_advance));
    bufp->fullQData(oldp+126,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_input_y),64);
    bufp->fullQData(oldp+128,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_input_x),64);
    bufp->fullBit(oldp+130,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_in_bounds));
    bufp->fullQData(oldp+131,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_source_offset),64);
    bufp->fullQData(oldp+133,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_source_address_wide),64);
    bufp->fullIData(oldp+135,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_area),32);
    bufp->fullIData(oldp+136,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_y),32);
    bufp->fullIData(oldp+137,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_x),32);
    bufp->fullQData(oldp+138,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_input_y),64);
    bufp->fullQData(oldp+140,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_input_x),64);
    bufp->fullBit(oldp+142,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_tap_in_bounds));
    bufp->fullQData(oldp+143,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index_wide),64);
    bufp->fullIData(oldp+145,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_index),32);
    bufp->fullCData(oldp+146,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[0]),8);
    bufp->fullCData(oldp+147,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[1]),8);
    bufp->fullCData(oldp+148,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[2]),8);
    bufp->fullCData(oldp+149,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[3]),8);
    bufp->fullCData(oldp+150,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[4]),8);
    bufp->fullCData(oldp+151,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[5]),8);
    bufp->fullCData(oldp+152,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[6]),8);
    bufp->fullCData(oldp+153,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[7]),8);
    bufp->fullCData(oldp+154,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[0]),8);
    bufp->fullCData(oldp+155,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[1]),8);
    bufp->fullCData(oldp+156,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[2]),8);
    bufp->fullCData(oldp+157,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[3]),8);
    bufp->fullCData(oldp+158,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[4]),8);
    bufp->fullCData(oldp+159,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[5]),8);
    bufp->fullCData(oldp+160,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[6]),8);
    bufp->fullCData(oldp+161,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[7]),8);
    bufp->fullSData(oldp+162,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[0]),16);
    bufp->fullSData(oldp+163,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[1]),16);
    bufp->fullSData(oldp+164,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[2]),16);
    bufp->fullSData(oldp+165,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[3]),16);
    bufp->fullSData(oldp+166,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[4]),16);
    bufp->fullSData(oldp+167,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[5]),16);
    bufp->fullSData(oldp+168,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[6]),16);
    bufp->fullSData(oldp+169,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[7]),16);
    bufp->fullQData(oldp+170,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[0]),33);
    bufp->fullQData(oldp+172,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[1]),33);
    bufp->fullQData(oldp+174,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[2]),33);
    bufp->fullQData(oldp+176,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[3]),33);
    bufp->fullQData(oldp+178,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[4]),33);
    bufp->fullQData(oldp+180,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[5]),33);
    bufp->fullQData(oldp+182,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[6]),33);
    bufp->fullQData(oldp+184,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[7]),33);
    bufp->fullBit(oldp+186,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_bad_argument));
    bufp->fullBit(oldp+187,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_overflow));
    bufp->fullCData(oldp+188,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mapped_response_error),3);
    bufp->fullIData(oldp+189,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__comb_lane),32);
    bufp->fullQData(oldp+190,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_output_height),33);
    bufp->fullQData(oldp+192,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_output_width),33);
    bufp->fullCData(oldp+194,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_count),4);
    bufp->fullSData(oldp+195,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask),9);
    Vtb_s2a_backend_fault_recovery___024root__trace_full_dtype____0(vlSelf, bufp, 196, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address);
    Vtb_s2a_backend_fault_recovery___024root__trace_full_dtype____1(vlSelf, bufp, 205, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_channel);
    Vtb_s2a_backend_fault_recovery___024root__trace_full_dtype____2(vlSelf, bufp, 214, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y);
    Vtb_s2a_backend_fault_recovery___024root__trace_full_dtype____3(vlSelf, bufp, 232, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x);
    bufp->fullCData(oldp+250,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_error_code),3);
    bufp->fullBit(oldp+251,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_inputs_valid));
    bufp->fullBit(oldp+252,(((0U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_error_code)) 
                             & ((4U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_count)) 
                                & ((0x0fU == (0x0000000fU 
                                              & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask))) 
                                   & ((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_output_height 
                                       == (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_h))) 
                                      & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_output_width 
                                         == (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_w)))))))));
    bufp->fullQData(oldp+253,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_offset_work),64);
    bufp->fullWData(oldp+255,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_address_work),65);
    bufp->fullIData(oldp+258,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__selected_input_word_address),32);
    bufp->fullCData(oldp+259,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__selected_input_lane),4);
    bufp->fullQData(oldp+260,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__extent_y),33);
    bufp->fullQData(oldp+262,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__extent_x),33);
    bufp->fullQData(oldp+264,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_height_work),33);
    bufp->fullQData(oldp+266,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_width_work),33);
    bufp->fullQData(oldp+268,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__origin_y),64);
    bufp->fullQData(oldp+270,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__origin_x),64);
    bufp->fullQData(oldp+272,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_y_step),64);
    bufp->fullQData(oldp+274,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__output_x_step),64);
    bufp->fullQData(oldp+276,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_y_work),64);
    bufp->fullQData(oldp+278,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__source_x_work),64);
    bufp->fullWData(oldp+280,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__channel_row_work),96);
    bufp->fullWData(oldp+283,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__row_work),96);
    bufp->fullWData(oldp+286,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__logical_offset_work),96);
    bufp->fullWData(oldp+289,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__address_work),97);
    bufp->fullIData(oldp+293,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__tap_index),32);
    bufp->fullIData(oldp+294,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_y_work),32);
    bufp->fullIData(oldp+295,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__kernel_x_work),32);
    bufp->fullBit(oldp+296,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_geometry__DOT__tap_range_error));
    bufp->fullIData(oldp+297,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_input_count),32);
    bufp->fullIData(oldp+298,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_route_start[0U]),32);
    bufp->fullIData(oldp+299,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_route_end[0U]),32);
    bufp->fullIData(oldp+300,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_base[1U]),32);
    bufp->fullIData(oldp+301,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_length[1U]),32);
    bufp->fullIData(oldp+302,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_c[1U]),32);
    bufp->fullIData(oldp+303,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[1U]),32);
    bufp->fullIData(oldp+304,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[1U]),32);
    bufp->fullIData(oldp+305,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_route_start[1U]),32);
    bufp->fullIData(oldp+306,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_route_end[1U]),32);
    bufp->fullIData(oldp+307,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__selected_word_address),32);
    bufp->fullCData(oldp+308,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__selected_read_lane),4);
    bufp->fullQData(oldp+309,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_output_height),64);
    bufp->fullQData(oldp+311,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_output_width),64);
    bufp->fullIData(oldp+313,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_channel),32);
    bufp->fullIData(oldp+314,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_y),32);
    bufp->fullIData(oldp+315,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_x),32);
    bufp->fullIData(oldp+316,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_address),32);
    bufp->fullCData(oldp+317,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_unused_value),8);
    bufp->fullCData(oldp+318,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_error_code),3);
    bufp->fullQData(oldp+319,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__output_offset_work),64);
    bufp->fullWData(oldp+321,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__output_address_work),65);
    bufp->fullQData(oldp+324,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__output_height_work),64);
    bufp->fullQData(oldp+326,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__output_width_work),64);
    bufp->fullQData(oldp+328,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__channel_row_work),64);
    bufp->fullQData(oldp+330,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__row_work),64);
    bufp->fullQData(oldp+332,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__byte_offset_work),64);
    bufp->fullIData(oldp+334,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__plane_index_work),32);
    bufp->fullWData(oldp+335,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__u_query__DOT__address_work),65);
    bufp->fullCData(oldp+338,((((1U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__backend_memory_error_code)) 
                                | ((2U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__backend_memory_error_code)) 
                                   | (6U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__backend_memory_error_code))))
                                ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__backend_memory_error_code)
                                : 6U)),3);
    bufp->fullBit(oldp+339,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__backend_start));
    bufp->fullBit(oldp+340,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__backend_abort));
    bufp->fullBit(oldp+341,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__busy));
    bufp->fullBit(oldp+342,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__done));
    bufp->fullBit(oldp+343,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__error));
    bufp->fullBit(oldp+344,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__buffer_owner_pl));
    bufp->fullBit(oldp+345,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__head_output_valid));
    bufp->fullCData(oldp+346,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state),3);
    bufp->fullCData(oldp+347,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor),6);
    bufp->fullIData(oldp+348,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_element_index),32);
    bufp->fullBit(oldp+349,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_pending));
    bufp->fullIData(oldp+350,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_data_latched),32);
    bufp->fullCData(oldp+351,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_error_latched),3);
    bufp->fullCData(oldp+352,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_target_latched),3);
    bufp->fullIData(oldp+353,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__request_address_latched),32);
    bufp->fullIData(oldp+354,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__request_wdata_latched),32);
    bufp->fullBit(oldp+355,((0x13U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__state))));
    bufp->fullCData(oldp+356,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__result_error_latched),3);
    bufp->fullBit(oldp+357,((6U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__state))));
    __Vtemp_2[0U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched[0U];
    __Vtemp_2[1U] = vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched[1U];
    __Vtemp_2[2U] = (IData)((((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched[3U])) 
                              << 0x00000020U) | (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched[2U]))));
    __Vtemp_2[3U] = (IData)(((((QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched[3U])) 
                               << 0x00000020U) | (QData)((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched[2U]))) 
                             >> 0x00000020U));
    bufp->fullWData(oldp+358,(__Vtemp_2),128);
    bufp->fullIData(oldp+362,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_address_latched),32);
    bufp->fullCData(oldp+363,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__result_value_latched),8);
    bufp->fullCData(oldp+364,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__result_error_latched),3);
    bufp->fullBit(oldp+365,((7U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__state))));
    bufp->fullIData(oldp+366,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source_index_latched),32);
    bufp->fullIData(oldp+367,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source_address_latched),32);
    bufp->fullIData(oldp+368,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_address_latched),32);
    bufp->fullCData(oldp+369,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__result_value_latched),8);
    bufp->fullCData(oldp+370,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__result_error_latched),3);
    bufp->fullBit(oldp+371,((5U == (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__state))));
    bufp->fullIData(oldp+372,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__source_address_latched),32);
    bufp->fullIData(oldp+373,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__output_address_latched),32);
    bufp->fullCData(oldp+374,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__copied_value_latched),8);
    bufp->fullCData(oldp+375,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__result_error_latched),3);
    bufp->fullCData(oldp+376,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_result_error),3);
    bufp->fullIData(oldp+377,(((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_LAYER_INDEX
                               [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor]
                                : 0U)),32);
    bufp->fullIData(oldp+378,(((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_WEIGHT_LAYER_INDEX
                               [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor]
                                : 0U)),32);
    bufp->fullIData(oldp+379,(((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_KERNEL_H
                               [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor]
                                : 0U)),32);
    bufp->fullIData(oldp+380,(((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_KERNEL_W
                               [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor]
                                : 0U)),32);
    bufp->fullIData(oldp+381,(((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_STRIDE_H
                               [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor]
                                : 0U)),32);
    bufp->fullIData(oldp+382,(((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_STRIDE_W
                               [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor]
                                : 0U)),32);
    bufp->fullIData(oldp+383,(((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_PADDING_LEFT
                               [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor]
                                : 0U)),32);
    bufp->fullIData(oldp+384,(((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_PADDING_RIGHT
                               [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor]
                                : 0U)),32);
    bufp->fullIData(oldp+385,(((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_PADDING_TOP
                               [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor]
                                : 0U)),32);
    bufp->fullIData(oldp+386,(((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_PADDING_BOTTOM
                               [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor]
                                : 0U)),32);
    bufp->fullIData(oldp+387,(((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_GROUP_COUNT
                               [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor]
                                : 0U)),32);
    bufp->fullIData(oldp+388,((((- (IData)((1U & ((
                                                   (0x25U 
                                                    >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
                                                    ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_PADDING_VALUE_INT8
                                                   [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor]
                                                    : 0U) 
                                                  >> 7U)))) 
                                << 8U) | ((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
                                           ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_PADDING_VALUE_INT8
                                          [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor]
                                           : 0U))),32);
    bufp->fullIData(oldp+389,(((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_GF8_WEIGHT_OFFSET
                               [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor]
                                : 0U)),32);
    bufp->fullIData(oldp+390,(((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_GF8_WEIGHT_BYTES
                               [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor]
                                : 0U)),32);
    bufp->fullCData(oldp+391,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_conv_engine__activation_mode),2);
    bufp->fullBit(oldp+392,((0U != (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__state))));
    bufp->fullCData(oldp+393,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__state),5);
    bufp->fullIData(oldp+394,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched),32);
    bufp->fullIData(oldp+395,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_layer_index_latched),32);
    bufp->fullIData(oldp+396,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_base_latched),32);
    bufp->fullIData(oldp+397,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_length_latched),32);
    bufp->fullIData(oldp+398,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_batch_count_latched),32);
    bufp->fullIData(oldp+399,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_channels_latched),32);
    bufp->fullIData(oldp+400,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_height_latched),32);
    bufp->fullIData(oldp+401,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_width_latched),32);
    bufp->fullIData(oldp+402,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_base_latched),32);
    bufp->fullIData(oldp+403,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_length_latched),32);
    bufp->fullIData(oldp+404,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_batch_count_latched),32);
    bufp->fullIData(oldp+405,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_channels_latched),32);
    bufp->fullIData(oldp+406,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_latched),32);
    bufp->fullIData(oldp+407,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_latched),32);
    bufp->fullIData(oldp+408,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_height_latched),32);
    bufp->fullIData(oldp+409,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_width_latched),32);
    bufp->fullIData(oldp+410,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__stride_y_latched),32);
    bufp->fullIData(oldp+411,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__stride_x_latched),32);
    bufp->fullIData(oldp+412,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__pad_left_latched),32);
    bufp->fullIData(oldp+413,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__pad_right_latched),32);
    bufp->fullIData(oldp+414,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__pad_top_latched),32);
    bufp->fullIData(oldp+415,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__pad_bottom_latched),32);
    bufp->fullIData(oldp+416,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__groups_latched),32);
    bufp->fullIData(oldp+417,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__padding_latched),32);
    bufp->fullIData(oldp+418,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_package_base_latched),32);
    bufp->fullIData(oldp+419,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_package_length_latched),32);
    bufp->fullIData(oldp+420,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__quantized_weight_offset_latched),32);
    bufp->fullIData(oldp+421,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__quantized_weight_bytes_latched),32);
    bufp->fullIData(oldp+422,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_batch_latched),32);
    bufp->fullCData(oldp+423,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__activation_mode_latched),2);
    Vtb_s2a_backend_fault_recovery___024root__trace_full_dtype____4(vlSelf, bufp, 424, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator);
    bufp->fullIData(oldp+432,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_latched),32);
    bufp->fullIData(oldp+433,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base),32);
    bufp->fullIData(oldp+434,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_y),32);
    bufp->fullIData(oldp+435,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_x),32);
    bufp->fullIData(oldp+436,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__tile_height),32);
    bufp->fullIData(oldp+437,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__tile_width),32);
    bufp->fullIData(oldp+438,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__patch_height),32);
    bufp->fullIData(oldp+439,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__patch_width),32);
    bufp->fullIData(oldp+440,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__patch_byte_count),32);
    bufp->fullIData(oldp+441,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__tile_point_count),32);
    bufp->fullIData(oldp+442,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count),32);
    bufp->fullIData(oldp+443,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_index),32);
    bufp->fullIData(oldp+444,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_lane_index),32);
    bufp->fullIData(oldp+445,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_reduction_index),32);
    bufp->fullIData(oldp+446,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_index),32);
    bufp->fullIData(oldp+447,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_reduction_index),32);
    bufp->fullIData(oldp+448,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_lane_index),32);
    bufp->fullIData(oldp+449,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_point_index),32);
    bufp->fullCData(oldp+450,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__request_strobe_latched),4);
    bufp->fullBit(oldp+451,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__request_write_latched));
    bufp->fullIData(oldp+452,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_address_latched),32);
    bufp->fullCData(oldp+453,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_value_latched),8);
    bufp->fullWData(oldp+454,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_elements_wide),128);
    bufp->fullWData(oldp+458,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_elements_wide),128);
    bufp->fullWData(oldp+462,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__expected_weight_bytes_wide),128);
    bufp->fullWData(oldp+466,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_wide),128);
    bufp->fullWData(oldp+470,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_end_wide),128);
    bufp->fullWData(oldp+474,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_end_wide),128);
    bufp->fullWData(oldp+478,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_package_end_wide),128);
    bufp->fullWData(oldp+482,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__quantized_weight_end_wide),128);
    bufp->fullQData(oldp+486,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_numerator),64);
    bufp->fullQData(oldp+488,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_numerator),64);
    bufp->fullQData(oldp+490,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_shape_span),64);
    bufp->fullQData(oldp+492,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_shape_span),64);
    bufp->fullQData(oldp+494,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_shape_product),64);
    bufp->fullQData(oldp+496,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_shape_product),64);
    bufp->fullQData(oldp+498,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_span_plus_stride),64);
    bufp->fullQData(oldp+500,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_span_plus_stride),64);
    bufp->fullWData(oldp+502,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_height_wide),128);
    bufp->fullWData(oldp+506,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_width_wide),128);
    bufp->fullWData(oldp+510,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__full_tile_patch_bytes_wide),128);
    bufp->fullWData(oldp+514,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__full_weight_group_bytes_wide),128);
    bufp->fullBit(oldp+518,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__validation_ok));
    bufp->fullCData(oldp+519,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__validation_error),3);
    bufp->fullIData(oldp+520,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_channel),32);
    bufp->fullIData(oldp+521,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_y),32);
    bufp->fullIData(oldp+522,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_x),32);
    bufp->fullIData(oldp+523,((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base 
                               + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_lane_index)),32);
    bufp->fullQData(oldp+524,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_source_address_wide),64);
    bufp->fullIData(oldp+526,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_input_channel),32);
    bufp->fullIData(oldp+527,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_y),32);
    bufp->fullIData(oldp+528,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_kernel_x),32);
    bufp->fullIData(oldp+529,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_lane),32);
    bufp->fullIData(oldp+530,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_index),32);
    bufp->fullWData(oldp+531,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_parameter),80);
    bufp->fullIData(oldp+534,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_bias),32);
    bufp->fullBit(oldp+535,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_prefetch_invalid));
    Vtb_s2a_backend_fault_recovery___024root__trace_full_dtype____5(vlSelf, bufp, 536, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_mq_parameter);
    Vtb_s2a_backend_fault_recovery___024root__trace_full_dtype____6(vlSelf, bufp, 560, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_bias);
    bufp->fullIData(oldp+568,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_lane_index),32);
    bufp->fullWData(oldp+569,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_parameter),80);
    bufp->fullIData(oldp+572,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_accumulator),32);
    bufp->fullIData(oldp+573,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier),32);
    bufp->fullIData(oldp+574,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift),32);
    bufp->fullIData(oldp+575,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude),32);
    bufp->fullQData(oldp+576,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product),64);
    bufp->fullQData(oldp+578,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add),64);
    bufp->fullQData(oldp+580,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude),64);
    bufp->fullQData(oldp+582,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value),64);
    bufp->fullCData(oldp+584,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requantized_value),8);
    bufp->fullIData(oldp+585,((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_y 
                               + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_point_scan_y)),32);
    bufp->fullIData(oldp+586,((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_x 
                               + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_point_scan_x)),32);
    bufp->fullIData(oldp+587,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_point_scan_y),32);
    bufp->fullIData(oldp+588,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_point_scan_x),32);
    bufp->fullIData(oldp+589,((vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base 
                               + vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_lane_index)),32);
    bufp->fullQData(oldp+590,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_byte_offset_wide),64);
    bufp->fullQData(oldp+592,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_address_wide),64);
    bufp->fullCData(oldp+594,((3U & (0x00030210U >> 
                                     ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__request_strobe_latched) 
                                      << 1U)))),2);
    bufp->fullIData(oldp+595,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__seq_lane),32);
    bufp->fullIData(oldp+596,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__layer_index),32);
    bufp->fullIData(oldp+597,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_height),32);
    bufp->fullIData(oldp+598,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width),32);
    bufp->fullIData(oldp+599,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_y),32);
    bufp->fullIData(oldp+600,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_x),32);
    bufp->fullIData(oldp+601,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__darknet_padding_parameter),32);
    bufp->fullCData(oldp+602,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__state),4);
    Vtb_s2a_backend_fault_recovery___024root__trace_full_dtype____7(vlSelf, bufp, 603, vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched);
    bufp->fullWData(oldp+607,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__candidate_values_latched),72);
    bufp->fullCData(oldp+610,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__read_tap_index),3);
    bufp->fullIData(oldp+611,((0x00000018U & ((- (IData)(
                                                         (4U 
                                                          > (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__read_tap_index)))) 
                                              & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched
                                                 [(3U 
                                                   & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__read_tap_index))] 
                                                 << 3U)))),32);
    bufp->fullCData(oldp+612,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__mapped_response_error),3);
    bufp->fullCData(oldp+613,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__window_max_value),8);
    bufp->fullCData(oldp+614,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__window_error_code),3);
    bufp->fullIData(oldp+615,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_index),32);
    bufp->fullCData(oldp+616,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__candidate_value),8);
    bufp->fullCData(oldp+617,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__u_window__DOT__current_maximum),8);
    bufp->fullIData(oldp+618,(((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_ROUTE_GROUP_ID
                               [vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor]
                                : 0U)),32);
    bufp->fullIData(oldp+619,(vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_ROUTE_SOURCE_MULTIPLIER_Q31
                              [((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
                                 ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor)
                                 : 0U)][0U]),32);
    bufp->fullIData(oldp+620,(vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_ROUTE_SOURCE_MULTIPLIER_Q31
                              [((0x25U >= (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor))
                                 ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor)
                                 : 0U)][1U]),32);
    bufp->fullCData(oldp+621,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__state),4);
    bufp->fullIData(oldp+622,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source_count_latched),32);
    bufp->fullIData(oldp+623,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__groups_latched),32);
    bufp->fullIData(oldp+624,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__group_id_latched),32);
    bufp->fullIData(oldp+625,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_channel_latched),32);
    bufp->fullIData(oldp+626,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_y_latched),32);
    bufp->fullIData(oldp+627,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_x_latched),32);
    bufp->fullIData(oldp+628,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_base_latched),32);
    bufp->fullIData(oldp+629,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_length_latched),32);
    bufp->fullIData(oldp+630,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_channels_latched),32);
    bufp->fullIData(oldp+631,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_height_latched),32);
    bufp->fullIData(oldp+632,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_width_latched),32);
    bufp->fullIData(oldp+633,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_start_latched),32);
    bufp->fullIData(oldp+634,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_end_latched),32);
    bufp->fullIData(oldp+635,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_multiplier_latched),32);
    bufp->fullCData(oldp+636,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_value_latched),8);
    bufp->fullIData(oldp+637,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_base_latched),32);
    bufp->fullIData(oldp+638,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_length_latched),32);
    bufp->fullIData(oldp+639,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_channels_latched),32);
    bufp->fullIData(oldp+640,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_height_latched),32);
    bufp->fullIData(oldp+641,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_width_latched),32);
    bufp->fullIData(oldp+642,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_start_latched),32);
    bufp->fullIData(oldp+643,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_end_latched),32);
    bufp->fullIData(oldp+644,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_multiplier_latched),32);
    bufp->fullCData(oldp+645,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_value_latched),8);
    bufp->fullIData(oldp+646,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_base_latched),32);
    bufp->fullIData(oldp+647,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_length_latched),32);
    bufp->fullIData(oldp+648,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_channels_latched),32);
    bufp->fullIData(oldp+649,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_height_latched),32);
    bufp->fullIData(oldp+650,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_width_latched),32);
    bufp->fullIData(oldp+651,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__query_output_channels),32);
    bufp->fullIData(oldp+652,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__query_output_height),32);
    bufp->fullIData(oldp+653,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__query_output_width),32);
    bufp->fullIData(oldp+654,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__query_source_index),32);
    bufp->fullIData(oldp+655,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__query_source_channel),32);
    bufp->fullIData(oldp+656,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__query_source_address),32);
    bufp->fullCData(oldp+657,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__query_output_value),8);
    bufp->fullCData(oldp+658,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__query_error_code),3);
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
    bufp->fullWData(oldp+659,(__Vtemp_9),65);
    bufp->fullWData(oldp+662,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_offset_work),65);
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
    bufp->fullWData(oldp+665,(__Vtemp_14),65);
    bufp->fullIData(oldp+668,((0x00000018U & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source_address_latched 
                                              << 3U))),32);
    bufp->fullCData(oldp+669,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__mapped_response_error),3);
    bufp->fullBit(oldp+670,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_argument));
    bufp->fullBit(oldp+671,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__bad_range));
    bufp->fullQData(oldp+672,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source0_shape_bytes),64);
    bufp->fullQData(oldp+674,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_shape_bytes),64);
    bufp->fullQData(oldp+676,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source0_plane_elements),64);
    bufp->fullQData(oldp+678,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_plane_elements),64);
    bufp->fullQData(oldp+680,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source0_object_end),64);
    bufp->fullQData(oldp+682,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_object_end),64);
    bufp->fullQData(oldp+684,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__output_channels_wide),64);
    bufp->fullQData(oldp+686,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__expected_group_start),64);
    bufp->fullQData(oldp+688,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__expected_group_end),64);
    bufp->fullQData(oldp+690,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_offset),64);
    bufp->fullQData(oldp+692,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_address_wide),64);
    bufp->fullIData(oldp+694,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source0_selected_count),32);
    bufp->fullIData(oldp+695,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__source1_selected_count),32);
    bufp->fullIData(oldp+696,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_multiplier),32);
    bufp->fullIData(oldp+697,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_base_address),32);
    bufp->fullIData(oldp+698,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_length_bytes),32);
    bufp->fullCData(oldp+699,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_value),8);
    bufp->fullCData(oldp+700,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_magnitude),8);
    bufp->fullQData(oldp+701,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__scaled_product),64);
    bufp->fullQData(oldp+703,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__rounded_magnitude),64);
    bufp->fullQData(oldp+705,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__scaled_signed),64);
    bufp->fullIData(oldp+707,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_source_index),32);
    bufp->fullIData(oldp+708,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__u_query__DOT__selected_source_channel),32);
    bufp->fullIData(oldp+709,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_upsample_engine__stride),32);
    bufp->fullCData(oldp+710,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__state),3);
    bufp->fullIData(oldp+711,((0x00000018U & (vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__source_address_latched 
                                              << 3U))),32);
    bufp->fullCData(oldp+712,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__mapped_response_error),3);
    bufp->fullCData(oldp+713,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__error_code),3);
    bufp->fullIData(oldp+714,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__frame_id),32);
    bufp->fullIData(oldp+715,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__active_frame_id),32);
    bufp->fullIData(oldp+716,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__input_addr),32);
    bufp->fullIData(oldp+717,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__input_bytes),32);
    bufp->fullIData(oldp+718,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__weight_addr),32);
    bufp->fullIData(oldp+719,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__weight_bytes),32);
    bufp->fullIData(oldp+720,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__timeout_cycles),32);
    bufp->fullIData(oldp+721,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__elapsed_cycles),32);
    bufp->fullBit(oldp+722,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__config_idle));
    bufp->fullBit(oldp+723,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__clk));
    bufp->fullCData(oldp+724,((((4U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
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
    bufp->fullIData(oldp+725,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__simulation_cycle_count),32);
    bufp->fullIData(oldp+726,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__memory_read_handshakes),32);
    bufp->fullIData(oldp+727,(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__memory_write_side_effects),32);
    bufp->fullBit(oldp+728,(((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__hard_reset) 
                             | (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__backend_abort))));
    bufp->fullBit(oldp+729,(((4U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                              ? ((~ ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                     >> 1U)) & ((1U 
                                                 & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                                                 ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_valid)
                                                 : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_valid)))
                              : (((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                  >> 1U) & ((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                                             ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_valid)
                                             : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_valid))))));
    bufp->fullBit(oldp+730,(((4U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                              ? ((~ ((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                     >> 1U)) & ((1U 
                                                 & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                                                 ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_write)
                                                 : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_write)))
                              : (((IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state) 
                                  >> 1U) & ((1U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
                                             ? (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_write)
                                             : (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_write))))));
    bufp->fullCData(oldp+731,(((4U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
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
    bufp->fullCData(oldp+732,(((4U & (IData)(vlSelfRef.tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state))
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

VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root__trace_full_dtype____0(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd::Buffer* bufp, uint32_t offset, const VlUnpacked<IData/*31:0*/, 9>& __VdtypeVar) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root__trace_full_dtype____0\n"); );
    Vtb_s2a_backend_fault_recovery__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    uint32_t* const oldp VL_ATTR_UNUSED = bufp->oldp(vlSymsp->__Vm_baseCode + offset);
    bufp->fullIData(oldp+0,(__VdtypeVar[0]),32);
    bufp->fullIData(oldp+1,(__VdtypeVar[1]),32);
    bufp->fullIData(oldp+2,(__VdtypeVar[2]),32);
    bufp->fullIData(oldp+3,(__VdtypeVar[3]),32);
    bufp->fullIData(oldp+4,(__VdtypeVar[4]),32);
    bufp->fullIData(oldp+5,(__VdtypeVar[5]),32);
    bufp->fullIData(oldp+6,(__VdtypeVar[6]),32);
    bufp->fullIData(oldp+7,(__VdtypeVar[7]),32);
    bufp->fullIData(oldp+8,(__VdtypeVar[8]),32);
}

VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root__trace_full_dtype____1(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd::Buffer* bufp, uint32_t offset, const VlUnpacked<IData/*31:0*/, 9>& __VdtypeVar) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root__trace_full_dtype____1\n"); );
    Vtb_s2a_backend_fault_recovery__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    uint32_t* const oldp VL_ATTR_UNUSED = bufp->oldp(vlSymsp->__Vm_baseCode + offset);
    bufp->fullIData(oldp+0,(__VdtypeVar[0]),32);
    bufp->fullIData(oldp+1,(__VdtypeVar[1]),32);
    bufp->fullIData(oldp+2,(__VdtypeVar[2]),32);
    bufp->fullIData(oldp+3,(__VdtypeVar[3]),32);
    bufp->fullIData(oldp+4,(__VdtypeVar[4]),32);
    bufp->fullIData(oldp+5,(__VdtypeVar[5]),32);
    bufp->fullIData(oldp+6,(__VdtypeVar[6]),32);
    bufp->fullIData(oldp+7,(__VdtypeVar[7]),32);
    bufp->fullIData(oldp+8,(__VdtypeVar[8]),32);
}

VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root__trace_full_dtype____2(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd::Buffer* bufp, uint32_t offset, const VlUnpacked<QData/*63:0*/, 9>& __VdtypeVar) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root__trace_full_dtype____2\n"); );
    Vtb_s2a_backend_fault_recovery__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    uint32_t* const oldp VL_ATTR_UNUSED = bufp->oldp(vlSymsp->__Vm_baseCode + offset);
    bufp->fullQData(oldp+0,(__VdtypeVar[0]),64);
    bufp->fullQData(oldp+2,(__VdtypeVar[1]),64);
    bufp->fullQData(oldp+4,(__VdtypeVar[2]),64);
    bufp->fullQData(oldp+6,(__VdtypeVar[3]),64);
    bufp->fullQData(oldp+8,(__VdtypeVar[4]),64);
    bufp->fullQData(oldp+10,(__VdtypeVar[5]),64);
    bufp->fullQData(oldp+12,(__VdtypeVar[6]),64);
    bufp->fullQData(oldp+14,(__VdtypeVar[7]),64);
    bufp->fullQData(oldp+16,(__VdtypeVar[8]),64);
}

VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root__trace_full_dtype____3(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd::Buffer* bufp, uint32_t offset, const VlUnpacked<QData/*63:0*/, 9>& __VdtypeVar) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root__trace_full_dtype____3\n"); );
    Vtb_s2a_backend_fault_recovery__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    uint32_t* const oldp VL_ATTR_UNUSED = bufp->oldp(vlSymsp->__Vm_baseCode + offset);
    bufp->fullQData(oldp+0,(__VdtypeVar[0]),64);
    bufp->fullQData(oldp+2,(__VdtypeVar[1]),64);
    bufp->fullQData(oldp+4,(__VdtypeVar[2]),64);
    bufp->fullQData(oldp+6,(__VdtypeVar[3]),64);
    bufp->fullQData(oldp+8,(__VdtypeVar[4]),64);
    bufp->fullQData(oldp+10,(__VdtypeVar[5]),64);
    bufp->fullQData(oldp+12,(__VdtypeVar[6]),64);
    bufp->fullQData(oldp+14,(__VdtypeVar[7]),64);
    bufp->fullQData(oldp+16,(__VdtypeVar[8]),64);
}

VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root__trace_full_dtype____4(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd::Buffer* bufp, uint32_t offset, const VlUnpacked<IData/*31:0*/, 8>& __VdtypeVar) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root__trace_full_dtype____4\n"); );
    Vtb_s2a_backend_fault_recovery__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    uint32_t* const oldp VL_ATTR_UNUSED = bufp->oldp(vlSymsp->__Vm_baseCode + offset);
    bufp->fullIData(oldp+0,(__VdtypeVar[0]),32);
    bufp->fullIData(oldp+1,(__VdtypeVar[1]),32);
    bufp->fullIData(oldp+2,(__VdtypeVar[2]),32);
    bufp->fullIData(oldp+3,(__VdtypeVar[3]),32);
    bufp->fullIData(oldp+4,(__VdtypeVar[4]),32);
    bufp->fullIData(oldp+5,(__VdtypeVar[5]),32);
    bufp->fullIData(oldp+6,(__VdtypeVar[6]),32);
    bufp->fullIData(oldp+7,(__VdtypeVar[7]),32);
}

VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root__trace_full_dtype____5(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd::Buffer* bufp, uint32_t offset, const VlUnpacked<VlWide<3>/*79:0*/, 8>& __VdtypeVar) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root__trace_full_dtype____5\n"); );
    Vtb_s2a_backend_fault_recovery__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    uint32_t* const oldp VL_ATTR_UNUSED = bufp->oldp(vlSymsp->__Vm_baseCode + offset);
    bufp->fullWData(oldp+0,(__VdtypeVar[0]),80);
    bufp->fullWData(oldp+3,(__VdtypeVar[1]),80);
    bufp->fullWData(oldp+6,(__VdtypeVar[2]),80);
    bufp->fullWData(oldp+9,(__VdtypeVar[3]),80);
    bufp->fullWData(oldp+12,(__VdtypeVar[4]),80);
    bufp->fullWData(oldp+15,(__VdtypeVar[5]),80);
    bufp->fullWData(oldp+18,(__VdtypeVar[6]),80);
    bufp->fullWData(oldp+21,(__VdtypeVar[7]),80);
}

VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root__trace_full_dtype____6(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd::Buffer* bufp, uint32_t offset, const VlUnpacked<IData/*31:0*/, 8>& __VdtypeVar) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root__trace_full_dtype____6\n"); );
    Vtb_s2a_backend_fault_recovery__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    uint32_t* const oldp VL_ATTR_UNUSED = bufp->oldp(vlSymsp->__Vm_baseCode + offset);
    bufp->fullIData(oldp+0,(__VdtypeVar[0]),32);
    bufp->fullIData(oldp+1,(__VdtypeVar[1]),32);
    bufp->fullIData(oldp+2,(__VdtypeVar[2]),32);
    bufp->fullIData(oldp+3,(__VdtypeVar[3]),32);
    bufp->fullIData(oldp+4,(__VdtypeVar[4]),32);
    bufp->fullIData(oldp+5,(__VdtypeVar[5]),32);
    bufp->fullIData(oldp+6,(__VdtypeVar[6]),32);
    bufp->fullIData(oldp+7,(__VdtypeVar[7]),32);
}

VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root__trace_full_dtype____7(Vtb_s2a_backend_fault_recovery___024root* vlSelf, VerilatedVcd::Buffer* bufp, uint32_t offset, const VlUnpacked<IData/*31:0*/, 4>& __VdtypeVar) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root__trace_full_dtype____7\n"); );
    Vtb_s2a_backend_fault_recovery__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    uint32_t* const oldp VL_ATTR_UNUSED = bufp->oldp(vlSymsp->__Vm_baseCode + offset);
    bufp->fullIData(oldp+0,(__VdtypeVar[0]),32);
    bufp->fullIData(oldp+1,(__VdtypeVar[1]),32);
    bufp->fullIData(oldp+2,(__VdtypeVar[2]),32);
    bufp->fullIData(oldp+3,(__VdtypeVar[3]),32);
}
