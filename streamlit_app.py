"""
英语学习助手 - Streamlit应用入口
AI增强OCR系统 + 智能文档生成

基于PaddleOCR 3.1 + 智普AI GLM-4.5-flash
"""

import sys
import os
from pathlib import Path
import streamlit as st

# 设置API密钥环境变量（如果尚未设置）
if not os.getenv("ENGLISH_LEARNING_ZHIPU_API_KEY"):
    os.environ["ENGLISH_LEARNING_ZHIPU_API_KEY"] = "17e5feb32ed94b66823c9f9e0f188752.XOQDn1kygRTltwfD"

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 导入应用模块
try:
    from src.ui.main_interface import create_main_interface
    # 延迟导入config，确保环境变量已设置
    import importlib
    config_module = importlib.import_module('src.utils.config')
    config = config_module.config
except ImportError as e:
    st.error(f"模块导入失败: {e}")
    st.error("请确保项目结构完整，并安装了所有依赖包")
    st.stop()


def check_environment():
    """检查运行环境"""
    issues = []
    
    # 检查API密钥
    api_key = config.get_api_key()
    if not api_key:
        issues.append({
            'type': 'warning',
            'message': '未配置AI API密钥',
            'solution': '请设置环境变量 ENGLISH_LEARNING_ZHIPU_API_KEY'
        })
    
    # 检查PaddleOCR（云端版本使用备用方案）
    try:
        import importlib.util
        paddleocr_spec = importlib.util.find_spec("paddleocr")
        if paddleocr_spec is not None:
            # 延迟导入避免触发自动安装
            paddleocr = importlib.import_module("paddleocr")
            ocr_version = getattr(paddleocr, '__version__', '未知')
            st.sidebar.success(f"PaddleOCR版本: {ocr_version}")
        else:
            raise ImportError("PaddleOCR not available")
    except ImportError:
        # 云端模式：使用备用OCR方案
        st.sidebar.info("🌐 云端模式：使用AI增强文本分析（手动输入）")
        st.sidebar.markdown("*完整OCR功能可在本地环境使用*")
    
    # 检查OpenCV
    try:
        import cv2
        cv_version = cv2.__version__
        st.sidebar.success(f"OpenCV版本: {cv_version}")
    except ImportError:
        issues.append({
            'type': 'error',
            'message': 'OpenCV未安装',
            'solution': '运行命令: pip install opencv-python'
        })
    
    # 检查必要的目录
    output_dir = Path('./output')
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)
        st.sidebar.info("已创建输出目录: ./output")
    
    # 显示问题
    if issues:
        st.sidebar.markdown("### ⚠️ 环境检查")
        for issue in issues:
            if issue['type'] == 'error':
                st.sidebar.error(f"❌ {issue['message']}")
                st.sidebar.code(issue['solution'])
            else:
                st.sidebar.warning(f"⚠️ {issue['message']}")
                st.sidebar.code(issue['solution'])
        
        if any(issue['type'] == 'error' for issue in issues):
            st.error("存在严重环境问题，应用可能无法正常工作")
            return False
    
    return True


def main():
    """主函数"""
    # 环境检查
    if not check_environment():
        st.stop()
    
    # 创建并运行主界面
    try:
        interface = create_main_interface()
        interface.run()
        
    except Exception as e:
        st.error(f"应用运行错误: {e}")
        
        # 显示详细错误信息（仅在开发模式）
        if st.checkbox("显示详细错误信息"):
            import traceback
            st.code(traceback.format_exc())
        
        st.markdown("### 🔧 故障排除建议")
        st.markdown("""
        1. **检查依赖安装**：确保已安装所有必需的Python包
        2. **API密钥配置**：确认环境变量设置正确
        3. **网络连接**：确保可以正常访问AI服务
        4. **文件权限**：确保应用有权限读写输出目录
        5. **重新启动**：尝试重新启动Streamlit应用
        """)


if __name__ == "__main__":
    main()