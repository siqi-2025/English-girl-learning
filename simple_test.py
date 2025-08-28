"""
Simple Playwright Test for English Learning Assistant
Version: v1.2.3
"""

import asyncio
import os
import time
from pathlib import Path
from playwright.async_api import async_playwright

async def run_test():
    """Run simple automated test"""
    print("[Test] Starting automated test...")
    
    # Create test image
    try:
        from PIL import Image, ImageDraw
        
        img = Image.new('RGB', (400, 200), color='white')
        draw = ImageDraw.Draw(img)
        
        text_lines = [
            "Unit 1: Hello World",
            "Vocabulary:",
            "1. Hello", 
            "2. World",
            "3. Good"
        ]
        
        y_pos = 20
        for line in text_lines:
            draw.text((20, y_pos), line, fill='black')
            y_pos += 30
        
        test_image = "./test_image.jpg"
        img.save(test_image, 'JPEG')
        print(f"[Test] Created test image: {test_image}")
        
    except Exception as e:
        print(f"[Test] Failed to create image: {e}")
        return False

    # Run browser test
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            print("[Test] Opening Streamlit app...")
            await page.goto("http://localhost:8504")
            await page.wait_for_load_state('networkidle', timeout=30000)
            
            # Check version
            title = await page.text_content('h1')
            print(f"[Test] Page title: {title}")
            
            # Find file upload
            print("[Test] Looking for file upload...")
            await page.wait_for_selector('input[type="file"]', timeout=10000)
            
            # Upload file
            print("[Test] Uploading test image...")
            file_input = page.locator('input[type="file"]')
            await file_input.set_input_files(test_image)
            await asyncio.sleep(2)
            
            # Click process button
            print("[Test] Clicking process button...")
            await page.wait_for_selector('button:has-text("开始处理")', timeout=10000)
            process_btn = page.locator('button:has-text("开始处理")')
            await process_btn.click()
            
            # Wait for results
            print("[Test] Waiting for processing...")
            await asyncio.sleep(30)  # Wait 30 seconds for processing
            
            # Take screenshot
            screenshot = f"test_result_{int(time.time())}.png"
            await page.screenshot(path=screenshot, full_page=True)
            print(f"[Test] Screenshot saved: {screenshot}")
            
            # Check page content
            content = await page.content()
            
            # Analyze results
            has_error_400 = "Error code: 400" in content
            has_error_1210 = "1210" in content
            has_success = "success\":true" in content.lower()
            has_telegraph = "telegraph" in content.lower()
            has_processing_complete = "处理完成" in content
            
            print(f"[Test] Analysis:")
            print(f"  - Has 400 error: {has_error_400}")
            print(f"  - Has 1210 error: {has_error_1210}")  
            print(f"  - Has success: {has_success}")
            print(f"  - Has Telegraph upload: {has_telegraph}")
            print(f"  - Processing complete: {has_processing_complete}")
            
            if has_error_400 or has_error_1210:
                print("[Test] FAILED: Still has API errors")
                return False
            elif has_success:
                print("[Test] SUCCESS: GLM-4V-Flash working!")
                return True
            else:
                print("[Test] UNCERTAIN: Need to check manually")
                return False
                
        except Exception as e:
            print(f"[Test] Exception: {e}")
            return False
        finally:
            await browser.close()
            # Cleanup
            if os.path.exists(test_image):
                os.remove(test_image)

if __name__ == "__main__":
    result = asyncio.run(run_test())
    print(f"[Test] Final result: {result}")