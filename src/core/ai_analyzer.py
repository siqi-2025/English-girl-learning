"""
AI分析和增强模块

基于智普AI GLM-4V-Flash的图像识别和内容分析
"""

import streamlit as st
import requests
import json
import time
import logging
import base64
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from ..utils.config import config

# 智普AI SDK
try:
    from zhipuai import ZhipuAI
    ZHIPUAI_SDK_AVAILABLE = True
except ImportError:
    ZhipuAI = None
    ZHIPUAI_SDK_AVAILABLE = False


@dataclass
class AnalysisResult:
    """分析结果数据类"""
    unit: Optional[int] = None
    title: Optional[str] = None
    content_type: Optional[str] = None
    main_content: str = ""
    vocabulary: List[Dict] = None
    grammar_points: List[str] = None
    corrected_text: str = ""
    confidence: float = 0.0
    corrections: List[Dict] = None
    
    def __post_init__(self):
        if self.vocabulary is None:
            self.vocabulary = []
        if self.grammar_points is None:
            self.grammar_points = []
        if self.corrections is None:
            self.corrections = []


class ZhipuAIClient:
    """智普AI客户端 - 支持GLM-4V-Flash视觉识别"""
    
    def __init__(self):
        self.api_key = config.get_api_key()
        self.base_url = config.get("ai.base_url")
        self.model = config.get("ai.model", "glm-4-flash")
        self.vision_model = "glm-4v-flash"  # 视觉识别模型
        
        # 初始化智普AI客户端
        if ZHIPUAI_SDK_AVAILABLE and self.api_key:
            self.client = ZhipuAI(api_key=self.api_key)
        else:
            self.client = None
            
        # Debug: 输出API密钥信息
        print(f"DEBUG - ZhipuAIClient init - API Key: {bool(self.api_key)}")
        print(f"DEBUG - ZhipuAI SDK Available: {ZHIPUAI_SDK_AVAILABLE}")
        print(f"DEBUG - Vision Model: {self.vision_model}")
        
        # 保留原有的headers用于备用API调用
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
    
    def _upload_image_to_url(self, image_path: str) -> Optional[str]:
        """将图片上传到临时URL服务"""
        try:
            print(f"[GLM-4V-Flash] 准备上传图片到临时URL服务: {image_path}")
            
            # 使用免费图床服务 - imgbb
            api_key = "a2c2e4b2b8e9d5f9d5a2e4b2b8e9d5f9"  # 临时API key，实际使用时请申请自己的
            url = "https://api.imgbb.com/1/upload"
            
            with open(image_path, 'rb') as image_file:
                files = {
                    'image': image_file
                }
                data = {
                    'key': api_key,
                    'expiration': 600  # 10分钟过期
                }
                
                print(f"[GLM-4V-Flash] 正在上传图片...")
                response = requests.post(url, files=files, data=data, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        image_url = result['data']['url']
                        print(f"[GLM-4V-Flash] 图片上传成功: {image_url}")
                        return image_url
                    else:
                        print(f"[GLM-4V-Flash] 图床服务返回失败: {result}")
                else:
                    print(f"[GLM-4V-Flash] 图片上传失败: {response.status_code} - {response.text}")
                    
        except Exception as e:
            print(f"[GLM-4V-Flash] 图片上传异常: {e}")
            logging.error(f"图片上传失败: {e}")
        
        # 如果上传失败，尝试使用本地文件路径（仅适用于本地图片）
        print(f"[GLM-4V-Flash] 图片上传失败，尝试直接使用本地路径")
        return None
    
    def recognize_image_text(self, image_path: str, context: str = "英语教材内容") -> Dict:
        """
        使用GLM-4V-Flash识别图片中的文字
        
        Args:
            image_path: 图片文件路径
            context: 上下文信息，帮助模型理解图片内容
            
        Returns:
            识别结果字典
        """
        print(f"[GLM-4V-Flash] 开始识别图像: {image_path}")
        
        if not self.client:
            error_msg = '智普AI SDK不可用'
            print(f"[GLM-4V-Flash] 错误: {error_msg}")
            return {
                'success': False,
                'error': error_msg,
                'raw_text': '',
                'confidence': 0.0
            }
        
        try:
            # 准备视觉识别的提示词
            vision_prompt = f"""请仔细识别这张{context}图片中的所有英语文字内容，要求：

1. **完整识别**：识别图片中所有可见的英语文字，包括标题、正文、注释等
2. **保持格式**：尽量保持原始的段落结构和换行
3. **准确性**：确保拼写和语法的准确性
4. **完整性**：不要遗漏任何文字内容

请直接返回识别出的英语文字内容，不需要额外的解释。"""

            # 上传图像到URL服务
            image_url = self._upload_image_to_url(image_path)
            if not image_url:
                error_msg = f'图像上传失败: {image_path}'
                print(f"[GLM-4V-Flash] 错误: {error_msg}")
                return {
                    'success': False,
                    'error': error_msg,
                    'raw_text': '',
                    'confidence': 0.0
                }

            print(f"[GLM-4V-Flash] 图像URL准备完成: {image_url}")

            # 构建消息 - 使用网络URL格式
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": vision_prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url
                            }
                        }
                    ]
                }
            ]
            
            print(f"[GLM-4V-Flash] 调用API，模型: {self.vision_model}")
            
            # 调用GLM-4V-Flash API - 按照参考代码格式
            response = self.client.chat.completions.create(
                model=self.vision_model,  # "glm-4v-flash"
                messages=messages,
                top_p=0.7,
                temperature=0.95,  # 按照参考代码使用0.95
                max_tokens=1024,   # 按照参考代码使用1024
                stream=False       # 确保非流式
            )
            
            print(f"[GLM-4V-Flash] API调用完成")
            
            # 解析响应
            if response and response.choices:
                recognized_text = response.choices[0].message.content.strip()
                print(f"[GLM-4V-Flash] 识别成功，文本长度: {len(recognized_text)}")
                
                return {
                    'success': True,
                    'raw_text': recognized_text,
                    'confidence': 0.95,  # GLM-4V-Flash高置信度
                    'details': [{
                        'text': recognized_text,
                        'confidence': 0.95,
                        'method': 'GLM-4V-Flash'
                    }],
                    'vision_model': self.vision_model
                }
            else:
                error_msg = '视觉识别返回为空'
                print(f"[GLM-4V-Flash] 错误: {error_msg}")
                return {
                    'success': False,
                    'error': error_msg,
                    'raw_text': '',
                    'confidence': 0.0
                }
                
        except Exception as e:
            error_msg = f'视觉识别失败: {e}'
            print(f"[GLM-4V-Flash] 异常: {error_msg}")
            logging.error(f"GLM-4V-Flash视觉识别失败: {e}")
            return {
                'success': False,
                'error': error_msg,
                'raw_text': '',
                'confidence': 0.0
            }
    
    def _make_request(self, messages: List[Dict], **kwargs) -> Optional[Dict]:
        """
        发送API请求
        
        Args:
            messages: 对话消息列表
            **kwargs: 其他参数
            
        Returns:
            API响应结果
        """
        if not self.api_key:
            print("DEBUG - _make_request: No API key")
            st.error("未配置AI API密钥")
            return None
        
        # 智普AI官方API格式
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", config.get("ai.temperature", 0.7)),
            "top_p": kwargs.get("top_p", config.get("ai.top_p", 0.8)),
            "max_tokens": kwargs.get("max_tokens", config.get("ai.max_tokens", 2000)),
            "stream": False  # 关闭流式输出
        }
        
        retry_times = config.get("ai.retry_times", 3)
        timeout = config.get("ai.timeout", 30)
        
        for attempt in range(retry_times):
            try:
                response = requests.post(
                    self.base_url,
                    headers=self.headers,
                    json=payload,
                    timeout=timeout
                )
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:  # 限流
                    wait_time = 2 ** attempt  # 指数退避
                    time.sleep(wait_time)
                    continue
                else:
                    logging.error(f"API请求失败: {response.status_code} - {response.text}")
                    return None
                    
            except requests.exceptions.RequestException as e:
                logging.error(f"API请求异常 (尝试 {attempt + 1}/{retry_times}): {e}")
                if attempt < retry_times - 1:
                    time.sleep(2 ** attempt)
                    continue
                return None
        
        return None
    
    def test_connection(self) -> bool:
        """
        测试API连接
        
        Returns:
            连接是否成功
        """
        print("DEBUG - Testing AI connection...")
        if not self.api_key:
            print("DEBUG - No API key available")
            return False
            
        messages = [{"role": "user", "content": "测试连接"}]
        result = self._make_request(messages, max_tokens=10)
        success = result is not None
        print(f"DEBUG - Connection test result: {success}")
        if not success and result is None:
            print("DEBUG - API request returned None")
        return success


