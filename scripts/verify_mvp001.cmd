@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0verify_mvp001.ps1" %*
exit /b %ERRORLEVEL%
