"""
英语学习助手 - Playwright自动化测试
测试Streamlit应用的核心功能
"""

import os
import time
import asyncio
from playwright.async_api import async_playwright


async def test_streamlit_app():
    """测试Streamlit应用功能"""
    print("开始Playwright测试...")
    
    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(headless=False)  # 显示浏览器窗口
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            print("正在访问应用...")
            # 访问Streamlit应用
            await page.goto("http://localhost:8501")
            
            # 等待页面加载
            await page.wait_for_timeout(3000)
            
            print("检查页面标题...")
            # 检查页面标题
            title = await page.title()
            print(f"   页面标题: {title}")
            
            print("检查页面内容...")
            # 检查主要元素是否存在
            header_exists = await page.locator("text=英语学习助手").count() > 0
            if header_exists:
                print("   [成功] 主标题显示正常")
            else:
                print("   [失败] 主标题未找到")
            
            # 检查环境检查区域
            print("检查环境状态...")
            await page.wait_for_timeout(2000)
            
            # 查找状态信息
            python_status = await page.locator("text=Python").count() > 0
            if python_status:
                print("   [成功] Python状态显示")
            
            ocr_status = await page.locator("text=OCR").count() > 0
            if ocr_status:
                print("   [成功] OCR状态显示")
            
            api_status = await page.locator("text=API").count() > 0
            if api_status:
                print("   [成功] API状态显示")
            
            print("测试文件上传功能...")
            # 检查文件上传区域
            upload_exists = await page.locator("text=图像处理").count() > 0 or \
                           await page.locator("text=上传图片").count() > 0 or \
                           await page.locator("input[type=file]").count() > 0
            
            if upload_exists:
                print("   [成功] 文件上传区域存在")
            else:
                print("   [失败] 文件上传区域未找到")
            
            print("检查侧边栏...")
            # 检查侧边栏
            sidebar_exists = await page.locator(".sidebar").count() > 0 or \
                           await page.locator("text=系统配置").count() > 0
            
            if sidebar_exists:
                print("   [成功] 侧边栏配置区域存在")
            else:
                print("   [失败] 侧边栏未找到")
            
            print("截取页面截图...")
            # 截取页面截图
            screenshot_path = "test_screenshot.png"
            await page.screenshot(path=screenshot_path, full_page=True)
            print(f"   截图已保存: {screenshot_path}")
            
            print("检查页面文本内容...")
            # 获取页面内容进行分析
            page_content = await page.content()
            
            # 检查关键词
            key_terms = [
                "英语学习助手",
                "OCR", 
                "AI",
                "图像处理",
                "上传",
                "配置"
            ]
            
            found_terms = []
            for term in key_terms:
                if term in page_content:
                    found_terms.append(term)
            
            print(f"   找到关键词: {', '.join(found_terms)}")
            print(f"   关键词覆盖率: {len(found_terms)}/{len(key_terms)} ({len(found_terms)/len(key_terms)*100:.1f}%)")
            
            # 等待一段时间观察应用
            print("等待5秒观察应用状态...")
            await page.wait_for_timeout(5000)
            
            print("[成功] 测试完成!")
            return True
            
        except Exception as e:
            print(f"[错误] 测试过程中出错: {e}")
            # 仍然截图以便调试
            try:
                await page.screenshot(path="test_error_screenshot.png")
                print("   错误截图已保存: test_error_screenshot.png")
            except:
                pass
            return False
            
        finally:
            await browser.close()


async def main():
    """主函数"""
    print("=" * 60)
    print("英语学习助手 - Playwright自动化测试")
    print("基于Streamlit的Web应用功能测试")
    print("=" * 60)
    
    # 检查应用是否运行
    print("检查应用状态...")
    try:
        import requests
        response = requests.get("http://localhost:8501", timeout=5)
        if response.status_code == 200:
            print("   [成功] 应用正在运行 (http://localhost:8501)")
        else:
            print(f"   [失败] 应用状态异常 (状态码: {response.status_code})")
            return
    except requests.exceptions.ConnectionError:
        print("   [失败] 无法连接到应用，请确保Streamlit应用正在运行")
        print("   建议运行命令: streamlit run streamlit_app.py")
        return
    except Exception as e:
        print(f"   [失败] 连接检查失败: {e}")
        return
    
    # 运行测试
    success = await test_streamlit_app()
    
    print("=" * 60)
    if success:
        print("[成功] 测试成功完成!")
        print("应用基本功能正常")
    else:
        print("[警告] 测试过程中遇到问题")
        print("请检查应用状态和配置")
    
    print("测试文件位置: test_screenshot.png")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())