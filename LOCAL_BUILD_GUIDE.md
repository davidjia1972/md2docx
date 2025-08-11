# 本地构建指南

本指南解决了在本地环境中构建md2docx时遇到的PEP 517和兼容性问题。

## 问题背景

在本地构建时可能遇到以下错误：
- `Requirements should be satisfied by a PEP 517 installer`
- `RecursionError: maximum recursion depth exceeded`
- `'pathlib' package is an obsolete backport`
- py2app与PySide6的兼容性问题

## 解决方案

### 方法一：使用PyInstaller（推荐）

PyInstaller对PySide6的支持比py2app更好，是推荐的本地构建方案。

#### 快速构建
```bash
# 直接运行PyInstaller构建脚本
python build_macos_pyinstaller.py
```

#### 手动构建步骤
1. **安装PyInstaller**
   ```bash
   pip install --upgrade pyinstaller>=5.13
   ```

2. **移除冲突的pathlib包**
   ```bash
   pip uninstall pathlib -y
   ```

3. **运行构建命令**
   ```bash
   python -m PyInstaller \
       --name md2docx \
       --windowed \
       --onedir \
       --icon assets/icons/app_icon.icns \
       --add-data "locales:locales" \
       --add-data "templates:templates" \
       --add-data "assets/icons:assets/icons" \
       --hidden-import PySide6.QtCore \
       --hidden-import PySide6.QtWidgets \
       --hidden-import PySide6.QtGui \
       --hidden-import emoji \
       --hidden-import platformdirs \
       --hidden-import ui \
       --hidden-import ui.main_window \
       --hidden-import converter \
       --hidden-import utils \
       --hidden-import templates \
       --exclude-module tkinter \
       --exclude-module matplotlib \
       --exclude-module numpy \
       --exclude-module scipy \
       --exclude-module PIL \
       src/main.py
   ```

#### 构建结果
- 输出位置: `dist/md2docx.app`
- 应用大小: ~107MB
- 包含所有依赖和资源文件

### 方法二：通用构建脚本（备用）

如果需要跨平台构建能力，可以使用改进的构建脚本：

```bash
# 运行通用构建脚本
python build_local.py

# 或指定平台
python build_local.py macos
python build_local.py windows
python build_local.py linux
```

该脚本特点：
- 自动检测和修复PEP 517问题
- 升级构建工具到兼容版本
- 处理setuptools依赖冲突
- 支持多平台构建

### 方法三：简化py2app（实验性）

对于特殊需求，可以尝试简化的py2app方案：

```bash
cd packaging/macos
python setup_simple.py py2app
```

**注意**：此方法可能因PySide6兼容性问题而失败。

## 常见问题解决

### 1. PEP 517兼容性错误

**错误信息**：
```
Requirements should be satisfied by a PEP 517 installer.
If you are using pip, you can try `pip install --use-pep517`.
```

**解决方案**：
```bash
# 升级构建工具
pip install --upgrade pip setuptools wheel build

# 使用PEP 517模式安装
pip install --use-pep517 -r requirements.txt
```

### 2. pathlib包冲突

**错误信息**：
```
ERROR: The 'pathlib' package is an obsolete backport
```

**解决方案**：
```bash
pip uninstall pathlib -y
```

### 3. 递归深度超限

**错误信息**：
```
RecursionError: maximum recursion depth exceeded
```

**解决方案**：
- 切换到PyInstaller而不是py2app
- 或在脚本中增加递归限制：`sys.setrecursionlimit(5000)`

### 4. 模块导入失败

**错误信息**：
```
No module named 'ui'
```

**解决方案**：添加hidden-import参数
```bash
--hidden-import ui
--hidden-import ui.main_window
--hidden-import converter
--hidden-import utils
--hidden-import templates
```

### 5. setuptools依赖冲突

**解决方案**：安装缺失的依赖包
```bash
pip install --upgrade backports.tarfile jaraco.context importlib-metadata
```

## 环境要求

### macOS
- macOS 10.15+ 
- Python 3.8+
- Xcode Command Line Tools
- PyInstaller 5.13+ 或 py2app 0.28+

### 推荐环境配置
```bash
# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
pip install pyinstaller>=5.13
```

## 构建输出说明

### 成功构建的标志
```
✅ macOS应用构建成功: /path/to/dist/md2docx.app
✅ 应用大小: 107M
🎉 构建完成!
```

### 使用构建的应用
1. **测试运行**：`open dist/md2docx.app`
2. **安装到Applications**：`cp -r dist/md2docx.app /Applications/`
3. **安装Pandoc**：`brew install pandoc`

### 文件结构
```
dist/
└── md2docx.app/
    ├── Contents/
    │   ├── Info.plist
    │   ├── MacOS/
    │   │   └── md2docx         # 主执行文件
    │   └── Resources/
    │       ├── locales/        # 翻译文件
    │       ├── templates/      # DOCX模板
    │       └── assets/         # 图标资源
    └── ...
```

## 性能优化

### 减小应用大小
- 使用`--exclude-module`排除不需要的库
- 考虑使用`--onefile`创建单文件应用（启动较慢）
- 移除development依赖

### 提高构建速度
- 使用虚拟环境减少依赖扫描
- 缓存构建结果
- 并行化构建过程

## 故障排除

如果仍有问题，可以：

1. **查看详细日志**：添加`--debug`参数到PyInstaller命令
2. **清理缓存**：删除`build/`和`dist/`目录后重新构建
3. **验证依赖**：确保所有required packages已正确安装
4. **测试源码**：先确保`python src/main.py`能正常运行

## 联系支持

如果遇到无法解决的构建问题，请：
- 查看GitHub Issues页面
- 提供详细的错误日志和环境信息
- 说明操作系统版本和Python版本

---

**注意**：此指南专门解决本地构建中的PEP 517兼容性问题。对于生产发布，仍建议使用GitHub Actions进行自动化构建。