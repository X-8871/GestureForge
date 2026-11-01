$ErrorActionPreference='Continue'
Remove-Item Env:SHELL -ErrorAction SilentlyContinue
$env:HOME='D:\FPGA_Competition\report\evidence\S2A-T66\weightcap_boundary_4608_20261006\msys_env_home'
$env:MSYSTEM='MINGW64'
$env:MSYS2_PATH_TYPE='inherit'
$env:PATH='D:\FPGA_S2A_MSYS2_20261001\env\usr\bin;D:\FPGA_S2A_MSYS2_20261001\env\mingw64\bin;'+$env:PATH
$env:VERILATOR_ROOT='D:\FPGA_S2A_MSYS2_20261001\env\mingw64\share\verilator'
& 'D:\FPGA_S2A_MSYS2_20261001\env\usr\bin\sh.exe' -c 'echo PATH=$PATH; command -v uname; command -v g++; uname -a; g++ --version; printf "int main(){}" | g++ -std=c++20 -fcoroutines -x c++ -c -o /dev/null -'