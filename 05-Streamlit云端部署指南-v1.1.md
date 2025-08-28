# Streamlit Cloud 部署完整指南
**文档版本**: v1.1 (James版本号系统)  
**创建日期**: 2024-08-28  
**最后更新**: 2024-08-28

## 🔄 更新记录
- **v1.1** (2024-08-28): 
  - 更新依赖配置支持AI增强OCR (PaddleOCR 3.1.0)
  - 更新环境变量命名为项目特定名称
  - 优化云端部署配置

## 预备工作检查清单

### 1. 账户准备
- [ ] GitHub账户已创建并验证
- [ ] Streamlit账户已注册 (访问 https://share.streamlit.io)
- [ ] 智普AI账户已开通，API Key可用

### 2. 项目准备
- [ ] 项目代码已完成并测试
- [ ] GitHub仓库已创建 (公开仓库)
- [ ] 必需文件已准备完成

## 必需文件配置

### 1. 应用入口文件
```python
# streamlit_app.py
import streamlit as st
import sys
import os

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def main():
    st.set_page_config(
        page_title="English Learning Assistant",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("📚 英语学习助手")
    st.markdown("基于OCR和AI的英语教材处理工具")
    
    # 导入主应用逻辑
    from src.ui.main_page import render_main_page
    render_main_page()

if __name__ == "__main__":
    main()
```

### 2. 依赖配置文件
```txt
# requirements.txt - 云端兼容优化版本
streamlit>=1.28.0
requests>=2.25.0
pyyaml>=6.0
markdown>=3.3.0
pillow>=8.0.0
numpy>=1.21.0,<2.0.0
opencv-python-headless>=4.5.0
scikit-image>=0.19.0
```

### 3. Streamlit配置
```toml
# .streamlit/config.toml
[server]
port = 8501
maxUploadSize = 50
enableXsrfProtection = false
enableCORS = false
enableWebsocketCompression = false

[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF" 
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[browser]
gatherUsageStats = false
serverAddress = "0.0.0.0"

[logger]
level = "info"
```

### 4. 密钥配置 (本地开发用)
```toml
# .streamlit/secrets.toml (不要提交到Git!)
[api]
ENGLISH_LEARNING_ZHIPU_API_KEY = "your-api-key-here"

[english_learning_settings]
MAX_UPLOAD_SIZE = 50
BATCH_SIZE = 5
PROJECT_NAME = "English Learning Assistant"
```

## Git仓库配置

### 1. .gitignore文件
```gitignore
# .gitignore
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
english-learning-env/
ENV/
env.bak/
venv.bak/

# Streamlit
.streamlit/secrets.toml

# 临时文件
*.tmp
*.temp
.cache/
temp/
output/
logs/

# 系统文件
.DS_Store
Thumbs.db
*.log

# IDE
.vscode/
.idea/
*.swp
*.swo

# 测试文件
.pytest_cache/
.coverage
htmlcov/
```

### 2. 推送到GitHub
```bash
# 初始化Git仓库
git init
git add .
git commit -m "Initial commit: English Learning Assistant"

# 连接远程仓库
git remote add origin https://github.com/yourusername/English-girl-learning.git
git branch -M main
git push -u origin main
```

## Streamlit Cloud部署步骤

### 步骤1: 访问Streamlit Cloud
1. 打开浏览器，访问 https://share.streamlit.io
2. 点击 "Sign in with GitHub"
3. 授权Streamlit访问您的GitHub账户

### 步骤2: 创建新应用
1. 点击 "New app" 按钮
2. 在 "Repository" 下拉菜单中选择 `yourusername/English-girl-learning`
3. 在 "Branch" 中选择 `main`
4. 在 "Main file path" 中输入 `streamlit_app.py`
5. 在 "App URL" 中设置自定义URL (可选)

### 步骤3: 配置环境变量
1. 点击 "Advanced settings..."
2. 在 "Secrets" 部分添加以下内容:
```toml
[api]
ZHIPU_API_KEY = "17e5feb32ed94b66823c9f9e0f188752.XOQDn1kygRTltwfD"

[settings]
MAX_UPLOAD_SIZE = 50
BATCH_SIZE = 5
DEBUG = false
```

### 步骤4: 部署应用
1. 检查所有配置无误后，点击 "Deploy!"
2. 等待部署完成 (通常需要3-5分钟)
3. 部署成功后会显示应用URL

## 云端代码适配

### 1. 密钥获取适配
```python
# src/utils/config.py
import streamlit as st
import os

def get_api_key():
    """获取API密钥 - 云端适配版本"""
    try:
        # 首先尝试从Streamlit secrets获取
        return st.secrets["api"]["ZHIPU_API_KEY"]
    except (KeyError, FileNotFoundError):
        # 回退到环境变量
        api_key = os.getenv("ZHIPU_API_KEY")
        if not api_key:
            st.error("❌ 未找到API密钥，请检查配置")
            st.stop()
        return api_key

def get_config(key, default=None):
    """获取配置项"""
    try:
        return st.secrets.get("settings", {}).get(key, default)
    except (KeyError, FileNotFoundError):
        return os.getenv(key, default)
```

### 2. 内存优化代码
```python
# src/core/ocr_processor.py
import streamlit as st
from paddleocr import PaddleOCR

@st.cache_resource
def load_ocr_model():
    """加载OCR模型 - 使用缓存避免重复加载"""
    return PaddleOCR(
        use_angle_cls=True, 
        lang='ch',
        use_gpu=False,  # 云端使用CPU版本
        show_log=False
    )

@st.cache_data
def process_image_cached(image_bytes, _ocr_model):
    """缓存图像处理结果"""
    import io
    from PIL import Image
    import numpy as np
    
    # 转换图像格式
    image = Image.open(io.BytesIO(image_bytes))
    img_array = np.array(image)
    
    # OCR识别
    result = _ocr_model.ocr(img_array, cls=True)
    
    # 提取文字
    text_results = []
    if result and result[0]:
        for line in result[0]:
            text_results.append(line[1][0])
    
    return '\n'.join(text_results)
```

### 3. 错误处理增强
```python
# src/utils/error_handler.py
import streamlit as st
import traceback
import time

def handle_ocr_error(error):
    """OCR错误处理"""
    st.error("🔍 OCR处理失败")
    st.warning("可能原因：图片模糊、文字不清晰或格式不支持")
    
    with st.expander("技术详情"):
        st.code(str(error))
    
    st.info("💡 建议：尝试上传更清晰的图片或调整图片角度")

def handle_ai_error(error):
    """AI API错误处理"""
    if "rate limit" in str(error).lower():
        st.error("🚫 API调用频率过高，请稍后重试")
        st.info("系统将在30秒后自动重试")
        time.sleep(30)
    elif "api key" in str(error).lower():
        st.error("🔑 API密钥无效，请检查配置")
        st.stop()
    else:
        st.error("🤖 AI服务暂时不可用")
        st.warning("请稍后重试或联系技术支持")

def safe_execute(func, error_handler=None):
    """安全执行函数，统一错误处理"""
    try:
        return func()
    except Exception as e:
        if error_handler:
            error_handler(e)
        else:
            st.error(f"执行过程中出现错误: {str(e)}")
        return None
```

## 应用监控和维护

### 1. 健康检查页面
```python
# src/ui/health_page.py
import streamlit as st
import time
import requests

def render_health_page():
    """渲染健康检查页面"""
    st.header("🏥 系统健康状态")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("OCR服务")
        try:
            from src.core.ocr_processor import load_ocr_model
            ocr_model = load_ocr_model()
            st.success("✅ 正常")
        except Exception as e:
            st.error("❌ 异常")
            st.code(str(e))
    
    with col2:
        st.subheader("AI服务")
        try:
            from src.core.ai_analyzer import test_connection
            if test_connection():
                st.success("✅ 正常")
            else:
                st.warning("⚠️ 连接异常")
        except Exception as e:
            st.error("❌ 异常")
            st.code(str(e))
    
    with col3:
        st.subheader("系统资源")
        import psutil
        memory_usage = psutil.virtual_memory().percent
        if memory_usage < 80:
            st.success(f"✅ 内存使用: {memory_usage:.1f}%")
        else:
            st.warning(f"⚠️ 内存使用: {memory_usage:.1f}%")
```

### 2. 使用分析
```python
# src/utils/analytics.py
import streamlit as st
import json
from datetime import datetime

def log_usage(action, details=None):
    """记录使用情况"""
    if not st.session_state.get('analytics_enabled', True):
        return
    
    usage_data = {
        'timestamp': datetime.now().isoformat(),
        'action': action,
        'details': details or {},
        'session_id': st.session_state.get('session_id', 'unknown')
    }
    
    # 可以发送到简单的分析服务
    # 这里只是示例，实际可以集成Google Analytics等
    
def track_processing_time(func):
    """装饰器：跟踪处理时间"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        log_usage('processing_time', {
            'function': func.__name__,
            'duration': end_time - start_time
        })
        
        return result
    return wrapper
```

## 性能优化建议

### 1. 缓存策略
```python
# 合理使用Streamlit缓存
@st.cache_data(ttl=3600)  # 1小时缓存
def expensive_computation(data):
    return process_data(data)

@st.cache_resource  # 全局资源缓存
def load_models():
    return load_heavy_models()
```

### 2. 批处理优化
```python
# 分批处理大量文件
def process_files_in_batches(files, batch_size=5):
    progress_bar = st.progress(0)
    results = []
    
    for i in range(0, len(files), batch_size):
        batch = files[i:i+batch_size]
        batch_results = process_batch(batch)
        results.extend(batch_results)
        
        progress = (i + len(batch)) / len(files)
        progress_bar.progress(progress)
        
        # 给系统一点喘息时间
        time.sleep(0.1)
    
    return results
```

### 3. 内存清理
```python
# 及时清理大对象
def process_large_data(data):
    try:
        result = heavy_processing(data)
        return result
    finally:
        # 清理内存
        del data
        import gc
        gc.collect()
```

## 故障排除指南

### 常见问题及解决方案

#### 1. 部署失败
**问题**: 应用部署时出错
**解决**: 
- 检查 `requirements.txt` 格式
- 确保 `streamlit_app.py` 存在
- 查看部署日志排查具体错误

#### 2. 内存溢出
**问题**: 应用运行时内存不足
**解决**:
- 减少批处理大小
- 使用 `@st.cache_data` 缓存结果
- 及时清理大对象

#### 3. API调用失败
**问题**: 智普AI API调用异常
**解决**:
- 检查API密钥配置
- 验证网络连接
- 添加重试机制

#### 4. 文件上传失败
**问题**: 大文件上传超时
**解决**:
- 调整 `maxUploadSize` 配置
- 添加文件大小检查
- 提供压缩建议

### 调试技巧
```python
# 添加调试信息
if st.checkbox("显示调试信息"):
    st.json({
        'session_state': dict(st.session_state),
        'secrets_available': bool(st.secrets),
        'memory_usage': f"{psutil.virtual_memory().percent:.1f}%"
    })
```

## 更新和维护

### 代码更新流程
```bash
# 本地测试
streamlit run streamlit_app.py

# 推送更新
git add .
git commit -m "Update: description of changes"
git push origin main

# Streamlit Cloud会自动重新部署
```

### 版本管理建议
- 使用语义化版本号
- 重要更新前创建备份分支
- 在README.md中维护更新日志

---

通过以上配置和部署流程，您的英语学习助手应用将成功运行在Streamlit Cloud平台上，为用户提供稳定可靠的服务。