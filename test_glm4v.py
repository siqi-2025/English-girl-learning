"""
GLM-4V-Flash API测试脚本
版本: v1.2.0
"""

import os
import base64
from zhipuai import ZhipuAI

def encode_image_to_base64(image_path):
    """将图片编码为base64格式"""
    try:
        with open(image_path, 'rb') as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return f"data:image/jpeg;base64,{encoded_string}"
    except Exception as e:
        print(f"图片编码失败: {e}")
        return None

def test_glm4v_flash():
    """测试GLM-4V-Flash API"""
    
    # 设置API密钥
    api_key = "17e5feb32ed94b66823c9f9e0f188752.XOQDn1kygRTltwfD"
    
    print(f"[测试] 初始化GLM-4V-Flash客户端")
    
    try:
        client = ZhipuAI(api_key=api_key)
        print(f"[测试] 客户端初始化成功")
    except Exception as e:
        print(f"[测试] 客户端初始化失败: {e}")
        return False
    
    # 测试用的提示词 - 简化提示
    test_prompt = "请仔细描述这个图片"
    
    # 使用一个简单的测试图片URL
    test_image_url = "https://pic1.zhimg.com/80/v2-5b2b7c2e5e4f4b4a3c7b6a4e9d8c8a4e_720w.webp"
    
    test_messages = [
        {
            "role": "user", 
            "content": [
                {
                    "type": "text",
                    "text": test_prompt
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": test_image_url
                    }
                }
            ]
        }
    ]
    
    print(f"[测试] 调用GLM-4V-Flash API")
    print(f"[测试] 模型: glm-4v-flash")
    print(f"[测试] 消息格式: {test_messages}")
    
    try:
        response = client.chat.completions.create(
            model="glm-4v-flash",
            messages=test_messages,
            top_p=0.7,
            temperature=0.95,
            max_tokens=1024,
            stream=False
        )
        
        print(f"[测试] API调用成功")
        print(f"[测试] 响应: {response}")
        
        if response and response.choices:
            content = response.choices[0].message.content
            print(f"[测试] 识别结果: {content}")
            return True
        else:
            print(f"[测试] 响应为空")
            return False
            
    except Exception as e:
        print(f"[测试] API调用失败: {e}")
        return False

if __name__ == "__main__":
    success = test_glm4v_flash()
    print(f"测试结果: {'成功' if success else '失败'}")