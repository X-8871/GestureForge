timestamp_utc8=2026-09-15T16:10:08.5886602+08:00
working_directory=D:\FPGA_Data\darknet
build_directory=D:\FPGA_Data\darknet\build\s1_t01_vc_cuda134
vcvars64=C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat
CUDA_PATH=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4
CUDACXX=nvcc.exe
command=C:\Espressif\tools\cmake\3.30.2\bin\cmake.exe -S D:\FPGA_Data\darknet -B D:\FPGA_Data\darknet\build\s1_t01_vc_cuda134 -G "Visual Studio 17 2022" -T cuda=13.4 -A x64 -DENABLE_CUDA=ON -DENABLE_CUDNN=OFF -DENABLE_CUDNN_HALF=OFF -DENABLE_OPENCV=OFF -DBUILD_SHARED_LIBS=OFF -DBUILD_USELIB_TRACK=OFF -DCMAKE_CUDA_ARCHITECTURES=89
stdout_log=D:\FPGA_Competition\report\evidence\S1-T01\20260915_darknet_cmake_configure_cuda134.stdout.log
stderr_log=D:\FPGA_Competition\report\evidence\S1-T01\20260915_darknet_cmake_configure_cuda134.stderr.log
exit_code=1
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
-- Looking for a CUDA compiler - NOTFOUND
-- CUDA_PATH: C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4
-- CUDACXX: nvcc.exe
-- Configuring incomplete, errors occurred!

stderr:
Darknet_VERSION: 0.2.5.7
CMake Error at CMakeLists.txt:185 (message):
  CUDA not found, please build explicitly with -DENABLE_CUDA=OFF if you do
  not want CUDA.
