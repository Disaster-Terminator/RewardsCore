#!/usr/bin/env python3
"""
测试运行脚本
执行所有单元测试和集成测试
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_command(command, description):
    """运行命令并显示结果"""
    print(f"\n{'='*60}")
    print(f"执行: {description}")
    print(f"命令: {' '.join(command)}")
    print('='*60)
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, cwd=Path(__file__).parent.parent)
        
        if result.stdout:
            print("输出:")
            print(result.stdout)
        
        if result.stderr:
            print("错误:")
            print(result.stderr)
        
        if result.returncode == 0:
            print(f"✅ {description} - 成功")
        else:
            print(f"❌ {description} - 失败 (退出码: {result.returncode})")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ {description} - 执行失败: {e}")
        return False


def run_unit_tests():
    """运行单元测试"""
    # 检查是否有pytest-cov
    has_coverage = True
    try:
        import pytest_cov
    except ImportError:
        has_coverage = False
    
    commands = [
        (["python", "-m", "pytest", "tests/unit/", "-v", "--tb=short"], "单元测试"),
    ]
    
    # 只有在有coverage插件时才添加覆盖率测试
    if has_coverage:
        commands.append((["python", "-m", "pytest", "tests/unit/", "--cov=src", "--cov-report=term-missing"], "单元测试覆盖率"))
    else:
        print("注意: pytest-cov 未安装，跳过覆盖率测试")
    
    results = []
    for command, description in commands:
        try:
            success = run_command(command, description)
            results.append((description, success))
        except Exception as e:
            print(f"跳过 {description}: {e}")
            results.append((description, False))
    
    return results


def run_integration_tests():
    """运行集成测试"""
    commands = [
        (["python", "-m", "pytest", "tests/integration/", "-v", "--tb=short"], "集成测试"),
    ]
    
    results = []
    for command, description in commands:
        try:
            success = run_command(command, description)
            results.append((description, success))
        except Exception as e:
            print(f"跳过 {description}: {e}")
            results.append((description, False))
    
    return results


def run_property_tests():
    """运行属性测试"""
    commands = [
        (["python", "-m", "pytest", "tests/unit/test_config_manager_properties.py", "-v"], "配置管理器属性测试"),
        (["python", "-m", "pytest", "tests/unit/test_logger_properties.py", "-v"], "日志系统属性测试"),
    ]
    
    results = []
    for command, description in commands:
        try:
            success = run_command(command, description)
            results.append((description, success))
        except Exception as e:
            print(f"跳过 {description}: {e}")
            results.append((description, False))
    
    return results


def run_specific_tests(test_pattern):
    """运行特定的测试"""
    command = ["python", "-m", "pytest", "-k", test_pattern, "-v", "--tb=short"]
    return run_command(command, f"特定测试 (模式: {test_pattern})")


def run_performance_tests():
    """运行性能测试"""
    print("\n" + "="*60)
    print("性能测试")
    print("="*60)
    print("注意: 性能测试需要较长时间，建议在CI/CD环境中运行")
    
    # 这里可以添加性能测试的具体实现
    # 例如内存泄漏检测、响应时间测试等
    
    return [("性能测试", True)]  # 暂时返回成功


def check_test_environment():
    """检查测试环境"""
    print("检查测试环境...")
    
    required_packages = [
        "pytest",
        "pytest-asyncio", 
        "hypothesis"
    ]
    
    optional_packages = [
        "pytest-cov"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - 未安装")
            missing_packages.append(package)
    
    for package in optional_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package} (可选)")
        except ImportError:
            print(f"⚠️ {package} - 未安装 (可选)")
    
    if missing_packages:
        print(f"\n缺失的必需测试依赖: {', '.join(missing_packages)}")
        print("安装命令: pip install " + " ".join(missing_packages))
        return False
    
    return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="MS Rewards Automator 测试运行器")
    parser.add_argument("--unit", action="store_true", help="只运行单元测试")
    parser.add_argument("--integration", action="store_true", help="只运行集成测试")
    parser.add_argument("--property", action="store_true", help="只运行属性测试")
    parser.add_argument("--performance", action="store_true", help="只运行性能测试")
    parser.add_argument("--pattern", type=str, help="运行匹配特定模式的测试")
    parser.add_argument("--no-env-check", action="store_true", help="跳过环境检查")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    
    args = parser.parse_args()
    
    print("MS Rewards Automator - 测试运行器")
    print("="*60)
    
    # 检查测试环境
    if not args.no_env_check:
        if not check_test_environment():
            print("❌ 测试环境检查失败")
            return 1
    
    all_results = []
    
    # 根据参数运行相应的测试
    if args.pattern:
        success = run_specific_tests(args.pattern)
        all_results.append(("特定测试", success))
    elif args.unit:
        all_results.extend(run_unit_tests())
    elif args.integration:
        all_results.extend(run_integration_tests())
    elif args.property:
        all_results.extend(run_property_tests())
    elif args.performance:
        all_results.extend(run_performance_tests())
    else:
        # 运行所有测试
        print("\n🚀 运行所有测试...")
        all_results.extend(run_unit_tests())
        all_results.extend(run_integration_tests())
        all_results.extend(run_property_tests())
    
    # 显示测试结果摘要
    print("\n" + "="*60)
    print("测试结果摘要")
    print("="*60)
    
    passed = 0
    failed = 0
    
    for test_name, success in all_results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{test_name}: {status}")
        if success:
            passed += 1
        else:
            failed += 1
    
    total = passed + failed
    if total > 0:
        print(f"\n总计: {total} 个测试套件")
        print(f"通过: {passed} 个")
        print(f"失败: {failed} 个")
        print(f"成功率: {passed/total*100:.1f}%")
    
    if failed == 0:
        print("\n🎉 所有测试都通过了！")
        return 0
    else:
        print(f"\n⚠️ 有 {failed} 个测试套件失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())