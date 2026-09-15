timestamp_utc8=2026-09-15T16:08:57.9601798+08:00
working_directory=D:\FPGA_Data\darknet
build_directory=D:\FPGA_Data\darknet\build\s1_t01_vc
vcvars64=C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat
command=C:\Espressif\tools\cmake\3.30.2\bin\cmake.exe -S D:\FPGA_Data\darknet -B D:\FPGA_Data\darknet\build\s1_t01_vc -G "Visual Studio 17 2022" -A x64 -DENABLE_CUDA=ON -DENABLE_CUDNN=OFF -DENABLE_CUDNN_HALF=OFF -DENABLE_OPENCV=OFF -DBUILD_SHARED_LIBS=OFF -DBUILD_USELIB_TRACK=OFF -DCMAKE_CUDA_ARCHITECTURES=89 -DCMAKE_CUDA_COMPILER= C:\PROGRA~1\NVIDIA~2\CUDA\v13.4\bin\nvcc.exe -DCMAKE_CUDA_HOST_COMPILER= C:\PROGRA~2\MICROS~3\2022\BUILDT~1\VC\Tools\MSVC\1444~1.352\bin\Hostx64\x64\cl.exe
stdout_log=D:\FPGA_Competition\report\evidence\S1-T01\20260915_darknet_cmake_configure_v3.stdout.log
stderr_log=D:\FPGA_Competition\report\evidence\S1-T01\20260915_darknet_cmake_configure_v3.stderr.log
exit_code=1
stdout:
-- vcpkg not found, toolchain not defined, using integrated libs on win32
-- Selecting Windows SDK version 10.0.26100.0 to target Windows 10.0.26200.
-- CUDA_PATH: C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4
-- CUDACXX: C:\PROGRA~1\NVIDIA~2\CUDA\v13.4\bin\nvcc.exe
-- Configuring incomplete, errors occurred!

stderr:
CMake Warning:
  Ignoring extra path from command line:

   "C:\PROGRA~2\MICROS~3\2022\BUILDT~1\VC\Tools\MSVC\1444~1.352\bin\Hostx64\x64\cl.exe"


Darknet_VERSION: 0.2.5.7
CMake Error at CMakeLists.txt:185 (message):
  CUDA not found, please build explicitly with -DENABLE_CUDA=OFF if you do
  not want CUDA.
