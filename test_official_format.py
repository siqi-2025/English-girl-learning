"""
严格按照官方示例格式测试GLM-4V API
"""

import os

# 禁用代理
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)
os.environ.pop('ALL_PROXY', None)
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)
os.environ.pop('all_proxy', None)

from zhipuai import ZhipuAI

# 初始化客户端
client = ZhipuAI(api_key="17e5feb32ed94b66823c9f9e0f188752.XOQDn1kygRTltwfD")

# 测试不同的模型名称
models_to_test = ["glm-4v-flash", "glm-4v", "glm-4.5v", "glm-4-vision"]

for model_name in models_to_test:
    print(f"\n测试模型: {model_name}")
    print("-" * 50)
    
    try:
        # 严格按照官方格式
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": ""
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "描述这张图片"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": "https://raw.githubusercontent.com/siqi-2025/English-girl-learning/main/test_english_content.jpg"
                            }
                        }
                    ]
                }
            ],
            top_p=0.6,
            temperature=0.8,
            max_tokens=1024,
            stream=False
        )
        
        print(f"成功! 模型 {model_name} 可用")
        if hasattr(response, 'choices') and response.choices:
            content = response.choices[0].message.content
            print(f"响应内容前100字符: {content[:100]}...")
        break
        
    except Exception as e:
        print(f"失败: {e}")
        
print("\n测试完成")