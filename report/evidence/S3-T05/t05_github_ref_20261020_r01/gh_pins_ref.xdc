#############SPI Configurate Setting##################
set_property BITSTREAM.CONFIG.SPI_BUSWIDTH 4 [current_design]
set_property CONFIG_MODE SPIx4 [current_design]
set_property BITSTREAM.CONFIG.CONFIGRATE 50 [current_design]

set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design]
set_property BITSTREAM.CONFIG.UNUSEDPIN Pullup [current_design]
set_property CFGBVS VCCO [current_design]
set_property CONFIG_VOLTAGE 3.3 [current_design]
############## clock define##################
create_clock -period 5.000 [get_ports ddr_clk_p]
set_property PACKAGE_PIN K22 [get_ports ddr_clk_p]
set_property PACKAGE_PIN K23 [get_ports ddr_clk_n]
set_property IOSTANDARD DIFF_SSTL12 [get_ports ddr_clk_n]


create_clock -period 5.000 [get_ports sys_clk_p]
set_property PACKAGE_PIN AC13 [get_ports sys_clk_p]
set_property PACKAGE_PIN AC14 [get_ports sys_clk_n]
set_property IOSTANDARD LVDS_25 [get_ports sys_clk_n]
set_property IOSTANDARD LVDS_25 [get_ports sys_clk_p]
############## key define##################
set_property PACKAGE_PIN J14 [get_ports rst_n]
set_property IOSTANDARD LVCMOS33 [get_ports rst_n]

set_property PACKAGE_PIN J15 [get_ports key]
set_property IOSTANDARD LVCMOS33 [get_ports key]
############## fan define##################
set_property IOSTANDARD LVCMOS33 [get_ports fan_pwm]
set_property PACKAGE_PIN Y16 [get_ports fan_pwm]


set_property PACKAGE_PIN AF17 [get_ports hdmi_out_clk]
set_property PACKAGE_PIN AF24 [get_ports {hdmi_out_data[0]}]
set_property PACKAGE_PIN AD25 [get_ports {hdmi_out_data[1]}]
set_property PACKAGE_PIN AB26 [get_ports {hdmi_out_data[2]}]
set_property PACKAGE_PIN AD24 [get_ports {hdmi_out_data[3]}]
set_property PACKAGE_PIN AB25 [get_ports {hdmi_out_data[4]}]
set_property PACKAGE_PIN AE26 [get_ports {hdmi_out_data[5]}]
set_property PACKAGE_PIN AE17 [get_ports {hdmi_out_data[6]}]
set_property PACKAGE_PIN AE25 [get_ports {hdmi_out_data[7]}]
set_property PACKAGE_PIN Y21 [get_ports {hdmi_out_data[8]}]
set_property PACKAGE_PIN AF19 [get_ports {hdmi_out_data[9]}]
set_property PACKAGE_PIN AC24 [get_ports {hdmi_out_data[10]}]
set_property PACKAGE_PIN AF18 [get_ports {hdmi_out_data[11]}]
set_property PACKAGE_PIN AB24 [get_ports {hdmi_out_data[12]}]
set_property PACKAGE_PIN AA17 [get_ports {hdmi_out_data[13]}]
set_property PACKAGE_PIN AB19 [get_ports {hdmi_out_data[14]}]
set_property PACKAGE_PIN AB20 [get_ports {hdmi_out_data[15]}]
set_property PACKAGE_PIN AA19 [get_ports {hdmi_out_data[16]}]
set_property PACKAGE_PIN Y17 [get_ports {hdmi_out_data[17]}]
set_property PACKAGE_PIN AA20 [get_ports {hdmi_out_data[18]}]
set_property PACKAGE_PIN AE16 [get_ports {hdmi_out_data[19]}]
set_property PACKAGE_PIN AD18 [get_ports {hdmi_out_data[20]}]
set_property PACKAGE_PIN AD16 [get_ports {hdmi_out_data[21]}]
set_property PACKAGE_PIN AC18 [get_ports {hdmi_out_data[22]}]
set_property PACKAGE_PIN AC19 [get_ports {hdmi_out_data[23]}]
set_property PACKAGE_PIN AC26 [get_ports hdmi_out_de]
set_property PACKAGE_PIN AF25 [get_ports hdmi_out_hs]
set_property PACKAGE_PIN Y20 [get_ports hdmi_nreset]
set_property PACKAGE_PIN AD26 [get_ports hdmi_out_vs]
set_property PACKAGE_PIN AB17 [get_ports hdmi_scl]
set_property PACKAGE_PIN AC17 [get_ports hdmi_sda]

