# GitHub Actions 工作流

此目录包含 md2docx 项目的自动化构建和发布工作流。

## 📁 工作流文件

### `build-release.yml`
主要的跨平台构建和发布工作流。

**触发条件**：
- 推送 `v*.*.*` 格式的标签
- 手动触发

**构建平台**：
- Ubuntu (Linux + AppImage)
- Windows (ZIP 包)
- macOS (DMG 安装包)

**输出**：
- 自动创建 GitHub Release
- 上传三平台安装包
- 生成 SHA256 校验和

## 🚀 快速使用

```bash
# 发布新版本
git tag v1.1.0
git push origin v1.1.0

# 等待 15-25 分钟
# 在 GitHub Releases 查看结果
```

## 📚 详细文档

- 完整使用指南：[GITHUB_ACTIONS.md](../../GITHUB_ACTIONS.md)
- 构建脚本文档：[BUILD.md](../../BUILD.md)
- 项目架构说明：[CLAUDE.md](../../CLAUDE.md)

## 🔧 维护

定期检查和更新：
- Actions 版本 (`actions/checkout@v4` 等)
- Python 版本 (`3.11`)
- 平台依赖版本

## 💰 成本

- **公开仓库**：完全免费 ✅
- **私有仓库**：每月 2000 分钟免费额度
- **单次构建**：约消耗 15-25 分钟