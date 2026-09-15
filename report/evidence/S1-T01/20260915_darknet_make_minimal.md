timestamp_utc8=2026-09-15T16:05:02.7793932+08:00
working_directory=D:\FPGA_Data\darknet
command=D:\mingw64\bin\mingw32-make.exe -j2 OS=MSYS_NT GPU=1 CUDNN=0 CUDNN_HALF=0 OPENCV=0
stdout_log=D:\FPGA_Competition\report\evidence\S1-T01\20260915_darknet_make_minimal.stdout.log
stderr_log=D:\FPGA_Competition\report\evidence\S1-T01\20260915_darknet_make_minimal.stderr.log
exit_code=2
stdout:
mkdir -p ./obj/
mkdir -p results

stderr:
process_begin: CreateProcess(NULL, uname, ...) failed.
mingw32-make: Makefile:24: pipe: No error
The syntax of the command is incorrect.
mingw32-make: *** [Makefile:204: obj/] Error 1
mingw32-make: *** Waiting for unfinished jobs....
A subdirectory or file -p already exists.
Error occurred while processing: -p.
mingw32-make: *** [Makefile:208: results] Error 1
