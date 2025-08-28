"""
测试Streamlit上传文件的URL获取
"""
import streamlit as st
from PIL import Image
import tempfile
import os

st.title("测试Streamlit文件上传URL")

uploaded_file = st.file_uploader("上传图片", type=['jpg', 'jpeg', 'png'])

if uploaded_file is not None:
    # 显示上传的文件信息
    st.write("文件信息:")
    st.write(f"- 文件名: {uploaded_file.name}")
    st.write(f"- 文件类型: {uploaded_file.type}")
    st.write(f"- 文件大小: {uploaded_file.size} bytes")
    
    # 显示图片
    image = Image.open(uploaded_file)
    st.image(image, caption="上传的图片")
    
    # 尝试获取文件的URL或路径
    st.write("文件对象属性:")
    st.write(f"- uploaded_file对象: {type(uploaded_file)}")
    
    # 保存到临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        temp_path = tmp_file.name
        
    st.write(f"- 临时文件路径: {temp_path}")
    
    # 检查Streamlit是否提供URL
    if hasattr(uploaded_file, 'url'):
        st.write(f"- Streamlit URL: {uploaded_file.url}")
    else:
        st.write("- uploaded_file没有url属性")
    
    # 检查所有属性
    st.write("所有属性:")
    for attr in dir(uploaded_file):
        if not attr.startswith('_'):
            try:
                value = getattr(uploaded_file, attr)
                if not callable(value):
                    st.write(f"- {attr}: {value}")
            except:
                pass
    
    # 测试各种可能的URL格式
    if hasattr(uploaded_file, 'file_id') and uploaded_file.file_id:
        # 尝试不同的URL格式
        url_patterns = [
            f"http://localhost:8505/_stcore/uploaded_files/{uploaded_file.file_id}/{uploaded_file.name}",
            f"http://localhost:8505/media/{uploaded_file.file_id}/{uploaded_file.name}",
            f"http://localhost:8505/upload/{uploaded_file.file_id}",
            f"http://localhost:8505/_stcore/media/{uploaded_file.file_id}",
        ]
        
        import requests
        for i, url in enumerate(url_patterns):
            st.write(f"**测试URL {i+1}**: {url}")
            try:
                response = requests.head(url, timeout=3)
                st.write(f"  - HTTP {response.status_code}")
                if response.status_code == 200:
                    st.success("✅ 这个URL可以访问！")
                    break
            except Exception as e:
                st.write(f"  - 错误: {str(e)[:100]}")
    
    # 检查Streamlit内部如何处理文件
    st.write("**调试信息**:")
    st.write(f"- Streamlit version: {st.__version__}")
    
    # 尝试获取文件的实际二进制数据
    if uploaded_file:
        st.write(f"- 文件可读: {not uploaded_file.closed}")
        try:
            file_bytes = uploaded_file.getvalue()
            st.write(f"- 成功读取字节数: {len(file_bytes)}")
        except Exception as e:
            st.write(f"- 读取失败: {e}")
            
    # 检查是否有其他方式获取URL
    try:
        import streamlit.runtime.scriptrunner as sr
        ctx = sr.get_script_run_ctx()
        if ctx:
            st.write(f"- Session ID: {ctx.session_id}")
    except:
        pass