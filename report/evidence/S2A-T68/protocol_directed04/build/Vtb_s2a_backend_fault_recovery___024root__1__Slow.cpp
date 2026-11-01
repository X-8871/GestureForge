// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vtb_s2a_backend_fault_recovery.h for the primary calling header

#include "Vtb_s2a_backend_fault_recovery__pch.h"

#ifdef VL_DEBUG
VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root___dump_triggers__stl(const VlUnpacked<QData/*63:0*/, 1> &triggers, const std::string &tag);
#endif  // VL_DEBUG
VL_ATTR_COLD bool Vtb_s2a_backend_fault_recovery___024root___trigger_anySet__stl(const VlUnpacked<QData/*63:0*/, 1> &in);
VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root___stl_sequent__TOP__0(Vtb_s2a_backend_fault_recovery___024root* vlSelf);

VL_ATTR_COLD bool Vtb_s2a_backend_fault_recovery___024root___eval_phase__stl(Vtb_s2a_backend_fault_recovery___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root___eval_phase__stl\n"); );
    Vtb_s2a_backend_fault_recovery__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
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
        Vtb_s2a_backend_fault_recovery___024root___dump_triggers__stl(vlSelfRef.__VstlTriggered, "stl"s);
    }
#endif
    __VstlExecute = Vtb_s2a_backend_fault_recovery___024root___trigger_anySet__stl(vlSelfRef.__VstlTriggered);
    if (__VstlExecute) {
        {
            // Inlined CFunc: _eval_stl
            if ((1ULL & vlSelfRef.__VstlTriggered[0U])) {
                Vtb_s2a_backend_fault_recovery___024root___stl_sequent__TOP__0(vlSelf);
            }
        }
    }
    return (__VstlExecute);
}

bool Vtb_s2a_backend_fault_recovery___024root___trigger_anySet__act(const VlUnpacked<QData/*63:0*/, 1> &in);

#ifdef VL_DEBUG
VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root___dump_triggers__act(const VlUnpacked<QData/*63:0*/, 1> &triggers, const std::string &tag) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root___dump_triggers__act\n"); );
    // Body
    if ((1U & (~ (IData)(Vtb_s2a_backend_fault_recovery___024root___trigger_anySet__act(triggers))))) {
        VL_DBG_MSGS("         No '" + tag + "' region triggers active\n");
    }
    if ((1U & (IData)(triggers[0U]))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 0 is active: @(posedge tb_s2a_backend_fault_recovery.clk)\n");
    }
    if ((1U & (IData)((triggers[0U] >> 1U)))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 1 is active: @([true] __VdlySched.awaitingCurrentTime())\n");
    }
    if ((1U & (IData)((triggers[0U] >> 2U)))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 2 is active: @(negedge tb_s2a_backend_fault_recovery.clk)\n");
    }
}
#endif  // VL_DEBUG

