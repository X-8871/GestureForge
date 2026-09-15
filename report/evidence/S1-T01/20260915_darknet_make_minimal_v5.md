timestamp_utc8=2026-09-15T16:06:43.6784119+08:00
working_directory=D:\FPGA_Data\darknet
command=D:\mingw64\bin\mingw32-make.exe -e -j2 OS=MSYS_NT GPU=1 CUDNN=0 CUDNN_HALF=0 OPENCV=0 with CPATH="C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\include" LIBRARY_PATH="C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\lib\x64" CFLAGS="-Wall -Wfatal-errors -Wno-unused-result -Wno-unknown-pragmas -fPIC -Ofast" SHELL="C:\Program Files\Git\usr\bin\sh.exe"
stdout_log=D:\FPGA_Competition\report\evidence\S1-T01\20260915_darknet_make_minimal_v5.stdout.log
stderr_log=D:\FPGA_Competition\report\evidence\S1-T01\20260915_darknet_make_minimal_v5.stderr.log
exit_code=2
stdout:
mkdir -p ./obj/
chmod +x *.sh
g++ -std=c++11 -std=c++11 -Iinclude/ -I3rdparty/stb/include -DGPU -I/usr/local/cuda/include/ -Wall -Wfatal-errors -Wno-unused-result -Wno-unknown-pragmas -fPIC -Ofast -c ./src/image_opencv.cpp -o obj/image_opencv.o
g++ -std=c++11 -std=c++11 -Iinclude/ -I3rdparty/stb/include -DGPU -I/usr/local/cuda/include/ -Wall -Wfatal-errors -Wno-unused-result -Wno-unknown-pragmas -fPIC -Ofast -c ./src/http_stream.cpp -o obj/http_stream.o
gcc -Iinclude/ -I3rdparty/stb/include -DGPU -I/usr/local/cuda/include/ -Wall -Wfatal-errors -Wno-unused-result -Wno-unknown-pragmas -fPIC -Ofast -c ./src/gemm.c -o obj/gemm.o

stderr:
In file included from C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\include/device_types.h:59,
                 from C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\include/builtin_types.h:56,
                 from C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\include/cuda_runtime.h:90,
                 from include/darknet.h:41,
                 from ./src/image.h:3,
                 from ./src/http_stream.cpp:2:
C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\include/crt/host_defines.h:98: warning: "__cdecl" redefined
 #define __cdecl

In file included from C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\include/device_types.h:59,
                 from C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\include/builtin_types.h:56,
                 from C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\include/cuda_runtime.h:90,
                 from include/darknet.h:41,
                 from ./src/image.h:3,
                 from ./src/image_opencv.h:4,
                 from ./src/image_opencv.cpp:1:
C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\include/crt/host_defines.h:98: warning: "__cdecl" redefined
 #define __cdecl

<built-in>: note: this is the location of the previous definition
<built-in>: note: this is the location of the previous definition
./src/http_stream.cpp: In member function 'bool JSON_sender::write(const char*)':
./src/http_stream.cpp:227:28: warning: comparison of integer expressions of different signedness: 'SOCKET' {aka 'long long unsigned int'} and 'int' [-Wsign-compare]
                 if (client == SOCKET_ERROR)
                            ^
./src/http_stream.cpp:253:21: warning: unused variable 'n' [-Wunused-variable]
                 int n = _write(client, outputbuf, outlen);
                     ^
./src/http_stream.cpp: At global scope:
./src/http_stream.cpp:292:13: error: 'mutex' in namespace 'std' does not name a type
 static std::mutex mtx;
             ^~~~~
compilation terminated due to -Wfatal-errors.
mingw32-make: *** [Makefile:198: obj/http_stream.o] Error 1
mingw32-make: *** Waiting for unfinished jobs....
In file included from C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\include/device_types.h:59,
                 from C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\include/builtin_types.h:56,
                 from C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\include/cuda_runtime.h:90,
                 from include/darknet.h:41,
                 from ./src/activations.h:3,
                 from ./src/gemm.h:3,
                 from ./src/gemm.c:1:
C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\include/crt/host_defines.h:98: warning: "__cdecl" redefined
 #define __cdecl

<built-in>: note: this is the location of the previous definition
./src/gemm.c: In function 'convolution_2d':
./src/gemm.c:2042:15: warning: unused variable 'out_w' [-Wunused-variable]
     const int out_w = (w + 2 * pad - ksize) / stride + 1;    // output_width=input_width for stride=1 and pad=1
               ^~~~~
./src/gemm.c:2041:15: warning: unused variable 'out_h' [-Wunused-variable]
     const int out_h = (h + 2 * pad - ksize) / stride + 1;    // output_height=input_height for stride=1 and pad=1
               ^~~~~
