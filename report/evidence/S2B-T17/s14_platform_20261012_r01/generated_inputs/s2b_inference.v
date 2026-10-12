//Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
//Copyright 2022-2026 Advanced Micro Devices, Inc. All Rights Reserved.
//--------------------------------------------------------------------------------
//Tool Version: Vivado v.2026.1 (win64) Build 6511674 Tue Jun 16 11:02:23 MDT 2026
//Date        : Mon Oct 12 12:00:44 2026
//Host        : HAO running 64-bit major release  (build 9200)
//Command     : generate_target s2b_inference.bd
//Design      : s2b_inference
//Purpose     : IP block netlist
//--------------------------------------------------------------------------------
`timescale 1 ps / 1 ps

(* CORE_GENERATION_INFO = "s2b_inference,IP_Integrator,{x_ipVendor=xilinx.com,x_ipLibrary=BlockDiagram,x_ipName=s2b_inference,x_ipVersion=1.00.a,x_ipLanguage=VERILOG}" *) (* HW_HANDOFF = "s2b_inference.hwdef" *) 
module s2b_inference
   (DDR_addr,
    DDR_ba,
    DDR_cas_n,
    DDR_ck_n,
    DDR_ck_p,
    DDR_cke,
    DDR_cs_n,
    DDR_dm,
    DDR_dq,
    DDR_dqs_n,
    DDR_dqs_p,
    DDR_odt,
    DDR_ras_n,
    DDR_reset_n,
    DDR_we_n,
    FIXED_IO_ddr_vrn,
    FIXED_IO_ddr_vrp,
    FIXED_IO_mio,
    FIXED_IO_ps_clk,
    FIXED_IO_ps_porb,
    FIXED_IO_ps_srstb);
  (* X_INTERFACE_INFO = "xilinx.com:interface:ddrx:1.0 DDR ADDR" *) (* X_INTERFACE_MODE = "Master" *) (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME DDR, AXI_ARBITRATION_SCHEME TDM, BURST_LENGTH 8, CAN_DEBUG false, CAS_LATENCY 11, CAS_WRITE_LATENCY 11, CS_ENABLED true, DATA_MASK_ENABLED true, DATA_WIDTH 8, MEMORY_TYPE COMPONENTS, MEM_ADDR_MAP ROW_COLUMN_BANK, SLOT Single, TIMEPERIOD_PS 1250" *) inout [14:0]DDR_addr;
  (* X_INTERFACE_INFO = "xilinx.com:interface:ddrx:1.0 DDR BA" *) inout [2:0]DDR_ba;
  (* X_INTERFACE_INFO = "xilinx.com:interface:ddrx:1.0 DDR CAS_N" *) inout DDR_cas_n;
  (* X_INTERFACE_INFO = "xilinx.com:interface:ddrx:1.0 DDR CK_N" *) inout DDR_ck_n;
  (* X_INTERFACE_INFO = "xilinx.com:interface:ddrx:1.0 DDR CK_P" *) inout DDR_ck_p;
  (* X_INTERFACE_INFO = "xilinx.com:interface:ddrx:1.0 DDR CKE" *) inout DDR_cke;
  (* X_INTERFACE_INFO = "xilinx.com:interface:ddrx:1.0 DDR CS_N" *) inout DDR_cs_n;
  (* X_INTERFACE_INFO = "xilinx.com:interface:ddrx:1.0 DDR DM" *) inout [3:0]DDR_dm;
  (* X_INTERFACE_INFO = "xilinx.com:interface:ddrx:1.0 DDR DQ" *) inout [31:0]DDR_dq;
  (* X_INTERFACE_INFO = "xilinx.com:interface:ddrx:1.0 DDR DQS_N" *) inout [3:0]DDR_dqs_n;
  (* X_INTERFACE_INFO = "xilinx.com:interface:ddrx:1.0 DDR DQS_P" *) inout [3:0]DDR_dqs_p;
  (* X_INTERFACE_INFO = "xilinx.com:interface:ddrx:1.0 DDR ODT" *) inout DDR_odt;
  (* X_INTERFACE_INFO = "xilinx.com:interface:ddrx:1.0 DDR RAS_N" *) inout DDR_ras_n;
  (* X_INTERFACE_INFO = "xilinx.com:interface:ddrx:1.0 DDR RESET_N" *) inout DDR_reset_n;
  (* X_INTERFACE_INFO = "xilinx.com:interface:ddrx:1.0 DDR WE_N" *) inout DDR_we_n;
  (* X_INTERFACE_INFO = "xilinx.com:display_processing_system7:fixedio:1.0 FIXED_IO DDR_VRN" *) (* X_INTERFACE_MODE = "Master" *) (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME FIXED_IO, CAN_DEBUG false" *) inout FIXED_IO_ddr_vrn;
  (* X_INTERFACE_INFO = "xilinx.com:display_processing_system7:fixedio:1.0 FIXED_IO DDR_VRP" *) inout FIXED_IO_ddr_vrp;
  (* X_INTERFACE_INFO = "xilinx.com:display_processing_system7:fixedio:1.0 FIXED_IO MIO" *) inout [53:0]FIXED_IO_mio;
  (* X_INTERFACE_INFO = "xilinx.com:display_processing_system7:fixedio:1.0 FIXED_IO PS_CLK" *) inout FIXED_IO_ps_clk;
  (* X_INTERFACE_INFO = "xilinx.com:display_processing_system7:fixedio:1.0 FIXED_IO PS_PORB" *) inout FIXED_IO_ps_porb;
  (* X_INTERFACE_INFO = "xilinx.com:display_processing_system7:fixedio:1.0 FIXED_IO PS_SRSTB" *) inout FIXED_IO_ps_srstb;

  wire [14:0]DDR_addr;
  wire [2:0]DDR_ba;
  wire DDR_cas_n;
  wire DDR_ck_n;
  wire DDR_ck_p;
  wire DDR_cke;
  wire DDR_cs_n;
  wire [3:0]DDR_dm;
  wire [31:0]DDR_dq;
  wire [3:0]DDR_dqs_n;
  wire [3:0]DDR_dqs_p;
  wire DDR_odt;
  wire DDR_ras_n;
  wire DDR_reset_n;
  wire DDR_we_n;
  wire FIXED_IO_ddr_vrn;
  wire FIXED_IO_ddr_vrp;
  wire [53:0]FIXED_IO_mio;
  wire FIXED_IO_ps_clk;
  wire FIXED_IO_ps_porb;
  wire FIXED_IO_ps_srstb;
  wire [31:0]axi_gp0_lite_M_AXI_ARADDR;
  wire [2:0]axi_gp0_lite_M_AXI_ARPROT;
  wire axi_gp0_lite_M_AXI_ARREADY;
  wire axi_gp0_lite_M_AXI_ARVALID;
  wire [31:0]axi_gp0_lite_M_AXI_AWADDR;
  wire [2:0]axi_gp0_lite_M_AXI_AWPROT;
  wire axi_gp0_lite_M_AXI_AWREADY;
  wire axi_gp0_lite_M_AXI_AWVALID;
  wire axi_gp0_lite_M_AXI_BREADY;
  wire [1:0]axi_gp0_lite_M_AXI_BRESP;
  wire axi_gp0_lite_M_AXI_BVALID;
  wire [31:0]axi_gp0_lite_M_AXI_RDATA;
  wire axi_gp0_lite_M_AXI_RREADY;
  wire [1:0]axi_gp0_lite_M_AXI_RRESP;
  wire axi_gp0_lite_M_AXI_RVALID;
  wire [31:0]axi_gp0_lite_M_AXI_WDATA;
  wire axi_gp0_lite_M_AXI_WREADY;
  wire [3:0]axi_gp0_lite_M_AXI_WSTRB;
  wire axi_gp0_lite_M_AXI_WVALID;
  wire [0:0]const_one_dout;
  wire [0:0]const_zero_dout;
  wire [31:0]infer_M_AXI_ARADDR;
  wire [1:0]infer_M_AXI_ARBURST;
  wire [3:0]infer_M_AXI_ARCACHE;
  wire [5:0]infer_M_AXI_ARID;
  wire [3:0]infer_M_AXI_ARLEN;
  wire [1:0]infer_M_AXI_ARLOCK;
  wire [2:0]infer_M_AXI_ARPROT;
  wire [3:0]infer_M_AXI_ARQOS;
  wire infer_M_AXI_ARREADY;
  wire [2:0]infer_M_AXI_ARSIZE;
  wire infer_M_AXI_ARVALID;
  wire [31:0]infer_M_AXI_AWADDR;
  wire [1:0]infer_M_AXI_AWBURST;
  wire [3:0]infer_M_AXI_AWCACHE;
  wire [5:0]infer_M_AXI_AWID;
  wire [3:0]infer_M_AXI_AWLEN;
  wire [1:0]infer_M_AXI_AWLOCK;
  wire [2:0]infer_M_AXI_AWPROT;
  wire [3:0]infer_M_AXI_AWQOS;
  wire infer_M_AXI_AWREADY;
  wire [2:0]infer_M_AXI_AWSIZE;
  wire infer_M_AXI_AWVALID;
  wire [5:0]infer_M_AXI_BID;
  wire infer_M_AXI_BREADY;
  wire [1:0]infer_M_AXI_BRESP;
  wire infer_M_AXI_BVALID;
  wire [63:0]infer_M_AXI_RDATA;
  wire [5:0]infer_M_AXI_RID;
  wire infer_M_AXI_RLAST;
  wire infer_M_AXI_RREADY;
  wire [1:0]infer_M_AXI_RRESP;
  wire infer_M_AXI_RVALID;
  wire [63:0]infer_M_AXI_WDATA;
  wire [5:0]infer_M_AXI_WID;
  wire infer_M_AXI_WLAST;
  wire infer_M_AXI_WREADY;
  wire [7:0]infer_M_AXI_WSTRB;
  wire infer_M_AXI_WVALID;
  wire ps7_FCLK_CLK0;
  wire ps7_FCLK_RESET0_N;
  wire [31:0]ps7_M_AXI_GP0_ARADDR;
  wire [1:0]ps7_M_AXI_GP0_ARBURST;
  wire [3:0]ps7_M_AXI_GP0_ARCACHE;
  wire [11:0]ps7_M_AXI_GP0_ARID;
  wire [3:0]ps7_M_AXI_GP0_ARLEN;
  wire [1:0]ps7_M_AXI_GP0_ARLOCK;
  wire [2:0]ps7_M_AXI_GP0_ARPROT;
  wire [3:0]ps7_M_AXI_GP0_ARQOS;
  wire ps7_M_AXI_GP0_ARREADY;
  wire [2:0]ps7_M_AXI_GP0_ARSIZE;
  wire ps7_M_AXI_GP0_ARVALID;
  wire [31:0]ps7_M_AXI_GP0_AWADDR;
  wire [1:0]ps7_M_AXI_GP0_AWBURST;
  wire [3:0]ps7_M_AXI_GP0_AWCACHE;
  wire [11:0]ps7_M_AXI_GP0_AWID;
  wire [3:0]ps7_M_AXI_GP0_AWLEN;
  wire [1:0]ps7_M_AXI_GP0_AWLOCK;
  wire [2:0]ps7_M_AXI_GP0_AWPROT;
  wire [3:0]ps7_M_AXI_GP0_AWQOS;
  wire ps7_M_AXI_GP0_AWREADY;
  wire [2:0]ps7_M_AXI_GP0_AWSIZE;
  wire ps7_M_AXI_GP0_AWVALID;
  wire [11:0]ps7_M_AXI_GP0_BID;
  wire ps7_M_AXI_GP0_BREADY;
  wire [1:0]ps7_M_AXI_GP0_BRESP;
  wire ps7_M_AXI_GP0_BVALID;
  wire [31:0]ps7_M_AXI_GP0_RDATA;
  wire [11:0]ps7_M_AXI_GP0_RID;
  wire ps7_M_AXI_GP0_RLAST;
  wire ps7_M_AXI_GP0_RREADY;
  wire [1:0]ps7_M_AXI_GP0_RRESP;
  wire ps7_M_AXI_GP0_RVALID;
  wire [31:0]ps7_M_AXI_GP0_WDATA;
  wire [11:0]ps7_M_AXI_GP0_WID;
  wire ps7_M_AXI_GP0_WLAST;
  wire ps7_M_AXI_GP0_WREADY;
  wire [3:0]ps7_M_AXI_GP0_WSTRB;
  wire ps7_M_AXI_GP0_WVALID;
  wire [0:0]rst_fclk0_peripheral_aresetn;

  s2b_inference_axi_gp0_lite_0 axi_gp0_lite
       (.aclk(ps7_FCLK_CLK0),
        .aresetn(rst_fclk0_peripheral_aresetn),
        .m_axi_araddr(axi_gp0_lite_M_AXI_ARADDR),
        .m_axi_arprot(axi_gp0_lite_M_AXI_ARPROT),
        .m_axi_arready(axi_gp0_lite_M_AXI_ARREADY),
        .m_axi_arvalid(axi_gp0_lite_M_AXI_ARVALID),
        .m_axi_awaddr(axi_gp0_lite_M_AXI_AWADDR),
        .m_axi_awprot(axi_gp0_lite_M_AXI_AWPROT),
        .m_axi_awready(axi_gp0_lite_M_AXI_AWREADY),
        .m_axi_awvalid(axi_gp0_lite_M_AXI_AWVALID),
        .m_axi_bready(axi_gp0_lite_M_AXI_BREADY),
        .m_axi_bresp(axi_gp0_lite_M_AXI_BRESP),
        .m_axi_bvalid(axi_gp0_lite_M_AXI_BVALID),
        .m_axi_rdata(axi_gp0_lite_M_AXI_RDATA),
        .m_axi_rready(axi_gp0_lite_M_AXI_RREADY),
        .m_axi_rresp(axi_gp0_lite_M_AXI_RRESP),
        .m_axi_rvalid(axi_gp0_lite_M_AXI_RVALID),
        .m_axi_wdata(axi_gp0_lite_M_AXI_WDATA),
        .m_axi_wready(axi_gp0_lite_M_AXI_WREADY),
        .m_axi_wstrb(axi_gp0_lite_M_AXI_WSTRB),
        .m_axi_wvalid(axi_gp0_lite_M_AXI_WVALID),
        .s_axi_araddr(ps7_M_AXI_GP0_ARADDR),
        .s_axi_arburst(ps7_M_AXI_GP0_ARBURST),
        .s_axi_arcache(ps7_M_AXI_GP0_ARCACHE),
        .s_axi_arid(ps7_M_AXI_GP0_ARID),
        .s_axi_arlen(ps7_M_AXI_GP0_ARLEN),
        .s_axi_arlock(ps7_M_AXI_GP0_ARLOCK),
        .s_axi_arprot(ps7_M_AXI_GP0_ARPROT),
        .s_axi_arqos(ps7_M_AXI_GP0_ARQOS),
        .s_axi_arready(ps7_M_AXI_GP0_ARREADY),
        .s_axi_arsize(ps7_M_AXI_GP0_ARSIZE),
        .s_axi_arvalid(ps7_M_AXI_GP0_ARVALID),
        .s_axi_awaddr(ps7_M_AXI_GP0_AWADDR),
        .s_axi_awburst(ps7_M_AXI_GP0_AWBURST),
        .s_axi_awcache(ps7_M_AXI_GP0_AWCACHE),
        .s_axi_awid(ps7_M_AXI_GP0_AWID),
        .s_axi_awlen(ps7_M_AXI_GP0_AWLEN),
        .s_axi_awlock(ps7_M_AXI_GP0_AWLOCK),
        .s_axi_awprot(ps7_M_AXI_GP0_AWPROT),
        .s_axi_awqos(ps7_M_AXI_GP0_AWQOS),
        .s_axi_awready(ps7_M_AXI_GP0_AWREADY),
        .s_axi_awsize(ps7_M_AXI_GP0_AWSIZE),
        .s_axi_awvalid(ps7_M_AXI_GP0_AWVALID),
        .s_axi_bid(ps7_M_AXI_GP0_BID),
        .s_axi_bready(ps7_M_AXI_GP0_BREADY),
        .s_axi_bresp(ps7_M_AXI_GP0_BRESP),
        .s_axi_bvalid(ps7_M_AXI_GP0_BVALID),
        .s_axi_rdata(ps7_M_AXI_GP0_RDATA),
        .s_axi_rid(ps7_M_AXI_GP0_RID),
        .s_axi_rlast(ps7_M_AXI_GP0_RLAST),
        .s_axi_rready(ps7_M_AXI_GP0_RREADY),
        .s_axi_rresp(ps7_M_AXI_GP0_RRESP),
        .s_axi_rvalid(ps7_M_AXI_GP0_RVALID),
        .s_axi_wdata(ps7_M_AXI_GP0_WDATA),
        .s_axi_wid(ps7_M_AXI_GP0_WID),
        .s_axi_wlast(ps7_M_AXI_GP0_WLAST),
        .s_axi_wready(ps7_M_AXI_GP0_WREADY),
        .s_axi_wstrb(ps7_M_AXI_GP0_WSTRB),
        .s_axi_wvalid(ps7_M_AXI_GP0_WVALID));
  s2b_inference_const_one_0 const_one
       (.dout(const_one_dout));
  s2b_inference_const_zero_0 const_zero
       (.dout(const_zero_dout));
  s2b_inference_infer_0 infer
       (.clk(ps7_FCLK_CLK0),
        .cold_resetn(rst_fclk0_peripheral_aresetn),
        .m_axi_araddr(infer_M_AXI_ARADDR),
        .m_axi_arburst(infer_M_AXI_ARBURST),
        .m_axi_arcache(infer_M_AXI_ARCACHE),
        .m_axi_arid(infer_M_AXI_ARID),
        .m_axi_arlen(infer_M_AXI_ARLEN),
        .m_axi_arlock(infer_M_AXI_ARLOCK),
        .m_axi_arprot(infer_M_AXI_ARPROT),
        .m_axi_arqos(infer_M_AXI_ARQOS),
        .m_axi_arready(infer_M_AXI_ARREADY),
        .m_axi_arsize(infer_M_AXI_ARSIZE),
        .m_axi_arvalid(infer_M_AXI_ARVALID),
        .m_axi_awaddr(infer_M_AXI_AWADDR),
        .m_axi_awburst(infer_M_AXI_AWBURST),
        .m_axi_awcache(infer_M_AXI_AWCACHE),
        .m_axi_awid(infer_M_AXI_AWID),
        .m_axi_awlen(infer_M_AXI_AWLEN),
        .m_axi_awlock(infer_M_AXI_AWLOCK),
        .m_axi_awprot(infer_M_AXI_AWPROT),
        .m_axi_awqos(infer_M_AXI_AWQOS),
        .m_axi_awready(infer_M_AXI_AWREADY),
        .m_axi_awsize(infer_M_AXI_AWSIZE),
        .m_axi_awvalid(infer_M_AXI_AWVALID),
        .m_axi_bid(infer_M_AXI_BID),
        .m_axi_bready(infer_M_AXI_BREADY),
        .m_axi_bresp(infer_M_AXI_BRESP),
        .m_axi_bvalid(infer_M_AXI_BVALID),
        .m_axi_rdata(infer_M_AXI_RDATA),
        .m_axi_rid(infer_M_AXI_RID),
        .m_axi_rlast(infer_M_AXI_RLAST),
        .m_axi_rready(infer_M_AXI_RREADY),
        .m_axi_rresp(infer_M_AXI_RRESP),
        .m_axi_rvalid(infer_M_AXI_RVALID),
        .m_axi_wdata(infer_M_AXI_WDATA),
        .m_axi_wid(infer_M_AXI_WID),
        .m_axi_wlast(infer_M_AXI_WLAST),
        .m_axi_wready(infer_M_AXI_WREADY),
        .m_axi_wstrb(infer_M_AXI_WSTRB),
        .m_axi_wvalid(infer_M_AXI_WVALID),
        .s_axi_araddr(axi_gp0_lite_M_AXI_ARADDR),
        .s_axi_arprot(axi_gp0_lite_M_AXI_ARPROT),
        .s_axi_arready(axi_gp0_lite_M_AXI_ARREADY),
        .s_axi_arvalid(axi_gp0_lite_M_AXI_ARVALID),
        .s_axi_awaddr(axi_gp0_lite_M_AXI_AWADDR),
        .s_axi_awprot(axi_gp0_lite_M_AXI_AWPROT),
        .s_axi_awready(axi_gp0_lite_M_AXI_AWREADY),
        .s_axi_awvalid(axi_gp0_lite_M_AXI_AWVALID),
        .s_axi_bready(axi_gp0_lite_M_AXI_BREADY),
        .s_axi_bresp(axi_gp0_lite_M_AXI_BRESP),
        .s_axi_bvalid(axi_gp0_lite_M_AXI_BVALID),
        .s_axi_rdata(axi_gp0_lite_M_AXI_RDATA),
        .s_axi_rready(axi_gp0_lite_M_AXI_RREADY),
        .s_axi_rresp(axi_gp0_lite_M_AXI_RRESP),
        .s_axi_rvalid(axi_gp0_lite_M_AXI_RVALID),
        .s_axi_wdata(axi_gp0_lite_M_AXI_WDATA),
        .s_axi_wready(axi_gp0_lite_M_AXI_WREADY),
        .s_axi_wstrb(axi_gp0_lite_M_AXI_WSTRB),
        .s_axi_wvalid(axi_gp0_lite_M_AXI_WVALID));
  s2b_inference_ps7_0 ps7
       (.DDR_Addr(DDR_addr),
        .DDR_BankAddr(DDR_ba),
        .DDR_CAS_n(DDR_cas_n),
        .DDR_CKE(DDR_cke),
        .DDR_CS_n(DDR_cs_n),
        .DDR_Clk(DDR_ck_p),
        .DDR_Clk_n(DDR_ck_n),
        .DDR_DM(DDR_dm),
        .DDR_DQ(DDR_dq),
        .DDR_DQS(DDR_dqs_p),
        .DDR_DQS_n(DDR_dqs_n),
        .DDR_DRSTB(DDR_reset_n),
        .DDR_ODT(DDR_odt),
        .DDR_RAS_n(DDR_ras_n),
        .DDR_VRN(FIXED_IO_ddr_vrn),
        .DDR_VRP(FIXED_IO_ddr_vrp),
        .DDR_WEB(DDR_we_n),
        .FCLK_CLK0(ps7_FCLK_CLK0),
        .FCLK_RESET0_N(ps7_FCLK_RESET0_N),
        .MIO(FIXED_IO_mio),
        .M_AXI_GP0_ACLK(ps7_FCLK_CLK0),
        .M_AXI_GP0_ARADDR(ps7_M_AXI_GP0_ARADDR),
        .M_AXI_GP0_ARBURST(ps7_M_AXI_GP0_ARBURST),
        .M_AXI_GP0_ARCACHE(ps7_M_AXI_GP0_ARCACHE),
        .M_AXI_GP0_ARID(ps7_M_AXI_GP0_ARID),
        .M_AXI_GP0_ARLEN(ps7_M_AXI_GP0_ARLEN),
        .M_AXI_GP0_ARLOCK(ps7_M_AXI_GP0_ARLOCK),
        .M_AXI_GP0_ARPROT(ps7_M_AXI_GP0_ARPROT),
        .M_AXI_GP0_ARQOS(ps7_M_AXI_GP0_ARQOS),
        .M_AXI_GP0_ARREADY(ps7_M_AXI_GP0_ARREADY),
        .M_AXI_GP0_ARSIZE(ps7_M_AXI_GP0_ARSIZE),
        .M_AXI_GP0_ARVALID(ps7_M_AXI_GP0_ARVALID),
        .M_AXI_GP0_AWADDR(ps7_M_AXI_GP0_AWADDR),
        .M_AXI_GP0_AWBURST(ps7_M_AXI_GP0_AWBURST),
        .M_AXI_GP0_AWCACHE(ps7_M_AXI_GP0_AWCACHE),
        .M_AXI_GP0_AWID(ps7_M_AXI_GP0_AWID),
        .M_AXI_GP0_AWLEN(ps7_M_AXI_GP0_AWLEN),
        .M_AXI_GP0_AWLOCK(ps7_M_AXI_GP0_AWLOCK),
        .M_AXI_GP0_AWPROT(ps7_M_AXI_GP0_AWPROT),
        .M_AXI_GP0_AWQOS(ps7_M_AXI_GP0_AWQOS),
        .M_AXI_GP0_AWREADY(ps7_M_AXI_GP0_AWREADY),
        .M_AXI_GP0_AWSIZE(ps7_M_AXI_GP0_AWSIZE),
        .M_AXI_GP0_AWVALID(ps7_M_AXI_GP0_AWVALID),
        .M_AXI_GP0_BID(ps7_M_AXI_GP0_BID),
        .M_AXI_GP0_BREADY(ps7_M_AXI_GP0_BREADY),
        .M_AXI_GP0_BRESP(ps7_M_AXI_GP0_BRESP),
        .M_AXI_GP0_BVALID(ps7_M_AXI_GP0_BVALID),
        .M_AXI_GP0_RDATA(ps7_M_AXI_GP0_RDATA),
        .M_AXI_GP0_RID(ps7_M_AXI_GP0_RID),
        .M_AXI_GP0_RLAST(ps7_M_AXI_GP0_RLAST),
        .M_AXI_GP0_RREADY(ps7_M_AXI_GP0_RREADY),
        .M_AXI_GP0_RRESP(ps7_M_AXI_GP0_RRESP),
        .M_AXI_GP0_RVALID(ps7_M_AXI_GP0_RVALID),
        .M_AXI_GP0_WDATA(ps7_M_AXI_GP0_WDATA),
        .M_AXI_GP0_WID(ps7_M_AXI_GP0_WID),
        .M_AXI_GP0_WLAST(ps7_M_AXI_GP0_WLAST),
        .M_AXI_GP0_WREADY(ps7_M_AXI_GP0_WREADY),
        .M_AXI_GP0_WSTRB(ps7_M_AXI_GP0_WSTRB),
        .M_AXI_GP0_WVALID(ps7_M_AXI_GP0_WVALID),
        .PS_CLK(FIXED_IO_ps_clk),
        .PS_PORB(FIXED_IO_ps_porb),
        .PS_SRSTB(FIXED_IO_ps_srstb),
        .S_AXI_HP0_ACLK(ps7_FCLK_CLK0),
        .S_AXI_HP0_ARADDR(infer_M_AXI_ARADDR),
        .S_AXI_HP0_ARBURST(infer_M_AXI_ARBURST),
        .S_AXI_HP0_ARCACHE(infer_M_AXI_ARCACHE),
        .S_AXI_HP0_ARID(infer_M_AXI_ARID),
        .S_AXI_HP0_ARLEN(infer_M_AXI_ARLEN),
        .S_AXI_HP0_ARLOCK(infer_M_AXI_ARLOCK),
        .S_AXI_HP0_ARPROT(infer_M_AXI_ARPROT),
        .S_AXI_HP0_ARQOS(infer_M_AXI_ARQOS),
        .S_AXI_HP0_ARREADY(infer_M_AXI_ARREADY),
        .S_AXI_HP0_ARSIZE(infer_M_AXI_ARSIZE),
        .S_AXI_HP0_ARVALID(infer_M_AXI_ARVALID),
        .S_AXI_HP0_AWADDR(infer_M_AXI_AWADDR),
        .S_AXI_HP0_AWBURST(infer_M_AXI_AWBURST),
        .S_AXI_HP0_AWCACHE(infer_M_AXI_AWCACHE),
        .S_AXI_HP0_AWID(infer_M_AXI_AWID),
        .S_AXI_HP0_AWLEN(infer_M_AXI_AWLEN),
        .S_AXI_HP0_AWLOCK(infer_M_AXI_AWLOCK),
        .S_AXI_HP0_AWPROT(infer_M_AXI_AWPROT),
        .S_AXI_HP0_AWQOS(infer_M_AXI_AWQOS),
        .S_AXI_HP0_AWREADY(infer_M_AXI_AWREADY),
        .S_AXI_HP0_AWSIZE(infer_M_AXI_AWSIZE),
        .S_AXI_HP0_AWVALID(infer_M_AXI_AWVALID),
        .S_AXI_HP0_BID(infer_M_AXI_BID),
        .S_AXI_HP0_BREADY(infer_M_AXI_BREADY),
        .S_AXI_HP0_BRESP(infer_M_AXI_BRESP),
        .S_AXI_HP0_BVALID(infer_M_AXI_BVALID),
        .S_AXI_HP0_RDATA(infer_M_AXI_RDATA),
        .S_AXI_HP0_RDISSUECAP1_EN(1'b0),
        .S_AXI_HP0_RID(infer_M_AXI_RID),
        .S_AXI_HP0_RLAST(infer_M_AXI_RLAST),
        .S_AXI_HP0_RREADY(infer_M_AXI_RREADY),
        .S_AXI_HP0_RRESP(infer_M_AXI_RRESP),
        .S_AXI_HP0_RVALID(infer_M_AXI_RVALID),
        .S_AXI_HP0_WDATA(infer_M_AXI_WDATA),
        .S_AXI_HP0_WID(infer_M_AXI_WID),
        .S_AXI_HP0_WLAST(infer_M_AXI_WLAST),
        .S_AXI_HP0_WREADY(infer_M_AXI_WREADY),
        .S_AXI_HP0_WRISSUECAP1_EN(1'b0),
        .S_AXI_HP0_WSTRB(infer_M_AXI_WSTRB),
        .S_AXI_HP0_WVALID(infer_M_AXI_WVALID));
  s2b_inference_rst_fclk0_0 rst_fclk0
       (.aux_reset_in(const_zero_dout),
        .dcm_locked(const_one_dout),
        .ext_reset_in(ps7_FCLK_RESET0_N),
        .mb_debug_sys_rst(const_zero_dout),
        .peripheral_aresetn(rst_fclk0_peripheral_aresetn),
        .slowest_sync_clk(ps7_FCLK_CLK0));
endmodule
