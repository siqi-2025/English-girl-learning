# 为什么需要图床？GLM-4V-Flash技术要求说明

## 问题背景
用户问题："另外 streamlit不支持上传图片吗？为什么另外找图床？"

## 技术原理解释

### Streamlit文件上传 vs GLM-4V-Flash要求

1. **Streamlit文件上传**：
   - ✅ 支持用户上传图片文件
   - ✅ 文件存储在本地临时目录
   - ❌ 只能被本地应用访问，无法被外部API访问

2. **GLM-4V-Flash API要求**：
   - ❌ 不支持本地文件路径
   - ❌ 不支持base64编码的图片
   - ✅ **只支持网络可访问的URL**

### 具体技术实现

```python
# GLM-4V-Flash API调用格式（智普AI官方要求）
messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "image_url",
                "image_url": {
                    "url": "https://example.com/image.jpg"  # 必须是网络URL
                }
            },
            {
                "type": "text", 
                "text": "请识别这张图片中的文字"
            }
        ]
    }
]
```

### 解决方案：图床上传流程

1. **用户上传** → Streamlit接收文件
2. **自动上传** → 将文件上传到GitHub作为图床
3. **获取URL** → 获得GitHub提供的公开访问URL
4. **API调用** → 使用这个URL调用GLM-4V-Flash
5. **图像识别** → AI模型识别图片内容

### 为什么选择GitHub作图床？

- ✅ 免费且稳定
- ✅ 支持API上传
- ✅ 提供公开访问URL
- ✅ 用户已有GitHub账号
- ✅ 无需额外服务注册

## 总结

**不是Streamlit不支持上传，而是GLM-4V-Flash只接受网络URL**
这是智普AI视觉模型的技术限制，需要通过图床桥接解决。