# 只导出脚本；维持同一源码与全部断言，限制为单线程和有限运行时间。
set_param general.maxThreads 1
set simset [get_filesets sim_1]
set_property XSIM.COMPILE.XVLOG.RELAX false $simset
set_property XSIM.ELABORATE.RELAX false $simset
set_property XSIM.COMPILE.XSC.MT_LEVEL off $simset
set_property XSIM.ELABORATE.MT_LEVEL off $simset
set_property XSIM.ELABORATE.LOAD_GLBL false $simset
set_property XSIM.ELABORATE.DEBUG_LEVEL typical $simset
set_property XSIM.SIMULATE.RUNTIME 2ms $simset
set_property XSIM.SIMULATE.LOG_ALL_SIGNALS false $simset
launch_simulation -simset sim_1 -mode behavioral -scripts_only -absolute_path
puts "XSIM_EXPORT_SCRIPTS_ONLY_OK"
