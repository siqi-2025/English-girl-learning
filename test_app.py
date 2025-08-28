"""
英语学习助手 - 本地测试版
不依赖网络连接，仅测试基础功能
"""

print("=== 英语学习助手测试启动 ===")

import sys
import os
from pathlib import Path

def test_environment():
    """测试运行环境"""
    print("\n🔍 环境检查:")
    print(f"✅ Python版本: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    print(f"✅ 工作目录: {os.getcwd()}")
    
    # 检查API密钥
    api_key = os.environ.get("ENGLISH_LEARNING_ZHIPU_API_KEY")
    if api_key:
        print(f"✅ API密钥已配置: {api_key[:8]}...")
    else:
        print("⚠️  API密钥未配置")
        print("   请运行: set ENGLISH_LEARNING_ZHIPU_API_KEY=your_key")
    
    return True

def test_modules():
    """测试模块导入"""
    print("\n📦 模块测试:")
    
    modules = [
        ("os", "操作系统接口"),
        ("sys", "系统相关"),
        ("pathlib", "路径处理"),
        ("json", "JSON处理"),
        ("io", "输入输出"),
        ("PIL", "图像处理"),
        ("numpy", "数值计算"),
        ("cv2", "OpenCV"),
        ("streamlit", "Web框架"),
        ("requests", "HTTP客户端")
    ]
    
    success_count = 0
    for module_name, description in modules:
        try:
            __import__(module_name)
            print(f"✅ {module_name}: {description}")
            success_count += 1
        except ImportError:
            print(f"❌ {module_name}: 未安装")
        except Exception as e:
            print(f"⚠️  {module_name}: {e}")
    
    print(f"\n📊 模块状态: {success_count}/{len(modules)} 可用")
    return success_count >= 5  # 至少需要5个基础模块

def test_project_structure():
    """测试项目结构"""
    print("\n📁 项目结构:")
    
    required_files = [
        "streamlit_app.py",
        "src/core/ocr_processor.py",
        "src/core/ai_analyzer.py", 
        "src/core/document_generator.py",
        "src/ui/main_interface.py",
        "src/utils/config.py",
        "requirements.txt"
    ]
    
    project_root = Path(__file__).parent
    success_count = 0
    
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
            success_count += 1
        else:
            print(f"❌ {file_path}")
    
    print(f"\n📊 文件状态: {success_count}/{len(required_files)} 存在")
    return success_count >= 4

def test_basic_functionality():
    """测试基础功能"""
    print("\n🧪 功能测试:")
    
    # 测试配置管理
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from src.utils.config import config
        
        print("✅ 配置模块导入成功")
        
        # 测试配置读取
        api_key = config.get_api_key()
        if api_key:
            print(f"✅ API密钥读取成功: {api_key[:8]}...")
        else:
            print("⚠️  API密钥未配置")
            
        base_url = config.get("ai.base_url", "默认值")
        print(f"✅ 配置读取成功: base_url={base_url}")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("英语学习助手 - AI增强OCR系统")
    print("本地环境测试工具")
    
    # 运行所有测试
    tests = [
        ("环境检查", test_environment),
        ("模块测试", test_modules),
        ("项目结构", test_project_structure),
        ("基础功能", test_basic_functionality)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ {test_name} 执行失败: {e}")
            results.append(False)
    
    # 总结
    print("\n" + "="*50)
    print("📋 测试总结:")
    success_count = sum(results)
    total_count = len(results)
    
    if success_count == total_count:
        print("🎉 所有测试通过！系统准备就绪")
        print("\n🚀 下一步操作:")
        print("   1. 设置API密钥: set ENGLISH_LEARNING_ZHIPU_API_KEY=your_key")
        print("   2. 运行应用: python -m streamlit run streamlit_app.py")
    elif success_count >= 2:
        print("⚠️  部分测试通过，系统基本可用")
        print(f"   成功率: {success_count}/{total_count}")
        print("\n🔧 建议操作:")
        print("   1. 安装缺失的依赖包")
        print("   2. 检查项目文件完整性")
    else:
        print("❌ 多项测试失败，系统需要修复")
        print(f"   成功率: {success_count}/{total_count}")
        print("\n🆘 必要操作:")
        print("   1. 重新安装Python依赖")
        print("   2. 检查项目结构")
        print("   3. 验证网络环境")
    
    print("="*50)
    return success_count >= 2

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)