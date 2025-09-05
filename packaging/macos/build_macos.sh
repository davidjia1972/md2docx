#!/bin/bash
# macOS构建脚本 - 调用项目统一构建系统

set -e

echo "🍎 macOS构建 - 使用统一构建系统"

# 获取项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

echo "项目根目录: $PROJECT_ROOT"

# 使用项目统一的构建脚本
cd "$PROJECT_ROOT"
python3 build.py macos

echo "✅ macOS构建完成！"