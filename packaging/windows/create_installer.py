#!/usr/bin/env python3
"""
Create Windows installer using NSIS or Inno Setup
"""

import os
import sys
from pathlib import Path
import subprocess

def create_nsis_script():
    """Create NSIS installer script"""
    
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    
    # Read version
    version = "1.0.0"
    version_file = project_root / "VERSION"
    if version_file.exists():
        with open(version_file, 'r') as f:
            version = f.read().strip() or "1.0.0"
    
    nsis_script = f"""
; md2docx NSIS Installer Script
; Generated automatically

!include "MUI2.nsh"

; Application info
Name "md2docx"
OutFile "md2docx-v{version}-windows-installer.exe"
InstallDir "$PROGRAMFILES\\md2docx"
InstallDirRegKey HKLM "Software\\md2docx" "InstallDir"
RequestExecutionLevel admin

; Interface
!define MUI_ABORTWARNING
!define MUI_ICON "..\\..\\assets\\icons\\app_icon.ico"

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "..\\..\\LICENSE"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; Languages
!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "SimpChinese"

; Version info
VIProductVersion "{version}.0"
VIAddVersionKey "ProductName" "md2docx"
VIAddVersionKey "ProductVersion" "{version}"
VIAddVersionKey "CompanyName" "md2docx"
VIAddVersionKey "FileDescription" "Markdown to Word Converter"
VIAddVersionKey "FileVersion" "{version}"

; Installer sections
Section "md2docx" SecMain
    SetOutPath "$INSTDIR"
    
    ; Copy all files from dist/md2docx/
    File /r "dist\\md2docx\\*"
    
    ; Create uninstaller
    WriteUninstaller "$INSTDIR\\Uninstall.exe"
    
    ; Registry entries
    WriteRegStr HKLM "Software\\md2docx" "InstallDir" "$INSTDIR"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\md2docx" "DisplayName" "md2docx"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\md2docx" "UninstallString" "$INSTDIR\\Uninstall.exe"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\md2docx" "DisplayVersion" "{version}"
    
    ; Start Menu shortcuts
    CreateDirectory "$SMPROGRAMS\\md2docx"
    CreateShortCut "$SMPROGRAMS\\md2docx\\md2docx.lnk" "$INSTDIR\\md2docx.exe"
    CreateShortCut "$SMPROGRAMS\\md2docx\\Uninstall.lnk" "$INSTDIR\\Uninstall.exe"
    
    ; Desktop shortcut (optional)
    CreateShortCut "$DESKTOP\\md2docx.lnk" "$INSTDIR\\md2docx.exe"
    
SectionEnd

; Uninstaller
Section "Uninstall"
    ; Remove files
    RMDir /r "$INSTDIR"
    
    ; Remove shortcuts
    RMDir /r "$SMPROGRAMS\\md2docx"
    Delete "$DESKTOP\\md2docx.lnk"
    
    ; Remove registry entries
    DeleteRegKey HKLM "Software\\md2docx"
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\md2docx"
SectionEnd
"""
    
    nsis_file = script_dir / "installer.nsi"
    with open(nsis_file, 'w', encoding='utf-8') as f:
        f.write(nsis_script)
    
    return nsis_file

def build_installer():
    """Build installer if NSIS is available"""
    
    script_dir = Path(__file__).parent
    
    # Check if dist directory exists
    dist_dir = script_dir / "dist" / "md2docx"
    if not dist_dir.exists():
        print("❌ dist/md2docx directory not found. Run build_windows.bat first.")
        return False
    
    # Create NSIS script
    nsis_file = create_nsis_script()
    print(f"✅ Created NSIS script: {nsis_file}")
    
    # Try to build with NSIS
    nsis_paths = [
        "C:\\Program Files (x86)\\NSIS\\makensis.exe",
        "C:\\Program Files\\NSIS\\makensis.exe",
        "makensis.exe"  # In PATH
    ]
    
    makensis = None
    for path in nsis_paths:
        if Path(path).exists() or path == "makensis.exe":
            try:
                result = subprocess.run([path, "/VERSION"], capture_output=True, text=True)
                if result.returncode == 0:
                    makensis = path
                    break
            except:
                continue
    
    if makensis:
        print(f"✅ Found NSIS: {makensis}")
        try:
            # Change to packaging directory
            os.chdir(script_dir)
            
            result = subprocess.run([makensis, str(nsis_file)], check=True)
            
            installer_path = script_dir / f"md2docx-v{get_version()}-windows-installer.exe"
            if installer_path.exists():
                print(f"✅ Installer created: {installer_path}")
                print(f"   Size: {installer_path.stat().st_size / 1024 / 1024:.1f} MB")
                return True
            else:
                print("❌ Installer not found after build")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"❌ NSIS build failed: {e}")
            return False
    else:
        print("⚠️  NSIS not found. Installer creation skipped.")
        print("   Download NSIS from: https://nsis.sourceforge.io/")
        return False

def get_version():
    """Get version from VERSION file"""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    version_file = project_root / "VERSION"
    
    if version_file.exists():
        with open(version_file, 'r') as f:
            return f.read().strip() or "1.0.0"
    return "1.0.0"

def main():
    print("=== Windows Installer Creator ===")
    
    if build_installer():
        print("\n✅ Installer creation completed!")
    else:
        print("\n⚠️  Installer creation skipped or failed.")
        print("   You can still use the ZIP package for distribution.")

if __name__ == "__main__":
    main()
    input("\nPress Enter to exit...")