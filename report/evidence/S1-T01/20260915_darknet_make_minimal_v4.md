timestamp_utc8=2026-09-15T16:06:15.3892723+08:00
working_directory=D:\FPGA_Data\darknet
command=D:\mingw64\bin\mingw32-make.exe -e -j2 OS=MSYS_NT GPU=1 CUDNN=0 CUDNN_HALF=0 OPENCV=0 with environment CFLAGS="-Wall -Wfatal-errors -Wno-unused-result -Wno-unknown-pragmas -fPIC -Ofast" SHELL="C:\Program Files\Git\usr\bin\sh.exe"
stdout_log=D:\FPGA_Competition\report\evidence\S1-T01\20260915_darknet_make_minimal_v4.stdout.log
stderr_log=D:\FPGA_Competition\report\evidence\S1-T01\20260915_darknet_make_minimal_v4.stderr.log
exit_code=2
stdout:
mkdir -p ./obj/
chmod +x *.sh
g++ -std=c++11 -std=c++11 -Iinclude/ -I3rdparty/stb/include -DGPU -I/usr/local/cuda/include/ -Wall -Wfatal-errors -Wno-unused-result -Wno-unknown-pragmas -fPIC -Ofast -c ./src/image_opencv.cpp -o obj/image_opencv.o
g++ -std=c++11 -std=c++11 -Iinclude/ -I3rdparty/stb/include -DGPU -I/usr/local/cuda/include/ -Wall -Wfatal-errors -Wno-unused-result -Wno-unknown-pragmas -fPIC -Ofast -c ./src/http_stream.cpp -o obj/http_stream.o

stderr:
In file included from ./src/image.h:3,
                 from ./src/http_stream.cpp:2:
include/darknet.h:41:10: fatal error: cuda_runtime.h: No such file or directory
 #include <cuda_runtime.h>
          ^~~~~~~~~~~~~~~~
In file included from ./src/image.h:3,
                 from ./src/image_opencv.h:4,
                 from ./src/image_opencv.cpp:1:
include/darknet.h:41:10: fatal error: cuda_runtime.h: No such file or directory
 #include <cuda_runtime.h>
          ^~~~~~~~~~~~~~~~
compilation terminated.
compilation terminated.
mingw32-make: *** [Makefile:198: obj/http_stream.o] Error 1
mingw32-make: *** Waiting for unfinished jobs....
mingw32-make: *** [Makefile:198: obj/image_opencv.o] Error 1
