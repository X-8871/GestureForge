$ErrorActionPreference='Continue'
Remove-Item Env:SHELL -ErrorAction SilentlyContinue
Remove-Item Env:MSYSTEM -ErrorAction SilentlyContinue
Remove-Item Env:MSYS2_PATH_TYPE -ErrorAction SilentlyContinue
$env:HOME='D:\FPGA_Competition\report\evidence\S2A-T66\weightcap_boundary_4608_20261006\msys_env_home'
$env:PATH='D:\FPGA_S2A_MSYS2_20261001\env\usr\bin;D:\FPGA_S2A_MSYS2_20261001\env\mingw64\bin;'+$env:PATH
& 'D:\FPGA_S2A_MSYS2_20261001\env\usr\bin\sh.exe' -c 'echo PATH=$PATH; command -v uname; command -v g++; uname -a; g++ --version; printf "int main(){}" | g++ -std=c++20 -fcoroutines -x c++ -c -o /dev/null -'