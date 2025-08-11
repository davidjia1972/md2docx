# Linux Compatibility Guide

## 📋 Supported Distributions

### ✅ Full Support (Recommended)
The following modern Linux distributions are tested and fully compatible with md2docx AppImage:

| Distribution | Version | Status |
|--------------|---------|---------|
| Ubuntu | 20.04 LTS, 22.04 LTS | ✅ Full Support |
| Debian | 11 (Bullseye), 12 (Bookworm) | ✅ Full Support |
| Fedora | 35+, 36+, 37+ | ✅ Full Support |
| Arch Linux | Rolling | ✅ Full Support |
| Manjaro | 21+ | ✅ Full Support |
| openSUSE Leap | 15.4+ | ✅ Full Support |
| Pop!_OS | 20.04+, 22.04+ | ✅ Full Support |
| Linux Mint | 20+ | ✅ Full Support |
| Elementary OS | 6+ | ✅ Full Support |

### ⚠️ May Require Additional Configuration
| Distribution | Version | Notes |
|--------------|---------|-------|
| CentOS Stream | 8+ | May need EPEL repository |
| RHEL | 8+ | May require additional packages |
| Alpine Linux | 3.15+ | May need gcompat installation |

### ❌ Unsupported Systems
| Distribution | Version | Alternative |
|--------------|---------|-------------|
| Ubuntu | 18.04 and earlier | Run from source |
| Debian | 10 and earlier | Run from source |
| CentOS | 7 and earlier | Run from source |
| RHEL | 7 and earlier | Run from source |

## 🔧 Technical Requirements

### Essential Components
- **glibc**: 2.31 or higher
- **FUSE**: Filesystem support (included by default in most modern distributions)
- **X11 or Wayland**: Graphics interface support

### Check System Compatibility
```bash
# Check glibc version
ldd --version | head -1

# Check FUSE support
modprobe fuse && echo "FUSE support OK" || echo "FUSE installation needed"

# Check distribution info
lsb_release -a 2>/dev/null || cat /etc/os-release
```

## 🚀 Installation Methods

### Method 1: AppImage (Recommended)
```bash
# Download and run
wget https://github.com/davidjia1972/md2docx/releases/latest/download/md2docx-v1.0.0-x86_64.AppImage
chmod +x md2docx-v1.0.0-x86_64.AppImage
./md2docx-v1.0.0-x86_64.AppImage
```

### Method 2: Portable Version
```bash
# Download and extract
wget https://github.com/davidjia1972/md2docx/releases/latest/download/md2docx-v1.0.0-Linux.tar.gz
tar -xzf md2docx-v1.0.0-Linux.tar.gz
./md2docx/md2docx
```

### Method 3: Run from Source (Universal)
Suitable for all Linux systems, including older distributions:

```bash
# Install Python and dependencies
sudo apt update && sudo apt install python3 python3-pip pandoc  # Ubuntu/Debian
sudo dnf install python3 python3-pip pandoc                    # Fedora
sudo pacman -S python python-pip pandoc                        # Arch
sudo zypper install python3 python3-pip pandoc                # openSUSE

# Clone project
git clone https://github.com/davidjia1972/md2docx.git
cd md2docx

# Install Python dependencies
pip3 install --user -r requirements.txt

# Run application
python3 src/main.py
```

## 🛠️ Troubleshooting

### Common Issues and Solutions

#### 1. FUSE-related Errors
```bash
# Error: fuse: device not found
# Solution
sudo modprobe fuse

# Or use extraction mode
./md2docx.AppImage --appimage-extract
./squashfs-root/md2docx
```

#### 2. Permission Issues
```bash
# Error: Permission denied
# Solution
chmod +x md2docx-v1.0.0-x86_64.AppImage
```

#### 3. glibc Version Too Old
```bash
# Error: version `GLIBC_2.XX' not found
# Solution: Use source code execution
python3 src/main.py
```

#### 4. Missing Graphics Libraries
```bash
# Ubuntu/Debian
sudo apt install libxcb-xinerama0 libxcb-cursor0

# Fedora
sudo dnf install libxcb xcb-util

# Arch
sudo pacman -S libxcb
```

## 📈 Feedback and Improvements

If you successfully run md2docx on a distribution not listed, please let us know through:

1. **GitHub Issues**: Report compatibility status
2. **System Information**: Include distribution name, version, kernel version
3. **Execution Method**: AppImage, portable, or source code

### Report Template
```
**Distribution**: [e.g., Ubuntu 22.04]
**Kernel Version**: Output of `uname -r`
**glibc Version**: Output of `ldd --version`
**Execution Method**: [AppImage/Portable/Source]
**Status**: [Success/Failure/Needs Additional Configuration]
**Notes**: [Issues encountered or solutions found]
```

## 💡 Recommendations

### For Regular Users
- **Recommended**: Use modern Linux distributions (Ubuntu 20.04+, Fedora 35+)
- **First Choice**: AppImage version, simple and easy to use
- **Fallback**: If AppImage doesn't work, try running from source

### For System Administrators
- **Enterprise Environment**: Recommend standardizing on supported modern distributions
- **Legacy Systems**: Use source deployment method
- **Containerization**: Can run modern versions in Docker

---

**Summary**: md2docx focuses on providing the best experience for modern Linux distributions while maintaining flexibility for older systems through source code execution. This strategy ensures software simplicity and maintainability without abandoning any users.

> **Language**: [English](LINUX_COMPATIBILITY.md) | [简体中文](LINUX_COMPATIBILITY_zh_CN.md)