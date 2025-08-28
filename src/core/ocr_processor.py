"""
AI视觉识别OCR处理模块

基于智普AI GLM-4V-Flash的视觉识别系统
"""

import streamlit as st
import numpy as np
from PIL import Image
import io
import logging
from typing import Dict, List, Optional, Tuple, Union
from pathlib import Path

from .ai_analyzer import ZhipuAIClient
from ..utils.config import config


class VisionOCRProcessor:
    """基于GLM-4V-Flash的视觉识别OCR处理器"""
    
    def __init__(self):
        self.ai_client = ZhipuAIClient()
    
    def _prepare_image(self, image_input: Union[str, bytes, Image.Image, np.ndarray]) -> str:
        """
        准备图像数据，保存为临时文件
        
        Args:
            image_input: 各种格式的图像输入
            
        Returns:
            临时图像文件路径
        """
        import tempfile
        import os
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
            temp_path = temp_file.name
        
        try:
            if isinstance(image_input, str):
                # 已经是文件路径
                return image_input
            
            elif isinstance(image_input, bytes):
                # 字节数据
                image = Image.open(io.BytesIO(image_input))
                image.save(temp_path, 'JPEG')
                return temp_path
            
            elif isinstance(image_input, Image.Image):
                # PIL图像
                image_input.save(temp_path, 'JPEG')
                return temp_path
            
            elif isinstance(image_input, np.ndarray):
                # numpy数组
                image = Image.fromarray(image_input)
                image.save(temp_path, 'JPEG')
                return temp_path
            
            else:
                raise ValueError(f"不支持的图像输入类型: {type(image_input)}")
                
        except Exception as e:
            # 清理临时文件
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise e
    
    def process_image(self, image_input: Union[str, bytes, Image.Image, np.ndarray], 
                     enhance: bool = True) -> Dict:
        """
        使用GLM-4V-Flash处理图像并进行文字识别
        
        Args:
            image_input: 图像输入（文件路径、字节数据、PIL图像或numpy数组）
            enhance: 是否进行图像增强（对GLM-4V-Flash无效，保留兼容性）
            
        Returns:
            OCR识别结果字典
        """
        temp_file = None
        
        try:
            # 准备图像文件
            image_path = self._prepare_image(image_input)
            
            # 如果是临时文件，记录以便清理
            if not isinstance(image_input, str):
                temp_file = image_path
            
            # 使用GLM-4V-Flash进行视觉识别
            vision_result = self.ai_client.recognize_image_text(image_path, "英语教材内容")
            
            # 转换为统一的OCR结果格式
            if vision_result['success']:
                return {
                    'success': True,
                    'raw_text': vision_result['raw_text'],
                    'confidence': vision_result['confidence'],
                    'details': vision_result.get('details', []),
                    'method': 'GLM-4V-Flash',
                    'vision_model': vision_result.get('vision_model', 'glm-4v-flash')
                }
            else:
                return {
                    'success': False,
                    'error': vision_result.get('error', '视觉识别失败'),
                    'raw_text': '',
                    'confidence': 0.0,
                    'details': []
                }
                
        except Exception as e:
            logging.error(f"GLM-4V-Flash处理失败: {e}")
            return {
                'success': False,
                'error': f'图像处理失败: {e}',
                'raw_text': '',
                'confidence': 0.0,
                'details': []
            }
        
        finally:
            # 清理临时文件
            if temp_file and temp_file != image_input:
                try:
                    import os
                    if os.path.exists(temp_file):
                        os.unlink(temp_file)
                except Exception:
                    pass  # 忽略清理错误
    
    def batch_process(self, image_list: List[Union[str, bytes, Image.Image]], 
                     progress_callback=None) -> List[Dict]:
        """
        批量处理图像
        
        Args:
            image_list: 图像列表
            progress_callback: 进度回调函数
            
        Returns:
            批量处理结果列表
        """
        results = []
        total = len(image_list)
        
        for i, image_input in enumerate(image_list):
            # 处理单个图像
            result = self.process_image(image_input)
            result['index'] = i
            results.append(result)
            
            # 更新进度
            if progress_callback:
                progress_callback(i + 1, total)
        
        return results


# 保持向后兼容的OCRProcessor类
class OCRProcessor(VisionOCRProcessor):
    """OCR处理器 - 兼容旧版本接口"""
    pass


@st.cache_resource
def create_ocr_processor() -> VisionOCRProcessor:
    """创建基于GLM-4V-Flash的OCR处理器实例"""
    return VisionOCRProcessor()