"""
主界面模块

英语学习助手的Streamlit主界面
"""

import streamlit as st
import os
from pathlib import Path
from typing import List, Dict, Optional
import time

from ..core.vision_processor import create_vision_processor
from ..core.ai_analyzer import create_ai_enhanced_ocr, test_ai_connection
from ..core.document_generator import DocumentGenerator
from ..utils.config import config


class EnglishLearningInterface:
    """英语学习助手主界面"""
    
    def __init__(self):
        self.version = "v1.2.6"
        self.vision_processor = None
        self.ai_analyzer = None
        self.doc_generator = None
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
        """渲染侧边栏"""
        with st.sidebar:
            st.markdown("### ⚙️ 系统配置")
            
            # API密钥配置
            st.markdown("#### 🔑 API设置")
            current_key = config.get_api_key()
            key_status = "✅ 已配置" if current_key else "❌ 未配置"
            st.info(f"当前状态: {key_status}")
            
            if st.button("🔄 重新加载配置"):
                st.experimental_rerun()
            
            st.markdown("---")
            
            # 视觉识别设置
            st.markdown("#### 👁️ 视觉识别设置")
            st.info("使用GLM-4V-Flash进行图像识别")
            print("[UI] 显示视觉识别设置面板")
            
            # AI设置
            st.markdown("#### 🤖 AI设置")
            temperature = st.slider("生成温度", 0.1, 1.0, 0.7, 0.1)
            max_tokens = st.slider("最大生成长度", 500, 4000, 2000, 100)
            
            st.markdown("---")
            st.markdown("### 📊 使用统计")
            
            # 初始化session state
            if 'processed_count' not in st.session_state:
                st.session_state.processed_count = 0
            if 'generated_docs' not in st.session_state:
                st.session_state.generated_docs = 0
                
            st.metric("处理图片数", st.session_state.processed_count)
            st.metric("生成文档数", st.session_state.generated_docs)
            
            return {
                'temperature': temperature,
                'max_tokens': max_tokens
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
                return self._process_uploaded_files(uploaded_files, settings)
                
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
            print(f"[处理] 用户点击开始处理按钮")
            
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
                    print(f"[处理] 开始处理上传文件: {uploaded_file.name}")
                    vision_result = self.vision_processor.process_image(uploaded_file.getvalue())
                    print(f"[处理] 视觉识别完成，成功: {vision_result['success']}")
                    
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
                vision_result = self.vision_processor.process_image(str(image_path))
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
        """渲染处理结果区域"""
        if not processing_results or not processing_results.get('results'):
            return
        
        results = processing_results['results']
        st.markdown("### 📋 处理结果详情")
        
        # 统计信息
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("总文件数", len(results))
        with col2:
            successful = sum(1 for r in results if r.get('success'))
            st.metric("成功处理", successful)
        with col3:
            avg_confidence = sum(r.get('confidence', 0) for r in results) / len(results)
            st.metric("平均置信度", f"{avg_confidence:.2f}")
        with col4:
            total_text = sum(len(r.get('corrected_text', '')) for r in results)
            st.metric("总文本长度", f"{total_text:,}")
        
        # 结果展示选项
        st.markdown("### 📊 结果展示选项")
        
        # 添加模式说明
        with st.expander("📖 模式说明", expanded=False):
            st.markdown("""
            **🔍 概览模式**：快速查看所有处理文件的基本信息
            - 显示识别文本预览（前200字符）
            - 显示AI分析的基本信息（标题、类型、词汇数等）
            - 适合快速浏览多个文件的处理结果
            
            **📋 详细模式**：查看单个文件的完整处理结果
            - 显示完整的识别文本内容
            - 显示详细的AI分析结果（词汇表、语法点、练习题等）
            - 适合深入了解特定文件的内容
            
            **📄 文档生成**：将处理结果生成学习文档
            - 生成结构化的Markdown学习文档
            - 包含课文内容、词汇表、语法点和练习题
            - 支持下载保存到本地
            """)
        
        view_mode = st.radio(
            "选择显示模式：",
            ["概览模式", "详细模式", "文档生成"],
            horizontal=True
        )
        
        if view_mode == "概览模式":
            self._render_overview_mode(results)
        elif view_mode == "详细模式":
            self._render_detailed_mode(results)
        else:
            self._render_document_generation(results)
    
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