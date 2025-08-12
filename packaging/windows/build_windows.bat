@echo off
setlocal enabledelayedexpansion

REM Windows build script for md2docx
echo 🪟 Building md2docx for Windows...

REM Get script directory
set "SCRIPT_DIR=%~dp0"
if "!SCRIPT_DIR:~-1!"=="\" set "SCRIPT_DIR=!SCRIPT_DIR:~0,-1!"

REM Get project root directory (2 levels up from script dir)
for %%i in ("!SCRIPT_DIR!\..\..") do set "PROJECT_ROOT=%%~fi"
if "!PROJECT_ROOT:~-1!"=="\" set "PROJECT_ROOT=!PROJECT_ROOT:~0,-1!"

REM Get packaging directory
for %%i in ("!SCRIPT_DIR!") do set "PACKAGING_DIR=%%~fi"
if "!PACKAGING_DIR:~-1!"=="\" set "PACKAGING_DIR=!PACKAGING_DIR:~0,-1!"

echo Script directory: !SCRIPT_DIR!
echo Project root: !PROJECT_ROOT!
echo Packaging directory: !PACKAGING_DIR!

REM Change to project root directory
cd /d "!PROJECT_ROOT!"
if errorlevel 1 (
    echo ❌ Failed to change to project root directory: !PROJECT_ROOT!
    exit /b 1
)

echo Current directory after cd: %cd%

REM Read version from VERSION file
set "VERSION=1.0.0"
if exist VERSION (
    set /p VERSION=<VERSION
    if "!VERSION!"=="" set "VERSION=1.0.0"
)
echo Version: !VERSION!

REM Check Python
echo Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.8 or higher.
    exit /b 1
)

REM Check if PyInstaller is installed
echo Checking PyInstaller...
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo ❌ Failed to install PyInstaller
        exit /b 1
    )
)

REM Install Python dependencies
echo Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install dependencies
    exit /b 1
)

REM Change to packaging directory
cd /d "!PACKAGING_DIR!"
if errorlevel 1 (
    echo ❌ Failed to change to packaging directory: !PACKAGING_DIR!
    exit /b 1
)

echo Current directory: %cd%

REM Clean previous build
echo Cleaning previous build...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Build the executable
echo Building Windows executable with PyInstaller...
python setup_pyinstaller.py
if errorlevel 1 (
    echo ❌ Build failed with error level !errorlevel!
    echo Contents of current directory:
    dir
    if exist build (
        echo Contents of build directory:
        dir build
    )
    if exist dist (
        echo Contents of dist directory:
        dir dist
    )
    exit /b 1
)

echo Build completed successfully!

REM Check if executable was created
set "EXE_PATH=!PACKAGING_DIR!\dist\md2docx\md2docx.exe"
echo Checking for executable at: !EXE_PATH!
if exist "!EXE_PATH!" (
    echo ✅ Build successful!
    echo Executable created at: !EXE_PATH!
    
    REM Copy to releases directory
    echo Copying to releases directory...
    python -c "import sys; sys.path.append('!PROJECT_ROOT!\packaging'); from build_utils import copy_to_releases, calculate_checksums, update_release_notes, create_latest_symlink; source_path = r'!PACKAGING_DIR!\dist\md2docx'; print(f'Source path: {source_path}'); releases_dir = copy_to_releases(source_path, 'windows', '!VERSION!'); print(f'Releases dir: {releases_dir}'); releases_dir and [calculate_checksums(releases_dir), update_release_notes('!VERSION!'), create_latest_symlink('!VERSION!'), print('✅ Release artifacts ready')]"
    if errorlevel 1 (
        echo ❌ Failed to copy to releases directory
        exit /b 1
    )
    
    echo 🎉 Windows build completed successfully!
    echo Build artifacts are in releases\v!VERSION!\
) else (
    echo ❌ Build failed - executable not found at: !EXE_PATH!
    echo Contents of dist directory:
    if exist dist (
        dir dist
    ) else (
        echo dist directory does not exist
    )
    exit /b 1
)

pause