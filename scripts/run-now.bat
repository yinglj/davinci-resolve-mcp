@echo off
REM Quick Start Script for DaVinci Resolve MCP Server (Windows Version)
REM This script sets up the environment and starts the MCP server

REM Set color codes
set RED=[91m
set GREEN=[92m
set YELLOW=[93m
set BLUE=[94m
set NC=[0m

echo %BLUE%=============================================%NC%
echo %BLUE%  DaVinci Resolve MCP Server - Quick Start   %NC%
echo %BLUE%=============================================%NC%
echo.

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo %RED%Python is not installed or not in your PATH%NC%
    echo %YELLOW%Please install Python 3.6+ from https://www.python.org/downloads/%NC%
    echo %YELLOW%Make sure to check "Add Python to PATH" during installation%NC%
    pause
    exit /b 1
)

REM Get the script directory
set SCRIPT_DIR=%~dp0
set VENV_DIR=%SCRIPT_DIR%venv
set RESOLVE_MCP_SERVER=%SCRIPT_DIR%resolve_mcp_server.py

REM Check if DaVinci Resolve is running
tasklist /fi "imagename eq Resolve.exe" | find /i "Resolve.exe" >nul
if %ERRORLEVEL% NEQ 0 (
    echo %RED%DaVinci Resolve is not running%NC%
    echo %YELLOW%Please start DaVinci Resolve before running this script%NC%
    
    REM Ask if user wants to start DaVinci Resolve
    set /p START_RESOLVE="Would you like to try starting DaVinci Resolve now? (y/n): "
    if /i "%START_RESOLVE%"=="y" (
        echo %YELLOW%Attempting to start DaVinci Resolve...%NC%
        
        REM Try to find Resolve executable in Program Files
        set RESOLVE_EXE="C:\Program Files\Blackmagic Design\DaVinci Resolve\Resolve.exe"
        if exist %RESOLVE_EXE% (
            start "" %RESOLVE_EXE%
            echo %YELLOW%Waiting for DaVinci Resolve to start...%NC%
            timeout /t 5 /nobreak >nul
        ) else (
            echo %RED%Could not find DaVinci Resolve executable%NC%
            echo %YELLOW%Please start DaVinci Resolve manually%NC%
            pause
            exit /b 1
        )
    ) else (
        echo %RED%DaVinci Resolve must be running for the MCP server to function properly%NC%
        pause
        exit /b 1
    )
)

REM Create virtual environment if it doesn't exist
if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo %YELLOW%Creating Python virtual environment...%NC%
    python -m venv "%VENV_DIR%"
    
    if %ERRORLEVEL% NEQ 0 (
        echo %RED%Failed to create virtual environment%NC%
        pause
        exit /b 1
    )
)

REM Install or upgrade MCP with CLI support
echo %YELLOW%Installing MCP SDK with CLI support in virtual environment...%NC%
call "%VENV_DIR%\Scripts\pip" install "mcp[cli]"

REM Set environment variables
echo %YELLOW%Setting environment variables...%NC%
set RESOLVE_SCRIPT_API=C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting
set RESOLVE_SCRIPT_LIB=C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll

REM Add Modules path to PYTHONPATH
set PYTHONPATH=%PYTHONPATH%;%RESOLVE_SCRIPT_API%\Modules

REM Save environment variables for user
setx RESOLVE_SCRIPT_API "%RESOLVE_SCRIPT_API%" >nul
setx RESOLVE_SCRIPT_LIB "%RESOLVE_SCRIPT_LIB%" >nul

REM Get current PYTHONPATH and add to it if needed
for /f "tokens=2*" %%a in ('reg query "HKCU\Environment" /v PYTHONPATH 2^>nul ^| find "PYTHONPATH"') do (
    set CURRENT_PYTHONPATH=%%b
)

if defined CURRENT_PYTHONPATH (
    if not "x%CURRENT_PYTHONPATH:Modules=%"=="x%CURRENT_PYTHONPATH%" (
        echo %YELLOW%PYTHONPATH already contains Modules path%NC%
    ) else (
        setx PYTHONPATH "%CURRENT_PYTHONPATH%;%RESOLVE_SCRIPT_API%\Modules" >nul
    )
) else (
    setx PYTHONPATH "%RESOLVE_SCRIPT_API%\Modules" >nul
)

REM Start the server with the virtual environment's Python
echo %GREEN%Starting DaVinci Resolve MCP Server...%NC%
echo %YELLOW%Make sure DaVinci Resolve is running!%NC%
echo.

call "%VENV_DIR%\Scripts\mcp" dev "%RESOLVE_MCP_SERVER%"

pause 