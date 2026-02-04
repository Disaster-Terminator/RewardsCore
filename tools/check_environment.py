#!/usr/bin/env python3
"""
环境依赖检查脚本
验证 Python 版本、Playwright 浏览器和必需的 Python 包
"""

import sys
import subprocess
from pathlib import Path


def check_python_version():
    """检查 Python 版本是否 >= 3.8"""
    print("检查 Python 版本...")
    version = sys.version_info
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 版本过低: {version.major}.{version.minor}.{version.micro}")
        print("   需要 Python 3.8 或更高版本")
        return False
    
    print(f"✓ Python 版本: {version.major}.{version.minor}.{version.micro}")
    return True


def check_package_imports():
    """检查必需的 Python 包是否可以导入"""
    print("\n检查 Python 包...")
    
    required_packages = {
        'playwright': 'playwright',
        'playwright_stealth': 'playwright-stealth',
        'yaml': 'pyyaml',
        'aiohttp': 'aiohttp',
        'bs4': 'beautifulsoup4',
        'hypothesis': 'hypothesis',
        'pytest': 'pytest',
        'pytest_asyncio': 'pytest-asyncio',
    }
    
    missing_packages = []
    
    for module_name, package_name in required_packages.items():
        try:
            __import__(module_name)
            print(f"✓ {package_name}")
        except ImportError:
            print(f"❌ {package_name} - 未安装")
            missing_packages.append(package_name)
    
    if missing_packages:
        print("\n缺失的包:")
        for pkg in missing_packages:
            print(f"  - {pkg}")
        print("\n安装命令:")
        print(f"  pip install {' '.join(missing_packages)}")
        return False
    
    return True


def check_playwright_browsers():
    """检查 Playwright 浏览器是否已安装"""
    print("\n检查 Playwright 浏览器...")
    
    try:
        # 尝试导入 playwright 并检查浏览器
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            # 尝试启动 chromium 来验证是否已安装
            try:
                browser = p.chromium.launch(headless=True)
                browser.close()
                print("✓ Playwright 浏览器已安装")
                return True
            except Exception:
                print("❌ Playwright 浏览器未安装")
                print("\n安装命令:")
                print("  playwright install chromium")
                print("  或")
                print("  python -m playwright install chromium")
                return False
                
    except ImportError:
        print("❌ Playwright 未安装")
        print("\n安装命令:")
        print("  pip install playwright")
        print("  playwright install chromium")
        return False
    except Exception as e:
        print(f"⚠ 无法检查浏览器状态: {e}")
        print("  请手动运行: playwright install chromium")
        return False


def check_project_structure():
    """检查项目目录结构"""
    print("\n检查项目结构...")
    
    required_dirs = ['src', 'tests', 'logs', 'docs', 'scripts']
    required_files = ['requirements.txt', 'environment.yml', 'config.yaml']
    
    all_exist = True
    
    for dir_name in required_dirs:
        if Path(dir_name).exists():
            print(f"✓ {dir_name}/")
        else:
            print(f"❌ {dir_name}/ - 目录不存在")
            all_exist = False
    
    for file_name in required_files:
        if Path(file_name).exists():
            print(f"✓ {file_name}")
        else:
            print(f"⚠ {file_name} - 文件不存在")
    
    return all_exist


def main():
    """主函数"""
    print("=" * 50)
    print("MS Rewards Automator - 环境依赖检查")
    print("=" * 50)
    print()
    
    checks = [
        ("Python 版本", check_python_version),
        ("Python 包", check_package_imports),
        ("Playwright 浏览器", check_playwright_browsers),
        ("项目结构", check_project_structure),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ 检查 {name} 时出错: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 50)
    print("检查结果汇总")
    print("=" * 50)
    
    all_passed = True
    for name, result in results:
        status = "✓ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
        if not result:
            all_passed = False
    
    print()
    
    if all_passed:
        print("✅ 所有检查通过！环境配置正确。")
        print("\n下一步:")
        print("  python main.py")
        return 0
    else:
        print("⚠ 部分检查未通过，请按照上述提示修复。")
        print("\n常见解决方案:")
        print("1. 安装依赖: pip install -r requirements.txt")
        print("2. 安装浏览器: playwright install")
        print("3. 或使用 Conda: bash setup_env.sh")
        return 1


if __name__ == "__main__":
    sys.exit(main())
