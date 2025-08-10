#!/usr/bin/env python3
"""
翻译完整性检查工具

用法：
python check_translations.py                    # 检查所有语言
python check_translations.py --lang fr_FR      # 检查特定语言
python check_translations.py --critical        # 只检查关键翻译键
python check_translations.py --detailed        # 显示详细报告
"""

import sys
import argparse
from pathlib import Path

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from utils.i18n_manager import I18nManager

def main():
    parser = argparse.ArgumentParser(description='检查翻译完整性')
    parser.add_argument('--lang', help='指定要检查的语言代码 (如: fr_FR)')
    parser.add_argument('--critical', action='store_true', help='只检查关键翻译键')
    parser.add_argument('--detailed', action='store_true', help='显示详细报告')
    parser.add_argument('--stats', action='store_true', help='显示翻译统计')
    
    args = parser.parse_args()
    
    i18n = I18nManager()
    
    print("🌍 翻译完整性检查工具")
    print("=" * 50)
    
    # 获取要检查的语言列表
    if args.lang:
        if args.lang not in i18n.get_available_languages():
            print(f"❌ 语言 {args.lang} 不可用")
            return 1
        languages_to_check = [args.lang]
    else:
        languages_to_check = list(i18n.get_available_languages().keys())
    
    # 执行检查
    all_complete = True
    
    for lang_code in languages_to_check:
        print(f"\n🔍 检查语言: {lang_code}")
        
        if args.critical:
            # 只检查关键翻译键
            result = i18n.validate_critical_keys(lang_code)
            if result.get('error'):
                print(f"❌ 错误: {result['error']}")
                all_complete = False
                continue
            
            if result['critical_keys_complete']:
                print("✅ 所有关键翻译键完整")
            else:
                print(f"⚠️  缺失 {len(result['missing_critical_keys'])} 个关键翻译键")
                if args.detailed:
                    for key in result['missing_critical_keys']:
                        print(f"   - {key}")
                all_complete = False
        else:
            # 检查完整性
            result = i18n.validate_language_completeness(lang_code)
            if result.get('error'):
                print(f"❌ 错误: {result['error']}")
                all_complete = False
                continue
            
            ratio = result['completeness_ratio']
            if ratio == 1.0:
                print("✅ 语言包完整")
            else:
                print(f"📊 完整性: {ratio:.1%} ({result['present_keys']}/{result['total_keys']})")
                print(f"⚠️  缺失 {len(result['missing_keys'])} 个翻译键")
                
                if args.detailed and result['missing_keys']:
                    print("缺失的翻译键:")
                    for key in result['missing_keys'][:10]:  # 最多显示10个
                        print(f"   - {key}")
                    if len(result['missing_keys']) > 10:
                        print(f"   ... 还有 {len(result['missing_keys']) - 10} 个")
                
                all_complete = False
    
    # 显示统计信息
    if args.stats:
        print(f"\n📈 统计信息:")
        stats = i18n.get_translation_stats()
        if stats['missing_keys_count'] > 0 or stats['fallback_used_count'] > 0:
            print(f"运行时统计:")
            print(f"  缺失翻译键: {stats['missing_keys_count']}")
            print(f"  使用备用语言: {stats['fallback_used_count']}")
            print(f"  关键翻译缺失: {stats['critical_missing_count']}")
        else:
            print("  当前会话中没有翻译问题")
    
    print("\n" + "=" * 50)
    if all_complete:
        print("🎉 所有检查的语言都完整！")
        return 0
    else:
        print("⚠️  发现了一些翻译问题，请参考上面的报告")
        return 1

if __name__ == '__main__':
    sys.exit(main())