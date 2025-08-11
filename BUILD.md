# md2docx 构建指南

本文档介绍如何构建和发布 md2docx 应用程序。

## 🚀 快速开始

### 基本构建

```bash
# 构建当前平台版本
python build.py

# 构建指定平台
python build.py macos
python build.py windows  
python build.py linux

# 构建所有平台
python build.py all
```

### 发布管理

```bash
# 显示发布信息
python release.py info

# 构建并打包发布版本
python release.py build all
python release.py package

# 清理构建产物
python release.py clean

# 交互式模式
python release.py --interactive
```

## 📁 项目结构

```
md2docx/
├── build.py                 # 跨平台构建脚本
├── release.py              # 发布管理脚本
├── VERSION                 # 版本号文件
├── packaging/              # 打包脚本
│   ├── build_utils.py      # 构建工具库
│   ├── macos/              # macOS 打包
│   │   ├── build_macos.sh  # 构建脚本
│   │   └── setup_py2app.py # py2app 配置
│   ├── windows/            # Windows 打包
│   │   ├── build_windows.bat
│   │   └── setup_pyinstaller.py
│   └── linux/              # Linux 打包
│       ├── build_linux.sh
│       └── setup_pyinstaller.py
├── releases/               # 发布产物
│   ├── README.md          # 发布说明
│   └── v1.0.0/            # 版本目录
│       ├── md2docx-v1.0.0-macOS.dmg
│       ├── md2docx-v1.0.0-Windows.zip
│       ├── md2docx-v1.0.0-Linux.tar.gz
│       ├── checksums.txt  # 校验和
│       └── RELEASE_NOTES.md
└── src/                   # 源代码
```

## 🛠️ 构建要求

### 基本依赖

- **Python**: 3.8 或更高版本
- **pip**: Python 包管理器
- **virtualenv**: 虚拟环境（推荐）

### 平台特定依赖

#### macOS
```bash
# 必需
pip install py2app

# 可选（用于 DMG 创建）
brew install create-dmg
```

#### Windows
```bash
# 必需
pip install pyinstaller

# 可选（用于安装程序）
# Inno Setup 或 NSIS
```

#### Linux
```bash
# 必需
pip install pyinstaller

# 可选（用于 AppImage）
wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
chmod +x appimagetool-x86_64.AppImage
sudo mv appimagetool-x86_64.AppImage /usr/local/bin/appimagetool
```

### 外部依赖

- **Pandoc**: 文档转换引擎
  - macOS: `brew install pandoc`
  - Windows: 从 https://pandoc.org 下载
  - Linux: `sudo apt install pandoc` (Ubuntu/Debian)

## 📦 构建流程

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd md2docx

# 创建虚拟环境
python -m venv build-env
source build-env/bin/activate  # Linux/macOS
# 或
build-env\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
pip install pyinstaller  # 或 py2app (macOS)
```

### 2. 开发构建

```bash
# 检查构建环境
python release.py info

# 构建当前平台
python build.py

# 测试应用
# macOS: open packaging/macos/dist/md2docx.app
# Windows: packaging/windows/dist/md2docx/md2docx.exe
# Linux: packaging/linux/dist/md2docx/md2docx
```

### 3. 发布构建

```bash
# 构建所有平台
python release.py build all

# 打包发布版本
python release.py package

# 验证发布包
ls -la releases/v1.0.0/
cat releases/v1.0.0/checksums.txt
```

## 🔧 构建配置

### 版本管理

版本号存储在 `VERSION` 文件中：
```bash
# 更新版本号
echo "1.1.0" > VERSION

# 构建指定版本
python release.py package --version 1.1.0
```

### 构建选项

```bash
# 显示构建过程但不执行
python release.py build all --dry-run

# 跳过校验和生成
python release.py package --no-checksums

# 交互式选择
python release.py --interactive
```

## 📋 构建产物说明

### macOS (.dmg)
- **格式**: 磁盘镜像文件
- **内容**: 标准 .app 应用包
- **安装**: 拖拽到 Applications 文件夹
- **大小**: ~80MB

### Windows (.zip)
- **格式**: 压缩归档文件
- **内容**: 可执行文件和依赖
- **安装**: 解压到任意目录
- **大小**: ~120MB

### Linux (.tar.gz + .AppImage)
- **格式**: 压缩归档 + 便携镜像
- **内容**: 二进制文件和依赖
- **安装**: 解压或直接运行 AppImage
- **大小**: ~90MB

## 🐛 故障排除

### 常见问题

#### 1. "pandoc not found"
```bash
# 确保 pandoc 已安装
pandoc --version

# 如果未安装，根据系统安装
brew install pandoc        # macOS
choco install pandoc       # Windows
sudo apt install pandoc   # Linux
```

#### 2. "py2app/pyinstaller not found"
```bash
# 安装构建工具
pip install py2app        # macOS
pip install pyinstaller   # Windows/Linux
```

#### 3. "Permission denied"
```bash
# 给脚本添加执行权限
chmod +x packaging/*/build_*.sh
chmod +x build.py release.py
```

#### 4. 构建失败
```bash
# 清理后重试
python release.py clean
python release.py build all
```

### 调试构建

```bash
# 查看详细构建日志
python build.py <platform> 2>&1 | tee build.log

# 检查构建环境
python -c "
import sys, platform
print(f'Python: {sys.version}')
print(f'Platform: {platform.system()}')
print(f'Architecture: {platform.machine()}')
"

# 验证依赖
python -c "
import PySide6
import emoji
import platformdirs
print('All dependencies OK')
"
```

## 🚢 CI/CD 集成

### GitHub Actions 示例

```yaml
name: Build and Release

on:
  push:
    tags: ['v*']

jobs:
  build-macos:
    runs-on: macos-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - run: pip install -r requirements.txt py2app
    - run: brew install pandoc create-dmg
    - run: python build.py macos
    - uses: actions/upload-artifact@v3
      with:
        name: macos-build
        path: releases/v*/md2docx-*-macOS.dmg

  build-windows:
    runs-on: windows-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.11'  
    - run: pip install -r requirements.txt pyinstaller
    - run: python build.py windows
    - uses: actions/upload-artifact@v3
      with:
        name: windows-build
        path: releases/v*/md2docx-*-Windows.zip

  build-linux:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - run: |
        sudo apt update
        sudo apt install -y pandoc
        pip install -r requirements.txt pyinstaller
    - run: python build.py linux
    - uses: actions/upload-artifact@v3
      with:
        name: linux-build
        path: releases/v*/md2docx-*-Linux.*
```

## 📚 参考资料

- [py2app Documentation](https://py2app.readthedocs.io/)
- [PyInstaller Manual](https://pyinstaller.readthedocs.io/)
- [AppImage Documentation](https://docs.appimage.org/)
- [Pandoc Installation](https://pandoc.org/installing.html)
- [PySide6 Deployment](https://doc.qt.io/qtforpython/deployment.html)

---

**构建成功后，在 `releases/v1.0.0/` 目录中找到分发文件！**