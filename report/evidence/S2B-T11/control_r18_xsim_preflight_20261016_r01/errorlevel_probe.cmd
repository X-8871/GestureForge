@echo off
cmd /d /c exit 1
echo BEFORE_TYPE=%errorlevel%
call type "%~f0" >nul
echo AFTER_CALL_TYPE=%errorlevel%
exit /b 0
