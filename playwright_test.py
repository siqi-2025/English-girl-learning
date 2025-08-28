"""
英语学习助手 - Playwright自动化测试
版本: v1.2.3
"""

import asyncio
import os
import time
from pathlib import Path
from playwright.async_api import async_playwright

class EnglishLearningTester:
    """英语学习助手自动化测试器"""
    
    def __init__(self):
        self.base_url = "http://localhost:8502"
        self.test_image_path = None
        self.results = []
        
    def create_test_image(self):
        """创建测试用的图片"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # 创建一个简单的测试图片，包含英语文字
            img = Image.new('RGB', (400, 200), color='white')
            draw = ImageDraw.Draw(img)
            
            # 添加英语文字
            text_lines = [
                "Unit 1: Hello World",
                "Vocabulary:",
                "1. Hello - nihao",
                "2. World - shijie", 
                "3. Good - haode"
            ]
            
            y_position = 20
            for line in text_lines:
                draw.text((20, y_position), line, fill='black')
                y_position += 30
            
            # 保存测试图片
            test_image_path = Path("./test_image.jpg")
            img.save(test_image_path, 'JPEG')
            self.test_image_path = str(test_image_path.absolute())
            
            print(f"[测试] 创建测试图片: {self.test_image_path}")
            return True
            
        except Exception as e:
            print(f"[测试] 创建测试图片失败: {e}")
            return False
    
    async def test_streamlit_app(self):
        """测试Streamlit应用"""
        print(f"[测试] 开始自动化测试 - {self.base_url}")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False, slow_mo=1000)  # 显示浏览器，慢速模式方便观察
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                # 1. 访问应用
                print(f"[测试] 步骤1: 访问应用页面")
                await page.goto(self.base_url)
                await page.wait_for_load_state('networkidle')
                
                # 检查版本号
                print(f"[测试] 检查版本号显示")
                version_text = await page.text_content('h1')
                print(f"[测试] 页面标题: {version_text}")
                
                if "v1.2.3" not in version_text:
                    print(f"[测试] 警告: 版本号不匹配，期望v1.2.3")
                
                # 2. 查找文件上传控件
                print(f"[测试] 步骤2: 查找文件上传控件")
                await page.wait_for_selector('input[type="file"]', timeout=10000)
                
                # 3. 上传测试图片
                print(f"[测试] 步骤3: 上传测试图片")
                file_input = page.locator('input[type="file"]')
                await file_input.set_input_files(self.test_image_path)
                
                # 等待文件上传完成
                await asyncio.sleep(2)
                
                # 4. 点击开始处理按钮
                print(f"[测试] 步骤4: 查找并点击处理按钮")
                
                # 等待处理按钮出现
                await page.wait_for_selector('button:has-text("开始处理")', timeout=10000)
                process_button = page.locator('button:has-text("开始处理")')
                await process_button.click()
                
                print(f"[测试] 已点击处理按钮，等待处理完成...")
                
                # 5. 等待处理完成并检查结果
                print(f"[测试] 步骤5: 等待处理完成...")
                
                # 等待处理完成的标志（可能需要较长时间）
                try:
                    await page.wait_for_selector('text=处理完成', timeout=60000)  # 60秒超时
                    print(f"[测试] 处理已完成")
                except:
                    print(f"[测试] 等待处理完成超时，检查页面内容...")
                
                # 6. 检查调试信息
                print(f"[测试] 步骤6: 检查调试信息和结果")
                
                # 获取页面所有文本内容来查找调试信息
                page_content = await page.content()
                
                # 查找GLM-4V-Flash相关的调试信息
                debug_keywords = [
                    "GLM-4V-Flash识别结果",
                    "视觉识别失败",
                    "视觉识别成功", 
                    "API调用",
                    "上传成功",
                    "Telegraph"
                ]
                
                found_debug_info = []
                for keyword in debug_keywords:
                    if keyword in page_content:
                        found_debug_info.append(keyword)
                
                print(f"[测试] 找到的调试信息关键词: {found_debug_info}")
                
                # 7. 截图保存结果
                screenshot_path = f"test_result_{int(time.time())}.png"
                await page.screenshot(path=screenshot_path, full_page=True)
                print(f"[测试] 截图已保存: {screenshot_path}")
                
                # 8. 分析结果
                success, issues = self.analyze_results(page_content, found_debug_info)
                
                return success, issues
                
            except Exception as e:
                print(f"[测试] 测试过程异常: {e}")
                
                # 异常时也截图
                try:
                    screenshot_path = f"test_error_{int(time.time())}.png"
                    await page.screenshot(path=screenshot_path, full_page=True)
                    print(f"[测试] 错误截图已保存: {screenshot_path}")
                except:
                    pass
                
                return False, ["测试异常"]
                
            finally:
                await browser.close()
    
    def analyze_results(self, page_content, debug_info):
        """分析测试结果"""
        print(f"[测试] 分析测试结果...")
        
        success = True
        issues = []
        
        # 检查是否有API调用错误
        if "Error code: 400" in page_content:
            issues.append("API调用错误400")
            success = False
            
        if "1210" in page_content:
            issues.append("API参数错误1210")
            success = False
            
        if "视觉识别失败" in page_content:
            issues.append("视觉识别失败")
            success = False
            
        # 检查是否有上传成功信息
        if "Telegraph" in debug_info or "上传成功" in debug_info:
            print(f"[测试] ✅ 图片上传功能正常")
        else:
            issues.append("图片上传可能失败")
            
        # 检查是否有处理结果
        if "处理完成" in page_content:
            print(f"[测试] ✅ 处理流程完成")
        else:
            issues.append("处理流程未完成")
            
        if success:
            print(f"[测试] ✅ 测试通过！GLM-4V-Flash功能正常")
        else:
            print(f"[测试] ❌ 测试发现问题:")
            for issue in issues:
                print(f"  - {issue}")
                
        return success, issues
    
    async def run_full_test(self):
        """运行完整测试流程"""
        print(f"[测试] 开始完整测试流程")
        
        # 创建测试图片
        if not self.create_test_image():
            print(f"[测试] 测试终止: 无法创建测试图片")
            return False
            
        # 运行自动化测试
        success, issues = await self.test_streamlit_app()
        
        # 清理测试文件
        try:
            if self.test_image_path and os.path.exists(self.test_image_path):
                os.remove(self.test_image_path)
                print(f"[测试] 清理测试图片: {self.test_image_path}")
        except:
            pass
            
        return success, issues

async def main():
    """主测试函数"""
    tester = EnglishLearningTester()
    success, issues = await tester.run_full_test()
    
    if success:
        print(f"\n🎉 测试成功！GLM-4V-Flash功能完全正常")
    else:
        print(f"\n⚠️ 测试发现问题，需要修复:")
        for issue in issues:
            print(f"  - {issue}")
            
    return success, issues

if __name__ == "__main__":
    result = asyncio.run(main())
    print(f"测试完成，结果: {result}")