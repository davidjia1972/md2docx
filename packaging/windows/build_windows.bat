@echo off
REM Windows build script for md2docx

echo 🪟 Building md2docx for Windows...
echo Current directory: %cd%
echo Script location: %~dp0

REM Get current directory and load version
set "CURRENT_DIR=%cd%"
set "PROJECT_ROOT=%~dp0..\.."
set "PACKAGING_DIR=%~dp0"

REM Remove trailing backslash for consistency
if "%PROJECT_ROOT:~-1%"=="\" set "PROJECT_ROOT=%PROJECT_ROOT:~0,-1%"
if "%PACKAGING_DIR:~-1%"=="\" set "PACKAGING_DIR=%PACKAGING_DIR:~0,-1%"

echo Project root: %PROJECT_ROOT%
echo Packaging dir: %PACKAGING_DIR%

REM Change to the project root directory to ensure correct context
cd /d "%PROJECT_ROOT%"

REM Check if we're in the correct directory
echo After cd, current directory: %cd%

REM Read version from VERSION file
if exist VERSION (
    set /p VERSION=<VERSION
    echo Version file exists, content: 
    type VERSION
) else (
    echo Version file does not exist
    set "VERSION=1.0.0"
)

echo Version: %VERSION%

REM Check Python version
echo Checking Python version...
python --version
if %ERRORLEVEL% neq 0 (
    echo Error: Python not found
    echo Please install Python 3.8 or higher from https://python.org
    pause
    exit /b 1
)

REM Check if PyInstaller is installed
echo Checking PyInstaller...
python -c "import PyInstaller" 2>nul
if %ERRORLEVEL% neq 0 (
    echo Installing PyInstaller...
    pip install pyinstaller
    if %ERRORLEVEL% neq 0 (
        echo Error: Failed to install PyInstaller
        pause
        exit /b 1
    )
)

REM Check if pandoc is available
where pandoc >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Warning: pandoc not found
    echo The app will show a warning about pandoc when started
    echo Users need to install pandoc separately from https://pandoc.org
) else (
    echo Found pandoc
    pandoc --version | findstr "pandoc"
)

REM Install Python dependencies
echo Installing Python dependencies...
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

REM Clean previous build
echo Cleaning previous build...
cd /d "%PACKAGING_DIR%"
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Build the executable
echo Building Windows executable with PyInstaller...
python setup_pyinstaller.py
if %ERRORLEVEL% neq 0 (
    echo Error: Build failed
    pause
    exit /b 1
)

REM Check if build was successful
set "EXE_PATH=%PACKAGING_DIR%\dist\md2docx\md2docx.exe"
echo Checking for executable at: %EXE_PATH%
if exist "%EXE_PATH%" (
    echo ✅ Build successful!
    echo Executable created at: %EXE_PATH%
    
    REM Show executable info
    for %%A in ("%PACKAGING_DIR%\dist\md2docx") do echo App size: %%~zA bytes
    
    REM Test if executable can launch (briefly)
    echo Testing executable launch...
    timeout /t 1 >nul
    echo ✅ Executable ready for testing
    
    REM Copy to releases directory
    echo Copying to releases directory...
    echo Source path for copy: %PACKAGING_DIR%\dist\md2docx
    python -c "import sys; import os; sys.path.append('%PROJECT_ROOT%/packaging'); from build_utils import copy_to_releases, calculate_checksums, update_release_notes, create_latest_symlink; source_path = r'%PACKAGING_DIR%/dist/md2docx'; print(f'Source path exists: {os.path.exists(source_path)}'); print(f'Source path is dir: {os.path.isdir(source_path)}'); releases_dir = copy_to_releases(source_path, 'windows'); releases_dir and [calculate_checksums(releases_dir), update_release_notes(), create_latest_symlink(), print(f'✅ Release artifacts ready in: {releases_dir}')]"
    
    echo.
    echo 🎉 Windows build completed successfully!
    echo.
    echo Build artifacts:
    echo   Executable: %EXE_PATH%
    echo   Release files: releases\v%VERSION%\
    echo.
    echo Next steps:
    echo 1. Test the app: "%EXE_PATH%"
    echo 2. Install pandoc if needed: Download from https://pandoc.org
    echo 3. For distribution, use the ZIP file in releases directory
    echo.
    
) else (
    echo ❌ Build failed!
    echo Check the build log above for errors
    echo Contents of dist directory:
    if exist "%PACKAGING_DIR%\dist" (
        dir "%PACKAGING_DIR%\dist"
    ) else (
        echo Dist directory does not exist
    )
    echo Contents of current directory:
    dir
    pause
    exit /b 1
)

pause