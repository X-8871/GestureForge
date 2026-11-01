@echo off
rem #
rem # COPYRIGHT NOTICE
rem # Copyright 1986-1999, 2001-2018 Xilinx, Inc. All Rights Reserved.
rem # Copyright (c) 2022-2026 Advanced Micro Devices, Inc. All rights reserved.
rem #
set RDI_EXIT=

setlocal enableextensions enabledelayedexpansion

rem # RDI_ARGS_FUNCTION must be cleared here, otherwise child
rem # planAhead processes will inherit the parent's args.
set RDI_ARGS_FUNCTION=

rem # to fix HLS debug from Vivado

set PYTHONPATH=
set PYTHONHOME=
 

 call "%~dp0/setupEnv.bat"

if defined _RDI_SETENV_RUN (
  set _RDI_SETENV_RUN=
)

set _RDI_DONT_SET_XILINX_AS_PATH=True
set XIL_NO_OVERRIDE=0
set XIL_SUPPRESS_OVERRIDE_WARNINGS=1
set RDI_NO_JRE=1
set RDI_USE_JDK11=1

if defined RDI_EXIT (
  goto :EOF
)

set RDI_OS_ARCH=64
set RDI_OPT_EXT=.o

rem #
rem # If True check for the existence of RDI_PROG prior to calling into
rem # rdiArgs.bat
rem #
set RDI_CHECK_PROG=True
set RDI_TEMPINSTALL=%RDI_BASEROOT:/=\%
for %%A in ("%RDI_TEMPINSTALL%") do set RDI_INSTALLVERSION=%%~nxA
if not defined XILINX_VIVADO if exist "%RDI_INSTALLROOT%/%RDI_INSTALLVERSION%/Vivado" (
  set XILINX_VIVADO=%RDI_INSTALLROOT%/%RDI_INSTALLVERSION%/Vivado
)

set XILINX_VITIS=%RDI_APPROOT%

set XILINX_VITIS_VERSION=UnknownVersion
if exist "%RDI_BINROOT%/unwrapped/win64.o/prodversion.exe" (
    for /F "delims=" %%i in ('%RDI_BINROOT%/loader.bat -exec prodversion Vitis') do set XILINX_VITIS_VERSION=%%i
)
if exist "%RDI_APPROOT%/data/version.bat" (
  call "%RDI_APPROOT%/data/version.bat"
)

if exist "%RDI_INSTALLROOT%/Vitis/%RDI_INSTALLVER%" (
  set XILINX_VITIS=%RDI_INSTALLROOT%/Vitis/%RDI_INSTALLVER%
)

if exist "%RDI_INSTALLROOT%/Vivado/%RDI_INSTALLVER%" (
  set PATH=%XILINX_VIVADO%/bin;!PATH!
)

if not defined XILINX_HLS (
  if exist "%XILINX_VITIS%/data/hls" (    
    set XILINX_HLS=%XILINX_VITIS%
  )
)

if not defined XILINX_VITIS_AIETOOLS (
  if exist "%XILINX_VITIS%/aietools" (
    set XILINX_VITIS_AIETOOLS=%XILINX_VITIS%/aietools
  )
)

rem Find all tool/tps location (check Vivado then Vitis)
set TOOLS_CLANGD=%RDI_APPROOT%\win64\tools\clang-16\bin

if not defined XILINX_VITIS_GDB (
  rem XILINX_VITIS_GDB is used within IDE code
  set XILINX_VITIS_GDB=%XILINX_VITIS%\tps\win64\gdb-16.3
  if not exist "%XILINX_VITIS_GDB%" set XILINX_VITIS_GDB=
)

set tooldir=tps\win64\jre24.0.2_12
set JAVA_HOME=%XILINX_VIVADO%\%tooldir%
if not exist "%JAVA_HOME%" set JAVA_HOME=%XILINX_VITIS%\%tooldir%

set tooldir=tps\win64\libxslt
set TPS_LIBXSLT=%XILINX_VIVADO%\%tooldir%
if not exist "%TPS_LIBXSLT%" set TPS_LIBXSLT=%XILINX_VITIS%\%tooldir%

set tooldir=tps\win64\python-3.13.0
set TPS_PYTHON=%XILINX_VIVADO%\%tooldir%
if not exist "%TPS_PYTHON%" set TPS_PYTHON=%XILINX_VITIS%\%tooldir%

