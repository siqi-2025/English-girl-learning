"""
测试修复后的GLM-4V-Flash API调用
"""

import os

# 禁用代理以避免SOCKS错误
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)
os.environ.pop('ALL_PROXY', None)
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)
os.environ.pop('all_proxy', None)

from zhipuai import ZhipuAI

def test_glm4v_fixed():
    """测试修复后的API调用格式"""
    print("[测试] 开始测试修复后的GLM-4V-Flash API...")
    
    # 设置API Key
    api_key = "17e5feb32ed94b66823c9f9e0f188752.XOQDn1kygRTltwfD"
    client = ZhipuAI(api_key=api_key)
    
    # 使用多个测试图片URL，包括标准的公开图片
    test_urls = [
        # GitHub上的项目图片
        "https://raw.githubusercontent.com/siqi-2025/English-girl-learning/main/test_english_content.jpg",
        # 公开的测试图片（备选）
        "https://picsum.photos/200/300",
        # 另一个公开图片源
        "https://via.placeholder.com/600x400.jpg"
    ]
    
    test_image_url = test_urls[0]  # 先尝试第一个
    
    print(f"[测试] 使用测试图片URL: {test_image_url}")
    
    try:
        # 严格按照官方格式构建消息
        messages = [
            {
                "role": "system",
                "content": "You are a professional OCR assistant specialized in recognizing English educational content."
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Please identify and extract all English text visible in this image. Return only the text content without any explanation."
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
        
        print("[测试] 调用API...")
        
        # 调用API
        response = client.chat.completions.create(
            model="glm-4v-flash",
            messages=messages,
            top_p=0.6,
            temperature=0.8,
            max_tokens=1024,
            stream=False
        )
        
        print("[测试] API调用成功!")
        
        if hasattr(response, 'choices') and response.choices:
            content = response.choices[0].message.content
            print(f"[测试] 识别结果:\n{content[:500]}...")
            return True
        else:
            print(f"[测试] 响应格式异常: {response}")
            return False
            
    except Exception as e:
        print(f"[测试] API调用失败: {e}")
        print(f"[测试] 错误类型: {type(e).__name__}")
        import traceback
        print(f"[测试] 详细错误:\n{traceback.format_exc()}")
        return False

if __name__ == "__main__":
    result = test_glm4v_fixed()
    print(f"\n[测试] 最终结果: {'✅ 成功' if result else '❌ 失败'}")