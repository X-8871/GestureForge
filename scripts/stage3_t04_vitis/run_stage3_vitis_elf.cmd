@echo off
setlocal enabledelayedexpansion
rem ============================================================================
rem Stage3 T04: Vitis 2026.1 standalone ELF reproduction (XSA -> BSP -> app -> ELF)
rem This file is intentionally ASCII-only: cmd.exe parses .cmd in the OEM code page
rem and non-ASCII comments corrupt command parsing. Chinese notes live in the report.
rem
rem Usage: run_stage3_vitis_elf.cmd <XSA> <OUT_DIR> <APP_SRC_DIR> [ELF_NAME] [PATCH_FILE]
rem   Builds a Cortex-A9 standalone ELF for the given XSA and vendor application
rem   source tree (T03 vdma_hdmi, T04 an5642_single, ...). The output ELF is named
rem   after the source directory basename unless ELF_NAME is given.
rem   PATCH_FILE : optional git patch applied with "git apply -p1" inside the app dir.
rem The XSA is copied under OUT/_input first, because hsi::open_hw_design unpacks
rem XSA members next to the .xsa file; the original input dir is never written.
rem No network, no hardware, no programming. Requires Vitis 2026.1 install.
rem ============================================================================

if "%~1"=="" goto usage
if "%~2"=="" goto usage
if "%~3"=="" goto usage

set "SCRIPT_DIR=%~dp0"
set "XILINX_ROOT=D:\Xilinx\2026.1"
set "XILINXD_LICENSE_FILE=D:\Xilinx_licenses\basic_only.lic"

set "S3_XSA=%~f1"
set "S3_OUT=%~f2"
set "S3_OUT_N=%~f2"
set "S3_APP_SRC=%~f3"
rem Output ELF is named after the application source directory (e.g. vdma_hdmi.elf,
rem an5642_single.elf); override with a 4th argument if needed.
for %%I in ("%~f3") do set "S3_APP_NAME=%%~nxI"
set "S3_EXEC_NAME=%S3_APP_NAME%.elf"
if not "%~4"=="" set "S3_EXEC_NAME=%~4"
rem Use forward slashes on the TCL side to avoid backslash escape ambiguity.
set "S3_XSA=%S3_XSA:\=/%"
set "S3_OUT=%S3_OUT:\=/%"
set "S3_PROC=ps7_cortexa9_0"
set "S3_APP_TEMPLATE=empty_application"
set "S3_DO_BSP=1"

if not exist "%XILINX_ROOT%\Vitis\bin\sdtgen.bat" (
  echo [FAIL] sdtgen.bat not found: %XILINX_ROOT%\Vitis\bin\sdtgen.bat
  exit /b 3
)
if not exist "%~f1" ( echo [FAIL] XSA not found: %~f1 & exit /b 3 )
if not exist "%~f3" ( echo [FAIL] vendor app source dir not found: %~f3 & exit /b 3 )
if not "%~5"=="" set "S3_APP_PATCH=%~f5"

rem IMPORTANT: hsi::open_hw_design extracts the XSA members (bit, ps7_init.*) into
rem the directory that holds the .xsa file. Always stage a copy under OUT so that
rem neither the vendor reference cache nor the caller's build directory is written.
set "S3_IN_STAGE=%S3_OUT_N%\_input"
if not exist "%S3_IN_STAGE%" mkdir "%S3_IN_STAGE%" >nul 2>&1
copy /Y "%~f1" "%S3_IN_STAGE%\design_1_wrapper.xsa" >nul
set "S3_XSA=%S3_IN_STAGE%\design_1_wrapper.xsa"
set "S3_XSA=%S3_XSA:\=/%"
echo [INFO] staged XSA copy = %S3_XSA%

rem Do NOT call settings64.bat here: it defines RDI_SETUP_ENV_FUNCTION, which makes
rem sdtgen.bat's internal setupEnv.bat call take a wrong branch ("syntax of the
rem command is incorrect"). sdtgen.bat configures itself; make only needs the two
rem toolchain directories on PATH plus RDI_PLATFORM=win for the generated Makefiles.
set "RDI_PLATFORM=win"
set "PATH=%XILINX_ROOT%\Vitis\gnu\aarch32\nt\gcc-arm-none-eabi\bin;%XILINX_ROOT%\Vitis\gnuwin\bin;%PATH%"