set tooldir=tps\win64\cmake-4.0.1
set TPS_CMAKE=%XILINX_VIVADO%\%tooldir%
if not exist "%TPS_CMAKE%" set TPS_CMAKE=%XILINX_VITIS%\%tooldir%

set tooldir=tps\win64\git-2.53.0
set TPS_GIT=%XILINX_VIVADO%\tps\win64\git-2.53.0
if not exist "%TPS_GIT%" set TPS_GIT=%XILINX_VITIS%\%tooldir%

if defined XILINX_HLS if not [%XILINX_HLS%] == [%XILINX_VITIS%] (
  set PATH=%XILINX_HLS%\bin;!PATH!
  set PATH=%XILINX_HLS%\lib\win64.o;!PATH!
)

set PATH=%XILINX_VITIS%/bin;!PATH!
if exist "%TPS_LIBXSLT%" set PATH=%TPS_LIBXSLT%/bin;!PATH!
set PATH=%XILINX_VITIS%/lib/win64.o;!PATH!

if defined VITIS_IDE_USER_TOOLCHAIN (
  set PATH=%VITIS_IDE_USER_TOOLCHAIN%;!PATH!
)

set NOSPLASH=false
set VITISNEW=true

set args=%*
set arr.length=0

for %%I in (%args%) do (
  set val=%%I
  set arr[!arr.length!]=!val:"=!
  if not %%I == -classic (
    if not %%I == --classic (
      set args_for_classic=!args_for_classic! !val:"=!
    )
  )
  
  if not %%I == -s (
    if not %%I == --source (
      set args_for_source=!args_for_source! !val:"=!
    )
  )
  
  set /a arr.length=!arr.length! + 1
)

set /a arr.Ubound=%arr.length% - 1
for /L %%I in (0, 1, %arr.Ubound%) do (
  if !arr[%%I]! == -nosplash (
    set NOSPLASH=true
    @REM GOTO:doneProcessing
  ) else if !arr[%%I]! == -i (
    set INTERACTIVE=true
    goto doneProcessing
  ) else if !arr[%%I]! == --interactive (
    set INTERACTIVE=true
    goto doneProcessing
  ) else if !arr[%%I]! == -s (
    set SOURCE=true
    call set /a n=%%I+1
    goto SOURCEFILE
  ) else if !arr[%%I]! == --source (
    set SOURCE=true
    call set /a n=%%I+1
    goto SOURCEFILE     
  ) else if !arr[%%I]! == -w (
    set WORKSPACE=true
    call set /a dirIndex=%%I+1
    goto WORKSPACEDIR
  ) else if !arr[%%I]! == --workspace (
    set WORKSPACE=true
    call set /a dirIndex=%%I+1
    goto WORKSPACEDIR
  ) else if !arr[%%I]! == -h (
    goto HELP
  ) else if !arr[%%I]! == --help (
    goto HELP
  ) else if !arr[%%I]! == -new (
    echo "Error: -new option is not supported by vitis."
    echo "The default IDE is the new Unified Vitis IDE."
    exit /b 1
  ) else if !arr[%%I]! == -classic (
    echo "Error: -classic option is not supported by vitis."
    echo "The default IDE is the new Unified Vitis IDE."
    exit /b 1
  )else if !arr[%%I]! == --classic (
    echo "Error: --classic option is not supported by vitis."
    echo "The default IDE is the new Unified Vitis IDE."
    exit /b 1
  )else if !arr[%%I]! == -v (
   goto echoData
  )else if !arr[%%I]! == --version (
   goto echoData
  )else (
    echo.
    echo Error: Unsupported option !arr[%%I]!
    echo Please provide a valid option to continue.
    echo.
    goto HELP
  )
)

:SOURCEFILE
set sourceFile=!arr[%n%]!
for %%A in ("!sourceFile!") do (
  set "sourceWithoutExtension=%%~nA"
)

:WORKSPACEDIR
set workspaceDir=!arr[%dirIndex%]!

:doneProcessing
if [!NOSPLASH!] == [true] (
  GOTO:launch
)