class AIAnalyzer:
    """AI分析器"""
    
    def __init__(self):
        self.client = ZhipuAIClient()
    
    def enhance_ocr_result(self, raw_text: str, context: str = "英语教材内容识别") -> Dict:
        """
        AI增强OCR结果
        
        Args:
            raw_text: OCR原始识别文本
            context: 上下文信息
            
        Returns:
            增强后的结果
        """
        prompt = f"""请对以下OCR识别的英语教材文本进行校正和优化：

上下文：{context}
OCR原文：
{raw_text}

请执行以下任务：
1. 纠正OCR识别错误（如字母识别错误、单词拼写错误等）
2. 优化标点符号和格式
3. 保持原文的结构和含义
4. 标出进行了哪些修正

请用JSON格式返回结果：
{{
    "corrected_text": "校正后的文本",
    "confidence": 0.95,
    "corrections": [
        {{"original": "错误文本", "corrected": "正确文本", "reason": "修正原因"}}
    ]
}}"""

        messages = [{"role": "user", "content": prompt}]
        result = self.client._make_request(messages)
        
        if result and "choices" in result:
            try:
                content = result["choices"][0]["message"]["content"]
                # 尝试解析JSON
                if content.startswith("```json"):
                    content = content.replace("```json", "").replace("```", "").strip()
                
                parsed_result = json.loads(content)
                return parsed_result
            except (json.JSONDecodeError, KeyError) as e:
                logging.error(f"解析AI响应失败: {e}")
        
        # 返回默认结果
        return {
            "corrected_text": raw_text,
            "confidence": 0.5,
            "corrections": []
        }
    
    def analyze_content(self, text: str) -> AnalysisResult:
        """
        分析课文内容
        
        Args:
            text: 课文文本
            
        Returns:
            分析结果
        """
        prompt = f"""请分析以下英语教材内容，并按JSON格式返回分析结果：

文本内容：
{text}

请提取以下信息：
1. 单元编号（如果有）
2. 标题或主题
3. 内容类型（dialog对话、reading阅读、grammar语法等）
4. 主要内容概述
5. 重要词汇及其中文含义
6. 语法点

返回JSON格式：
{{
    "unit": 1,
    "title": "单元标题",
    "content_type": "dialog",
    "main_content": "主要内容概述",
    "vocabulary": [
        {{
            "word": "单词",
            "meaning": "中文含义",
            "level": "primary/middle",
            "example": "例句"
        }}
    ],
    "grammar_points": ["语法点1", "语法点2"]
}}"""

        messages = [{"role": "user", "content": prompt}]
        result = self.client._make_request(messages)
        
        if result and "choices" in result:
            try:
                content = result["choices"][0]["message"]["content"]
                if content.startswith("```json"):
                    content = content.replace("```json", "").replace("```", "").strip()
                
                parsed_result = json.loads(content)
                
                # 转换为AnalysisResult对象
                return AnalysisResult(
                    unit=parsed_result.get("unit"),
                    title=parsed_result.get("title"),
                    content_type=parsed_result.get("content_type"),
                    main_content=parsed_result.get("main_content", ""),
                    vocabulary=parsed_result.get("vocabulary", []),
                    grammar_points=parsed_result.get("grammar_points", [])
                )
            except (json.JSONDecodeError, KeyError) as e:
                logging.error(f"解析内容分析结果失败: {e}")
        
        # 返回默认结果
        return AnalysisResult(main_content=text)
    
    def classify_vocabulary(self, words: List[str]) -> Dict[str, List[Dict]]:
        """
        词汇难度分级
        
        Args:
            words: 单词列表
            
        Returns:
            分级结果 {"primary": [...], "middle": [...]}
        """
        words_text = ", ".join(words)
        
        prompt = f"""请将以下英语单词按照难度等级分类：
- primary: 小学水平词汇
- middle: 初中水平词汇

单词列表：{words_text}

对每个单词提供中文释义和例句。

返回JSON格式：
{{
    "primary": [
        {{"word": "单词", "meaning": "中文", "example": "例句"}}
    ],
    "middle": [
        {{"word": "单词", "meaning": "中文", "example": "例句"}}
    ]
}}"""

        messages = [{"role": "user", "content": prompt}]
        result = self.client._make_request(messages)
        
        if result and "choices" in result:
            try:
                content = result["choices"][0]["message"]["content"]
                if content.startswith("```json"):
                    content = content.replace("```json", "").replace("```", "").strip()
                
                return json.loads(content)
            except (json.JSONDecodeError, KeyError) as e:
                logging.error(f"解析词汇分级结果失败: {e}")
        
        # 返回默认结果
        return {"primary": [], "middle": []}
    
    def generate_exercises(self, content: str, vocabulary: List[Dict]) -> Dict:
        """
        生成习题
        
        Args:
            content: 课文内容
            vocabulary: 词汇列表
            
        Returns:
            习题字典
        """
        vocab_text = ", ".join([f"{v.get('word', '')}" for v in vocabulary])
        
        prompt = f"""根据以下课文内容和词汇列表，生成英语练习题：

课文内容：
{content}

词汇列表：{vocab_text}

请生成以下类型的习题：
1. 中英互译题（5题）
2. 字母填空题（5题，用_表示空缺字母）
3. 短语填空题（3题，用___表示空缺短语）
4. 课文默写题（按段落分割，提供中文翻译）

返回JSON格式：
{{
    "translation": [
        {{"question": "题目", "answer": "答案", "type": "zh_to_en"}}
    ],
    "letter_filling": [
        {{"question": "题目（如：h_llo）", "answer": "hello"}}
    ],
    "phrase_filling": [
        {{"question": "句子___空缺", "answer": "正确短语"}}
    ],
    "dictation": [
        {{"chinese": "中文段落", "english": "对应英文段落"}}
    ]
}}"""

        messages = [{"role": "user", "content": prompt}]
        result = self.client._make_request(messages)
        
        if result and "choices" in result:
            try:
                content = result["choices"][0]["message"]["content"]
                if content.startswith("```json"):
                    content = content.replace("```json", "").replace("```", "").strip()
                
                return json.loads(content)
            except (json.JSONDecodeError, KeyError) as e:
                logging.error(f"解析习题生成结果失败: {e}")
        
        # 返回默认结果
        return {
            "translation": [],
            "letter_filling": [],
            "phrase_filling": [],
            "dictation": []
        }


