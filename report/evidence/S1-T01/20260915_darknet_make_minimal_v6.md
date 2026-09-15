timestamp_utc8=2026-09-15T16:07:12.5093313+08:00
working_directory=D:\FPGA_Data\darknet
command=D:\mingw64\bin\mingw32-make.exe -e -j2 OS=MSYS_NT GPU=1 CUDNN=0 CUDNN_HALF=0 OPENCV=0 with CFLAGS="-Wall -Wfatal-errors -Wno-unused-result -Wno-unknown-pragmas -fPIC -Ofast -pthread" CPATH="C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\include" LIBRARY_PATH="C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\lib\x64" SHELL="C:\Program Files\Git\usr\bin\sh.exe"
stdout_log=D:\FPGA_Competition\report\evidence\S1-T01\20260915_darknet_make_minimal_v6.stdout.log
stderr_log=D:\FPGA_Competition\report\evidence\S1-T01\20260915_darknet_make_minimal_v6.stderr.log
exit_code=2
stdout:
mkdir -p ./obj/
chmod +x *.sh
g++ -std=c++11 -std=c++11 -Iinclude/ -I3rdparty/stb/include -DGPU -I/usr/local/cuda/include/ -Wall -Wfatal-errors -Wno-unused-result -Wno-unknown-pragmas -fPIC -Ofast -pthread -c ./src/http_stream.cpp -o obj/http_stream.o
gcc -Iinclude/ -I3rdparty/stb/include -DGPU -I/usr/local/cuda/include/ -Wall -Wfatal-errors -Wno-unused-result -Wno-unknown-pragmas -fPIC -Ofast -pthread -c ./src/utils.c -o obj/utils.o

stderr:
In file included from C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\include/device_types.h:59,
                 from C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\include/builtin_types.h:56,
                 from C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\include/cuda_runtime.h:90,
                 from include/darknet.h:41,
                 from ./src/image.h:3,
                 from ./src/http_stream.cpp:2:
C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\include/crt/host_defines.h:98: warning: "__cdecl" redefined
 #define __cdecl

<built-in>: note: this is the location of the previous definition
In file included from C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\include/device_types.h:59,
                 from C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\include/builtin_types.h:56,
                 from C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\include/cuda_runtime.h:90,
                 from include/darknet.h:41,
                 from ./src/utils.h:3,
                 from ./src/utils.c:4:
C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\include/crt/host_defines.h:98: warning: "__cdecl" redefined
 #define __cdecl

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
In file included from ./src/utils.c:15:
./src/darkunistd.h:24: warning: "X_OK" redefined
 #define X_OK R_OK       /* execute permission - unsupported in Windows, */

In file included from D:/mingw64/x86_64-w64-mingw32/include/direct.h:10,
                 from ./src/darkunistd.h:11,
                 from ./src/utils.c:15:
D:/mingw64/x86_64-w64-mingw32/include/io.h:183: note: this is the location of the previous definition
 #define X_OK 1 /* Check for execute permission. */

./src/utils.c: In function 'size_to_IEC_string':
./src/utils.c:377:48: warning: format '%ld' expects argument of type 'long int', but argument 3 has type 'size_t' {aka 'const long long unsigned int'} [-Wformat=]
     if (size < KiB)         sprintf(buffer, "%ld bytes", size);
                                              ~~^         ~~~~
                                              %I64d
./src/utils.c:377:48: warning: format '%ld' expects argument of type 'long int', but argument 3 has type 'size_t' {aka 'const long long unsigned int'} [-Wformat=]
     if (size < KiB)         sprintf(buffer, "%ld bytes", size);
                                              ~~^         ~~~~
                                              %I64d
./src/utils.c: In function 'custom_hash':
./src/utils.c:1095:12: warning: suggest parentheses around assignment used as truth value [-Wparentheses]
     while (c = *str++)
            ^
In function 'copy_string',
    inlined from 'basecfg' at ./src/utils.c:180:9:
./src/utils.c:565:5: warning: 'strncpy' specified bound depends on the length of the source argument [-Wstringop-overflow=]
     strncpy(copy, s, strlen(s)+1);
     ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~
./src/utils.c: In function 'basecfg':
./src/utils.c:565:22: note: length computed here
     strncpy(copy, s, strlen(s)+1);
                      ^~~~~~~~~
./src/utils.c: In function 'copy_string':
./src/utils.c:565:5: warning: 'strncpy' specified bound depends on the length of the source argument [-Wstringop-overflow=]
     strncpy(copy, s, strlen(s)+1);
     ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~
./src/utils.c:565:22: note: length computed here
     strncpy(copy, s, strlen(s)+1);
                      ^~~~~~~~~
In function 'copy_string',
    inlined from 'parse_csv_line' at ./src/utils.c:578:28:
./src/utils.c:565:5: warning: 'strncpy' specified bound depends on the length of the source argument [-Wstringop-overflow=]
     strncpy(copy, s, strlen(s)+1);
     ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~
./src/utils.c: In function 'parse_csv_line':
./src/utils.c:565:22: note: length computed here
     strncpy(copy, s, strlen(s)+1);
                      ^~~~~~~~~
In function 'copy_string',
    inlined from 'parse_csv_line' at ./src/utils.c:582:20:
./src/utils.c:565:5: warning: 'strncpy' specified bound depends on the length of the source argument [-Wstringop-overflow=]
     strncpy(copy, s, strlen(s)+1);
     ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~
./src/utils.c: In function 'parse_csv_line':
./src/utils.c:565:22: note: length computed here
     strncpy(copy, s, strlen(s)+1);
                      ^~~~~~~~~