echo.
echo ****** Xilinx Vitis Development Environment
echo ****** %XILINX_VITIS_VERSION%
echo|set /p="****** " || cmd /c "exit /b 0"
rem # Need to pass args, in particular -dbg, otherwise the executable might not be found
rem # sdsbuildinfo itself ignores all arguments, so extra arguments should be safe.
call %RDI_BINROOT%/buildinfo.bat %*
echo     ** Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
echo     ** Copyright 2022-2026 Advanced Micro Devices, Inc. All Rights Reserved.
echo.
rem # echo Loading Vitis plugins ...

set supports_classic_ide=true
if exist "%XILINX_VITIS%/.vitis_embedded" (
  set VITIS_EMBEDDED_INSTALL=true
  set supports_classic_ide=false
) 
if exist "%XILINX_VITIS%/.vitis_for_hls" (
  set VITIS_HLS_INSTALL=true
  set supports_classic_ide=false
)

:launch
if [!VITISNEW!] == [false] (
  if not [!supports_classic_ide!] == [true] (
    echo Error: -classic option is only supported by full Vitis installation.
    echo If you wish to run the classic Vitis IDE, please download the AMD Unified Installer and perform a full Vitis installation.
    exit /b 1
  )
  set RDI_PROG=%~n0
  call "%RDI_BINROOT%/loader.bat" -exec rdi_vitis %args_for_classic%
  goto :EOF
)

@REM Unified Vitis Env settings
if exist "%JAVA_HOME%\bin" set PATH=%JAVA_HOME%\bin;!PATH!
if exist "%TOOLS_CLANGD%" set PATH=%TOOLS_CLANGD%;!PATH!
if exist "%TPS_CMAKE%\bin" set PATH=%TPS_CMAKE%\bin;%PATH%
if exist "%TPS_GIT%\bin" set PATH=%TPS_GIT%\bin;%PATH%

@REM Added the required JRE Server lib path to resolve the jvm.dll dependency for xv_commontasks.dll
if exist "%JAVA_HOME%\bin" set PATH=%JAVA_HOME%\bin\server;!PATH!

set XILINX_VITIS_GIT=%TPS_GIT%\bin


@REM unset RDI_DEPENDENCY variable
set RDI_DEPENDENCY=

@REM Lopper Evnironment
if exist "%TPS_PYTHON%" set PATH=%TPS_PYTHON%;%PATH%

@REM Multi-patch XILINX_PATH:
@REM   Sort patches by patch.number desc, then for vitis-server/cli/ide folders the
@REM   first (highest-version) patch with that folder wins. Stop when all three are
@REM   satisfied; drop patches that contribute no new folder from XILINX_PATH.
if not defined XILINX_PATH goto :mp_done

echo Got variable XILINX_PATH at !XILINX_PATH!
set "_C=0" & set "_R=!XILINX_PATH!"
:mp_p
if not defined _R goto :mp_pd
for /f "tokens=1* delims=;" %%a in ("!_R!") do (set "_X=%%a" & set "_R=%%b")
if not defined _X goto :mp_pd
if not exist "!_X!\patch.properties" (echo Warning: patch.properties not found at !_X!, skipping. & set "_X=" & goto :mp_p)
set "_N=" & set "_RL=" & set "_D="
for /f "usebackq tokens=1,* delims==" %%a in ("!_X!\patch.properties") do (
  set "_K=%%a"
  set "_V=%%b"
  for /f "tokens=* delims= " %%k in ("!_K!") do set "_K=%%k"
  for /f "tokens=* delims= " %%v in ("!_V!") do set "_V=%%v"
  if /i not "!_K:patch.number=!"=="!_K!"      set "_N=!_V!"
  if /i not "!_K:patch.release=!"=="!_K!"     set "_RL=!_V!"
  if /i not "!_K:patch.description=!"=="!_K!" set "_D=!_V!"
)
if not defined _N  (echo Warning: patch.number missing at !_X!, skipping.  & set "_X=" & goto :mp_p)
if not defined _RL (echo Warning: patch.release missing at !_X!, skipping. & set "_X=" & goto :mp_p)
echo !XILINX_VITIS_VERSION! | findstr /C:"!_RL!" >nul
if errorlevel 1 (echo Patch at !_X! ^(!_RL!^) is not compatible with !XILINX_VITIS_VERSION!, skipping. & set "_X=" & goto :mp_p)
for /f "tokens=1,2,3 delims=." %%a in ("!_N!") do (
  set "_a=%%a" & set "_b=%%b" & set "_c=%%c"
  if not defined _b set "_b=0"
  if not defined _c set "_c=0"
  set /a "_V=!_a!*1000000+!_b!*1000+!_c!"
)
set "P_!_C!=!_X!" & set "N_!_C!=!_N!" & set "L_!_C!=!_RL!" & set "D_!_C!=!_D!" & set "V_!_C!=!_V!"
set /a _C+=1 & set "_X="
goto :mp_p

