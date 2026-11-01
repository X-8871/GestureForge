// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vtb_s2a_network_backend_golden.h for the primary calling header

#include "Vtb_s2a_network_backend_golden__pch.h"

#ifdef VL_DEBUG
VL_ATTR_COLD void Vtb_s2a_network_backend_golden___024root___dump_triggers__stl(const VlUnpacked<QData/*63:0*/, 1> &triggers, const std::string &tag);
#endif  // VL_DEBUG
VL_ATTR_COLD bool Vtb_s2a_network_backend_golden___024root___trigger_anySet__stl(const VlUnpacked<QData/*63:0*/, 1> &in);
VL_ATTR_COLD void Vtb_s2a_network_backend_golden___024root___stl_sequent__TOP__0(Vtb_s2a_network_backend_golden___024root* vlSelf);

VL_ATTR_COLD bool Vtb_s2a_network_backend_golden___024root___eval_phase__stl(Vtb_s2a_network_backend_golden___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_network_backend_golden___024root___eval_phase__stl\n"); );
    Vtb_s2a_network_backend_golden__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    CData/*0:0*/ __VstlExecute;
    // Body
    {
        // Inlined CFunc: _eval_triggers_vec__stl
        vlSelfRef.__VstlTriggered[0U] = ((0xfffffffffffffffeULL 
                                          & vlSelfRef.__VstlTriggered[0U]) 
                                         | (IData)((IData)(vlSelfRef.__VstlFirstIteration)));
    }
#ifdef VL_DEBUG
    if (VL_UNLIKELY(vlSymsp->_vm_contextp__->debug())) {
        Vtb_s2a_network_backend_golden___024root___dump_triggers__stl(vlSelfRef.__VstlTriggered, "stl"s);
    }
#endif
    __VstlExecute = Vtb_s2a_network_backend_golden___024root___trigger_anySet__stl(vlSelfRef.__VstlTriggered);
    if (__VstlExecute) {
        {
            // Inlined CFunc: _eval_stl
            if ((1ULL & vlSelfRef.__VstlTriggered[0U])) {
                Vtb_s2a_network_backend_golden___024root___stl_sequent__TOP__0(vlSelf);
            }
        }
    }
    return (__VstlExecute);
}

bool Vtb_s2a_network_backend_golden___024root___trigger_anySet__act(const VlUnpacked<QData/*63:0*/, 1> &in);

#ifdef VL_DEBUG
VL_ATTR_COLD void Vtb_s2a_network_backend_golden___024root___dump_triggers__act(const VlUnpacked<QData/*63:0*/, 1> &triggers, const std::string &tag) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_network_backend_golden___024root___dump_triggers__act\n"); );
    // Body
    if ((1U & (~ (IData)(Vtb_s2a_network_backend_golden___024root___trigger_anySet__act(triggers))))) {
        VL_DBG_MSGS("         No '" + tag + "' region triggers active\n");
    }
    if ((1U & (IData)(triggers[0U]))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 0 is active: @(posedge tb_s2a_network_backend_golden.clk)\n");
    }
    if ((1U & (IData)((triggers[0U] >> 1U)))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 1 is active: @(negedge tb_s2a_network_backend_golden.clk)\n");
    }
    if ((1U & (IData)((triggers[0U] >> 2U)))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 2 is active: @([true] __VdlySched.awaitingCurrentTime())\n");
    }
}
#endif  // VL_DEBUG

