# Linux 兼容性说明

## 📋 支持的发行版

### ✅ 完全支持（推荐）
以下现代 Linux 发行版经过测试，完全兼容 md2docx AppImage：

| 发行版 | 版本 | 状态 |
|--------|------|------|
| Ubuntu | 20.04 LTS, 22.04 LTS | ✅ 完全支持 |
| Debian | 11 (Bullseye), 12 (Bookworm) | ✅ 完全支持 |
| Fedora | 35+, 36+, 37+ | ✅ 完全支持 |
| Arch Linux | Rolling | ✅ 完全支持 |
| Manjaro | 21+ | ✅ 完全支持 |
| openSUSE Leap | 15.4+ | ✅ 完全支持 |
| Pop!_OS | 20.04+, 22.04+ | ✅ 完全支持 |
| Linux Mint | 20+ | ✅ 完全支持 |
| Elementary OS | 6+ | ✅ 完全支持 |

### ⚠️ 可能需要额外配置
| 发行版 | 版本 | 说明 |
|--------|------|------|
| CentOS Stream | 8+ | 可能需要启用 EPEL 仓库 |
| RHEL | 8+ | 可能需要额外的软件包 |
| Alpine Linux | 3.15+ | 可能需要安装 gcompat |

### ❌ 不支持的系统
| 发行版 | 版本 | 替代方案 |
|--------|------|----------|
| Ubuntu | 18.04 及更早 | 源码运行 |
| Debian | 10 及更早 | 源码运行 |
| CentOS | 7 及更早 | 源码运行 |
| RHEL | 7 及更早 | 源码运行 |

## 🔧 技术要求

### 必需组件
- **glibc**: 2.31 或更高版本
- **FUSE**: 文件系统支持（大多数现代发行版默认包含）
- **X11 或 Wayland**: 图形界面支持

### 检查系统兼容性
```bash
# 检查 glibc 版本
ldd --version | head -1

# 检查 FUSE 支持
modprobe fuse && echo "FUSE 支持正常" || echo "需要安装 FUSE"

# 检查发行版信息
lsb_release -a 2>/dev/null || cat /etc/os-release
```

## 🚀 使用方法

### 方法一：AppImage（推荐）
```bash
# 下载并运行
wget https://github.com/davidjia1972/md2docx/releases/latest/download/md2docx-v1.0.0-x86_64.AppImage
chmod +x md2docx-v1.0.0-x86_64.AppImage
./md2docx-v1.0.0-x86_64.AppImage
```

### 方法二：便携版
```bash
# 下载并解压
wget https://github.com/davidjia1972/md2docx/releases/latest/download/md2docx-v1.0.0-Linux.tar.gz
tar -xzf md2docx-v1.0.0-Linux.tar.gz
./md2docx/md2docx
```

### 方法三：源码运行（通用）
适用于所有 Linux 系统，包括较老的发行版：

```bash
# 安装 Python 和依赖
sudo apt update && sudo apt install python3 python3-pip pandoc  # Ubuntu/Debian
sudo dnf install python3 python3-pip pandoc                    # Fedora
sudo pacman -S python python-pip pandoc                        # Arch
sudo zypper install python3 python3-pip pandoc                # openSUSE

# 克隆项目
git clone https://github.com/davidjia1972/md2docx.git
cd md2docx

# 安装 Python 依赖
pip3 install --user -r requirements.txt

# 运行应用
python3 src/main.py
```

## 🛠️ 故障排除

### 常见问题及解决方案

#### 1. FUSE 相关错误
```bash
# 错误：fuse: device not found
# 解决方案
sudo modprobe fuse

# 或者使用解压运行模式
./md2docx.AppImage --appimage-extract
./squashfs-root/md2docx
```

#### 2. 权限问题
```bash
# 错误：Permission denied
# 解决方案
chmod +x md2docx-v1.0.0-x86_64.AppImage
```

#### 3. glibc 版本过低
```bash
# 错误：version `GLIBC_2.XX' not found
# 解决方案：使用源码运行
python3 src/main.py
```

#### 4. 缺少图形库
```bash
# Ubuntu/Debian
sudo apt install libxcb-xinerama0 libxcb-cursor0

# Fedora
sudo dnf install libxcb xcb-util

# Arch
sudo pacman -S libxcb
```

## 📈 反馈和改进

如果您在未列出的 Linux 发行版上成功运行了 md2docx，请通过以下方式告诉我们：

1. **GitHub Issues**: 报告兼容性状况
2. **系统信息**: 包含发行版名称、版本、内核版本
3. **运行方式**: AppImage、便携版或源码运行

### 报告模板
```
**发行版**: [如 Ubuntu 22.04]
**内核版本**: `uname -r` 输出
**glibc 版本**: `ldd --version` 输出
**运行方式**: [AppImage/便携版/源码]
**状态**: [成功/失败/需要额外配置]
**备注**: [遇到的问题或解决方案]
```

## 💡 建议

### 对于普通用户
- **推荐**：使用现代 Linux 发行版（Ubuntu 20.04+, Fedora 35+）
- **首选**：AppImage 版本，简单易用
- **备选**：如果 AppImage 不工作，尝试源码运行

### 对于系统管理员
- **企业环境**：建议统一使用支持的现代发行版
- **Legacy 系统**：使用源码部署方式
- **容器化**：可以在 Docker 中运行现代版本

---

**总结**：md2docx 专注于支持现代 Linux 发行版的最佳体验，同时为较老系统提供源码运行的灵活性。这种策略确保了软件的简洁性和维护性，同时不遗弃任何用户。

> **语言**: [English](LINUX_COMPATIBILITY.md) | [简体中文](LINUX_COMPATIBILITY_zh_CN.md)