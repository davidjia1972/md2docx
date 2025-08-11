# md2docx Releases

This directory contains official releases of md2docx application for different platforms.

## Directory Structure

```
releases/
├── v1.0.0/                          # Version directory
│   ├── md2docx-v1.0.0-macOS.dmg     # macOS installer
│   ├── md2docx-v1.0.0-Windows.zip   # Windows portable
│   ├── md2docx-v1.0.0-Linux.tar.gz  # Linux portable
│   ├── md2docx-v1.0.0-x86_64.AppImage # Linux AppImage
│   ├── checksums.txt                # SHA256 checksums
│   └── RELEASE_NOTES.md             # Version changelog
└── latest -> v1.0.0/                # Symlink to latest version
```

## Platform Support

### macOS (Darwin)
- **Format**: `.app` bundle in `.dmg` disk image
- **Requirements**: macOS 10.15 or later
- **Installation**: Mount DMG and drag to Applications folder

### Windows
- **Format**: Portable `.zip` archive
- **Requirements**: Windows 10 or later
- **Installation**: Extract and run `md2docx.exe`

### Linux
- **Format**: Portable `.tar.gz` and `.AppImage`
- **Requirements**: Most modern distributions
- **Installation**: 
  - Portable: Extract and run `md2docx`
  - AppImage: Make executable and run directly

## Build Information

All releases are built automatically using the cross-platform build system:
- **Build tool**: PyInstaller (Windows/Linux), py2app (macOS)
- **Python version**: 3.8+
- **GUI framework**: PySide6 (Qt 6)
- **Packaging**: Platform-specific standards

## Verification

Each release includes SHA256 checksums for integrity verification:
```bash
# Verify download integrity
sha256sum -c checksums.txt
```

## Dependencies

### External Requirements
- **Pandoc**: Required for document conversion
  - macOS: `brew install pandoc`
  - Windows: Download from https://pandoc.org
  - Linux: `apt install pandoc` or equivalent

### Included Dependencies
- Python runtime environment
- PySide6 GUI framework
- emoji processing library
- Platform-specific directory utilities

## Installation Guide

### macOS
1. Download `md2docx-v1.0.0-macOS.dmg`
2. Open the DMG file
3. Drag `md2docx.app` to Applications folder
4. Install Pandoc: `brew install pandoc`

### Windows
1. Download `md2docx-v1.0.0-Windows.zip`
2. Extract to desired location
3. Run `md2docx.exe`
4. Install Pandoc from https://pandoc.org

### Linux
#### Option 1: AppImage (Recommended)
1. Download `md2docx-v1.0.0-x86_64.AppImage`
2. Make executable: `chmod +x md2docx-v1.0.0-x86_64.AppImage`
3. Run directly: `./md2docx-v1.0.0-x86_64.AppImage`

#### Option 2: Portable Archive
1. Download `md2docx-v1.0.0-Linux.tar.gz`
2. Extract: `tar -xzf md2docx-v1.0.0-Linux.tar.gz`
3. Run: `./md2docx/md2docx`
4. Or install system-wide: `sudo ./install.sh`

## Support

For issues and questions:
- GitHub Issues: https://github.com/your-username/md2docx/issues
- Documentation: See project README.md

## Changelog

See individual `RELEASE_NOTES.md` in each version directory for detailed changes.