timestamp_utc8=2026-09-15T16:19:07.0939282+08:00
working_directory=D:\FPGA_Data\darknet
build_directory=D:\FPGA_Data\darknet\build\s1_t01_vc_cuda134_v2
vcvars64=C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat
CUDA_PATH=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4
CUDA_PATH_V13_4=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4
CUDACXX=nvcc.exe
command=C:\Espressif\tools\cmake\3.30.2\bin\cmake.exe -S D:\FPGA_Data\darknet -B D:\FPGA_Data\darknet\build\s1_t01_vc_cuda134_v2 -G "Visual Studio 17 2022" -T cuda=13.4 -A x64 -DENABLE_CUDA=ON -DENABLE_CUDA_OPENGL_INTEGRATION=OFF -DENABLE_CUDNN=OFF -DENABLE_CUDNN_HALF=OFF -DENABLE_OPENCV=OFF -DBUILD_SHARED_LIBS=OFF -DBUILD_USELIB_TRACK=OFF -DCMAKE_CUDA_ARCHITECTURES=89
stdout_log=D:\FPGA_Competition\report\evidence\S1-T01\20260915_darknet_cmake_reconfigure.stdout.log
stderr_log=D:\FPGA_Competition\report\evidence\S1-T01\20260915_darknet_cmake_reconfigure.stderr.log
exit_code=0
stdout:
-- vcpkg not found, toolchain not defined, using integrated libs on win32
-- Selecting Windows SDK version 10.0.26100.0 to target Windows 10.0.26200.
-- Selected CMAKE_CUDA_ARCHITECTURES: 89
-- Your setup does not support half precision (it requires CUDA_ARCHITECTURES >= 70)
-- PThreads4W_DLL_DIR: D:/FPGA_Data/darknet/3rdparty/pthreads/include/../bin
-- CMAKE_CUDA_FLAGS:  -Wno-deprecated-declarations -Xcompiler=",/nologo,/wd4013,/wd4018,/wd4028,/wd4047,/wd4068,/wd4090,/wd4101,/wd4113,/wd4133,/wd4190,/wd4244,/wd4267,/wd4305,/wd4477,/wd4996,/wd4819,/fp:fast,/DGPU" -D_WINDOWS -Xcompiler=" /GR /EHsc"
-- Configuring done (0.2s)
-- Generating done (0.1s)
-- Build files have been written to: D:/FPGA_Data/darknet/build/s1_t01_vc_cuda134_v2

stderr:
Darknet_VERSION: 0.2.5.7
