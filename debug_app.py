#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用程序启动调试工具
帮助诊断为什么程序运行时看不到界面
"""

import sys
import os
from pathlib import Path

def check_environment():
    """检查运行环境"""
    print("🔍 环境检查:")
    print(f"  Python版本: {sys.version}")
    print(f"  平台: {sys.platform}")
    print(f"  工作目录: {os.getcwd()}")
    print(f"  脚本路径: {Path(__file__).absolute()}")
    print()

def check_pyside6():
    """检查PySide6"""
    print("📦 PySide6检查:")
    try:
        import PySide6
        print(f"  ✅ PySide6版本: {PySide6.__version__}")
        
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QGuiApplication
        print("  ✅ 核心模块导入成功")
    except ImportError as e:
        print(f"  ❌ PySide6导入失败: {e}")
        return False
    print()
    return True

def check_display():
    """检查显示环境"""
    print("🖥️  显示环境检查:")
    
    # 检查DISPLAY环境变量
    display = os.environ.get('DISPLAY')
    if display:
        print(f"  DISPLAY: {display}")
    else:
        print("  DISPLAY: 未设置")
    
    # 检查macOS特有的环境
    if sys.platform == "darwin":
        print("  平台: macOS")
        # 检查是否在Terminal.app中运行
        term_program = os.environ.get('TERM_PROGRAM')
        if term_program:
            print(f"  终端程序: {term_program}")
    
    print()

def test_simple_gui():
    """测试最简单的GUI"""
    print("🧪 测试最简单的GUI:")
    
    try:
        from PySide6.QtWidgets import QApplication, QLabel, QWidget
        
        # 创建应用
        app = QApplication(sys.argv)
        print("  ✅ QApplication创建成功")
        
        # 创建最简单的窗口
        window = QWidget()
        window.setWindowTitle("测试窗口")
        window.resize(300, 200)
        
        label = QLabel("如果你能看到这个窗口，说明GUI正常工作")
        label.setParent(window)
        label.move(20, 20)
        
        window.show()
        print("  ✅ 窗口应该已经显示")
        print("  📱 如果你能看到标题为'测试窗口'的窗口，请按Ctrl+C退出")
        
        # 运行5秒后自动退出
        from PySide6.QtCore import QTimer
        timer = QTimer()
        timer.timeout.connect(app.quit)
        timer.start(5000)  # 5秒
        
        return app.exec()
        
    except Exception as e:
        print(f"  ❌ GUI测试失败: {e}")
        return 1

def test_main_app():
    """测试主应用程序"""
    print("🚀 测试主应用程序:")
    
    try:
        # 添加src路径
        src_path = Path(__file__).parent / "src"
        sys.path.insert(0, str(src_path))
        
        print(f"  添加路径: {src_path}")
        
        # 导入测试
        from ui.main_window import MainWindow
        from PySide6.QtWidgets import QApplication
        
        print("  ✅ 主应用模块导入成功")
        
        # 创建应用
        app = QApplication(sys.argv)
        
        # 创建主窗口
        window = MainWindow()
        window.show()
        
        print("  ✅ 主窗口应该已经显示")
        print("  📱 如果你能看到主应用程序，请按Ctrl+C退出")
        
        # 运行10秒后自动退出
        from PySide6.QtCore import QTimer
        timer = QTimer()
        timer.timeout.connect(app.quit)
        timer.start(10000)  # 10秒
        
        return app.exec()
        
    except Exception as e:
        print(f"  ❌ 主应用测试失败: {e}")
        import traceback
        print(f"  错误详情: {traceback.format_exc()}")
        return 1

def main():
    print("🔧 应用程序启动调试工具")
    print("=" * 50)
    
    # 环境检查
    check_environment()
    
    # PySide6检查
    if not check_pyside6():
        print("❌ PySide6有问题，无法继续测试")
        return 1
    
    # 显示环境检查
    check_display()
    
    # 询问用户想进行哪种测试
    print("请选择测试类型:")
    print("1. 测试最简单的GUI (推荐先测试)")
    print("2. 测试主应用程序")
    print("3. 两个都测试")
    
    try:
        choice = input("请输入选择 (1/2/3): ").strip()
    except KeyboardInterrupt:
        print("\n用户取消")
        return 0
    
    if choice == "1":
        return test_simple_gui()
    elif choice == "2":
        return test_main_app()
    elif choice == "3":
        print("\n" + "=" * 30)
        result1 = test_simple_gui()
        if result1 == 0:
            print("\n简单GUI测试通过，继续测试主应用...")
            print("=" * 30)
            return test_main_app()
        else:
            print("\n简单GUI测试失败，跳过主应用测试")
            return result1
    else:
        print("无效选择，默认测试简单GUI")
        return test_simple_gui()

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n👋 用户中断，程序退出")
        sys.exit(0)