set_property IOSTANDARD LVCMOS18 [get_ports hdmi_out_clk]
set_property IOSTANDARD LVCMOS18 [get_ports {hdmi_out_data[*]}]
set_property IOSTANDARD LVCMOS18 [get_ports hdmi_out_de]
set_property IOSTANDARD LVCMOS18 [get_ports hdmi_out_hs]
set_property IOSTANDARD LVCMOS18 [get_ports hdmi_nreset]
set_property IOSTANDARD LVCMOS18 [get_ports hdmi_out_vs]
set_property IOSTANDARD LVCMOS18 [get_ports hdmi_scl]
set_property IOSTANDARD LVCMOS18 [get_ports hdmi_sda]

set_property SLEW FAST [get_ports {hdmi_out_data[*]}]
set_property SLEW FAST [get_ports hdmi_out_de]
set_property SLEW FAST [get_ports hdmi_out_hs]
set_property SLEW FAST [get_ports hdmi_out_vs]



####  AN5642 ################################
set_property PACKAGE_PIN A10 [get_ports {cmos2_db[9]}]
set_property PACKAGE_PIN B10 [get_ports cmos2_sda]
set_property PACKAGE_PIN B11 [get_ports {cmos2_db[6]}]
set_property PACKAGE_PIN C11 [get_ports cmos2_scl]
set_property PACKAGE_PIN E10 [get_ports {cmos2_db[7]}]
set_property PACKAGE_PIN E11 [get_ports {cmos2_db[2]}]
set_property PACKAGE_PIN A9 [get_ports cmos2_href]
set_property PACKAGE_PIN B9 [get_ports {cmos2_db[8]}]
set_property PACKAGE_PIN D10 [get_ports {cmos2_db[3]}]
set_property PACKAGE_PIN D11 [get_ports cmos2_rst_n]
set_property PACKAGE_PIN C9 [get_ports {cmos2_db[4]}]
set_property PACKAGE_PIN D9 [get_ports {cmos2_db[5]}]
set_property PACKAGE_PIN F9 [get_ports {cmos2_db[1]}]
set_property PACKAGE_PIN F10 [get_ports {cmos2_db[0]}]
set_property PACKAGE_PIN G9 [get_ports cmos2_vsync]
set_property PACKAGE_PIN G10 [get_ports cmos2_pclk]
set_property PACKAGE_PIN J9 [get_ports cmos1_sda]
set_property PACKAGE_PIN J10 [get_ports {cmos1_db[9]}]
set_property PACKAGE_PIN J11 [get_ports {cmos1_db[8]}]
set_property PACKAGE_PIN G11 [get_ports cmos1_scl]
set_property PACKAGE_PIN H11 [get_ports {cmos1_db[5]}]
set_property PACKAGE_PIN K9 [get_ports {cmos1_db[3]}]
set_property PACKAGE_PIN K10 [get_ports {cmos1_db[4]}]
set_property PACKAGE_PIN B12 [get_ports {cmos1_db[6]}]
set_property PACKAGE_PIN C12 [get_ports {cmos1_db[0]}]
set_property PACKAGE_PIN E12 [get_ports {cmos1_db[7]}]
set_property PACKAGE_PIN E13 [get_ports {cmos1_db[1]}]
set_property PACKAGE_PIN F12 [get_ports {cmos1_db[2]}]
set_property PACKAGE_PIN G12 [get_ports cmos1_pclk]
set_property PACKAGE_PIN A12 [get_ports cmos1_href]
set_property PACKAGE_PIN A13 [get_ports cmos1_vsync]
set_property PACKAGE_PIN D13 [get_ports cmos1_rst_n]