:mp_pd
@REM Bubble-sort by V_n descending (highest version first)
if !_C! LSS 2 goto :mp_apply
:mp_so
set "_W=0" & set "_J=0"
:mp_si
set /a "_K=!_J!+1"
if !_K! GEQ !_C! goto :mp_sid
call set "_A=%%V_!_J!%%" & call set "_B=%%V_!_K!%%"
if !_A! LSS !_B! (
  call set "_T=%%P_!_J!%%" & call set "_U=%%P_!_K!%%" & set "P_!_J!=!_U!" & set "P_!_K!=!_T!"
  call set "_T=%%N_!_J!%%" & call set "_U=%%N_!_K!%%" & set "N_!_J!=!_U!" & set "N_!_K!=!_T!"
  call set "_T=%%L_!_J!%%" & call set "_U=%%L_!_K!%%" & set "L_!_J!=!_U!" & set "L_!_K!=!_T!"
  call set "_T=%%D_!_J!%%" & call set "_U=%%D_!_K!%%" & set "D_!_J!=!_U!" & set "D_!_K!=!_T!"
  call set "_T=%%V_!_J!%%" & call set "_U=%%V_!_K!%%" & set "V_!_J!=!_U!" & set "V_!_K!=!_T!"
  set "_W=1"
)
set /a _J+=1 & goto :mp_si
:mp_sid
if "!_W!"=="1" goto :mp_so

:mp_apply
set "_S=0" & set "_CL=0" & set "_ID=0" & set "_ES=0" & set "_UP=" & set "_PI=" & set "_I=0"
:mp_al
if !_I! GEQ !_C! goto :mp_ad
call set "_p=%%P_!_I!%%" & call set "_n=%%N_!_I!%%" & call set "_l=%%L_!_I!%%" & call set "_d=%%D_!_I!%%"
if not defined _p (set /a _I+=1 & goto :mp_al)
set "_used=0" & set "_ds=" & set "_dc=" & set "_di="
if "!_S!"=="0"  if exist "!_p!\vitis-server" (set "_S=1"  & set "_used=1" & set "_ds=1")
if "!_CL!"=="0" if exist "!_p!\cli" (
  set "PYTHONPATH=!_p!\cli;!_p!\cli\python-packages\win64;!_p!\cli\python-packages\site-packages;!_p!\cli\proto;!_p!\scripts\python_pkg;!PYTHONPATH!"
  set "_CL=1" & set "_used=1" & set "_dc=1"
)
if "!_ES!"=="0" if exist "!_p!\data\embeddedsw" (set "_ES=1" & set "_used=1")
set "_app=!_p!\ide\electron-app\win64\resources\app"
if "!_ID!"=="0" if exist "!_app!\" if exist "!_app!\lib\backend\main.js" if exist "!_app!\lib\frontend\index.html" if exist "!_app!\lib\frontend\secondary-window.html" (
  set "CUSTOM_THEIA_PROJECT_APP_PATH=!_app!\"
  set "CUSTOM_THEIA_BACKEND_MAIN_PATH=!_app!\lib\backend\main.js"
  set "CUSTOM_THEIA_FRONTEND_PATH=!_app!\lib\frontend\index.html"
  set "CUSTOM_THEIA_SECONDARY_WINDOW_HTML_PATH=!_app!\lib\frontend\secondary-window.html"
  set "_ID=1" & set "_used=1" & set "_di=1"
)
if "!_used!"=="1" (
  echo Patch !_n! found at !_p!, activated successfully.
  if defined _ds echo   -^> vitis-server applied from !_p!
  if defined _dc echo   -^> cli applied from !_p!
  if defined _di echo   -^> ide applied from !_p!
  if defined _UP (set "_UP=!_UP!;!_p!") else (set "_UP=!_p!")
  if defined _PI (set "_PI=!_PI! ^| Patch !_p! ^(!_n!, !_l!^) - !_d!") else (set "_PI=Patch !_p! ^(!_n!, !_l!^) - !_d!")
) else (
  if "!_S!!_CL!!_ID!!_ES!"=="1111" echo Patch !_n! at !_p! ignored: required folders already provided by higher-version patches.
)
if "!_S!!_CL!!_ID!!_ES!"=="1111" (echo All patch folders ^(vitis-server, cli, ide^) are satisfied. Remaining patches ignored. & goto :mp_ad)
set /a _I+=1 & goto :mp_al

