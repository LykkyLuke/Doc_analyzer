@echo off
setlocal enabledelayedexpansion

:: Change to the script's directory
cd /d "%~dp0"

:: Set console title
title Document Analyzer Setup

echo Starting Document Analyzer Setup...
echo ================================

echo Checking Python installation...

:: Check if Python 3.10 is installed
py -3.10 --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python 3.10 is not installed.
    echo Please install Python 3.10 from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

:: Get Python version and check if it's 3.10
for /f "tokens=2" %%I in ('py -3.10 --version') do set PYTHON_VERSION=%%I
echo [OK] Found Python version %PYTHON_VERSION%

:: Check if virtual environment exists, create if it doesn't
if not exist "venv\Scripts\python.exe" (
    echo Creating virtual environment...
    py -3.10 -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        echo Please make sure you have write permissions in this directory
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
)

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)
echo [OK] Virtual environment activated

:: Clean up any invalid distributions
echo Cleaning up invalid distributions...
for /f "delims=" %%i in ('dir /b /s "venv\Lib\site-packages\-*"') do (
    echo Removing invalid distribution: %%i
    rd /s /q "%%i" 2>nul
    if exist "%%i" del /f /q "%%i"
)

:: Check and install required packages
echo Checking pip...
venv\Scripts\python.exe -m pip install --upgrade pip

:: Check if requirements.txt exists
if not exist "requirements.txt" (
    echo [ERROR] requirements.txt not found!
    echo Make sure you're running this script from the project root directory.
    pause
    exit /b 1
)

:: Install/upgrade required packages with better error handling
echo Installing/upgrading required packages...
venv\Scripts\python.exe -m pip install --upgrade --no-cache-dir setuptools wheel
venv\Scripts\python.exe -m pip install -r requirements.txt --no-cache-dir
if errorlevel 1 (
    echo [WARNING] Some packages may have failed to install
    echo Retrying installation with --no-deps flag...
    venv\Scripts\python.exe -m pip install -r requirements.txt --no-deps --no-cache-dir
    if errorlevel 1 (
        echo [ERROR] Failed to install required packages
        echo Please check the error messages above
        pause
        exit /b 1
    )
)
echo [OK] All packages installed

:: Verify critical packages with better error messages
echo Verifying critical packages...
venv\Scripts\python.exe -c "import docx" 2>nul
if errorlevel 1 (
    echo [ERROR] Failed to import python-docx package
    echo Attempting to reinstall python-docx...
    venv\Scripts\python.exe -m pip install --no-cache-dir python-docx
    venv\Scripts\python.exe -c "import docx" 2>nul
    if errorlevel 1 (
        echo [ERROR] Still unable to import python-docx package
        pause
        exit /b 1
    )
)

venv\Scripts\python.exe -c "import vertexai" 2>nul
if errorlevel 1 (
    echo [ERROR] Failed to import vertexai package
    echo Attempting to reinstall vertexai...
    venv\Scripts\python.exe -m pip install --no-cache-dir vertexai
    venv\Scripts\python.exe -c "import vertexai" 2>nul
    if errorlevel 1 (
        echo [ERROR] Still unable to import vertexai package
        pause
        exit /b 1
    )
)

venv\Scripts\python.exe -c "import google.cloud.aiplatform" 2>nul
if errorlevel 1 (
    echo [ERROR] Failed to import google.cloud.aiplatform package
    echo Attempting to reinstall google-cloud-aiplatform...
    venv\Scripts\python.exe -m pip install --no-cache-dir google-cloud-aiplatform
    venv\Scripts\python.exe -c "import google.cloud.aiplatform" 2>nul
    if errorlevel 1 (
        echo [ERROR] Still unable to import google.cloud.aiplatform package
        pause
        exit /b 1
    )
)

echo [OK] All critical packages verified

:: Check if main.py exists
if not exist "src\main.py" (
    echo [ERROR] main.py not found in src directory!
    echo Current directory: %CD%
    echo Please make sure you're running this script from the project root directory.
    pause
    exit /b 1
)

:: All checks passed, start the application
echo.
echo All checks passed. Starting Document Analyzer...
echo ============================================
echo.

:: Set console title for running application
title Document Analyzer

:: Start the application using the virtual environment's Python
venv\Scripts\python.exe src\main.py

:: If the application exits with an error, pause to show the error message
if errorlevel 1 (
    echo.
    echo [ERROR] Application exited with an error
    echo Please check the error messages above
    pause
)

:: Deactivate virtual environment
call venv\Scripts\deactivate.bat

endlocal 