echo [STEP 1/3] sdtgen + HSI: generate BSP and application skeleton
rem sdtgen.bat keeps the surrounding quotes of its TCL-file argument inside
rem "if [%1] == []" / "set RDI_ARGS=... %1", which makes rdiArgs.bat abort with
rem "The syntax of the command is incorrect." (fatal to the calling batch).
rem So run from a dedicated work directory with a bare relative file name; the
rem XSA/output paths reach the TCL through environment variables instead. Using a
rem work directory under OUT also keeps sdtgen's .Xil cache out of this repo dir.
set "SDT_WORK=%S3_OUT_N%\_sdtgen_cwd"
if not exist "%SDT_WORK%" mkdir "%SDT_WORK%" >nul 2>&1
copy /Y "%SCRIPT_DIR%gen_bsp_app.tcl" "%SDT_WORK%\gen_bsp_app.tcl" >nul
pushd "%SDT_WORK%"
call "%XILINX_ROOT%\Vitis\bin\sdtgen.bat" gen_bsp_app.tcl
set "SDTGEN_RC=%errorlevel%"
popd
if not "%SDTGEN_RC%"=="0" ( echo [FAIL] sdtgen returned %SDTGEN_RC% & exit /b 1 )

echo [STEP 2/3] import vendor application sources
if not exist "%S3_OUT%\app" ( echo [FAIL] app dir not generated: %S3_OUT%\app & exit /b 1 )
xcopy /E /I /Y /Q "%~f3\*" "%S3_OUT%\app\" >nul
copy /Y "%SCRIPT_DIR%Makefile.app" "%S3_OUT%\app\Makefile.app" >nul
if not defined S3_APP_PATCH goto after_patch
if not exist "%S3_APP_PATCH%" ( echo [FAIL] patch not found: %S3_APP_PATCH% & exit /b 1 )
rem NOTE: keep these lines OUT of a parenthesised block: %errorlevel% inside a block
rem is expanded when the block is parsed, so the check would compare an empty value.
pushd "%S3_OUT%\app"
git apply -p1 "%S3_APP_PATCH%"
set "PATCH_RC=%errorlevel%"
popd
if not "%PATCH_RC%"=="0" ( echo [FAIL] git apply returned %PATCH_RC% & exit /b 1 )
findstr /C:"S3_DIAG_APP_ENTER" "%S3_OUT%\app\display_demo.c" >nul
if errorlevel 1 ( echo [FAIL] patch self-check failed: S3_DIAG_APP_ENTER not in display_demo.c & exit /b 1 )
echo [OK] patch applied and self-checked: %S3_APP_PATCH%
:after_patch

echo [STEP 3/3] build BSP library, application objects and link ELF
pushd "%S3_OUT%\app"
make -f Makefile.app EXEC=%S3_EXEC_NAME%
set "MAKE_RC=%errorlevel%"
popd
if not "%MAKE_RC%"=="0" ( echo [FAIL] make returned non-zero: %MAKE_RC% & exit /b 1 )

if not exist "%S3_OUT%\app\%S3_EXEC_NAME%" ( echo [FAIL] %S3_EXEC_NAME% not produced & exit /b 1 )
echo [OK] ELF = %S3_OUT%\app\%S3_EXEC_NAME%
exit /b 0

:usage
echo Usage: run_stage3_vitis_elf.cmd ^<XSA^> ^<OUT_DIR^> ^<APP_SRC_DIR^> [ELF_NAME] [PATCH_FILE]
echo   APP_SRC_DIR : vendor application source directory (copied into the app)
echo   ELF_NAME    : optional output ELF name, default ^<APP_SRC_DIR basename^>.elf
echo   PATCH_FILE  : optional git patch applied inside the app dir (git apply -p1)
exit /b 2