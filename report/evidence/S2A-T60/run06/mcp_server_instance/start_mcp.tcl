# 本脚本只启动独立 T60 MCP 服务并保持 Tcl 事件循环，不创建或打开工程。
source {C:/Users/22061/.vivado-mcp/tcl/vivado_server.tcl}
if {![info exists ::vmcp::core::started] || !$::vmcp::core::started} {
    error "T60_RUN06_MCP_SERVER_START_FAILED"
}
vwait ::vmcp::core::started