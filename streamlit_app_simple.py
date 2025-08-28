"""
英语学习助手 - 简化测试版本
不依赖外部网络和复杂包
"""

import streamlit as st
import os
import sys
from pathlib import Path

def main():
    """主函数"""
    st.set_page_config(
        page_title="英语学习助手 - 测试版",
        page_icon="📚",
        layout="wide"
    )
    
    st.markdown("# 📚 英语学习助手 - 测试版")
    st.markdown("---")
    
    # 环境检查
    st.markdown("## 🔍 环境检查")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### Python版本")
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        st.success(f"✅ Python {python_version}")
    
    with col2:
        st.markdown("### 项目结构")
        project_root = Path(__file__).parent
        if (project_root / "src").exists():
            st.success("✅ 项目结构完整")
        else:
            st.error("❌ 项目结构不完整")
    
    with col3:
        st.markdown("### API密钥")
        api_key = os.environ.get("ENGLISH_LEARNING_ZHIPU_API_KEY")
        if api_key:
            st.success("✅ API密钥已配置")
            st.text(f"密钥前缀: {api_key[:8]}...")
        else:
            st.warning("⚠️ 未检测到API密钥")
            st.code("set ENGLISH_LEARNING_ZHIPU_API_KEY=your_key_here")
    
    st.markdown("---")
    
    # 功能测试
    st.markdown("## 🧪 功能测试")
    
    tab1, tab2, tab3 = st.tabs(["基础功能", "模块导入", "网络测试"])
    
    with tab1:
        st.markdown("### 文件上传测试")
        uploaded_file = st.file_uploader(
            "选择图片文件",
            type=['png', 'jpg', 'jpeg'],
            help="测试文件上传功能"
        )
        
        if uploaded_file:
            st.success(f"✅ 文件上传成功: {uploaded_file.name}")
            st.text(f"文件大小: {len(uploaded_file.getvalue())} 字节")
            
            # 显示图片
            try:
                from PIL import Image
                image = Image.open(uploaded_file)
                st.image(image, caption=uploaded_file.name, use_column_width=True)
                st.success("✅ 图片显示成功")
            except ImportError:
                st.error("❌ PIL/Pillow 未安装")
            except Exception as e:
                st.error(f"❌ 图片处理错误: {e}")
    
    with tab2:
        st.markdown("### 模块导入测试")
        
        modules_to_test = [
            ("streamlit", "✅ 已导入"),
            ("PIL", "Pillow图像处理"),
            ("numpy", "数值计算"),
            ("cv2", "OpenCV图像处理"),
            ("requests", "HTTP请求"),
            ("paddleocr", "OCR识别引擎")
        ]
        
        for module_name, description in modules_to_test:
            try:
                __import__(module_name)
                st.success(f"✅ {module_name}: {description}")
            except ImportError:
                st.error(f"❌ {module_name}: 未安装")
            except Exception as e:
                st.warning(f"⚠️ {module_name}: {e}")
    
    with tab3:
        st.markdown("### 网络连接测试")
        
        if st.button("测试网络连接"):
            # 测试基本网络连接
            try:
                import socket
                socket.create_connection(("8.8.8.8", 53), timeout=3)
                st.success("✅ 基本网络连接正常")
            except:
                st.error("❌ 网络连接异常")
            
            # 测试HTTP访问
            test_urls = [
                "https://www.baidu.com",
                "https://open.bigmodel.cn",
                "https://pypi.org"
            ]
            
            for url in test_urls:
                try:
                    import urllib.request
                    urllib.request.urlopen(url, timeout=5)
                    st.success(f"✅ {url} 访问正常")
                except Exception as e:
                    st.error(f"❌ {url} 访问失败: {e}")
    
    st.markdown("---")
    
    # 项目信息
    st.markdown("## 📋 项目信息")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 技术栈")
        st.markdown("""
        - **前端**: Streamlit
        - **OCR**: PaddleOCR 3.1
        - **AI**: 智普AI GLM-4.5-flash
        - **图像处理**: OpenCV + PIL
        - **部署**: Streamlit Cloud
        """)
    
    with col2:
        st.markdown("### 项目状态")
        project_files = [
            "streamlit_app.py",
            "src/core/ocr_processor.py", 
            "src/core/ai_analyzer.py",
            "src/ui/main_interface.py",
            "requirements.txt"
        ]
        
        project_root = Path(__file__).parent
        for file_path in project_files:
            full_path = project_root / file_path
            if full_path.exists():
                st.success(f"✅ {file_path}")
            else:
                st.error(f"❌ {file_path}")
    
    st.markdown("---")
    st.markdown(
        '<p style="text-align: center; color: #666;">'
        '🤖 英语学习助手测试版 | 基于 Streamlit + AI增强OCR'
        '</p>',
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()