VL_ATTR_COLD void Vtb_s2a_network_backend_golden___024root___ctor_var_reset(Vtb_s2a_network_backend_golden___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_network_backend_golden___024root___ctor_var_reset\n"); );
    Vtb_s2a_network_backend_golden__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    const uint64_t __VscopeHash = VL_MURMUR64_HASH(vlSelf->vlNamep);
    vlSelf->tb_s2a_network_backend_golden__DOT__mem_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 16100198414199411505ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__mem_write = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 6060134145391135197ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__mem_addr = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16029929573564882918ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__mem_wdata = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5962384585297802984ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__mem_rstrb = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 8527913995776095472ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__mem_wstrb = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 11171712500590747815ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__mem_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 16563846886932375195ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__mem_error_code = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 12878808059683324775ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__backend_memory_error_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 2037680343439438567ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__operator_result_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 16635222668099193927ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__operator_error_code = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 10201403422971403072ull);
    for (int __Vi0 = 0; __Vi0 < 519168; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__input_bytes[__Vi0] = 0;
    }
    for (int __Vi0 = 0; __Vi0 < 5903100; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__weight_bytes[__Vi0] = 0;
    }
    for (int __Vi0 = 0; __Vi0 < 11382200; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__feature_bytes[__Vi0] = 0;
    }
    for (int __Vi0 = 0; __Vi0 < 11382200; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__feature_byte_valid[__Vi0] = 0;
    }
    for (int __Vi0 = 0; __Vi0 < 11382150; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__expected_bytes[__Vi0] = 0;
    }
    for (int __Vi0 = 0; __Vi0 < 11382150; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__golden_byte_seen[__Vi0] = 0;
    }
    for (int __Vi0 = 0; __Vi0 < 38; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__golden_offset[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13911160734636342069ull);
    }
    for (int __Vi0 = 0; __Vi0 < 38; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__layer_write_count[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9726416475376545262ull);
    }
    for (int __Vi0 = 0; __Vi0 < 4; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__class_transfer_index[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 18340525652362302265ull);
    }
    for (int __Vi0 = 0; __Vi0 < 4; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__class_accepted_count[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15783076053982401452ull);
    }
    for (int __Vi0 = 0; __Vi0 < 4; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__class_selected_byte_count[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6858452777197071273ull);
    }
    vlSelf->tb_s2a_network_backend_golden__DOT__seq_owner = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9716120092829110394ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__seq_lane_owner = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2892132426058136527ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__seq_tensor_owner = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1432493383051430856ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__seq_transfer_class = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3477927022936153516ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__seq_golden_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8085887563466377429ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__verify_golden_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6516981951979910298ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__seq_feature_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 350559394991436580ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__input_bytes_this_transfer = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13908228073133168689ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__weight_bytes_this_transfer = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16952875417178419670ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__feature_bytes_this_transfer = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7418497957104589291ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__active_byte_count = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14860157155531172163ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__seq_lane_address = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10493551382415953498ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__state = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 2492193751728825027ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__layer_cursor = VL_SCOPED_RAND_RESET_I(6, __VscopeHash, 17420666702124239898ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_element_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12096703921370241124ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__response_pending = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 1991455680971125495ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__response_data_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9497935804535901287ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__response_error_latched = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 5347441095233030452ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__response_target_latched = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 17504115061574583495ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__current_op = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 1591820691374530562ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__current_input_count = VL_SCOPED_RAND_RESET_I(2, __VscopeHash, 4863867026171007089ull);
    for (int __Vi0 = 0; __Vi0 < 2; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_base[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11583133688056706677ull);
    }
    for (int __Vi0 = 0; __Vi0 < 2; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_length[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17310377544734334926ull);
    }
    for (int __Vi0 = 0; __Vi0 < 2; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_n[__Vi0] = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 4061181006501278662ull);
    }
    for (int __Vi0 = 0; __Vi0 < 2; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_c[__Vi0] = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 17119256223616776852ull);
    }
    for (int __Vi0 = 0; __Vi0 < 2; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_h[__Vi0] = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 2197192170791944193ull);
    }
    for (int __Vi0 = 0; __Vi0 < 2; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_w[__Vi0] = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 2737246143691316772ull);
    }
    for (int __Vi0 = 0; __Vi0 < 2; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_route_start[__Vi0] = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 16582630554902601414ull);
    }
    for (int __Vi0 = 0; __Vi0 < 2; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__source_route_end[__Vi0] = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 10956509261504322330ull);
    }
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_base = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 18254028070609691537ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_length = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4345845828091207697ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_n = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 13583765199652611028ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_c = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 7850388407913146998ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_h = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 4580269939905128119ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_w = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 1640106556434191314ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__output_element_count = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 13631403628916271676ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_channel = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9702308038307349880ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16724763010875344379ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__decoded_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15985174848948839361ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__alias_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 6072798412044919672ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__descriptor_fault = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 7097293191361464144ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__is_alias_row = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 18404459764623195580ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__alias_output_plane_elements = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 9813448087869424865ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__alias_output_element_count = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 18185388332617621647ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__conv_start_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 13231756471655936357ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__conv_start_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 4139463117361222169ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__maxpool_start_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 15071636668945572278ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__maxpool_start_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 4964172398404816026ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__route_start_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 3979571493063525574ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__route_start_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 13426582368030634005ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__upsample_start_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 4980207224640018163ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__upsample_start_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 13734317633714565355ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__conv_req_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 10604350682805699145ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__conv_req_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 7517994611627325824ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__maxpool_req_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 7277058378475747366ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__maxpool_req_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 18116798807422360825ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__route_req_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 10220641947343473131ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__route_req_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 12066841422901605071ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__upsample_req_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 1959745044612670603ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__upsample_req_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 8524116269610869678ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__conv_rsp_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 15467357143000797252ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__maxpool_rsp_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 17422248750690608842ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__route_rsp_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 313788663838042538ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__upsample_rsp_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 2242192424970303678ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__conv_result_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 10923047928912799696ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__maxpool_result_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 8731860478692925408ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__route_result_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 7634376353104578359ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__upsample_result_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 17882247220484225577ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__selected_result_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 2846070594720318276ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__selected_result_error = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 12769091853700423681ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__memory_handshake = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 47440525016962293ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__selected_start_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 15404692880337326379ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_conv_engine__activation_mode = 0;
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__darknet_padding_parameter = 0;
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_x = 0;
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_y = 0;
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width = 0;
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_height = 0;
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__layer_index = 0;
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT____Vcellinp__u_upsample_engine__stride = 0;
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__state = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 15711450754013964364ull);
    for (int __Vi0 = 0; __Vi0 < 4; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16480287378563875258ull);
    }
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_address_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15669110682939342810ull);
    VL_SCOPED_RAND_RESET_W(72, vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__candidate_values_latched, __VscopeHash, 10682540766135488902ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__read_tap_index = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 9565862273580026186ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__result_value_latched = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 8130862385066934453ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__result_error_latched = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 13028704436324204074ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_output_height = VL_SCOPED_RAND_RESET_Q(33, __VscopeHash, 6207937959582245916ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_output_width = VL_SCOPED_RAND_RESET_Q(33, __VscopeHash, 11803085728363717969ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_count = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 937406210897688303ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask = VL_SCOPED_RAND_RESET_I(9, __VscopeHash, 1017201663009446187ull);
    for (int __Vi0 = 0; __Vi0 < 9; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17385810500789780455ull);
    }
    for (int __Vi0 = 0; __Vi0 < 9; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[__Vi0] = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 8413087352107830726ull);
    }
    for (int __Vi0 = 0; __Vi0 < 9; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[__Vi0] = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 15822575308521172987ull);
    }
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_error_code = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 6873419061442842124ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_offset_work = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 7260769200988525191ull);
    VL_SCOPED_RAND_RESET_W(65, vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_address_work, __VscopeHash, 1385617825726183136ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__mapped_response_error = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 6114712815747579331ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__window_max_value = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 12221924636031550449ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_maxpool_engine__DOT__window_error_code = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 14841632341367197857ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__state = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 15278691175163198796ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__source_address_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14982792451914373759ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__output_address_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13169231948368907130ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__copied_value_latched = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 2754046961278013421ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__result_error_latched = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 12100594204200887699ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_channel = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10949850590258829802ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_address = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2156026763584506499ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__query_error_code = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 18138159687542809716ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__output_offset_work = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 12152982438550622826ull);
    VL_SCOPED_RAND_RESET_W(65, vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__output_address_work, __VscopeHash, 13977157297585003532ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_upsample_engine__DOT__mapped_response_error = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 15921142441585566205ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__state = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 10960733162566130458ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source_count_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3704626770822146483ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__groups_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11436960485483156170ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__group_id_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8645638888517794064ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_channel_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3756170359873865987ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_y_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13710668988592392195ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_x_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13014093185492558516ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_base_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9284350128772370679ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_length_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5227834261568788618ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_channels_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16371815011618711359ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_height_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11860468815881262070ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_width_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12193256959509197007ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_start_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9044282031618656733ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_end_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17869257475247520727ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_multiplier_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5369193014760278531ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source0_value_latched = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 1161354193894751313ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source1_base_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 18044806300045043657ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source1_length_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11061458939987428281ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source1_channels_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11184647453932152764ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source1_height_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13655996196554057746ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source1_width_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4177788514463799895ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source1_start_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7818659560466194741ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source1_end_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7669372535539626944ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source1_multiplier_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10895154635841802626ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source1_value_latched = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 4536625694533601681ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_base_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 18002122548107686793ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_length_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15526298147540000736ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_channels_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3602948644557889390ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_height_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14237965026397981453ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_width_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2409676593217158519ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source_index_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9299694979576740105ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__source_address_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 326725007391245305ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_address_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17972889933358287204ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__result_value_latched = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 1759100202155574907ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__result_error_latched = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 4286612736245719892ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__query_output_channels = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15394276623840365904ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__query_output_height = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12344051783052965693ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__query_output_width = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1411335286936844141ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__query_source_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6493057979531734097ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__query_source_address = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1012405736171004717ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__query_output_value = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 12913208674636401710ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__query_error_code = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 8708921188372310410ull);
    VL_SCOPED_RAND_RESET_W(65, vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__output_offset_work, __VscopeHash, 12595054863746896465ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__selected_byte_shift = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10627133812051168302ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_route_engine__DOT__mapped_response_error = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 16438688589215447139ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__state = VL_SCOPED_RAND_RESET_I(5, __VscopeHash, 14889565692329679276ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 384519945138116481ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_layer_index_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14657049037673641881ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_base_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10704069281828787240ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_length_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13780506050271528370ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_batch_count_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13165090760765627938ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_channels_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5114964483136933419ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_height_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17445182560078606275ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__input_width_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2649588431379203834ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_base_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14339810591499655225ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_length_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4437938483133683215ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_batch_count_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8261035290592733372ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_channels_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7714954163296474013ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1157356448097519670ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17173616447100372093ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_height_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9539721255718126180ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_width_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8307257829921206713ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__stride_y_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13630915682945312257ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__stride_x_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14978269015641538940ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__pad_left_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13402125134773734845ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__pad_right_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13525185344565348426ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__pad_top_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10503596982968943019ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__pad_bottom_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4643837325142558876ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__groups_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2346013889220210976ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__padding_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13254191643024330176ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_package_base_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10912111345912827242ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_package_length_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11518254366475057864ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__quantized_weight_offset_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6676982226102893582ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__quantized_weight_bytes_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8923522241876325424ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_batch_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5730472103591234735ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__activation_mode_latched = VL_SCOPED_RAND_RESET_I(2, __VscopeHash, 3145541650314554696ull);
    for (int __Vi0 = 0; __Vi0 < 51200; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_patch[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 11772419232826911430ull);
    }
    for (int __Vi0 = 0; __Vi0 < 36864; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_group[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 6847691878818360051ull);
    }
    for (int __Vi0 = 0; __Vi0 < 512; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_block[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 3783417804081936696ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10851504567823666468ull);
    }
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13785158159033326904ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11155634649802818365ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9230575091863492786ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 18335499671991303439ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_height = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9485981058852616498ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_width = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12248323764194740139ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__patch_height = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 620832222126860659ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__patch_width = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9195955769567491479ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__patch_byte_count = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17362209645211617757ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__tile_point_count = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9079551801147448462ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16630439370798564457ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7036940250762448533ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_lane_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2368253565793786435ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_reduction_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6957996991670076667ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 964498301884896963ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_reduction_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11757898023172129907ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_lane_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6360553972122796673ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_point_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17270592992530230010ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__request_address_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4446836773863578973ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__request_strobe_latched = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 16739636532576847380ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__request_wdata_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10586576825949133186ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__result_error_latched = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 10472253414111345643ull);
    VL_SCOPED_RAND_RESET_W(128, vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_elements_wide, __VscopeHash, 995237875522032997ull);
    VL_SCOPED_RAND_RESET_W(128, vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_wide, __VscopeHash, 15738579736219483832ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__validation_ok = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 14136151798595773670ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__validation_error = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 5016123832773439380ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_group_invalid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 10270556922623776988ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_in_bounds = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 16681306662221878741ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__feature_source_address_wide = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 15595760530934477248ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__weight_source_address_wide = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 15358913247823562188ull);
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 12908737793722345181ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 6014493900350247089ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[__Vi0] = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 9469685211791069632ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[__Vi0] = VL_SCOPED_RAND_RESET_Q(33, __VscopeHash, 10096495855394012867ull);
    }
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_bad_argument = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 1066713769358585484ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__compute_overflow = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 12721438541776263274ull);
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 18196685319393619926ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16016526092383267102ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6251036652106372227ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9183787350791211368ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product[__Vi0] = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 9977116478130123765ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add[__Vi0] = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 14163031444604499576ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[__Vi0] = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 3565767423629663571ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[__Vi0] = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 9668949254776504474ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__requantized_value[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 15707716089727146040ull);
    }
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_byte_offset_wide = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 2631951127939833172ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__output_address_wide = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 14134493819334236850ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__mapped_response_error = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 2619824505446794685ull);
    vlSelf->tb_s2a_network_backend_golden__DOT__u_backend__DOT__u_conv_engine__DOT__request_byte_lane = VL_SCOPED_RAND_RESET_I(2, __VscopeHash, 14192600385340166417ull);
    vlSelf->__Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__map_conv_activation__21__descriptor_activation = 0;
    vlSelf->__Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__normalize_engine_error__22__code = 0;
    vlSelf->__Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__normalize_engine_error__23__Vfuncout = 0;
    vlSelf->__Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__normalize_engine_error__23__code = 0;
    vlSelf->__Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__normalize_engine_error__24__code = 0;
    vlSelf->__Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__normalize_engine_error__25__Vfuncout = 0;
    vlSelf->__Vfunc_tb_s2a_network_backend_golden__DOT__u_backend__DOT__normalize_engine_error__25__code = 0;
    vlSelf->__VdfgRegularize_h6e95ff9d_0_6 = 0;
    vlSelf->__VdfgRegularize_h6e95ff9d_0_10 = 0;
    vlSelf->__VdfgRegularize_h6e95ff9d_0_11 = 0;
    vlSelf->__VdfgRegularize_h6e95ff9d_0_16 = 0;
    vlSelf->__VdfgRegularize_h6e95ff9d_0_17 = 0;
    vlSelf->__VdfgRegularize_h6e95ff9d_0_27 = 0;
    vlSelf->__VdfgRegularize_h6e95ff9d_0_187 = 0;
    vlSelf->__VdfgRegularize_h6e95ff9d_0_188 = 0;
    vlSelf->__VdfgRegularize_h6e95ff9d_0_189 = 0;
    VL_ZERO_RESET_W(65, vlSelf->__VdfgRegularize_h6e95ff9d_0_197);
    VL_ZERO_RESET_W(65, vlSelf->__VdfgRegularize_h6e95ff9d_0_198);
    for (int __Vi0 = 0; __Vi0 < 1; ++__Vi0) {
        vlSelf->__VstlTriggered[__Vi0] = 0;
    }
    for (int __Vi0 = 0; __Vi0 < 1; ++__Vi0) {
        vlSelf->__VactTriggered[__Vi0] = 0;
    }
    for (int __Vi0 = 0; __Vi0 < 1; ++__Vi0) {
        vlSelf->__VactTriggeredAcc[__Vi0] = 0;
    }
    vlSelf->__Vtrigprevexpr___TOP__tb_s2a_network_backend_golden__DOT__clk__0 = 0;
    for (int __Vi0 = 0; __Vi0 < 1; ++__Vi0) {
        vlSelf->__VnbaTriggered[__Vi0] = 0;
    }
    vlSelf->__Vi = 0;
}