set_property IOSTANDARD LVCMOS33 [get_ports cmos1_sda]
set_property IOSTANDARD LVCMOS33 [get_ports {cmos1_db[9]}]
set_property IOSTANDARD LVCMOS33 [get_ports {cmos1_db[8]}]
set_property IOSTANDARD LVCMOS33 [get_ports cmos1_scl]
set_property IOSTANDARD LVCMOS33 [get_ports {cmos1_db[5]}]
set_property IOSTANDARD LVCMOS33 [get_ports {cmos1_db[3]}]
set_property IOSTANDARD LVCMOS33 [get_ports {cmos1_db[4]}]
set_property IOSTANDARD LVCMOS33 [get_ports {cmos1_db[6]}]
set_property IOSTANDARD LVCMOS33 [get_ports {cmos1_db[0]}]
set_property IOSTANDARD LVCMOS33 [get_ports {cmos1_db[7]}]
set_property IOSTANDARD LVCMOS33 [get_ports {cmos1_db[1]}]
set_property IOSTANDARD LVCMOS33 [get_ports {cmos1_db[2]}]
set_property IOSTANDARD LVCMOS33 [get_ports cmos1_pclk]
set_property IOSTANDARD LVCMOS33 [get_ports cmos1_href]
set_property IOSTANDARD LVCMOS33 [get_ports cmos1_vsync]
set_property IOSTANDARD LVCMOS33 [get_ports cmos1_rst_n]

create_clock -period 11.904 [get_ports cmos1_pclk]
set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets cmos1_pclk_IBUF_inst/O]
set_input_delay -clock [get_clocks cmos1_pclk] 2.200 [get_ports {cmos1_db[*]}]
set_input_delay -clock [get_clocks cmos1_pclk] 2.200 [get_ports cmos1_href]
set_input_delay -clock [get_clocks cmos1_pclk] -min -add_delay 2.200 [get_ports cmos1_vsync]
set_input_delay -clock [get_clocks cmos1_pclk] -max -add_delay 4.000 [get_ports cmos1_vsync]

set_property IOSTANDARD LVCMOS33 [get_ports {cmos2_db[9]}]
set_property IOSTANDARD LVCMOS33 [get_ports cmos2_sda]
set_property IOSTANDARD LVCMOS33 [get_ports {cmos2_db[6]}]
set_property IOSTANDARD LVCMOS33 [get_ports cmos2_scl]
set_property IOSTANDARD LVCMOS33 [get_ports {cmos2_db[7]}]
set_property IOSTANDARD LVCMOS33 [get_ports {cmos2_db[2]}]
set_property IOSTANDARD LVCMOS33 [get_ports cmos2_href]
set_property IOSTANDARD LVCMOS33 [get_ports {cmos2_db[8]}]
set_property IOSTANDARD LVCMOS33 [get_ports {cmos2_db[3]}]
set_property IOSTANDARD LVCMOS33 [get_ports cmos2_rst_n]
set_property IOSTANDARD LVCMOS33 [get_ports {cmos2_db[4]}]
set_property IOSTANDARD LVCMOS33 [get_ports {cmos2_db[5]}]
set_property IOSTANDARD LVCMOS33 [get_ports {cmos2_db[1]}]
set_property IOSTANDARD LVCMOS33 [get_ports {cmos2_db[0]}]
set_property IOSTANDARD LVCMOS33 [get_ports cmos2_vsync]
set_property IOSTANDARD LVCMOS33 [get_ports cmos2_pclk]

create_clock -period 11.904 [get_ports cmos2_pclk]
set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets cmos2_pclk_IBUF_inst/O]
set_input_delay -clock [get_clocks cmos2_pclk] -min -add_delay 2.200 [get_ports {cmos2_db[*]}]
set_input_delay -clock [get_clocks cmos2_pclk] -max -add_delay 4.000 [get_ports {cmos2_db[*]}]
set_input_delay -clock [get_clocks cmos2_pclk] -min -add_delay 2.200 [get_ports cmos2_href]
set_input_delay -clock [get_clocks cmos2_pclk] -max -add_delay 4.000 [get_ports cmos2_href]
set_input_delay -clock [get_clocks cmos2_pclk] -min -add_delay 2.200 [get_ports cmos2_vsync]
set_input_delay -clock [get_clocks cmos2_pclk] -max -add_delay 4.000 [get_ports cmos2_vsync]
set_false_path -from [get_clocks clk_pll_i] -to [get_clocks clk_out1_video_pll]
set_false_path -from [get_clocks clk_out1_video_pll] -to [get_clocks clk_pll_i]

