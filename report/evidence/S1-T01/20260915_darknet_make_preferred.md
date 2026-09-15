timestamp_utc8=2026-09-15T16:04:29.5075661+08:00
working_directory=D:\FPGA_Data\darknet
command=d:\mingw64\bin\mingw32-make.exe -j2 GPU=1 CUDNN=1 CUDNN_HALF=1 OPENCV=0
stdout_log=D:\FPGA_Competition\report\evidence\S1-T01\20260915_darknet_make_preferred.stdout.log
stderr_log=D:\FPGA_Competition\report\evidence\S1-T01\20260915_darknet_make_preferred.stderr.log
exit_code=2
stdout:
mkdir -p ./obj/
mkdir -p backup

stderr:
process_begin: CreateProcess(NULL, uname, ...) failed.
mingw32-make: Makefile:24: pipe: No error
The syntax of the command is incorrect.
mingw32-make: *** [Makefile:204: obj/] Error 1
mingw32-make: *** Waiting for unfinished jobs....
