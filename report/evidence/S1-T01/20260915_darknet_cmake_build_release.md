timestamp_utc8=2026-09-15T16:19:56.9592498+08:00
working_directory=D:\FPGA_Data\darknet
build_directory=D:\FPGA_Data\darknet\build\s1_t01_vc_cuda134_v2
vcvars64=C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat
CUDA_PATH=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4
CUDA_PATH_V13_4=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4
CUDACXX=nvcc.exe
command=C:\Espressif\tools\cmake\3.30.2\bin\cmake.exe --build D:\FPGA_Data\darknet\build\s1_t01_vc_cuda134_v2 --config Release --target darknet -- /m:2 /verbosity:minimal
stdout_log=D:\FPGA_Competition\report\evidence\S1-T01\20260915_darknet_cmake_build_release.stdout.log
stderr_log=D:\FPGA_Competition\report\evidence\S1-T01\20260915_darknet_cmake_build_release.stderr.log
exit_code=0
stdout:
适用于 .NET Framework MSBuild 版本 17.14.51+25f168cee

  1>Checking Build System
  Building Custom Rule D:/FPGA_Data/darknet/CMakeLists.txt
  Compiling CUDA source file ..\..\src\activation_kernels.cu...

  D:\FPGA_Data\darknet\build\s1_t01_vc_cuda134_v2>"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\bin\nvcc.exe"  --use-local-env -ccbin "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.44.35207\bin\HostX64\x64" -x cu   -ID:\FPGA_Data\darknet\include -ID:\FPGA_Data\darknet\src -ID:\FPGA_Data\darknet\3rdparty\stb\include -ID:\FPGA_Data\darknet\3rdparty\getopt -I"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\include" -I"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\include\cccl" -ID:\FPGA_Data\darknet\3rdparty\pthreads\include -I"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\include"     --keep-dir darknet\x64\Release  -maxrregcount=0     --machine 64 --compile -Wno-deprecated-declarations --generate-code=arch=compute_89,code=[compute_89,sm_89] -Xcompiler=",/nologo,/wd4013,/wd4018,/wd4028,/wd4047,/wd4068,/wd4090,/wd4101,/wd4113,/wd4133,/wd4190,/wd4244,/wd4267,/wd4305,/wd4477,/wd4996,/wd4819,/fp:fast,/DGPU /EHsc -Ob2"   -D_WINDOWS -DNDEBUG -DUSE_CMAKE_LIBS -D_CRT_RAND_S -DNOMINMAX -D_USE_MATH_DEFINES -DGPU -D_TIMESPEC_DEFINED -D"CMAKE_INTDIR=\"Release\"" -D_MBCS -DWIN32 -D_WINDOWS -DNDEBUG -DUSE_CMAKE_LIBS -D_CRT_RAND_S -DNOMINMAX -D_USE_MATH_DEFINES -DGPU -D_TIMESPEC_DEFINED -D"CMAKE_INTDIR=\"Release\"" -Xcompiler "/EHsc /W1 /nologo /O2 /FS   /MD /GR" -Xcompiler "/Fddarknet.dir\Release\vc143.pdb" -o darknet.dir\Release\activation_kernels.obj "D:\FPGA_Data\darknet\src\activation_kernels.cu"
  Compiling CUDA source file ..\..\src\avgpool_layer_kernels.cu...

  D:\FPGA_Data\darknet\build\s1_t01_vc_cuda134_v2>"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\bin\nvcc.exe"  --use-local-env -ccbin "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.44.35207\bin\HostX64\x64" -x cu   -ID:\FPGA_Data\darknet\include -ID:\FPGA_Data\darknet\src -ID:\FPGA_Data\darknet\3rdparty\stb\include -ID:\FPGA_Data\darknet\3rdparty\getopt -I"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\include" -I"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\include\cccl" -ID:\FPGA_Data\darknet\3rdparty\pthreads\include -I"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\include"     --keep-dir darknet\x64\Release  -maxrregcount=0     --machine 64 --compile -Wno-deprecated-declarations --generate-code=arch=compute_89,code=[compute_89,sm_89] -Xcompiler=",/nologo,/wd4013,/wd4018,/wd4028,/wd4047,/wd4068,/wd4090,/wd4101,/wd4113,/wd4133,/wd4190,/wd4244,/wd4267,/wd4305,/wd4477,/wd4996,/wd4819,/fp:fast,/DGPU /EHsc -Ob2"   -D_WINDOWS -DNDEBUG -DUSE_CMAKE_LIBS -D_CRT_RAND_S -DNOMINMAX -D_USE_MATH_DEFINES -DGPU -D_TIMESPEC_DEFINED -D"CMAKE_INTDIR=\"Release\"" -D_MBCS -DWIN32 -D_WINDOWS -DNDEBUG -DUSE_CMAKE_LIBS -D_CRT_RAND_S -DNOMINMAX -D_USE_MATH_DEFINES -DGPU -D_TIMESPEC_DEFINED -D"CMAKE_INTDIR=\"Release\"" -Xcompiler "/EHsc /W1 /nologo /O2 /FS   /MD /GR" -Xcompiler "/Fddarknet.dir\Release\vc143.pdb" -o darknet.dir\Release\avgpool_layer_kernels.obj "D:\FPGA_Data\darknet\src\avgpool_layer_kernels.cu"
  activation_kernels.cu
  Compiling CUDA source file ..\..\src\blas_kernels.cu...
  avgpool_layer_kernels.cu

  D:\FPGA_Data\darknet\build\s1_t01_vc_cuda134_v2>"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\bin\nvcc.exe"  --use-local-env -ccbin "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.44.35207\bin\HostX64\x64" -x cu   -ID:\FPGA_Data\darknet\include -ID:\FPGA_Data\darknet\src -ID:\FPGA_Data\darknet\3rdparty\stb\include -ID:\FPGA_Data\darknet\3rdparty\getopt -I"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\include" -I"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\include\cccl" -ID:\FPGA_Data\darknet\3rdparty\pthreads\include -I"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\include"     --keep-dir darknet\x64\Release  -maxrregcount=0     --machine 64 --compile -Wno-deprecated-declarations --generate-code=arch=compute_89,code=[compute_89,sm_89] -Xcompiler=",/nologo,/wd4013,/wd4018,/wd4028,/wd4047,/wd4068,/wd4090,/wd4101,/wd4113,/wd4133,/wd4190,/wd4244,/wd4267,/wd4305,/wd4477,/wd4996,/wd4819,/fp:fast,/DGPU /EHsc -Ob2"   -D_WINDOWS -DNDEBUG -DUSE_CMAKE_LIBS -D_CRT_RAND_S -DNOMINMAX -D_USE_MATH_DEFINES -DGPU -D_TIMESPEC_DEFINED -D"CMAKE_INTDIR=\"Release\"" -D_MBCS -DWIN32 -D_WINDOWS -DNDEBUG -DUSE_CMAKE_LIBS -D_CRT_RAND_S -DNOMINMAX -D_USE_MATH_DEFINES -DGPU -D_TIMESPEC_DEFINED -D"CMAKE_INTDIR=\"Release\"" -Xcompiler "/EHsc /W1 /nologo /O2 /FS   /MD /GR" -Xcompiler "/Fddarknet.dir\Release\vc143.pdb" -o darknet.dir\Release\blas_kernels.obj "D:\FPGA_Data\darknet\src\blas_kernels.cu"
  Compiling CUDA source file ..\..\src\col2im_kernels.cu...

  D:\FPGA_Data\darknet\build\s1_t01_vc_cuda134_v2>"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\bin\nvcc.exe"  --use-local-env -ccbin "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.44.35207\bin\HostX64\x64" -x cu   -ID:\FPGA_Data\darknet\include -ID:\FPGA_Data\darknet\src -ID:\FPGA_Data\darknet\3rdparty\stb\include -ID:\FPGA_Data\darknet\3rdparty\getopt -I"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\include" -I"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\include\cccl" -ID:\FPGA_Data\darknet\3rdparty\pthreads\include -I"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\include"     --keep-dir darknet\x64\Release  -maxrregcount=0     --machine 64 --compile -Wno-deprecated-declarations --generate-code=arch=compute_89,code=[compute_89,sm_89] -Xcompiler=",/nologo,/wd4013,/wd4018,/wd4028,/wd4047,/wd4068,/wd4090,/wd4101,/wd4113,/wd4133,/wd4190,/wd4244,/wd4267,/wd4305,/wd4477,/wd4996,/wd4819,/fp:fast,/DGPU /EHsc -Ob2"   -D_WINDOWS -DNDEBUG -DUSE_CMAKE_LIBS -D_CRT_RAND_S -DNOMINMAX -D_USE_MATH_DEFINES -DGPU -D_TIMESPEC_DEFINED -D"CMAKE_INTDIR=\"Release\"" -D_MBCS -DWIN32 -D_WINDOWS -DNDEBUG -DUSE_CMAKE_LIBS -D_CRT_RAND_S -DNOMINMAX -D_USE_MATH_DEFINES -DGPU -D_TIMESPEC_DEFINED -D"CMAKE_INTDIR=\"Release\"" -Xcompiler "/EHsc /W1 /nologo /O2 /FS   /MD /GR" -Xcompiler "/Fddarknet.dir\Release\vc143.pdb" -o darknet.dir\Release\col2im_kernels.obj "D:\FPGA_Data\darknet\src\col2im_kernels.cu"
  col2im_kernels.cu
  Compiling CUDA source file ..\..\src\convolutional_kernels.cu...

  D:\FPGA_Data\darknet\build\s1_t01_vc_cuda134_v2>"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\bin\nvcc.exe"  --use-local-env -ccbin "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.44.35207\bin\HostX64\x64" -x cu   -ID:\FPGA_Data\darknet\include -ID:\FPGA_Data\darknet\src -ID:\FPGA_Data\darknet\3rdparty\stb\include -ID:\FPGA_Data\darknet\3rdparty\getopt -I"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\include" -I"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\include\cccl" -ID:\FPGA_Data\darknet\3rdparty\pthreads\include -I"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\include"     --keep-dir darknet\x64\Release  -maxrregcount=0     --machine 64 --compile -Wno-deprecated-declarations --generate-code=arch=compute_89,code=[compute_89,sm_89] -Xcompiler=",/nologo,/wd4013,/wd4018,/wd4028,/wd4047,/wd4068,/wd4090,/wd4101,/wd4113,/wd4133,/wd4190,/wd4244,/wd4267,/wd4305,/wd4477,/wd4996,/wd4819,/fp:fast,/DGPU /EHsc -Ob2"   -D_WINDOWS -DNDEBUG -DUSE_CMAKE_LIBS -D_CRT_RAND_S -DNOMINMAX -D_USE_MATH_DEFINES -DGPU -D_TIMESPEC_DEFINED -D"CMAKE_INTDIR=\"Release\"" -D_MBCS -DWIN32 -D_WINDOWS -DNDEBUG -DUSE_CMAKE_LIBS -D_CRT_RAND_S -DNOMINMAX -D_USE_MATH_DEFINES -DGPU -D_TIMESPEC_DEFINED -D"CMAKE_INTDIR=\"Release\"" -Xcompiler "/EHsc /W1 /nologo /O2 /FS   /MD /GR" -Xcompiler "/Fddarknet.dir\Release\vc143.pdb" -o darknet.dir\Release\convolutional_kernels.obj "D:\FPGA_Data\darknet\src\convolutional_kernels.cu"
  blas_kernels.cu
  Compiling CUDA source file ..\..\src\crop_layer_kernels.cu...

  D:\FPGA_Data\darknet\build\s1_t01_vc_cuda134_v2>"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\bin\nvcc.exe"  --use-local-env -ccbin "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.44.35207\bin\HostX64\x64" -x cu   -ID:\FPGA_Data\darknet\include -ID:\FPGA_Data\darknet\src -ID:\FPGA_Data\darknet\3rdparty\stb\include -ID:\FPGA_Data\darknet\3rdparty\getopt -I"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\include" -I"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\include\cccl" -ID:\FPGA_Data\darknet\3rdparty\pthreads\include -I"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\include"     --keep-dir darknet\x64\Release  -maxrregcount=0     --machine 64 --compile -Wno-deprecated-declarations --generate-code=arch=compute_89,code=[compute_89,sm_89] -Xcompiler=",/nologo,/wd4013,/wd4018,/wd4028,/wd4047,/wd4068,/wd4090,/wd4101,/wd4113,/wd4133,/wd4190,/wd4244,/wd4267,/wd4305,/wd4477,/wd4996,/wd4819,/fp:fast,/DGPU /EHsc -Ob2"   -D_WINDOWS -DNDEBUG -DUSE_CMAKE_LIBS -D_CRT_RAND_S -DNOMINMAX -D_USE_MATH_DEFINES -DGPU -D_TIMESPEC_DEFINED -D"CMAKE_INTDIR=\"Release\"" -D_MBCS -DWIN32 -D_WINDOWS -DNDEBUG -DUSE_CMAKE_LIBS -D_CRT_RAND_S -DNOMINMAX -D_USE_MATH_DEFINES -DGPU -D_TIMESPEC_DEFINED -D"CMAKE_INTDIR=\"Release\"" -Xcompiler "/EHsc /W1 /nologo /O2 /FS   /MD /GR" -Xcompiler "/Fddarknet.dir\Release\vc143.pdb" -o darknet.dir\Release\crop_layer_kernels.obj "D:\FPGA_Data\darknet\src\crop_layer_kernels.cu"
  convolutional_kernels.cu
  Compiling CUDA source file ..\..\src\deconvolutional_kernels.cu...

  D:\FPGA_Data\darknet\build\s1_t01_vc_cuda134_v2>"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\bin\nvcc.exe"  --use-local-env -ccbin "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.44.35207\bin\HostX64\x64" -x cu   -ID:\FPGA_Data\darknet\include -ID:\FPGA_Data\darknet\src -ID:\FPGA_Data\darknet\3rdparty\stb\include -ID:\FPGA_Data\darknet\3rdparty\getopt -I"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\include" -I"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\include\cccl" -ID:\FPGA_Data\darknet\3rdparty\pthreads\include -I"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\include"     --keep-dir darknet\x64\Release  -maxrregcount=0     --machine 64 --compile -Wno-deprecated-declarations --generate-code=arch=compute_89,code=[compute_89,sm_89] -Xcompiler=",/nologo,/wd4013,/wd4018,/wd4028,/wd4047,/wd4068,/wd4090,/wd4101,/wd4113,/wd4133,/wd4190,/wd4244,/wd4267,/wd4305,/wd4477,/wd4996,/wd4819,/fp:fast,/DGPU /EHsc -Ob2"   -D_WINDOWS -DNDEBUG -DUSE_CMAKE_LIBS -D_CRT_RAND_S -DNOMINMAX -D_USE_MATH_DEFINES -DGPU -D_TIMESPEC_DEFINED -D"CMAKE_INTDIR=\"Release\"" -D_MBCS -DWIN32 -D_WINDOWS -DNDEBUG -DUSE_CMAKE_LIBS -D_CRT_RAND_S -DNOMINMAX -D_USE_MATH_DEFINES -DGPU -D_TIMESPEC_DEFINED -D"CMAKE_INTDIR=\"Release\"" -Xcompiler "/EHsc /W1 /nologo /O2 /FS   /MD /GR" -Xcompiler "/Fddarknet.dir\Release\vc143.pdb" -o darknet.dir\Release\deconvolutional_kernels.obj "D:\FPGA_Data\darknet\src\deconvolutional_kernels.cu"
  crop_layer_kernels.cu
  Compiling CUDA source file ..\..\src\dropout_layer_kernels.cu...

  D:\FPGA_Data\darknet\build\s1_t01_vc_cuda134_v2>"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\bin\nvcc.exe"  --use-local-env -ccbin "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.44.35207\bin\HostX64\x64" -x cu   -ID:\FPGA_Data\darknet\include -ID:\FPGA_Data\darknet\src -ID:\FPGA_Data\darknet\3rdparty\stb\include -ID:\FPGA_Data\darknet\3rdparty\getopt -I"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\include" -I"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\include\cccl" -ID:\FPGA_Data\darknet\3rdparty\pthreads\include -I"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\include"     --keep-dir darknet\x64\Release  -maxrregcount=0     --machine 64 --compile -Wno-deprecated-declarations --generate-code=arch=compute_89,code=[compute_89,sm_89] -Xcompiler=",/nologo,/wd4013,/wd4018,/wd4028,/wd4047,/wd4068,/wd4090,/wd4101,/wd4113,/wd4133,/wd4190,/wd4244,/wd4267,/wd4305,/wd4477,/wd4996,/wd4819,/fp:fast,/DGPU /EHsc -Ob2"   -D_WINDOWS -DNDEBUG -DUSE_CMAKE_LIBS -D_CRT_RAND_S -DNOMINMAX -D_USE_MATH_DEFINES -DGPU -D_TIMESPEC_DEFINED -D"CMAKE_INTDIR=\"Release\"" -D_MBCS -DWIN32 -D_WINDOWS -DNDEBUG -DUSE_CMAKE_LIBS -D_CRT_RAND_S -DNOMINMAX -D_USE_MATH_DEFINES -DGPU -D_TIMESPEC_DEFINED -D"CMAKE_INTDIR=\"Release\"" -Xcompiler "/EHsc /W1 /nologo /O2 /FS   /MD /GR" -Xcompiler "/Fddarknet.dir\Release\vc143.pdb" -o darknet.dir\Release\dropout_layer_kernels.obj "D:\FPGA_Data\darknet\src\dropout_layer_kernels.cu"
  deconvolutional_kernels.cu
  Compiling CUDA source file ..\..\src\im2col_kernels.cu...

  D:\FPGA_Data\darknet\build\s1_t01_vc_cuda134_v2>"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\bin\nvcc.exe"  --use-local-env -ccbin "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.44.35207\bin\HostX64\x64" -x cu   -ID:\FPGA_Data\darknet\include -ID:\FPGA_Data\darknet\src -ID:\FPGA_Data\darknet\3rdparty\stb\include -ID:\FPGA_Data\darknet\3rdparty\getopt -I"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\include" -I"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\include\cccl" -ID:\FPGA_Data\darknet\3rdparty\pthreads\include -I"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\include"     --keep-dir darknet\x64\Release  -maxrregcount=0     --machine 64 --compile -Wno-deprecated-declarations --generate-code=arch=compute_89,code=[compute_89,sm_89] -Xcompiler=",/nologo,/wd4013,/wd4018,/wd4028,/wd4047,/wd4068,/wd4090,/wd4101,/wd4113,/wd4133,/wd4190,/wd4244,/wd4267,/wd4305,/wd4477,/wd4996,/wd4819,/fp:fast,/DGPU /EHsc -Ob2"   -D_WINDOWS -DNDEBUG -DUSE_CMAKE_LIBS -D_CRT_RAND_S -DNOMINMAX -D_USE_MATH_DEFINES -DGPU -D_TIMESPEC_DEFINED -D"CMAKE_INTDIR=\"Release\"" -D_MBCS -DWIN32 -D_WINDOWS -DNDEBUG -DUSE_CMAKE_LIBS -D_CRT_RAND_S -DNOMINMAX -D_USE_MATH_DEFINES -DGPU -D_TIMESPEC_DEFINED -D"CMAKE_INTDIR=\"Release\"" -Xcompiler "/EHsc /W1 /nologo /O2 /FS   /MD /GR" -Xcompiler "/Fddarknet.dir\Release\vc143.pdb" -o darknet.dir\Release\im2col_kernels.obj "D:\FPGA_Data\darknet\src\im2col_kernels.cu"
  dropout_layer_kernels.cu
  Compiling CUDA source file ..\..\src\maxpool_layer_kernels.cu...

  D:\FPGA_Data\darknet\build\s1_t01_vc_cuda134_v2>"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\bin\nvcc.exe"  --use-local-env -ccbin "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.44.35207\bin\HostX64\x64" -x cu   -ID:\FPGA_Data\darknet\include -ID:\FPGA_Data\darknet\src -ID:\FPGA_Data\darknet\3rdparty\stb\include -ID:\FPGA_Data\darknet\3rdparty\getopt -I"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\include" -I"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\include\cccl" -ID:\FPGA_Data\darknet\3rdparty\pthreads\include -I"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\include"     --keep-dir darknet\x64\Release  -maxrregcount=0     --machine 64 --compile -Wno-deprecated-declarations --generate-code=arch=compute_89,code=[compute_89,sm_89] -Xcompiler=",/nologo,/wd4013,/wd4018,/wd4028,/wd4047,/wd4068,/wd4090,/wd4101,/wd4113,/wd4133,/wd4190,/wd4244,/wd4267,/wd4305,/wd4477,/wd4996,/wd4819,/fp:fast,/DGPU /EHsc -Ob2"   -D_WINDOWS -DNDEBUG -DUSE_CMAKE_LIBS -D_CRT_RAND_S -DNOMINMAX -D_USE_MATH_DEFINES -DGPU -D_TIMESPEC_DEFINED -D"CMAKE_INTDIR=\"Release\"" -D_MBCS -DWIN32 -D_WINDOWS -DNDEBUG -DUSE_CMAKE_LIBS -D_CRT_RAND_S -DNOMINMAX -D_USE_MATH_DEFINES -DGPU -D_TIMESPEC_DEFINED -D"CMAKE_INTDIR=\"Release\"" -Xcompiler "/EHsc /W1 /nologo /O2 /FS   /MD /GR" -Xcompiler "/Fddarknet.dir\Release\vc143.pdb" -o darknet.dir\Release\maxpool_layer_kernels.obj "D:\FPGA_Data\darknet\src\maxpool_layer_kernels.cu"
  im2col_kernels.cu
  maxpool_layer_kernels.cu
  Compiling CUDA source file ..\..\src\network_kernels.cu...

  D:\FPGA_Data\darknet\build\s1_t01_vc_cuda134_v2>"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\bin\nvcc.exe"  --use-local-env -ccbin "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.44.35207\bin\HostX64\x64" -x cu   -ID:\FPGA_Data\darknet\include -ID:\FPGA_Data\darknet\src -ID:\FPGA_Data\darknet\3rdparty\stb\include -ID:\FPGA_Data\darknet\3rdparty\getopt -I"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\include" -I"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\include\cccl" -ID:\FPGA_Data\darknet\3rdparty\pthreads\include -I"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\include"     --keep-dir darknet\x64\Release  -maxrregcount=0     --machine 64 --compile -Wno-deprecated-declarations --generate-code=arch=compute_89,code=[compute_89,sm_89] -Xcompiler=",/nologo,/wd4013,/wd4018,/wd4028,/wd4047,/wd4068,/wd4090,/wd4101,/wd4113,/wd4133,/wd4190,/wd4244,/wd4267,/wd4305,/wd4477,/wd4996,/wd4819,/fp:fast,/DGPU /EHsc -Ob2"   -D_WINDOWS -DNDEBUG -DUSE_CMAKE_LIBS -D_CRT_RAND_S -DNOMINMAX -D_USE_MATH_DEFINES -DGPU -D_TIMESPEC_DEFINED -D"CMAKE_INTDIR=\"Release\"" -D_MBCS -DWIN32 -D_WINDOWS -DNDEBUG -DUSE_CMAKE_LIBS -D_CRT_RAND_S -DNOMINMAX -D_USE_MATH_DEFINES -DGPU -D_TIMESPEC_DEFINED -D"CMAKE_INTDIR=\"Release\"" -Xcompiler "/EHsc /W1 /nologo /O2 /FS   /MD /GR" -Xcompiler "/Fddarknet.dir\Release\vc143.pdb" -o darknet.dir\Release\network_kernels.obj "D:\FPGA_Data\darknet\src\network_kernels.cu"
  network_kernels.cu
  darknet.c
  activation_layer.c
  activations.c
  art.c
  avgpool_layer.c
  batchnorm_layer.c
  blas.c
  box.c
  captcha.c
  cifar.c
  classifier.c
  coco.c
  col2im.c
  compare.c
  connected_layer.c
  conv_lstm_layer.c
  convolutional_layer.c
  cost_layer.c
  cpu_gemm.c
  crnn_layer.c
  正在生成代码...
  正在编译...
  crop_layer.c
  dark_cuda.c
  data.c
  deconvolutional_layer.c
  demo.c
