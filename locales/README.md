# 多语言支持 (Internationalization)

本目录包含应用程序的多语言文件，支持动态语言切换。

## 目录结构

```
locales/
├── zh_CN/          # 简体中文
│   └── messages.json
├── en_US/          # 英语
│   └── messages.json
└── README.md       # 本文件
```

## 支持的语言

- **zh_CN**: 简体中文 (默认)
- **en_US**: English (备用语言)

## 添加新语言

### 1. 创建语言目录

```bash
mkdir locales/[语言代码]
```

例如添加法语：
```bash
mkdir locales/fr_FR
```

### 2. 复制并翻译消息文件

```bash
cp locales/en_US/messages.json locales/fr_FR/messages.json
```

然后编辑 `locales/fr_FR/messages.json`，将所有英文文本翻译为法语。

### 3. 更新语言配置

编辑 `config/languages.json`，添加新语言：

```json
{
  "languages": {
    "fr_FR": {
      "name": "Français",
      "native_name": "Français",
      "enabled": true
    }
  },
  "system_language_mapping": {
    "fr": "fr_FR",
    "fr_FR": "fr_FR"
  }
}
```

### 4. 重启应用

重启应用程序，新语言将自动被检测并出现在语言选择下拉框中。

## 消息文件格式

消息文件使用 JSON 格式，支持嵌套结构和参数化文本：

```json
{
  "app": {
    "title": "应用标题",
    "name": "应用名称"
  },
  "ui": {
    "labels": {
      "file_stats": "📊 {count} 个文件"
    }
  }
}
```

### 参数化文本

使用 `{参数名}` 格式支持动态参数：

```json
{
  "message": "成功转换了 {count} 个文件"
}
```

在代码中调用：
```python
t("message", count=5)  # 输出: "成功转换了 5 个文件"
```

## 使用方法

### 在代码中使用翻译

```python
from utils.i18n_manager import t

# 基本翻译
title = t("app.title")

# 带参数的翻译
status = t("ui.labels.file_stats", count=10)
```

### 语言切换

用户可以通过界面中的语言选择下拉框切换语言：
- **自动检测**: 根据系统语言自动选择
- **手动选择**: 选择特定语言

语言设置会自动保存到配置文件中，下次启动时会记住用户的选择。

## 技术细节

- 语言包在需要时动态加载，不会影响启动性能
- 支持运行时语言切换，无需重启应用
- 如果翻译缺失，会自动回退到备用语言（英语）
- 支持系统语言自动检测和映射

## 贡献翻译

欢迎为应用程序贡献新的语言翻译：

1. 按照上述步骤添加新语言
2. 确保翻译准确和完整
3. 测试语言切换功能
4. 提交翻译文件

## 注意事项

- 所有翻译文件必须使用 UTF-8 编码
- JSON 语法必须正确，否则语言包无法加载
- 建议保持翻译的一致性和风格统一