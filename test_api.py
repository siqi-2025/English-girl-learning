"""
测试智普AI API连接
"""

import os
import requests
import json

# 直接设置API密钥
API_KEY = "17e5feb32ed94b66823c9f9e0f188752.XOQDn1kygRTltwfD"
BASE_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

def test_zhipu_api():
    """测试智普AI API连接"""
    print("=" * 60)
    print("测试智普AI API连接")
    print("=" * 60)
    
    print(f"API Key: {API_KEY[:8]}...")
    print(f"API Key长度: {len(API_KEY)}")
    print(f"Base URL: {BASE_URL}")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    payload = {
        "model": "glm-4-flash",  # 使用免费的flash模型
        "messages": [
            {
                "role": "user",
                "content": "你好"
            }
        ],
        "temperature": 0.7,
        "top_p": 0.8,
        "max_tokens": 10,
        "stream": False
    }
    
    print("\n发送测试请求...")
    print(f"Headers: {headers}")
    print(f"Payload: {json.dumps(payload, ensure_ascii=False, indent=2)}")
    
    try:
        response = requests.post(
            BASE_URL,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"\n响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("[成功] API连接成功!")
            result = response.json()
            print(f"响应内容: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
            # 尝试提取回复内容
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                print(f"\nAI回复: {content}")
        else:
            print(f"[失败] API返回错误")
            print(f"响应内容: {response.text}")
            
            # 尝试解析错误信息
            try:
                error_data = response.json()
                if "error" in error_data:
                    print(f"错误详情: {error_data['error']}")
            except:
                pass
                
    except requests.exceptions.Timeout:
        print("[失败] 请求超时")
    except requests.exceptions.ConnectionError:
        print("[失败] 无法连接到API服务器")
    except Exception as e:
        print(f"[失败] 发生异常: {e}")
    
    print("=" * 60)

if __name__ == "__main__":
    test_zhipu_api()