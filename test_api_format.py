"""
测试正确的GLM-4V-Flash API调用格式
基于用户提供的官方示例
"""

import os
import json
from zhipuai import ZhipuAI

def test_api_format():
    """测试API格式"""
    print("[Test] 测试GLM-4V-Flash API格式...")
    
    # 使用真实的API Key
    api_key = "17e5feb32ed94b66823c9f9e0f188752.XOQDn1kygRTltwfD"
    client = ZhipuAI(api_key=api_key)
    
    # 使用一个公开的测试图片URL
    test_image_url = "https://raw.githubusercontent.com/microsoft/TypeScript/main/doc/spec-FORMATTING.md"
    
    print(f"[Test] 使用测试URL: {test_image_url}")
    
    try:
        # 按照用户提供的格式调用
        response = client.chat.completions.create(
            model="glm-4v-flash",
            messages=[
               {
                "role": "user",
                "content": [
                  {
                    "type": "text",
                    "text": "请仔细描述这个图片"
                  },
                  {
                    "type": "image_url",
                    "image_url": {
                        "url": test_image_url
                    }
                  }
                ]
              }
            ],
            top_p=0.7,
            temperature=0.95,
            max_tokens=1024,
            stream=False  # 先用False测试
        )
        
        print(f"[Test] API调用成功")
        print(f"[Test] 响应类型: {type(response)}")
        
        if hasattr(response, 'choices') and response.choices:
            content = response.choices[0].message.content
            print(f"[Test] 识别结果: {content[:200]}...")
            return True
        else:
            print(f"[Test] 响应格式异常: {response}")
            return False
            
    except Exception as e:
        print(f"[Test] API调用失败: {e}")
        print(f"[Test] 错误类型: {type(e)}")
        return False

if __name__ == "__main__":
    result = test_api_format()
    print(f"\n[Test] 测试结果: {result}")