:mp_ad
if defined _UP (set "XILINX_PATH=!_UP!" & echo Final XILINX_PATH: !XILINX_PATH!)
if defined _PI set "PATCH_INFO=!_PI!"

:mp_done

if not defined PATCH_INFO (
  if exist %XILINX_VITIS%\patch.properties (
    for /f "usebackq tokens=1,* delims==" %%a in ("%XILINX_VITIS%\patch.properties") do (
      set "key=%%a"
      set "value=%%b"
      for /f "tokens=* delims= " %%k in ("!key!") do set "key=%%k"
      for /f "tokens=* delims= " %%v in ("!value!") do set "value=%%v"
      if /i not "!key:patch.number=!"=="!key!" set patch_number=!value!
      if /i not "!key:patch.release=!"=="!key!" set patch_release=!value!
      if /i not "!key:patch.description=!"=="!key!" set patch_desc=!value!
    )
    set PATCH_INFO=Patch !XILINX_PATH! ^(!patch_number!, !patch_release!^) Details - !patch_desc!
    echo Patch !patch_number! found at %XILINX_VITIS%, activated successfully.
  ) else (
    set PATCH_INFO=
  )
)


@REM Env variable support to disable license check
set IDE_SKIP_SERVER_LICENSE=1
set CMAKE_OBJECT_PATH_MAX=4096

set RDI_DATADIR=%RDI_APPROOT%/data

if "!RDI_INSTALLVER!" == "aietools" (
  set RDI_SHARED_DATA=!RDI_INSTALLROOT!/../SharedData/!RDI_INSTALLVER!/data
) else (
  set RDI_SHARED_DATA=!RDI_INSTALLROOT!/SharedData/!RDI_INSTALLVER!/data
  if not exist "!RDI_SHARED_DATA!" if exist "!RDI_INSTALLROOT!/../SharedData/data" (
    set RDI_SHARED_DATA=!RDI_INSTALLROOT!/../SharedData/data
  )
)

if exist "!RDI_SHARED_DATA!" (
  set RDI_DATADIR=!RDI_SHARED_DATA!;!RDI_DATADIR!
)

