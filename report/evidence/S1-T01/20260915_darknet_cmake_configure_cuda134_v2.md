timestamp_utc8=2026-09-15T16:11:26.8495144+08:00
working_directory=D:\FPGA_Data\darknet
build_directory=D:\FPGA_Data\darknet\build\s1_t01_vc_cuda134_v2
vcvars64=C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat
CUDA_PATH=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4
CUDA_PATH_V13_4=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4
CUDACXX=nvcc.exe
command=C:\Espressif\tools\cmake\3.30.2\bin\cmake.exe -S D:\FPGA_Data\darknet -B D:\FPGA_Data\darknet\build\s1_t01_vc_cuda134_v2 -G "Visual Studio 17 2022" -T cuda=13.4 -A x64 -DENABLE_CUDA=ON -DENABLE_CUDNN=OFF -DENABLE_CUDNN_HALF=OFF -DENABLE_OPENCV=OFF -DBUILD_SHARED_LIBS=OFF -DBUILD_USELIB_TRACK=OFF -DCMAKE_CUDA_ARCHITECTURES=89
stdout_log=D:\FPGA_Competition\report\evidence\S1-T01\20260915_darknet_cmake_configure_cuda134_v2.stdout.log
stderr_log=D:\FPGA_Competition\report\evidence\S1-T01\20260915_darknet_cmake_configure_cuda134_v2.stderr.log
exit_code=0
stdout:
-- vcpkg not found, toolchain not defined, using integrated libs on win32
-- Selecting Windows SDK version 10.0.26100.0 to target Windows 10.0.26200.
-- The C compiler identification is MSVC 19.44.35228.0
-- The CXX compiler identification is MSVC 19.44.35228.0
-- Detecting C compiler ABI info
-- Detecting C compiler ABI info - done
-- Check for working C compiler: C:/Program Files (x86)/Microsoft Visual Studio/2022/BuildTools/VC/Tools/MSVC/14.44.35207/bin/Hostx64/x64/cl.exe - skipped
-- Detecting C compile features
-- Detecting C compile features - done
-- Detecting CXX compiler ABI info
-- Detecting CXX compiler ABI info - done
-- Check for working CXX compiler: C:/Program Files (x86)/Microsoft Visual Studio/2022/BuildTools/VC/Tools/MSVC/14.44.35207/bin/Hostx64/x64/cl.exe - skipped
-- Detecting CXX compile features
-- Detecting CXX compile features - done
-- Looking for a CUDA compiler
-- Looking for a CUDA compiler - C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v13.4/bin/nvcc.exe
-- The CUDA compiler identification is NVIDIA 13.4.59
-- Detecting CUDA compiler ABI info
-- Detecting CUDA compiler ABI info - done
-- Check for working CUDA compiler: C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v13.4/bin/nvcc.exe - skipped
-- Detecting CUDA compile features
-- Detecting CUDA compile features - done
-- Selected CMAKE_CUDA_ARCHITECTURES: 89
-- Your setup does not support half precision (it requires CUDA_ARCHITECTURES >= 70)
-- Performing Test CMAKE_HAVE_LIBC_PTHREAD
-- Performing Test CMAKE_HAVE_LIBC_PTHREAD - Failed
-- Looking for pthread_create in pthreads
-- Looking for pthread_create in pthreads - not found
-- Looking for pthread_create in pthread
-- Looking for pthread_create in pthread - not found
-- Found Threads: TRUE
-- Found PThreads4W: D:/FPGA_Data/darknet/3rdparty/pthreads/lib/pthreadVC2.lib
-- PThreads4W_DLL_DIR: D:/FPGA_Data/darknet/3rdparty/pthreads/include/../bin
-- Found Stb: D:/FPGA_Data/darknet/3rdparty/stb/include
-- Found OpenMP_C: -openmp (found version "2.0")
-- Found OpenMP_CXX: -openmp (found version "2.0")
-- Found OpenMP: TRUE (found version "2.0")
-- CMAKE_CUDA_FLAGS:  -Wno-deprecated-declarations -Xcompiler=",/nologo,/wd4013,/wd4018,/wd4028,/wd4047,/wd4068,/wd4090,/wd4101,/wd4113,/wd4133,/wd4190,/wd4244,/wd4267,/wd4305,/wd4477,/wd4996,/wd4819,/fp:fast,/DGPU,/DCUDA_OPENGL_INTEGRATION" -D_WINDOWS -Xcompiler=" /GR /EHsc"
-- Configuring done (33.5s)
-- Generating done (0.1s)
-- Build files have been written to: D:/FPGA_Data/darknet/build/s1_t01_vc_cuda134_v2

stderr:
Darknet_VERSION: 0.2.5.7
