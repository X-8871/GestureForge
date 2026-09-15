timestamp_utc8=2026-09-15T16:05:35.2597577+08:00
working_directory=D:\FPGA_Data\darknet
command=D:\mingw64\bin\mingw32-make.exe -j2 OS=MSYS_NT GPU=1 CUDNN=0 CUDNN_HALF=0 OPENCV=0 (PATH includes MinGW/Git usr/CUDA; SHELL=C:\Program Files\Git\usr\bin\sh.exe)
stdout_log=D:\FPGA_Competition\report\evidence\S1-T01\20260915_darknet_make_minimal_v2.stdout.log
stderr_log=D:\FPGA_Competition\report\evidence\S1-T01\20260915_darknet_make_minimal_v2.stderr.log
exit_code=2
stdout:
mkdir -p ./obj/
chmod +x *.sh
g++ -std=c++11 -std=c++11 -Iinclude/ -I3rdparty/stb/include -DGPU -I/usr/local/cuda/include/ -Wall -Wfatal-errors -Wno-unused-result -Wno-unknown-pragmas -fPIC -rdynamic -Ofast -DGPU -c ./src/image_opencv.cpp -o obj/image_opencv.o
g++ -std=c++11 -std=c++11 -Iinclude/ -I3rdparty/stb/include -DGPU -I/usr/local/cuda/include/ -Wall -Wfatal-errors -Wno-unused-result -Wno-unknown-pragmas -fPIC -rdynamic -Ofast -DGPU -c ./src/http_stream.cpp -o obj/http_stream.o

stderr:
g++: error: unrecognized command line option '-rdynamic'
g++: error: unrecognized command line option '-rdynamic'
mingw32-make: *** [Makefile:198: obj/http_stream.o] Error 1
mingw32-make: *** Waiting for unfinished jobs....
mingw32-make: *** [Makefile:198: obj/image_opencv.o] Error 1