if exist "!RDI_APPROOT!/data/vits" (
  set RDI_DATADIR=!RDI_APPROOT!/data/vits;!RDI_DATADIR!
)
set PATH=%RDI_APPROOT%\bin;%RDI_APPROOT%\gnu\microblaze\nt\bin;%RDI_APPROOT%\gnu\arm\nt\bin;%RDI_APPROOT%\gnu\microblaze\linux_toolchain\nt64_be\bin;%RDI_APPROOT%\gnu\microblaze\linux_toolchain\nt64_le\bin;%RDI_APPROOT%\gnu\aarch32\nt\gcc-arm-linux-gnueabi\bin;%RDI_APPROOT%\gnu\aarch32\nt\gcc-arm-none-eabi\bin;%RDI_APPROOT%\gnu\aarch64\nt\aarch64-linux\bin;%RDI_APPROOT%\gnu\aarch64\nt\aarch64-none\bin;%RDI_APPROOT%\gnu\armr5\nt\gcc-arm-none-eabi\bin;%RDI_APPROOT%\gnu\riscv\nt\bin;%RDI_APPROOT%\gnu\riscv\linux_toolchain\nt64\bin;%RDI_APPROOT%\gnu\riscv\linux_toolchain\nt32\bin;!PATH!
if [!INTERACTIVE!] == [true] (
   set PYTHONPATH=%XILINX_VITIS%\cli;%XILINX_VITIS%\cli\python-packages\win64;%XILINX_VITIS%\cli\python-packages\site-packages;%XILINX_VITIS%\cli\proto;%XILINX_VITIS%\scripts\python_pkg;!PYTHONPATH!
   if not exist "%XILINX_VITIS%/cli/vitis" (
     echo Error: XILINX_VITIS/cli/vitis directory not found
     exit /b 1
   )
   python.exe %XILINX_VITIS%/cli/vitis/_vitisshell.py
) else (
    if [!SOURCE!] == [true] (
      set PYTHONPATH=%XILINX_VITIS%\cli;%XILINX_VITIS%\cli\python-packages\win64;%XILINX_VITIS%\cli\python-packages\site-packages;%XILINX_VITIS%\cli\proto;%XILINX_VITIS%\scripts\python_pkg;!PYTHONPATH!
      set predef_class_file=%XILINX_VITIS%/cli/vitis/_predefined_classes.txt
      if exist "!predef_class_file!" (
        FOR /F "tokens=* delims=, " %%x in (!predef_class_file!) DO (
          set list=%%x
          for %%a in (!list!) do (
            if ^'!sourceWithoutExtension!^' == %%a (
              echo Error: The file name ^'!sourceWithoutExtension!^.py^' conflicts with Vitis pre-defined module names. 
              echo Using this file name may cause unexpected behavior. Please change the file name.
              echo For full list of pre-defined module name please refer !predef_class_file!
              exit /b 1
            )
          )
        )
      )
      python.exe %args_for_source%
    ) else (
      if not exist "%XILINX_VITIS%/ide/electron-app/win64/vitis-ide.exe" (
        echo Error: Vitis IDE not found in %XILINX_VITIS%
        exit /b 1
      )
      if defined VITIS_IDE_USER_TOOLCHAIN ( 
        set PATH=%VITIS_IDE_USER_TOOLCHAIN%;!PATH!
      )
      if [!WORKSPACE!] == [true] (
        if "%workspaceDir%" == "" (
          echo Error: The required argument for option --workspace is missing.
          echo Please provide a valid path or refer to vitis --help for more information.
          exit /b 1
        )
        if not exist %workspaceDir%\NUL (
          mkdir %workspaceDir%
        )
	    set VALIDATE_ARGS="False"
        start %XILINX_VITIS%/ide/electron-app/win64/vitis-ide.exe --no-sandbox --log-level=debug !workspaceDir!    
      ) else (
        @REM Invoke Unified Vitis IDE
	    set VALIDATE_ARGS="False"
        start %XILINX_VITIS%/ide/electron-app/win64/vitis-ide.exe --no-sandbox --log-level=debug
      )
   )
)
goto :EOF

:echoData
echo.
echo ****** Xilinx Vitis Development Environment
echo ****** %XILINX_VITIS_VERSION%
echo|set /p="****** " || cmd /c "exit /b 0"
rem # Need to pass args, in particular -dbg, otherwise the executable might not be found
rem # sdsbuildinfo itself ignores all arguments, so extra arguments should be safe.
call %RDI_BINROOT%/buildinfo.bat %*
echo     ** Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
echo     ** Copyright 2022-2026 Advanced Micro Devices, Inc. All Rights Reserved.
echo.
rem # echo Loading Vitis plugins ...

exit /b 1


:HELP
   echo.
   echo ****** Xilinx Vitis Development Environment
   echo ****** %XILINX_VITIS_VERSION%
   echo|set /p="****** " || cmd /c "exit /b 0"
   rem # Need to pass args, in particular -dbg, otherwise the executable might not be found
   rem # sdsbuildinfo itself ignores all arguments, so extra arguments should be safe.
   call %RDI_BINROOT%/buildinfo.bat %*
   echo     ** Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
   echo     ** Copyright 2022-2026 Advanced Micro Devices, Inc. All Rights Reserved.
   echo.
   rem # echo Loading Vitis plugins ...
   echo.
   echo Syntax: vitis [-w ^| -i ^| -s ^| -h ^| -v]
   echo.
   echo Options:
   echo   Launches New Vitis IDE (default option).  
   echo   -w/--workspace ^<workspace_location^>
   echo          Launches Vitis IDE with the given workspace location.
   echo              Usage: $ vitis -w ^<workspace_location^>
   echo   -i/--interactive
   echo          Launches Vitis python interactive shell.
   echo   -s/--source ^<python_script^>
   echo          Runs the given python script.
   echo              Usage: $ vitis -s ^<python_script^>
   echo   -h/--help
   echo          Display help message.
   echo   -v/--version
   echo          Display version message.


