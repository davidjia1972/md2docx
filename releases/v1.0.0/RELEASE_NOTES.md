# md2docx v1.0.0 Release Notes

**Release Date**: TBD  
**Build Date**: TBD  
**Platforms**: macOS, Windows, Linux

## 🎉 Initial Release

This is the first stable release of md2docx - a cross-platform GUI application for converting Markdown files to Microsoft Word documents.

## ✨ Features

### Core Functionality
- **Batch Conversion**: Convert multiple Markdown files at once
- **Template Support**: Use custom DOCX templates for consistent formatting
- **Drag & Drop**: Intuitive file selection interface
- **Progress Tracking**: Real-time conversion progress monitoring
- **Smart Naming**: Automatic output file naming with conflict resolution

### Document Processing
- **Pandoc Integration**: Leverages Pandoc for high-quality document conversion
- **Emoji Handling**: Optional emoji removal for professional documents
- **Format Preservation**: Maintains Markdown formatting in Word output
- **Template Management**: Easy custom template addition and management

### User Interface
- **Multi-Language Support**: 11 languages supported
  - 简体中文, English, 繁體中文, Français, Español
  - Deutsch, Português, Русский, Italiano, 日本語, 한국어
- **Clean Design**: Google-inspired minimalist interface
- **Responsive Layout**: Adapts to different screen sizes
- **Cross-Platform**: Native look and feel on each platform

### Technical Features
- **Cross-Platform Architecture**: Single codebase for all platforms
- **Platform-Specific Storage**: Uses OS-standard directories for user data
- **Configuration Persistence**: Remembers settings and preferences
- **Error Handling**: Comprehensive error reporting and recovery
- **Background Processing**: Non-blocking UI during conversions

## 🔧 Technical Specifications

### System Requirements
- **Python**: 3.8 or later (bundled in releases)
- **Pandoc**: Must be installed separately
- **Memory**: 100MB RAM minimum
- **Storage**: 200MB disk space
- **Graphics**: Any system supporting Qt 6

### 平台要求

#### macOS
- **版本**: macOS 10.15 Catalina 或更高
- **架构**: Intel 和 Apple Silicon 均支持

#### Windows  
- **版本**: Windows 10 或更高
- **架构**: x64

#### Linux
- **发行版**: 现代 Linux 发行版 (推荐 2020年后发布的版本)
- **测试兼容**: Ubuntu 20.04+, Debian 11+, Fedora 35+, Arch Linux, openSUSE Leap 15.4+
- **技术要求**: glibc 2.31+, FUSE 支持

**较老 Linux 系统的替代方案**:
- 源码运行: `python src/main.py` (需要 Python 3.8+ 环境)
- 本地构建: 使用项目提供的构建脚本进行本地编译

### Dependencies (Bundled)
- **PySide6** 6.5.0+: Qt-based GUI framework
- **emoji** 2.2.0+: Emoji processing library
- **platformdirs** 3.0.0+: Cross-platform directory management

### External Dependencies
- **Pandoc**: Document conversion engine (install separately)
  - Minimum version: 2.0+
  - Recommended: Latest stable version

## 📦 Installation

### macOS
```bash
# Install from DMG
open md2docx-v1.0.0-macOS.dmg

# Install Pandoc
brew install pandoc
```

### Windows
```bash
# Extract and run
unzip md2docx-v1.0.0-Windows.zip
cd md2docx
md2docx.exe

# Install Pandoc from https://pandoc.org
```

### Linux
```bash
# AppImage (推荐) - 适用于现代发行版
chmod +x md2docx-v1.0.0-x86_64.AppImage
./md2docx-v1.0.0-x86_64.AppImage

# 便携版本
tar -xzf md2docx-v1.0.0-Linux.tar.gz
./md2docx/md2docx

# 安装 Pandoc
sudo apt install pandoc        # Ubuntu/Debian
sudo dnf install pandoc        # Fedora  
sudo pacman -S pandoc          # Arch
sudo zypper install pandoc     # openSUSE

# 较老系统的源码运行方式
git clone https://github.com/davidjia1972/md2docx.git
cd md2docx
pip install -r requirements.txt
python src/main.py
```

## 🗂️ File Locations

Application stores user data in platform-standard locations:

### Configuration Files
- **macOS**: `~/Library/Application Support/md2docx/`
- **Windows**: `%APPDATA%\md2docx\`
- **Linux**: `~/.config/md2docx/`

### Cache & Logs
- **macOS**: `~/Library/Caches/md2docx/`, `~/Library/Logs/md2docx/`
- **Windows**: `%LOCALAPPDATA%\md2docx\`
- **Linux**: `~/.cache/md2docx/`, `~/.local/share/md2docx/logs/`

### User Templates
Stored alongside configuration files in `templates/` subdirectory.

## 🛠️ Build Information

### Build Environment
- **Python**: 3.11.x
- **Build Tools**: 
  - macOS: py2app 0.28+
  - Windows/Linux: PyInstaller 5.13+
- **CI/CD**: GitHub Actions (planned)

### Package Details
- **Code Signing**: Available for macOS (developer certificate required)
- **Notarization**: macOS builds can be notarized for Gatekeeper
- **Windows Defender**: Builds are scanned and should be clean
- **VirusTotal**: Release artifacts are automatically scanned

## 📈 Performance

### Conversion Speed
- **Small files** (< 1MB): Near-instant
- **Medium files** (1-10MB): 1-5 seconds
- **Large files** (10MB+): Varies based on content complexity

### Memory Usage
- **Idle**: ~50MB RAM
- **Converting**: +20-100MB per file (depending on size)
- **Peak**: Generally < 200MB total

### Disk Usage
- **Application**: 80-150MB (varies by platform)
- **User data**: Minimal (configs + templates)
- **Cache**: Temporary files cleaned automatically

## 🔍 Known Issues

### Limitations
1. **Very large files** (>50MB) may cause UI freezing
2. **Complex tables** may not convert perfectly
3. **Custom CSS** in Markdown is not preserved
4. **Mathematical equations** require Pandoc with LaTeX support

### Platform-Specific Notes
- **macOS**: First launch may be slow due to security scanning
- **Windows**: Some antivirus software may flag the executable (false positive)
- **Linux**: AppImage may require FUSE on older systems

### Workarounds
- For large files: Use command-line Pandoc directly
- For complex formatting: Use simpler Markdown syntax
- For equations: Install LaTeX distribution (MiKTeX, MacTeX, etc.)

## 🔐 Security

### Application Signing
- **macOS**: Code signed with Developer ID (if available)
- **Windows**: Authenticode signature (planned for future releases)
- **Linux**: GPG signature for AppImage (planned)

### Data Privacy
- **No telemetry**: Application does not send any data externally
- **Local processing**: All conversions happen locally
- **No cloud dependencies**: Works completely offline

### File Permissions
- **Read access**: Source Markdown files only
- **Write access**: Output directory and user data directories
- **No system modification**: Application is self-contained

## 🤝 Contributing

This is the initial release. Future contributions welcome:
- **Bug reports**: GitHub Issues
- **Feature requests**: GitHub Discussions
- **Translations**: Additional language support
- **Code contributions**: Pull requests welcome

## 📋 Changelog Summary

Initial release - all features are new in v1.0.0.

## 🔮 Future Roadmap

Potential features for future releases:
- **Cloud templates**: Template sharing and download
- **Batch processing**: Command-line interface
- **Custom styling**: Enhanced template customization
- **Plugin system**: Extensible conversion pipeline
- **Real-time preview**: Live Markdown to Word preview

---

**Full package contents and checksums available in `checksums.txt`**