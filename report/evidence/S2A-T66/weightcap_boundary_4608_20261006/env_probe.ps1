$ErrorActionPreference='Continue'
$env:PATH='D:\FPGA_S2A_MSYS2_20261001\env\usr\bin;D:\FPGA_S2A_MSYS2_20261001\env\mingw64\bin;'+$env:PATH
$env:VERILATOR_ROOT='D:\FPGA_S2A_MSYS2_20261001\env\mingw64\share\verilator'
Get-Command g++.exe, make.exe, uname.exe, sh.exe -All | Select-Object Name,Source | Format-Table -AutoSize
& 'D:\FPGA_S2A_MSYS2_20261001\env\usr\bin\uname.exe' -a
& 'D:\FPGA_S2A_MSYS2_20261001\env\usr\bin\sh.exe' -lc 'which g++; g++ --version; which uname; uname -a'
& 'D:\FPGA_S2A_MSYS2_20261001\env\mingw64\bin\g++.exe' -fcoroutines -x c++ -c -o NUL - <<< 'int main(){}'