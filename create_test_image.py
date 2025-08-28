"""
创建与你提供的英语教材图片相似的测试内容
"""
from PIL import Image, ImageDraw, ImageFont

def create_english_textbook_image():
    """创建英语教材样式的测试图片"""
    # 创建白色背景图片
    img = Image.new('RGB', (800, 1200), color='white')
    draw = ImageDraw.Draw(img)
    
    # 尝试使用系统字体，如果没有就使用默认字体
    try:
        title_font = ImageFont.truetype("arial.ttf", 24)
        section_font = ImageFont.truetype("arial.ttf", 18)
        content_font = ImageFont.truetype("arial.ttf", 14)
    except:
        # 如果没有找到字体文件，使用默认字体
        title_font = ImageFont.load_default()
        section_font = ImageFont.load_default()
        content_font = ImageFont.load_default()
    
    y = 50
    
    # 标题
    draw.text((50, y), "Listening Scripts", font=title_font, fill='black')
    y += 60
    
    # Starter Unit 1
    draw.text((50, y), "Starter Unit 1", font=section_font, fill='blue')
    y += 40
    
    # Section A, 2b
    draw.text((50, y), "Section A, 2b", font=section_font, fill='red')
    y += 30
    draw.text((50, y), "b, c, g, h, j, l, n, q, r, v, x, z", font=content_font, fill='black')
    y += 40
    
    # Section A, 2c
    draw.text((50, y), "Section A, 2c", font=section_font, fill='red')
    y += 30
    
    # Conversation 1
    draw.text((50, y), "Conversation 1", font=content_font, fill='black')
    y += 25
    draw.text((50, y), "Ms Gao: Good morning, class.", font=content_font, fill='black')
    y += 20
    draw.text((50, y), "Class:    Good morning, Ms Gao.", font=content_font, fill='black')
    y += 20
    draw.text((50, y), "Ms Gao: Sit down, please.", font=content_font, fill='black')
    y += 40
    
    # Conversation 2
    draw.text((50, y), "Conversation 2", font=content_font, fill='black')
    y += 25
    draw.text((50, y), "Ms Gao: Hello, Peter. Can you say hi to the class?", font=content_font, fill='black')
    y += 20
    draw.text((50, y), "Peter:    Hi, everyone! I'm Peter Brown.", font=content_font, fill='black')
    y += 20
    draw.text((50, y), "Ms Gao: Thank you, Peter. Now class, please", font=content_font, fill='black')
    y += 20
    draw.text((150, y), "say hi to each other.", font=content_font, fill='black')
    y += 40
    
    # Conversation 3
    draw.text((50, y), "Conversation 3", font=content_font, fill='black')
    y += 25
    draw.text((50, y), "Emma:  Good morning. My name is Emma.", font=content_font, fill='black')
    y += 20
    draw.text((50, y), "Fu Xing: Good morning, Emma.", font=content_font, fill='black')
    y += 20
    draw.text((50, y), "Emma:  So what's your name?", font=content_font, fill='black')
    y += 20
    draw.text((50, y), "Fu Xing: Oh, I'm Fu Xing. Nice to meet you,", font=content_font, fill='black')
    y += 20
    draw.text((150, y), "Emma.", font=content_font, fill='black')
    y += 20
    draw.text((50, y), "Emma:  Nice to meet you too, Fu Xing!", font=content_font, fill='black')
    
    # 保存图片
    img.save("english_textbook_test.jpg", 'JPEG', quality=95)
    print("测试图片已创建: english_textbook_test.jpg")

if __name__ == "__main__":
    create_english_textbook_image()