class AIEnhancedOCR:
    """AI增强OCR系统 - 整合OCR和AI分析"""
    
    def __init__(self):
        self.analyzer = AIAnalyzer()
    
    def process_image_with_ai(self, ocr_result: Dict, context: str = "英语教材") -> Dict:
        """
        对OCR结果进行AI增强处理
        
        Args:
            ocr_result: OCR识别结果
            context: 上下文信息
            
        Returns:
            AI增强后的完整结果
        """
        if not ocr_result.get('success'):
            return ocr_result
        
        raw_text = ocr_result['raw_text']
        
        # AI文本校正
        enhanced_result = self.analyzer.enhance_ocr_result(raw_text, context)
        
        # 内容分析
        analysis_result = self.analyzer.analyze_content(enhanced_result['corrected_text'])
        
        # 整合结果
        return {
            'success': True,
            'raw_ocr': raw_text,
            'corrected_text': enhanced_result['corrected_text'],
            'confidence': max(ocr_result.get('confidence', 0), enhanced_result.get('confidence', 0)),
            'corrections': enhanced_result.get('corrections', []),
            'analysis': {
                'unit': analysis_result.unit,
                'title': analysis_result.title,
                'content_type': analysis_result.content_type,
                'main_content': analysis_result.main_content,
                'vocabulary': analysis_result.vocabulary,
                'grammar_points': analysis_result.grammar_points
            }
        }


def create_ai_analyzer() -> AIAnalyzer:
    """创建AI分析器实例"""
    return AIAnalyzer()


def create_ai_enhanced_ocr() -> AIEnhancedOCR:
    """创建AI增强OCR系统实例"""
    return AIEnhancedOCR()


def test_ai_connection() -> bool:
    """测试AI连接"""
    client = ZhipuAIClient()
    return client.test_connection()