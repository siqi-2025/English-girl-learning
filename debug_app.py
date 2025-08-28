"""
调试应用中的AI连接问题
"""

import sys
import os
from pathlib import Path

# 设置API密钥环境变量
os.environ["ENGLISH_LEARNING_ZHIPU_API_KEY"] = "17e5feb32ed94b66823c9f9e0f188752.XOQDn1kygRTltwfD"

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("=" * 60)
print("调试AI连接问题")
print("=" * 60)

# 步骤1：检查环境变量
print("\n1. 检查环境变量")
env_key = os.getenv("ENGLISH_LEARNING_ZHIPU_API_KEY")
print(f"   环境变量 ENGLISH_LEARNING_ZHIPU_API_KEY: {bool(env_key)}")
if env_key:
    print(f"   API Key长度: {len(env_key)}")
    print(f"   API Key前缀: {env_key[:8]}...")

# 步骤2：测试配置模块
print("\n2. 测试配置模块")
try:
    from src.utils.config import config
    print("   ✓ 配置模块导入成功")
    
    api_key = config.get_api_key()
    print(f"   config.get_api_key(): {bool(api_key)}")
    if api_key:
        print(f"   API Key长度: {len(api_key)}")
        print(f"   API Key前缀: {api_key[:8]}...")
    
    base_url = config.get("ai.base_url")
    model = config.get("ai.model")
    print(f"   Base URL: {base_url}")
    print(f"   Model: {model}")
    
except Exception as e:
    print(f"   ✗ 配置模块错误: {e}")
    import traceback
    traceback.print_exc()

# 步骤3：测试AI客户端初始化
print("\n3. 测试AI客户端初始化")
try:
    from src.core.ai_analyzer import ZhipuAIClient
    print("   ✓ AI模块导入成功")
    
    client = ZhipuAIClient()
    print("   ✓ 客户端创建成功")
    print(f"   客户端API Key: {bool(client.api_key)}")
    print(f"   客户端Base URL: {client.base_url}")
    print(f"   客户端Model: {client.model}")
    
except Exception as e:
    print(f"   ✗ AI客户端错误: {e}")
    import traceback
    traceback.print_exc()

# 步骤4：测试AI连接
print("\n4. 测试AI连接")
try:
    from src.core.ai_analyzer import test_ai_connection
    print("   调用 test_ai_connection()...")
    result = test_ai_connection()
    print(f"   连接测试结果: {result}")
    
except Exception as e:
    print(f"   ✗ 连接测试错误: {e}")
    import traceback
    traceback.print_exc()

# 步骤5：直接测试API请求
print("\n5. 直接测试API请求")
try:
    import requests
    import json
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {env_key}"
    }
    
    payload = {
        "model": "glm-4-flash",
        "messages": [{"role": "user", "content": "测试"}],
        "temperature": 0.7,
        "max_tokens": 10,
        "stream": False
    }
    
    print("   发送请求到智普AI...")
    response = requests.post(
        "https://open.bigmodel.cn/api/paas/v4/chat/completions",
        headers=headers,
        json=payload,
        timeout=10
    )
    
    print(f"   响应状态码: {response.status_code}")
    if response.status_code == 200:
        print("   ✓ API直接请求成功")
    else:
        print(f"   ✗ API请求失败: {response.text[:200]}")
        
except Exception as e:
    print(f"   ✗ 直接请求错误: {e}")

print("\n" + "=" * 60)
print("调试完成")
print("=" * 60)