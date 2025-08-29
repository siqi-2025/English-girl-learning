"""
直接测试GLM-4V-Flash API调用
测试图像格式标准化是否解决了错误1210
"""

import os
import tempfile
from PIL import Image, ImageDraw
from src.core.ai_analyzer import ZhipuAIClient

def test_glm4v_direct():
    """直接测试GLM-4V-Flash"""
    print("[Test] 开始直接测试GLM-4V-Flash API...")
    
    # 设置环境变量
    os.environ['ENGLISH_LEARNING_ZHIPU_API_KEY'] = '17e5feb32ed94b66823c9f9e0f188752.XOQDn1kygRTltwfD'
    os.environ['GITHUB_TOKEN'] = 'ghp_test_token_placeholder'
    
    # 创建测试图片
    print("[Test] 创建标准化测试图片...")
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    # 添加清晰的英语内容
    text_lines = [
        "ENGLISH LEARNING - UNIT 5",
        "",
        "Vocabulary Words:",
        "1. apple - 苹果", 
        "2. book - 书",
        "3. chair - 椅子",
        "4. dog - 狗",
        "5. elephant - 大象",
        "",
        "Grammar: Present Simple",
        "I like apples.",
        "She reads books.",
        "We sit on chairs."
    ]
    
    y_pos = 50
    for line in text_lines:
        if line:  # 非空行用黑色
            draw.text((50, y_pos), line, fill='black')
        y_pos += 40
    
    # 保存为高质量JPEG
    test_image_path = "test_standard_image.jpg"
    img.save(test_image_path, 'JPEG', quality=95)
    print(f"[Test] 测试图片已保存: {test_image_path}")
    
    # 创建AI客户端并测试
    try:
        print("[Test] 初始化ZhipuAI客户端...")
        ai_client = ZhipuAIClient()
        
        print("[Test] 调用recognize_image_text...")
        result = ai_client.recognize_image_text(
            image_input=test_image_path,
            context="英语教材内容"
        )
        
        print(f"[Test] API调用结果:")
        print(f"  成功: {result['success']}")
        if result['success']:
            print(f"  识别文本: {result['raw_text'][:200]}...")
            print(f"  置信度: {result['confidence']}")
            print(f"  模型: {result.get('vision_model', 'N/A')}")
        else:
            print(f"  错误: {result['error']}")
            print(f"  详细信息: {result.get('details', 'N/A')}")
        
        return result
        
    except Exception as e:
        print(f"[Test] 测试异常: {e}")
        return {'success': False, 'error': str(e)}
    
    finally:
        # 清理测试文件
        if os.path.exists(test_image_path):
            os.remove(test_image_path)
            print(f"[Test] 清理测试文件: {test_image_path}")

if __name__ == "__main__":
    result = test_glm4v_direct()
    print(f"\n[Test] 最终结果: {result['success']}")