VL_ATTR_COLD void Vtb_s2a_backend_fault_recovery___024root___ctor_var_reset(Vtb_s2a_backend_fault_recovery___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_backend_fault_recovery___024root___ctor_var_reset\n"); );
    Vtb_s2a_backend_fault_recovery__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    const uint64_t __VscopeHash = VL_MURMUR64_HASH(vlSelf->vlNamep);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__csr_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 6079102690976410759ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__csr_rdata = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2230028280195105455ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__backend_memory_error_code = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 414584405539759482ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__operator_result_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 945301752331004765ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__operator_error_code = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 11692968540694261182ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__backend_start = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 3176038329200163404ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__backend_abort = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 5129139845124539287ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__busy = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 5563873840561047714ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__done = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 8606140970590962076ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__error = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 14407988617970081033ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__buffer_owner_pl = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 9675798143390124455ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__head_output_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 562491892733068062ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__mem_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 12866850128145328242ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__mem_write = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 5299012362422842519ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__mem_addr = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7974895254378462070ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__mem_wdata = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2331095788742164053ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__mem_rstrb = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 15476515364004764961ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__mem_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 16993649080506353406ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__state = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 6929541213646511396ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__layer_cursor = VL_SCOPED_RAND_RESET_I(6, __VscopeHash, 12418690731688588229ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_element_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10378220872242979612ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_pending = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 4356114394098153102ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_data_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14138369589800938252ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_error_latched = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 15023162897935931225ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__response_target_latched = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 6103600619472446435ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_op = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 1981781129754157272ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__current_input_count = VL_SCOPED_RAND_RESET_I(2, __VscopeHash, 15971875220833428969ull);
    for (int __Vi0 = 0; __Vi0 < 2; ++__Vi0) {
        vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_base[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10696046464258251441ull);
    }
    for (int __Vi0 = 0; __Vi0 < 2; ++__Vi0) {
        vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_length[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12673035177295869388ull);
    }
    for (int __Vi0 = 0; __Vi0 < 2; ++__Vi0) {
        vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_n[__Vi0] = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 4923501871272053294ull);
    }
    for (int __Vi0 = 0; __Vi0 < 2; ++__Vi0) {
        vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_c[__Vi0] = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 13630791466133379585ull);
    }
    for (int __Vi0 = 0; __Vi0 < 2; ++__Vi0) {
        vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_h[__Vi0] = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 1672217636180682817ull);
    }
    for (int __Vi0 = 0; __Vi0 < 2; ++__Vi0) {
        vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_w[__Vi0] = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 15383825631150592266ull);
    }
    for (int __Vi0 = 0; __Vi0 < 2; ++__Vi0) {
        vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_route_start[__Vi0] = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 16619958615751354390ull);
    }
    for (int __Vi0 = 0; __Vi0 < 2; ++__Vi0) {
        vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__source_route_end[__Vi0] = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 2561033619220680738ull);
    }
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_base = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14275611418570326880ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_length = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4143518257627048993ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_n = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 3016623861465507936ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_c = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 3369245796181925565ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_h = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 4925708171328460836ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_w = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 8083731816234480446ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__output_element_count = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 6447386311533511642ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_channel = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15633667865251584457ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9038848498597286723ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__decoded_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11749145933923542803ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 9596929237935897034ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__descriptor_fault = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 2237009001221084107ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__is_alias_row = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 16223479264518327644ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_output_plane_elements = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 4022509322805309150ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__alias_output_element_count = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 10410837099994675535ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_start_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 13691589597108600580ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_start_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 6338255101228482002ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_start_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 4729156392934882375ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_start_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 8468525990457774969ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_start_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 14021783555692816506ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_start_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 9546767633446028921ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_start_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 14083663309048253921ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_start_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 15769036706338397400ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 17546916403564528868ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 13162485707116482358ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_req_wstrb = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 16028384677110952104ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 2417352509182736376ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 8353496093033843844ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_req_wstrb = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 3491664911602724203ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 7845180572915227611ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 13400943974253134936ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_req_wstrb = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 8165321221120739988ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 2414866530499944642ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 12904967458893072497ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_req_wstrb = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 778924265436819751ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_rsp_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 1213442173067329936ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_rsp_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 14435873694575289129ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_rsp_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 1602447872241310985ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_rsp_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 12283825113903629444ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__conv_result_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 11649694341788494725ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__maxpool_result_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 17802039736266141893ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__route_result_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 8851694030884754459ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__upsample_result_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 201945397717327525ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_result_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 13785796770772881809ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_result_error = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 6956813425943538871ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__memory_handshake = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 12178129985400374577ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__selected_start_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 5441119171621358311ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_conv_engine__activation_mode = 0;
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__darknet_padding_parameter = 0;
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_x = 0;
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__stride_y = 0;
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_width = 0;
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__kernel_height = 0;
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_maxpool_engine__layer_index = 0;
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT____Vcellinp__u_upsample_engine__stride = 0;
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__state = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 13115790640413570203ull);
    for (int __Vi0 = 0; __Vi0 < 4; ++__Vi0) {
        vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__tap_address_latched[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7801955469578730284ull);
    }
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_address_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11151010087943728505ull);
    VL_SCOPED_RAND_RESET_W(72, vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__candidate_values_latched, __VscopeHash, 12313952252701148165ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__read_tap_index = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 9625282956027806075ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__result_value_latched = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 10521153066427210509ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__result_error_latched = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 15650625117333511582ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_output_height = VL_SCOPED_RAND_RESET_Q(33, __VscopeHash, 5667002660268219511ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_output_width = VL_SCOPED_RAND_RESET_Q(33, __VscopeHash, 2182627544194941689ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_count = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 8022844966401148225ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_valid_mask = VL_SCOPED_RAND_RESET_I(9, __VscopeHash, 3724992013019081744ull);
    for (int __Vi0 = 0; __Vi0 < 9; ++__Vi0) {
        vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_address[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 18325677709624945951ull);
    }
    for (int __Vi0 = 0; __Vi0 < 9; ++__Vi0) {
        vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_y[__Vi0] = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 10305747072396994317ull);
    }
    for (int __Vi0 = 0; __Vi0 < 9; ++__Vi0) {
        vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_tap_source_x[__Vi0] = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 11143565144736999697ull);
    }
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__query_error_code = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 8048591759146387801ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_offset_work = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 10684861224319008408ull);
    VL_SCOPED_RAND_RESET_W(65, vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__output_address_work, __VscopeHash, 6669720684231783280ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__mapped_response_error = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 3038561374591799638ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__window_max_value = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 8274095621443865467ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_maxpool_engine__DOT__window_error_code = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 17330782757134174916ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__state = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 12038888723445510804ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__source_address_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11535087384426194548ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__output_address_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 326721141324426389ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__copied_value_latched = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 5471283637228498800ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__result_error_latched = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 11312752144179156915ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_channel = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8124137385137151137ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_source_address = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16141636474347255091ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__query_error_code = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 830546156805003797ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__output_offset_work = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 3204216941745257449ull);
    VL_SCOPED_RAND_RESET_W(65, vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__output_address_work, __VscopeHash, 1751747260189672393ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_upsample_engine__DOT__mapped_response_error = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 5019139513263156798ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__state = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 11502423998283252458ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source_count_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12088994028110889415ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__groups_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10489492761043815716ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__group_id_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 184435147325561288ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_channel_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2610451251694508829ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_y_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2136713420863662384ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_x_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 738549836135471985ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_base_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9112448627660879561ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_length_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10439367193547369852ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_channels_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6535491529777826791ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_height_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6383949133660479114ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_width_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5012081448965003162ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_start_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14769539559056589757ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_end_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7696201985022320684ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_multiplier_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15150892937301136425ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source0_value_latched = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 6081678529120526995ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_base_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11321341822202873725ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_length_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12253112312592632559ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_channels_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 178871508982804200ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_height_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5105188643348462328ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_width_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16557932581924083859ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_start_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10584717358071597322ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_end_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16748044317841666980ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_multiplier_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12867464382022620876ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source1_value_latched = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 5623884266719232729ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_base_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6386219214516895105ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_length_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14532252727706298200ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_channels_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1339076347038924126ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_height_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17680336879063518110ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_width_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16683209903912950741ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source_index_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14253174189035202819ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__source_address_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3844078733420539382ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_address_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17447058482326622637ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__result_value_latched = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 1939738683718081062ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__result_error_latched = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 16345653072213600869ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__query_output_channels = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9184722388531561348ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__query_output_height = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16283377761467222765ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__query_output_width = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4460189787820106366ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__query_source_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8300398609504358009ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__query_source_address = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2647567147588758129ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__query_output_value = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 14977553970749073742ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__query_error_code = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 12309589415169080925ull);
    VL_SCOPED_RAND_RESET_W(65, vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__output_offset_work, __VscopeHash, 10227743364023054839ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__selected_byte_shift = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11427235559410555306ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_route_engine__DOT__mapped_response_error = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 17724640715689511241ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__state = VL_SCOPED_RAND_RESET_I(5, __VscopeHash, 6045273827333709454ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__layer_index_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10710862418520573034ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_layer_index_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7804548011249005317ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_base_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3729841278890536507ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_length_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8087958227841842922ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_batch_count_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5698215607795227318ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_channels_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4303228225416654894ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_height_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3182999040033676915ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__input_width_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1364089744629901922ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_base_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 460470484376674193ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_length_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4256390464913069923ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_batch_count_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9102611098304434658ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_channels_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9600864409922580558ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_height_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7399795626350160795ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_width_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10690868517460968911ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_height_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6289858295390080520ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__kernel_width_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11486644189270219655ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__stride_y_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16059664352288041589ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__stride_x_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3936025955765271879ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__pad_left_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17150088776376753183ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__pad_right_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16980402492456717383ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__pad_top_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4186244002447104205ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__pad_bottom_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 18082921573122683925ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__groups_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16166602547936948068ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__padding_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14014644956271760496ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_package_base_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13134314035020726858ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_package_length_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16089286589238663446ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__quantized_weight_offset_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15977565726654044479ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__quantized_weight_bytes_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10070866215644509781ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_batch_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13693814833093828168ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__activation_mode_latched = VL_SCOPED_RAND_RESET_I(2, __VscopeHash, 1552762952022931020ull);
    for (int __Vi0 = 0; __Vi0 < 51200; ++__Vi0) {
        vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_patch[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 17759649128178728815ull);
    }
    for (int __Vi0 = 0; __Vi0 < 36864; ++__Vi0) {
        vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_group[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 8931746362077184592ull);
    }
    for (int __Vi0 = 0; __Vi0 < 512; ++__Vi0) {
        vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_block[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 9010112618248158986ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__lane_accumulator[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4159904438363913609ull);
    }
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 18024520153527792905ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_group_base = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9043828821255074993ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10660098177796130933ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__tile_start_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16607237042188288724ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__tile_height = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2859376472233374402ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__tile_width = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9754202870993912666ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__patch_height = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12606393018359569389ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__patch_width = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11965726922579589688ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__patch_byte_count = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10499486433981415110ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__tile_point_count = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1170483913705570669ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__group_lane_count = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10058283270326938288ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7835691423883358168ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_lane_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16272183445686512452ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_reduction_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9930467377462192742ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_point_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9416795547069621590ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_reduction_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12384930003847776636ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_lane_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4717224215512095418ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_point_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3315685404964734153ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__request_address_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16627557811352493629ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__request_strobe_latched = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 3170732645635428005ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__request_wdata_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 684137598389709551ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__result_error_latched = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 1805219112949716692ull);
    VL_SCOPED_RAND_RESET_W(128, vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_elements_wide, __VscopeHash, 13528814100271775422ull);
    VL_SCOPED_RAND_RESET_W(128, vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__reduction_count_wide, __VscopeHash, 3058266481963643912ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__validation_ok = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 13204378780573683817ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__validation_error = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 12639190687866931540ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_group_invalid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 18318637912334694727ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_scan_in_bounds = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 1286710422885463140ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__feature_source_address_wide = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 17834424136553329997ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__weight_source_address_wide = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 851888967882421469ull);
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_feature_byte[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 14234039650130488760ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_weight_byte[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 16146704684016613493ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_product[__Vi0] = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 15733043348677942883ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_sum[__Vi0] = VL_SCOPED_RAND_RESET_Q(33, __VscopeHash, 10294298098376951935ull);
    }
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_bad_argument = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 51965741926993924ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__compute_overflow = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 4577499459605275732ull);
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mq_index_for_lane[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4786012976145112529ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_multiplier[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 259835599266314623ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_q_shift[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13462778465518428378ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_magnitude[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4978732638861720750ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_product[__Vi0] = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 13296344249829596689ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounding_add[__Vi0] = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 8499826287158832910ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_rounded_magnitude[__Vi0] = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 553363734801488661ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requant_signed_value[__Vi0] = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 2830038925576266115ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__requantized_value[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 4465912919325729159ull);
    }
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_byte_offset_wide = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 17719212861652574233ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__output_address_wide = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 6472993812494644231ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__mapped_response_error = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 16779742067079052356ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__u_conv_engine__DOT__request_byte_lane = VL_SCOPED_RAND_RESET_I(2, __VscopeHash, 5433151678748007642ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__error_code = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 2264950914891105351ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__frame_id = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12206741371267893170ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__active_frame_id = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12147466300530455537ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__input_addr = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2798664554832168717ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__input_bytes = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13030910272193799615ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__weight_addr = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1620688082659107546ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__weight_bytes = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3431200877656295937ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__timeout_cycles = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14168203505315556096ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__elapsed_cycles = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5318243418692743940ull);
    vlSelf->tb_s2a_backend_fault_recovery__DOT__u_csr__DOT__config_idle = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 5988385107242915811ull);
    vlSelf->__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__map_conv_activation__96__descriptor_activation = 0;
    vlSelf->__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__97__code = 0;
    vlSelf->__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__98__Vfuncout = 0;
    vlSelf->__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__98__code = 0;
    vlSelf->__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__99__code = 0;
    vlSelf->__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__100__Vfuncout = 0;
    vlSelf->__Vfunc_tb_s2a_backend_fault_recovery__DOT__u_backend__DOT__normalize_engine_error__100__code = 0;
    VL_ZERO_RESET_W(65, vlSelf->__VdfgRegularize_h6e95ff9d_0_7);
    VL_ZERO_RESET_W(65, vlSelf->__VdfgRegularize_h6e95ff9d_0_8);
    for (int __Vi0 = 0; __Vi0 < 1; ++__Vi0) {
        vlSelf->__VstlTriggered[__Vi0] = 0;
    }
    for (int __Vi0 = 0; __Vi0 < 1; ++__Vi0) {
        vlSelf->__VactTriggered[__Vi0] = 0;
    }
    for (int __Vi0 = 0; __Vi0 < 1; ++__Vi0) {
        vlSelf->__VactTriggeredAcc[__Vi0] = 0;
    }
    vlSelf->__Vtrigprevexpr___TOP__tb_s2a_backend_fault_recovery__DOT__clk__0 = 0;
    for (int __Vi0 = 0; __Vi0 < 1; ++__Vi0) {
        vlSelf->__VnbaTriggered[__Vi0] = 0;
    }
    vlSelf->__Vi = 0;
}
