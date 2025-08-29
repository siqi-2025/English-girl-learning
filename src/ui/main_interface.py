"""
主界面模块

英语学习助手的Streamlit主界面
"""

import streamlit as st
import os
import time
import tempfile
from pathlib import Path
from typing import List, Dict, Optional

from ..core.vision_processor import create_vision_processor
from ..core.ai_analyzer import create_ai_enhanced_ocr, test_ai_connection
from ..core.document_generator import DocumentGenerator
from ..utils.config import config


class EnglishLearningInterface:
    """英语学习助手主界面"""
    
    def __init__(self):
        self.version = "v2.0.0"  # 现代化UI重设计，左右分栏布局
        self.vision_processor = None
        self.ai_analyzer = None
        self.doc_generator = None
        self.processed_results = []  # 存储处理结果
        print(f"[EnglishLearningInterface] 初始化界面 {self.version}")
        
    def setup_page_config(self):
        """设置页面配置"""
        st.set_page_config(
            page_title="英语学习助手 - AI增强OCR系统",
            page_icon="📚",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # 自定义CSS样式
        st.markdown("""
        <style>
        .main-header {
            color: #1f77b4;
            text-align: center;
            font-size: 2.5rem;
            margin-bottom: 2rem;
        }
        .feature-card {
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            padding: 1rem;
            margin: 1rem 0;
            background-color: #f8f9fa;
        }
        .success-message {
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
            padding: 0.75rem;
            border-radius: 0.25rem;
            margin: 1rem 0;
        }
        .warning-message {
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            color: #856404;
            padding: 0.75rem;
            border-radius: 0.25rem;
            margin: 1rem 0;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def render_header(self):
        """渲染页面头部"""
        st.markdown(f'<h1 class="main-header">📚 英语学习助手 {self.version}</h1>', unsafe_allow_html=True)
        st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">纯AI视觉识别系统 + 智能文档生成</p>', unsafe_allow_html=True)
        st.markdown(f'<p style="text-align: center; font-size: 0.9rem; color: #888;">版本: {self.version} | 基于GLM-4V-Flash纯视觉识别</p>', unsafe_allow_html=True)
        print(f"[UI] 渲染头部，版本: {self.version}")
        
        # 系统状态检查
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if test_ai_connection():
                st.success("🤖 AI服务连接正常")
            else:
                st.error("❌ AI服务连接失败")
                
        with col2:
            st.success("👁️ GLM-4V-Flash视觉识别就绪")
            print("[UI] GLM-4V-Flash视觉识别模块状态: 就绪")
                
        with col3:
            api_key = config.get_api_key()
            if api_key:
                st.success("🔑 API密钥已配置")
            else:
                st.warning("⚠️ 请配置API密钥")
    
    def render_sidebar(self):
        """渲染简化的侧边栏"""
        with st.sidebar:
            st.markdown(f"### 🤖 英语学习助手 {self.version}")
            
            # API状态检查
            current_key = config.get_api_key()
            if current_key:
                st.success("🔑 API已配置")
            else:
                st.error("❌ 需要配置API密钥")
                st.code("设置环境变量: ENGLISH_LEARNING_ZHIPU_API_KEY")
            
            st.markdown("---")
            
            # 使用统计
            st.markdown("### 📊 本次会话统计")
            
            # 初始化session state
            if 'processed_count' not in st.session_state:
                st.session_state.processed_count = 0
            if 'generated_docs' not in st.session_state:
                st.session_state.generated_docs = 0
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("已处理", st.session_state.processed_count)
            with col2:
                st.metric("已导出", st.session_state.generated_docs)
            
            st.markdown("---")
            
            # 关于信息
            with st.expander("ℹ️ 关于", expanded=False):
                st.markdown(f"""
                **版本**: {self.version}  
                **核心技术**: GLM-4V-Flash  
                **图床**: GitHub  
                **功能**: OCR文字识别
                """)
            
            return {
                'temperature': 0.8,  # 固定参数
                'max_tokens': 1024
            }
    
    def render_image_upload_section(self, settings: Dict):
        """渲染图像上传区域"""
        st.markdown("### 📷 图像处理")
        
        # 选择输入方式
        input_method = st.radio(
            "选择输入方式：",
            ["上传图片文件", "批量处理文件夹"],
            horizontal=True
        )
        
        if input_method == "上传图片文件":
            uploaded_files = st.file_uploader(
                "选择英语教材图片",
                type=['png', 'jpg', 'jpeg', 'bmp', 'tiff'],
                accept_multiple_files=True,
                help="支持多种图片格式，可同时上传多个文件"
            )
            
            if uploaded_files:
                # 简单显示上传的图片，不调用AI
                return self._display_uploaded_images(uploaded_files)
                
        else:
            folder_path = st.text_input(
                "输入图片文件夹路径",
                value=r"D:\360MoveData\Users\wukon\Pictures\7上英语",
                help="输入包含英语教材图片的文件夹完整路径"
            )
            
            if st.button("🔍 扫描文件夹"):
                if os.path.exists(folder_path):
                    return self._process_folder(folder_path, settings)
                else:
                    st.error("文件夹路径不存在，请检查路径是否正确")
        
        return None
    
    def _process_uploaded_files(self, uploaded_files: List, settings: Dict) -> Optional[Dict]:
        """处理上传的文件"""
        if not uploaded_files:
            return None
            
        st.info(f"已上传 {len(uploaded_files)} 个文件")
        
        if st.button("🚀 开始处理", type="primary"):
            print(f"\n{'='*80}")
            print(f"[主流程] 🚀 用户点击开始处理按钮")
            print(f"[主流程] 系统版本: {self.version}")
            print(f"[主流程] 待处理文件数量: {len(uploaded_files)}")
            print(f"[主流程] 当前时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*80}")
            st.write("**🔄 开始处理，查看控制台获取详细日志...**")
            
            # 初始化处理器
            if not self._initialize_processors():
                print(f"[处理] 处理器初始化失败")
                return None
            else:
                print(f"[处理] 处理器初始化成功")
                
            results = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, uploaded_file in enumerate(uploaded_files):
                status_text.text(f"正在处理: {uploaded_file.name}")
                
                try:
                    # 调试：检查处理器状态
                    print(f"[调试] vision_processor存在: {self.vision_processor is not None}")
                    print(f"[调试] ai_analyzer存在: {self.ai_analyzer is not None}")
                    
                    # 步骤1: GLM-4V-Flash视觉识别
                    status_text.text(f"🔍 步骤1: GLM-4V-Flash视觉识别 - {uploaded_file.name}")
                    print(f"\n[第{i+1}步] ==================== 开始处理文件 ====================")
                    print(f"[第{i+1}步] 📁 文件名: {uploaded_file.name}")
                    print(f"[第{i+1}步] 📊 文件大小: {uploaded_file.size} bytes")
                    print(f"[第{i+1}步] 🎯 文件类型: {uploaded_file.type}")
                    print(f"[第{i+1}步] 🔄 调用VisionProcessor.process_image()...")
                    
                    vision_result = self.vision_processor.process_image(uploaded_file.getvalue(), uploaded_file=uploaded_file)
                    
                    print(f"[第{i+1}步] ✅ GLM-4V-Flash处理完成")
                    print(f"[第{i+1}步] 🎯 识别成功: {vision_result['success']}")
                    if vision_result['success']:
                        print(f"[第{i+1}步] 📝 识别文本长度: {len(vision_result.get('raw_text', ''))} 字符")
                        print(f"[第{i+1}步] 🎯 置信度: {vision_result.get('confidence', 0)}")
                    else:
                        print(f"[第{i+1}步] ❌ 识别失败原因: {vision_result.get('error', '未知错误')}")
                    
                    # 调试：显示视觉识别结果
                    st.write("**调试信息 - GLM-4V-Flash识别结果：**")
                    st.json(vision_result)
                    
                    # 步骤2: AI增强处理
                    if vision_result['success']:
                        status_text.text(f"🤖 步骤2: AI分析和增强 - {uploaded_file.name}")
                        st.info(f"识别到的文本长度: {len(vision_result.get('raw_text', ''))}")
                        print(f"[处理] 开始AI分析，文本长度: {len(vision_result.get('raw_text', ''))}")
                        
                        try:
                            enhanced_result = self.ai_analyzer.process_image_with_ai(
                                vision_result, f"英语教材 - {uploaded_file.name}"
                            )
                            # 调试：显示AI增强结果
                            st.write("**调试信息 - AI增强结果：**")
                            st.json(enhanced_result)
                            
                            enhanced_result['filename'] = uploaded_file.name
                            results.append(enhanced_result)
                            st.session_state.processed_count += 1
                        except Exception as ai_error:
                            print(f"[处理] AI分析失败: {ai_error}")
                            st.error(f"AI处理失败: {ai_error}")
                            # 创建基本的错误结果
                            enhanced_result = {
                                'success': False,
                                'error': str(ai_error),
                                'raw_text': vision_result.get('raw_text', ''),
                                'confidence': vision_result.get('confidence', 0),
                                'analysis': {}
                            }
                            enhanced_result['filename'] = uploaded_file.name
                            results.append(enhanced_result)
                    else:
                        print(f"[处理] 视觉识别失败: {vision_result.get('error', '未知错误')}")
                        st.error(f"视觉识别失败: {vision_result.get('error', '未知错误')}")
                        continue
                    
                except Exception as e:
                    print(f"[处理] 处理 {uploaded_file.name} 异常: {e}")
                    print(f"[处理] 异常详情: {type(e).__name__}")
                    import traceback
                    print(f"[处理] 堆栈跟踪: {traceback.format_exc()}")
                    st.error(f"处理 {uploaded_file.name} 时出错: {e}")
                
                progress_bar.progress((i + 1) / len(uploaded_files))
            
            status_text.text("✅ 处理完成！")
            return {'results': results, 'source': 'upload'}
        
        return None
    
    def _process_folder(self, folder_path: str, settings: Dict) -> Optional[Dict]:
        """处理文件夹中的图片"""
        try:
            # 扫描图片文件
            image_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']
            image_files = []
            
            for ext in image_extensions:
                image_files.extend(Path(folder_path).glob(f"*{ext}"))
                image_files.extend(Path(folder_path).glob(f"*{ext.upper()}"))
            
            if not image_files:
                st.warning("未找到图片文件")
                return None
            
            st.success(f"找到 {len(image_files)} 个图片文件")
            
            # 显示文件列表预览
            with st.expander("📁 文件列表预览"):
                for file_path in image_files[:10]:  # 只显示前10个
                    st.text(file_path.name)
                if len(image_files) > 10:
                    st.text(f"... 还有 {len(image_files) - 10} 个文件")
            
            if st.button("🚀 开始批量处理", type="primary"):
                return self._batch_process_images(image_files, settings)
                
        except Exception as e:
            st.error(f"扫描文件夹失败: {e}")
        
        return None
    
    def _batch_process_images(self, image_files: List[Path], settings: Dict) -> Optional[Dict]:
        """批量处理图片"""
        if not self._initialize_processors():
            return None
        
        results = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # 创建处理结果表格
        result_container = st.container()
        
        for i, image_path in enumerate(image_files):
            # 详细处理步骤日志
            status_text.text(f"📁 正在处理文件: {image_path.name} ({i+1}/{len(image_files)})")
            
            try:
                # 步骤1: GLM-4V-Flash视觉识别
                status_text.text(f"🔍 步骤1: GLM-4V-Flash视觉识别 - {image_path.name}")
                print(f"[批量处理] 开始处理文件: {image_path.name}")
                vision_result = self.vision_processor.process_image(str(image_path), uploaded_file=None)
                print(f"[批量处理] 视觉识别完成，成功: {vision_result['success']}")
                
                # 调试：显示视觉识别结果
                st.write("**调试信息 - GLM-4V-Flash识别结果：**")
                st.json(vision_result)
                
                # 步骤2: AI增强处理
                if vision_result['success']:
                    status_text.text(f"🤖 步骤2: AI分析和增强 - {image_path.name}")
                    st.info(f"识别到的文本长度: {len(vision_result.get('raw_text', ''))}")
                    print(f"[批量处理] 开始AI分析，文本长度: {len(vision_result.get('raw_text', ''))}")
                    time.sleep(0.5)  # 让用户看到处理步骤
                    
                    try:
                        enhanced_result = self.ai_analyzer.process_image_with_ai(
                            vision_result, f"英语教材 - {image_path.name}"
                        )
                        st.write("**调试信息 - AI增强结果：**")
                        st.json(enhanced_result)
                    except Exception as ai_error:
                        print(f"[批量处理] AI分析失败: {ai_error}")
                        st.error(f"AI处理失败: {ai_error}")
                        # 创建基本的错误结果
                        enhanced_result = {
                            'success': False,
                            'error': str(ai_error),
                            'raw_text': vision_result.get('raw_text', ''),
                            'confidence': vision_result.get('confidence', 0),
                            'analysis': {}
                        }
                else:
                    print(f"[批量处理] 视觉识别失败: {vision_result.get('error', '未知错误')}")
                    st.error(f"视觉识别失败: {vision_result.get('error', '未知错误')}")
                    continue
                
                # 步骤3: 整理结果
                status_text.text(f"📝 步骤3: 整理和分类内容 - {image_path.name}")
                enhanced_result['filename'] = image_path.name
                enhanced_result['filepath'] = str(image_path)
                results.append(enhanced_result)
                st.session_state.processed_count += 1
                
                # 步骤4: 显示完成状态
                status_text.text(f"✅ 完成处理: {image_path.name}")
                time.sleep(0.3)
                
                # 实时显示处理结果
                with result_container:
                    if len(results) == 1:
                        st.markdown("### 📊 处理结果")
                    
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.text(f"✅ {image_path.name}")
                    with col2:
                        st.text(f"置信度: {enhanced_result.get('confidence', 0):.2f}")
                    with col3:
                        analysis = enhanced_result.get('analysis', {})
                        st.text(f"类型: {analysis.get('content_type', '未知')}")
                
            except Exception as e:
                st.error(f"处理 {image_path.name} 失败: {e}")
                
            progress_bar.progress((i + 1) / len(image_files))
        
        status_text.text("✅ 批量处理完成！")
        return {'results': results, 'source': 'folder'}
    
    def _display_uploaded_images(self, uploaded_files: List) -> Dict:
        """准备图片文件并提供AI处理选项"""
        results = []
        
        # 现代化简洁显示
        with st.status("📤 正在上传图片到GitHub图床...", expanded=True) as status:
            for i, uploaded_file in enumerate(uploaded_files):
                st.write(f"处理 {uploaded_file.name}...")
                
                # 上传到GitHub图床
                image_url = self._upload_to_github_and_get_url(uploaded_file)
                
                # 记录结果
                results.append({
                    'filename': uploaded_file.name,
                    'size': uploaded_file.size,
                    'type': uploaded_file.type,
                    'url': image_url,
                    'displayed': True,
                    'success': image_url is not None
                })
            
            status.update(label="✅ 上传完成", state="complete")
        
        # 显示上传结果摘要
        successful_uploads = sum(1 for r in results if r.get('success'))
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("总文件数", len(results))
        with col2:
            st.metric("上传成功", successful_uploads)
        with col3:
            total_size = sum(r.get('size', 0) for r in results)
            st.metric("总大小", f"{total_size//1024} KB")
        
        if successful_uploads == 0:
            st.error("❌ 没有文件上传成功，请检查网络连接或GitHub配置")
            return None
        
        # 处理按钮
        st.markdown("---")
        if st.button("🤖 开始AI识别处理", type="primary", use_container_width=True):
            return self._process_images_with_ai(uploaded_files, results)
        
        return {'results': results, 'source': 'upload_display_only'}
    
    # 删除此方法 - 不再使用静态文件保存
    
    def _detect_cloud_environment(self) -> bool:
        """检测是否在云环境中运行"""
        import os
        
        # 检查Streamlit Cloud环境变量
        cloud_indicators = [
            'STREAMLIT_SHARING_MODE',
            'STREAMLIT_CLOUD',
            ('HOSTNAME', lambda x: 'streamlit' in str(x).lower()),
            ('SERVER_NAME', lambda x: 'streamlit.app' in str(x).lower())
        ]
        
        for indicator in cloud_indicators:
            if isinstance(indicator, tuple):
                var_name, check_func = indicator
                if var_name in os.environ and check_func(os.environ[var_name]):
                    print(f"[环境检测] 通过 {var_name}={os.environ[var_name]} 检测到云环境")
                    return True
            else:
                if indicator in os.environ:
                    print(f"[环境检测] 通过 {indicator} 检测到云环境")
                    return True
        
        print(f"[环境检测] 检测到本地环境")
        return False
    
    # 删除此方法 - 不再使用Streamlit媒体URL
    
    # 删除此方法 - 不再使用静态文件保存
    
    def _upload_to_github_and_get_url(self, uploaded_file) -> Optional[str]:
        """上传文件到GitHub并获取真实的访问URL"""
        try:
            print(f"[GitHub图床] 开始上传文件到GitHub")
            
            # 创建临时文件
            import tempfile
            import time
            import uuid
            
            timestamp = int(time.time())
            file_extension = uploaded_file.name.split('.')[-1] if '.' in uploaded_file.name else 'jpg'
            unique_id = str(uuid.uuid4())[:8]
            filename = f"upload_{timestamp}_{unique_id}.{file_extension}"
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_extension}') as temp_file:
                temp_file.write(uploaded_file.getvalue())
                temp_file_path = temp_file.name
            
            print(f"[GitHub图床] 临时文件创建: {temp_file_path}")
            
            # 使用AI分析器的GitHub上传功能
            from ..core.ai_analyzer import ZhipuAIClient
            ai_client = ZhipuAIClient()
            github_url = ai_client._upload_image_to_github(temp_file_path)
            
            # 清理临时文件
            import os
            try:
                os.unlink(temp_file_path)
                print(f"[GitHub图床] 清理临时文件: {temp_file_path}")
            except:
                pass
            
            return github_url
                
        except Exception as e:
            print(f"[GitHub图床] ❌ 上传异常: {e}")
            import streamlit as st
            st.error(f"❌ GitHub图床上传异常: {e}")
            return None
    
    def _process_images_with_ai(self, uploaded_files: List, file_results: List[Dict]) -> Dict:
        """使用AI处理图片"""
        # 初始化处理器
        if not self._initialize_processors():
            st.error("❌ 处理器初始化失败")
            return None
        
        processed_results = []
        
        with st.status("🤖 AI识别处理中...", expanded=True) as status:
            for i, (uploaded_file, file_info) in enumerate(zip(uploaded_files, file_results)):
                if not file_info.get('success'):  # 跳过上传失败的文件
                    continue
                
                st.write(f"🔍 处理: {uploaded_file.name}")
                
                try:
                    static_url = file_info.get('url')
                    if not static_url:
                        continue
                    
                    # GLM-4V-Flash视觉识别
                    vision_result = self.vision_processor.process_image(static_url, uploaded_file=None)
                    
                    if vision_result['success']:
                        # AI增强处理
                        enhanced_result = self.ai_analyzer.process_image_with_ai(
                            vision_result, f"英语教材 - {uploaded_file.name}"
                        )
                        
                        result = {
                            'filename': uploaded_file.name,
                            'static_url': static_url,
                            'success': True,
                            'vision_result': vision_result,
                            'enhanced_result': enhanced_result
                        }
                        
                        # 更新统计
                        st.session_state.processed_count += 1
                        
                    else:
                        result = {
                            'filename': uploaded_file.name,
                            'static_url': static_url,
                            'success': False,
                            'error': vision_result.get('error', '识别失败')
                        }
                    
                    processed_results.append(result)
                    
                except Exception as e:
                    processed_results.append({
                        'filename': uploaded_file.name,
                        'static_url': file_info.get('url'),
                        'success': False,
                        'error': str(e)
                    })
            
            status.update(label="✅ 处理完成", state="complete")
        
        return {
            'results': processed_results,
            'source': 'ai_processed'
        }
    
    def _get_static_file_path(self, static_url: str) -> Optional[str]:
        """从官方静态URL获取本地文件路径"""
        if not static_url:
            return None
        
        try:
            from pathlib import Path
            # 从官方URL格式中提取文件名 (/app/static/filename)
            if '/app/static/' in static_url:
                filename = static_url.split('/app/static/')[-1]
            elif '/static/' in static_url:  # 兼容旧格式
                filename = static_url.split('/static/')[-1]
            else:
                filename = static_url.split('/')[-1]
            
            print(f"[文件路径] 从URL提取文件名: {filename}")
            
            # 构造本地文件路径
            project_root = Path(__file__).parent.parent.parent
            static_dir = project_root / "static"
            file_path = static_dir / filename
            
            print(f"[文件路径] 构造的文件路径: {file_path}")
            print(f"[文件路径] 文件是否存在: {file_path.exists()}")
            
            return str(file_path) if file_path.exists() else None
        except Exception as e:
            print(f"[文件路径] ❌ 获取文件路径失败: {e}")
            return None
    
    def _cleanup_static_files(self, processed_results: List[Dict]) -> Dict:
        """清理处理完成的静态文件（只删除成功处理的文件）"""
        cleanup_summary = {
            'total_files': len(processed_results),
            'deleted_files': 0,
            'skipped_files': 0,
            'failed_deletions': 0,
            'deleted_list': [],
            'skipped_list': [],
            'failed_list': []
        }
        
        for result in processed_results:
            file_path = result.get('file_path')
            filename = result.get('filename', 'unknown')
            success = result.get('success', False)
            
            # 只删除成功处理的文件
            if not success:
                cleanup_summary['skipped_files'] += 1
                cleanup_summary['skipped_list'].append(filename)
                print(f"[清理] ⏭️ 跳过失败文件: {filename} (保留用于调试)")
                continue
            
            if file_path:
                try:
                    import os
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        cleanup_summary['deleted_files'] += 1
                        cleanup_summary['deleted_list'].append(filename)
                        print(f"[清理] ✅ 已删除: {file_path}")
                    else:
                        print(f"[清理] ⚠️ 文件不存在: {file_path}")
                except Exception as e:
                    cleanup_summary['failed_deletions'] += 1
                    cleanup_summary['failed_list'].append(filename)
                    print(f"[清理] ❌ 删除失败 {file_path}: {e}")
            else:
                print(f"[清理] ⚠️ 无法获取文件路径: {filename}")
        
        # 显示清理结果
        if cleanup_summary['deleted_files'] > 0:
            st.success(f"🧹 已清理 {cleanup_summary['deleted_files']} 个成功处理的文件")
        
        if cleanup_summary['skipped_files'] > 0:
            st.info(f"💾 保留 {cleanup_summary['skipped_files']} 个失败文件用于调试")
            
        if cleanup_summary['failed_deletions'] > 0:
            st.warning(f"⚠️ {cleanup_summary['failed_deletions']} 个文件清理失败")
        
        print(f"[清理] 📊 清理统计: {cleanup_summary}")
        return cleanup_summary
    
    def _initialize_processors(self) -> bool:
        """初始化处理器"""
        try:
            print(f"[初始化] 开始初始化处理器...")
            
            if self.vision_processor is None:
                with st.spinner("初始化GLM-4V-Flash视觉识别引擎..."):
                    print(f"[初始化] 创建视觉处理器...")
                    self.vision_processor = create_vision_processor()
            
            if self.ai_analyzer is None:
                with st.spinner("初始化AI分析引擎..."):
                    print(f"[初始化] 创建AI分析器...")
                    self.ai_analyzer = create_ai_enhanced_ocr()
            
            if self.doc_generator is None:
                print(f"[初始化] 创建文档生成器...")
                self.doc_generator = DocumentGenerator()
            
            print(f"[初始化] 处理器初始化完成")
            return True
            
        except Exception as e:
            print(f"[初始化] 初始化失败: {e}")
            st.error(f"初始化处理器失败: {e}")
            return False
    
    def render_results_section(self, processing_results: Dict):
        """渲染处理结果区域 - 现代化左右分栏布局"""
        if not processing_results or not processing_results.get('results'):
            return
        
        results = processing_results['results']
        source = processing_results.get('source', 'unknown')
        
        # 存储处理结果供后续使用
        self.processed_results = results
        
        # 检查是否是纯显示模式（上传但未处理）
        if source == 'upload_display_only':
            st.info("📋 图片已上传，点击 '🤖 开始AI识别处理' 按钮进行处理")
            return
        
        # 显示成功处理的结果
        successful_results = [r for r in results if r.get('success', False)]
        if not successful_results:
            st.error("❌ 没有成功处理的图片")
            return
        
        # 现代化UI - 左右分栏布局
        st.markdown("---")
        
        # 顶部工具栏
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.markdown("### 📋 处理结果")
        with col2:
            # 导出按钮
            if st.button("📄 导出文本", type="primary", use_container_width=True):
                self._export_all_text(successful_results)
        with col3:
            # 统计信息
            st.metric("成功处理", len(successful_results), delta=f"共{len(results)}个")
        
        # 左右分栏主要内容区域
        left_col, right_col = st.columns([3, 2])
        
        with left_col:
            st.markdown("#### 📝 识别文本内容")
            self._render_text_content(successful_results)
        
        with right_col:
            st.markdown("#### 🖼️ 图片列表")
            self._render_image_thumbnails(successful_results)
    
    def _render_text_content(self, results: List[Dict]):
        """渲染左侧文本内容区域"""
        if not results:
            st.info("暂无文本内容")
            return
        
        # 创建选择器让用户选择要查看的文件
        if len(results) > 1:
            selected_index = st.selectbox(
                "选择文件:",
                range(len(results)),
                format_func=lambda x: f"{x+1}. {results[x].get('filename', f'文件{x+1}')}",
                key="text_selector"
            )
        else:
            selected_index = 0
        
        result = results[selected_index]
        
        # 显示文件信息
        filename = result.get('filename', '未知文件')
        st.markdown(f"**📄 当前文件**: {filename}")
        
        # 获取识别文本 - 优先显示增强结果
        enhanced_result = result.get('enhanced_result', {})
        vision_result = result.get('vision_result', {})
        
        # 获取文本内容
        text_content = ""
        if enhanced_result and enhanced_result.get('corrected_text'):
            text_content = enhanced_result['corrected_text']
            st.success("✨ AI增强文本")
        elif vision_result and vision_result.get('raw_text'):
            text_content = vision_result['raw_text']
            st.info("🔍 原始识别文本")
        else:
            st.warning("⚠️ 暂无文本内容")
            return
        
        # 显示文本内容
        if text_content:
            # 创建可滚动的文本区域
            st.markdown("---")
            st.text_area(
                "识别文本:",
                value=text_content,
                height=400,
                disabled=True,
                key=f"text_content_{selected_index}"
            )
            
            # 显示文本统计信息
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("字符数", len(text_content))
            with col2:
                word_count = len(text_content.split()) if text_content else 0
                st.metric("单词数", word_count)
            with col3:
                confidence = enhanced_result.get('confidence') or vision_result.get('confidence', 0)
                st.metric("置信度", f"{confidence:.1%}")
    
    def _render_image_thumbnails(self, results: List[Dict]):
        """渲染右侧图片缩略图列表"""
        if not results:
            st.info("暂无图片")
            return
        
        # 创建滚动容器
        for i, result in enumerate(results):
            filename = result.get('filename', f'文件{i+1}')
            
            # 创建图片卡片
            with st.container():
                st.markdown(f"**{i+1}. {filename}**")
                
                # 显示处理状态
                success = result.get('success', False)
                if success:
                    st.success("✅ 处理成功", icon="✅")
                else:
                    error_msg = result.get('error', '未知错误')
                    st.error(f"❌ 处理失败: {error_msg}", icon="❌")
                
                # 如果有GitHub URL，显示缩略图
                github_url = result.get('static_url') or result.get('url')
                if github_url and success:
                    try:
                        st.image(github_url, width=200, caption=filename)
                    except Exception as e:
                        st.error(f"图片加载失败: {e}")
                
                # 显示基本信息
                if 'size' in result:
                    st.caption(f"大小: {result['size']:,} bytes")
                
                st.markdown("---")
    
    def _export_all_text(self, results: List[Dict]):
        """导出所有识别文本为一个文档"""
        if not results:
            st.warning("没有可导出的内容")
            return
        
        # 收集所有文本
        all_text = []
        export_time = time.strftime("%Y-%m-%d %H:%M:%S")
        
        all_text.append(f"# 英语学习助手 - 文本识别结果")
        all_text.append(f"**导出时间**: {export_time}")
        all_text.append(f"**导出版本**: {self.version}")
        all_text.append(f"**成功处理**: {len(results)} 个文件")
        all_text.append("")
        
        for i, result in enumerate(results):
            filename = result.get('filename', f'文件{i+1}')
            all_text.append(f"## {i+1}. {filename}")
            
            # 获取文本内容
            enhanced_result = result.get('enhanced_result', {})
            vision_result = result.get('vision_result', {})
            
            if enhanced_result and enhanced_result.get('corrected_text'):
                text_content = enhanced_result['corrected_text']
                confidence = enhanced_result.get('confidence', 0)
                all_text.append(f"**文本来源**: AI增强识别 (置信度: {confidence:.1%})")
            elif vision_result and vision_result.get('raw_text'):
                text_content = vision_result['raw_text']
                confidence = vision_result.get('confidence', 0)
                all_text.append(f"**文本来源**: 原始识别 (置信度: {confidence:.1%})")
            else:
                text_content = "无文本内容"
                all_text.append(f"**文本来源**: 识别失败")
            
            all_text.append("")
            all_text.append("### 识别文本:")
            all_text.append(text_content)
            all_text.append("")
            all_text.append("---")
            all_text.append("")
        
        # 生成下载内容
        export_content = "\n".join(all_text)
        filename = f"english_learning_export_{int(time.time())}.md"
        
        # 提供下载
        st.download_button(
            label="💾 下载文本文件",
            data=export_content,
            file_name=filename,
            mime="text/markdown",
            type="primary",
            use_container_width=True
        )
        
        st.success(f"✅ 已准备下载文件: {filename}")
        st.info(f"📊 导出统计: {len(results)} 个文件, 总计 {len(export_content)} 个字符")
    
    def _render_overview_mode(self, results: List[Dict]):
        """渲染概览模式"""
        for i, result in enumerate(results):
            with st.expander(f"📄 {result.get('filename', f'文件{i+1}')}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown("**识别文本预览：**")
                    text = result.get('corrected_text', '')
                    preview = text[:200] + "..." if len(text) > 200 else text
                    st.text_area("", preview, height=100, disabled=True)
                
                with col2:
                    st.markdown("**分析信息：**")
                    analysis = result.get('analysis', {})
                    st.write(f"- 标题: {analysis.get('title', '未知')}")
                    st.write(f"- 类型: {analysis.get('content_type', '未知')}")
                    st.write(f"- 单元: {analysis.get('unit', '未知')}")
                    
                    vocab_count = len(analysis.get('vocabulary', []))
                    grammar_count = len(analysis.get('grammar_points', []))
                    st.write(f"- 词汇数: {vocab_count}")
                    st.write(f"- 语法点: {grammar_count}")
    
    def _render_detailed_mode(self, results: List[Dict]):
        """渲染详细模式"""
        selected_file = st.selectbox(
            "选择要查看的文件：",
            range(len(results)),
            format_func=lambda x: results[x].get('filename', f'文件{x+1}')
        )
        
        result = results[selected_file]
        
        # 基本信息
        st.markdown("#### 📊 基本信息")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("置信度", f"{result.get('confidence', 0):.2%}")
        with col2:
            st.metric("修正数量", len(result.get('corrections', [])))
        with col3:
            analysis = result.get('analysis', {})
            st.metric("词汇数量", len(analysis.get('vocabulary', [])))
        
        # 文本对比
        st.markdown("#### 📝 文本内容")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**原始OCR文本：**")
            st.text_area("", result.get('raw_ocr', ''), height=200, disabled=True)
        
        with col2:
            st.markdown("**AI校正文本：**")
            st.text_area("", result.get('corrected_text', ''), height=200, disabled=True)
        
        # 修正详情
        corrections = result.get('corrections', [])
        if corrections:
            st.markdown("#### 🔍 修正详情")
            for correction in corrections:
                st.markdown(f"- `{correction.get('original', '')}` → `{correction.get('corrected', '')}` ({correction.get('reason', '')})")
        
        # 分析结果
        analysis = result.get('analysis', {})
        if analysis:
            st.markdown("#### 🧠 AI分析结果")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**词汇列表：**")
                vocabulary = analysis.get('vocabulary', [])
                for vocab in vocabulary:
                    st.markdown(f"- **{vocab.get('word', '')}**: {vocab.get('meaning', '')} ({vocab.get('level', '')})")
            
            with col2:
                st.markdown("**语法点：**")
                grammar_points = analysis.get('grammar_points', [])
                for point in grammar_points:
                    st.markdown(f"- {point}")
    
    def _render_document_generation(self, results: List[Dict]):
        """渲染文档生成模式"""
        st.markdown("#### 📚 文档生成设置")
        
        col1, col2 = st.columns(2)
        with col1:
            output_dir = st.text_input(
                "输出目录",
                value="./output",
                help="生成文档的保存目录"
            )
        
        with col2:
            doc_format = st.selectbox(
                "文档格式",
                ["markdown", "html", "pdf"],
                help="选择生成文档的格式"
            )
        
        # 生成选项
        st.markdown("**生成内容选择：**")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            gen_lessons = st.checkbox("课文文档", value=True)
        with col2:
            gen_vocab = st.checkbox("词汇表", value=True)
        with col3:
            gen_exercises = st.checkbox("练习题", value=True)
        with col4:
            gen_index = st.checkbox("索引目录", value=True)
        
        if st.button("🎯 生成文档", type="primary"):
            if not self.doc_generator:
                self.doc_generator = DocumentGenerator()
            
            try:
                with st.spinner("正在生成文档..."):
                    # 组织数据
                    lessons = []
                    vocabulary = []
                    
                    for result in results:
                        analysis = result.get('analysis', {})
                        
                        # 课文数据
                        lesson_data = {
                            'unit': analysis.get('unit'),
                            'title': analysis.get('title', result.get('filename', '')),
                            'content_type': analysis.get('content_type'),
                            'content': result.get('corrected_text', ''),
                            'vocabulary': analysis.get('vocabulary', []),
                            'grammar_points': analysis.get('grammar_points', [])
                        }
                        lessons.append(lesson_data)
                        
                        # 词汇数据
                        vocab_list = analysis.get('vocabulary', [])
                        for vocab in vocab_list:
                            vocab['unit'] = analysis.get('unit')
                            vocabulary.append(vocab)
                    
                    # 生成文档
                    generated_files = []
                    
                    if gen_lessons:
                        lesson_file = self.doc_generator.generate_lesson_document(
                            lessons, output_dir, doc_format
                        )
                        if lesson_file:
                            generated_files.append(lesson_file)
                    
                    if gen_vocab:
                        vocab_file = self.doc_generator.generate_vocabulary_document(
                            vocabulary, output_dir, doc_format
                        )
                        if vocab_file:
                            generated_files.append(vocab_file)
                    
                    if gen_exercises:
                        # 生成练习题需要AI
                        exercises_data = []
                        for lesson in lessons:
                            exercises = self.ai_ocr.analyzer.generate_exercises(
                                lesson['content'], lesson['vocabulary']
                            )
                            exercises_data.append({
                                'unit': lesson['unit'],
                                'title': lesson['title'],
                                'exercises': exercises
                            })
                        
                        exercise_file = self.doc_generator.generate_exercise_document(
                            exercises_data, output_dir, doc_format
                        )
                        if exercise_file:
                            generated_files.append(exercise_file)
                    
                    if gen_index and generated_files:
                        index_file = self.doc_generator.generate_index_document(
                            generated_files, output_dir, doc_format
                        )
                        if index_file:
                            generated_files.append(index_file)
                    
                    # 显示结果
                    st.success(f"✅ 成功生成 {len(generated_files)} 个文档！")
                    st.session_state.generated_docs += len(generated_files)
                    
                    # 添加下载功能
                    st.markdown("### 📥 下载生成的文档")
                    
                    for file_path in generated_files:
                        if os.path.exists(file_path):
                            filename = os.path.basename(file_path)
                            
                            # 读取文件内容
                            with open(file_path, 'r', encoding='utf-8') as f:
                                file_content = f.read()
                            
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.markdown(f"📄 **{filename}**")
                                # 显示文件预览
                                with st.expander(f"预览 {filename}"):
                                    if filename.endswith('.md'):
                                        st.markdown(file_content)
                                    else:
                                        st.text(file_content)
                            
                            with col2:
                                # 添加下载按钮
                                st.download_button(
                                    label="💾 下载",
                                    data=file_content,
                                    file_name=filename,
                                    mime="text/markdown" if filename.endswith('.md') else "text/plain",
                                    key=f"download_{filename}"
                                )
                        else:
                            st.warning(f"⚠️ 文件不存在: {file_path}")
                
            except Exception as e:
                st.error(f"文档生成失败: {e}")
    
    def run(self):
        """运行主界面"""
        self.setup_page_config()
        self.render_header()
        
        # 渲染侧边栏
        settings = self.render_sidebar()
        
        # 主要内容区域
        processing_results = self.render_image_upload_section(settings)
        
        # 调试：检查处理结果
        print(f"[主界面] processing_results: {processing_results}")
        
        if processing_results:
            print(f"[主界面] 开始渲染结果区域")
            self.render_results_section(processing_results)
        else:
            print(f"[主界面] 没有处理结果需要显示")
        
        # 页脚
        st.markdown("---")
        st.markdown(
            f'<p style="text-align: center; color: #666; font-size: 0.8rem;">'
            f'🤖 纯AI视觉识别系统 {self.version} | 基于智普AI GLM-4V-Flash + GLM-4-Flash'
            '</p>',
            unsafe_allow_html=True
        )
        print(f"[UI] 渲染页脚，版本: {self.version}")


def create_main_interface() -> EnglishLearningInterface:
    """创建主界面实例"""
    return EnglishLearningInterface()