"""
Playwright自动化测试 - 访问Streamlit Cloud应用
调试GLM-4V-Flash API调用问题
"""

import asyncio
import time
from pathlib import Path
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw

async def test_streamlit_app():
    """测试Streamlit Cloud应用"""
    print("[Test] 开始测试Streamlit Cloud应用...")
    
    # 创建测试图片
    print("[Test] 创建测试图片...")
    try:
        img = Image.new('RGB', (600, 400), color='white')
        draw = ImageDraw.Draw(img)
        
        # 添加英语教材内容
        text_lines = [
            "Unit 3: My School Day",
            "",
            "Vocabulary:",
            "1. morning - 早上",
            "2. afternoon - 下午", 
            "3. evening - 晚上",
            "4. homework - 作业",
            "5. classroom - 教室",
            "",
            "Grammar Point:",
            "Present Simple Tense"
        ]
        
        y_pos = 30
        for line in text_lines:
            draw.text((30, y_pos), line, fill='black')
            y_pos += 30
        
        test_image_path = "english_textbook_test.jpg"
        img.save(test_image_path, 'JPEG', quality=95)
        print(f"[Test] 测试图片已创建: {test_image_path}")
        
    except Exception as e:
        print(f"[Test] 创建测试图片失败: {e}")
        return False

    # 启动浏览器测试
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # 显示浏览器便于观察
        page = await browser.new_page()
        
        # 监听控制台消息
        console_messages = []
        def handle_console(msg):
            console_messages.append(f"[Console] {msg.type}: {msg.text}")
            print(f"[Console] {msg.type}: {msg.text}")
        
        page.on("console", handle_console)
        
        # 监听网络请求
        network_logs = []
        def handle_request(request):
            if 'api' in request.url.lower() or 'zhipuai' in request.url.lower():
                network_logs.append(f"[Network] Request: {request.method} {request.url}")
                print(f"[Network] Request: {request.method} {request.url}")
        
        def handle_response(response):
            if 'api' in response.url.lower() or 'zhipuai' in response.url.lower():
                network_logs.append(f"[Network] Response: {response.status} {response.url}")
                print(f"[Network] Response: {response.status} {response.url}")
        
        page.on("request", handle_request)
        page.on("response", handle_response)
        
        try:
            print("[Test] 访问Streamlit Cloud应用...")
            await page.goto("https://engirl.streamlit.app/", timeout=60000)
            await page.wait_for_load_state('networkidle', timeout=30000)
            
            # 等待应用加载
            print("[Test] 等待应用完全加载...")
            await asyncio.sleep(5)
            
            # 截图保存当前状态
            await page.screenshot(path=f"streamlit_loaded_{int(time.time())}.png")
            print("[Test] 应用加载完成截图已保存")
            
            # 第一步：查找并上传图片文件
            print("[Test] 第一步：查找文件上传区域...")
            file_uploaded = False
            
            try:
                # 先等待页面完全加载
                await asyncio.sleep(3)
                
                # 第一步：尝试多种方式找到Browse files按钮
                browse_selectors = [
                    'button:has-text("Browse files")',
                    'button[data-testid="stBaseButton-secondary"]',
                    'button.st-emotion-cache-ttv98w',  # 从HTML中看到的class
                    '[aria-label=""] button:has-text("Browse files")',
                    'section button:has-text("Browse files")'
                ]
                
                browse_found = False
                for selector in browse_selectors:
                    try:
                        browse_btn = page.locator(selector)
                        if await browse_btn.count() > 0:
                            print(f"[Test] Found Browse files button with: {selector}")
                            browse_found = True
                            break
                    except:
                        continue
                
                if browse_found:
                    print("[Test] Clicking Browse files button...")
                    await browse_btn.click()
                    await asyncio.sleep(3)  # 给更多时间处理
                    
                    # 第二步：找到文件输入框并上传文件
                    file_input = page.locator('input[type="file"]')
                    if await file_input.count() > 0:
                        print("[Test] Found file input after clicking browse")
                        await file_input.set_input_files(test_image_path)
                        file_uploaded = True
                        print("[Test] File upload successful")
                        await asyncio.sleep(5)  # 等待文件处理和界面更新
                    else:
                        print("[Test] File input not found after clicking browse")
                        # 尝试等待更长时间
                        await asyncio.sleep(2)
                        file_input = page.locator('input[type="file"]')
                        if await file_input.count() > 0:
                            print("[Test] Found file input after additional wait")
                            await file_input.set_input_files(test_image_path)
                            file_uploaded = True
                            print("[Test] File upload successful (delayed)")
                            await asyncio.sleep(5)
                else:
                    print("[Test] Browse files button not found with any selector")
                    # 打印页面内容以调试
                    page_text = await page.text_content('body')
                    print(f"[Test] Page contains Browse files: {'Browse files' in page_text}")
                    
                    # 备用方案：直接尝试找隐藏的文件输入
                    file_input = page.locator('input[type="file"]')
                    if await file_input.count() > 0:
                        print("[Test] Found hidden file input")
                        await file_input.set_input_files(test_image_path)
                        file_uploaded = True
                        print("[Test] File upload successful (hidden input)")
                        await asyncio.sleep(5)
                    
            except Exception as e:
                print(f"[Test] File upload failed: {e}")
                
            # 截图记录上传后状态
            await page.screenshot(path=f"after_upload_{int(time.time())}.png")
            
            if file_uploaded:
                # 第二步：查找并点击处理按钮
                print("[Test] 第二步：查找处理按钮...")
                
                # 等待界面更新
                await asyncio.sleep(2)
                
                # 查找🚀开始处理按钮 - 使用准确的选择器
                button_selectors = [
                    'button[data-testid="stBaseButton-primary"]:has-text("🚀 开始处理")',
                    'button[data-testid="stBaseButton-primary"]',
                    'button:has-text("🚀 开始处理")',
                    'button:has-text("开始处理")',
                    # 备用选择器
                    'button[kind="primary"]',
                    '.st-emotion-cache-1wa92ot'
                ]
                
                process_clicked = False
                for selector in button_selectors:
                    try:
                        button = page.locator(selector)
                        if await button.count() > 0:
                            print(f"[Test] Found process button: {selector}")
                            await button.click()
                            process_clicked = True
                            print("[Test] Process button clicked")
                            break
                    except Exception as e:
                        continue
                
                if not process_clicked:
                    print("[Test] No process button found, checking page content...")
                    # 打印页面文本内容以便调试
                    page_text = await page.text_content('body')
                    print(f"[Test] Page text preview: {page_text[:500]}...")
                
                # 截图记录点击后状态
                await page.screenshot(path=f"after_click_{int(time.time())}.png")
                
                if process_clicked:
                    # 第三步：等待处理结果并监控
                    print("[Test] 第三步：监控处理过程...")
                    start_time = time.time()
                    
                    # 等待60秒并持续监控
                    while time.time() - start_time < 60:
                        await asyncio.sleep(3)
                        
                        # 每10秒截图一次记录进度
                        elapsed = int(time.time() - start_time)
                        if elapsed % 10 == 0 and elapsed > 0:
                            await page.screenshot(path=f"processing_{elapsed}s.png")
                            print(f"[Test] 处理中... {elapsed}秒")
                        
                        # 检查是否有错误信息或结果
                        page_content = await page.content()
                        if "1210" in page_content or "API 调用参数有误" in page_content:
                            print("[Test] Detected API error 1210")
                            break
                        if "success" in page_content.lower() and "true" in page_content.lower():
                            print("[Test] Detected success message")
                            break
                    
                    # 最终状态截图
                    await page.screenshot(path=f"final_result_{int(time.time())}.png", full_page=True)
                    print("[Test] 处理流程完成，最终截图已保存")
            else:
                print("[Test] Skipping subsequent steps due to file upload failure")
            
            # 获取页面内容进行分析
            print("[Test] 获取页面内容分析...")
            page_content = await page.content()
            
            # 检查关键信息
            has_api_error = "1210" in page_content or "API 调用参数有误" in page_content
            has_success = "success\":true" in page_content.lower()
            has_glm4v = "glm-4v" in page_content.lower()
            
            print(f"[Test] 页面分析结果:")
            print(f"  - 包含API 1210错误: {has_api_error}")
            print(f"  - 包含成功信息: {has_success}")
            print(f"  - 包含GLM-4V模型: {has_glm4v}")
            
        except Exception as e:
            print(f"[Test] 测试过程异常: {e}")
            await page.screenshot(path=f"error_{int(time.time())}.png")
        
        finally:
            print(f"[Test] 控制台消息总计: {len(console_messages)}")
            print(f"[Test] 网络日志总计: {len(network_logs)}")
            
            # 保存完整日志
            with open(f"test_log_{int(time.time())}.txt", "w", encoding="utf-8") as f:
                f.write("=== 控制台消息 ===\n")
                for msg in console_messages:
                    f.write(msg + "\n")
                f.write("\n=== 网络日志 ===\n")
                for log in network_logs:
                    f.write(log + "\n")
            
            print("[Test] 日志已保存到文件")
            await browser.close()
    
    return True

if __name__ == "__main__":
    result = asyncio.run(test_streamlit_app())
    print(f"[Test] 测试完成: {result}")