D:\FPGA_Data\darknet\src\dark_cuda.c(252,18): warning C5287: 操作数是不同的枚举类型“cudaError”和“cudaError_enum”；请使用显式强制转换来静音此警告 [D:\FPGA_Data\darknet\build\s1_t01_vc_cuda134_v2\darknet.vcxproj]
  detection_layer.c
  detector.c
  dice.c
  dropout_layer.c
  gaussian_yolo_layer.c
  gemm.c
  gettimeofday.c
  go.c
  gru_layer.c
  im2col.c
  image.c
  layer.c
  list.c
  local_layer.c
  lstm_layer.c
  正在生成代码...
  正在编译...
  matrix.c
  maxpool_layer.c
  network.c
  nightmare.c
  normalization_layer.c
  option_list.c
  parser.c
  region_layer.c
  reorg_layer.c
  reorg_old_layer.c
  representation_layer.c
  rnn.c
  rnn_layer.c
  rnn_vid.c
  route_layer.c
  sam_layer.c
  scale_channels_layer.c
  shortcut_layer.c
  softmax_layer.c
  super.c
  正在生成代码...
  正在编译...
  swag.c
  tag.c
  tree.c
  upsample_layer.c
  utils.c
  voxel.c
  writing.c
  yolo.c
  yolo_layer.c
  getopt.c
  正在生成代码...
  http_stream.cpp
  image_opencv.cpp
  正在生成代码...
  darknet.vcxproj -> D:\FPGA_Data\darknet\build\s1_t01_vc_cuda134_v2\Release\darknet.exe

stderr:
