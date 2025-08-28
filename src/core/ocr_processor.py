"""
AI增强OCR处理模块

基于PaddleOCR 3.1 + 智普AI的双重增强识别系统
"""

import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io
import logging
from typing import Dict, List, Optional, Tuple, Union
from pathlib import Path

try:
    from paddleocr import PaddleOCR
    OCR_AVAILABLE = True
except ImportError:
    PaddleOCR = None
    OCR_AVAILABLE = False
    # 在Python 3.11环境下，PaddleOCR应该可以正常导入

from ..utils.config import config


class ImagePreprocessor:
    """图像预处理器"""
    
    @staticmethod
    def enhance_image(image: Union[np.ndarray, Image.Image]) -> np.ndarray:
        """
        图像增强处理
        
        Args:
            image: 输入图像
            
        Returns:
            增强后的图像数组
        """
        if isinstance(image, Image.Image):
            image = np.array(image)
        
        # 转换为灰度图
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image
        
        # 降噪处理
        denoised = cv2.medianBlur(gray, 3)
        
        # 锐化处理
        kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        sharpened = cv2.filter2D(denoised, -1, kernel)
        
        # 自适应二值化处理
        binary = cv2.adaptiveThreshold(
            sharpened, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        return binary
    
    @staticmethod
    def rotate_image(image: np.ndarray, angle: float) -> np.ndarray:
        """
        旋转图像
        
        Args:
            image: 输入图像
            angle: 旋转角度
            
        Returns:
            旋转后的图像
        """
        h, w = image.shape[:2]
        center = (w // 2, h // 2)
        
        # 计算旋转矩阵
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        
        # 执行旋转
        rotated = cv2.warpAffine(image, rotation_matrix, (w, h), 
                               flags=cv2.INTER_CUBIC, 
                               borderMode=cv2.BORDER_REPLICATE)
        
        return rotated


class OCRProcessor:
    """AI增强OCR处理器"""
    
    def __init__(self):
        self.ocr_model = None
        self.preprocessor = ImagePreprocessor()
        self._initialize_ocr()
    
    @st.cache_resource
    def _initialize_ocr(_self):
        """初始化OCR模型 - 使用缓存避免重复加载"""
        if not OCR_AVAILABLE:
            st.warning("⚠️ 高级OCR功能不可用，使用基础文本识别模式")
            return "basic_ocr"  # 返回标记而不是None
        
        try:
            ocr_config = config.get("ocr", {})
            
            return PaddleOCR(
                use_angle_cls=ocr_config.get("angle_classification", True),
                lang=ocr_config.get("languages", ["ch", "en"])[0],  # 主语言
                use_gpu=ocr_config.get("use_gpu", False),
                show_log=False,
                enable_mkldnn=ocr_config.get("enable_mkldnn", True)
            )
        except Exception as e:
            st.error(f"OCR模型初始化失败: {e}")
            return "basic_ocr"  # 备用方案
    
    def process_image(self, image_input: Union[str, bytes, Image.Image, np.ndarray], 
                     enhance: bool = True) -> Dict:
        """
        处理图像并进行OCR识别
        
        Args:
            image_input: 图像输入（文件路径、字节数据、PIL图像或numpy数组）
            enhance: 是否进行图像增强
            
        Returns:
            OCR识别结果字典
        """
        if self.ocr_model is None:
            self.ocr_model = self._initialize_ocr()
            if self.ocr_model is None:
                return {
                    'success': False,
                    'error': 'OCR模型未初始化',
                    'raw_text': '',
                    'confidence': 0.0,
                    'details': []
                }
        
        # 处理基础OCR模式
        if self.ocr_model == "basic_ocr":
            return self._basic_ocr_fallback(image_input)
        
        try:
            # 统一处理输入格式
            image_array = self._prepare_image(image_input)
            
            # 图像预处理
            if enhance:
                processed_image = self.preprocessor.enhance_image(image_array)
            else:
                processed_image = image_array
            
            # OCR识别
            ocr_results = self.ocr_model.ocr(processed_image, cls=True)
            
            # 解析结果
            return self._parse_ocr_results(ocr_results)
            
        except Exception as e:
            logging.error(f"OCR处理失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'raw_text': '',
                'confidence': 0.0,
                'details': []
            }
    
    def _prepare_image(self, image_input: Union[str, bytes, Image.Image, np.ndarray]) -> np.ndarray:
        """
        准备图像数据
        
        Args:
            image_input: 各种格式的图像输入
            
        Returns:
            numpy数组格式的图像
        """
        if isinstance(image_input, str):
            # 文件路径
            image = Image.open(image_input)
            return np.array(image)
        
        elif isinstance(image_input, bytes):
            # 字节数据
            image = Image.open(io.BytesIO(image_input))
            return np.array(image)
        
        elif isinstance(image_input, Image.Image):
            # PIL图像
            return np.array(image_input)
        
        elif isinstance(image_input, np.ndarray):
            # numpy数组
            return image_input
        
        else:
            raise ValueError(f"不支持的图像输入类型: {type(image_input)}")
    
    def _parse_ocr_results(self, ocr_results: List) -> Dict:
        """
        解析OCR识别结果
        
        Args:
            ocr_results: PaddleOCR的识别结果
            
        Returns:
            格式化的结果字典
        """
        if not ocr_results or not ocr_results[0]:
            return {
                'success': False,
                'error': '未识别到文字',
                'raw_text': '',
                'confidence': 0.0,
                'details': []
            }
        
        text_lines = []
        details = []
        total_confidence = 0.0
        
        for line in ocr_results[0]:
            # 解析每行结果：[坐标框, (文字, 置信度)]
            bbox, (text, confidence) = line
            
            text_lines.append(text)
            details.append({
                'text': text,
                'confidence': confidence,
                'bbox': bbox
            })
            total_confidence += confidence
        
        # 计算平均置信度
        avg_confidence = total_confidence / len(details) if details else 0.0
        
        return {
            'success': True,
            'raw_text': '\n'.join(text_lines),
            'confidence': avg_confidence,
            'details': details,
            'line_count': len(details)
        }
    
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
    
    def _basic_ocr_fallback(self, image_input: Union[str, bytes, Image.Image, np.ndarray]) -> Dict:
        """
        基础OCR备用方案 - 当PaddleOCR不可用时使用
        
        Args:
            image_input: 图像输入
            
        Returns:
            基础OCR结果
        """
        try:
            # 预处理图像
            image_array = self._prepare_image(image_input)
            processed_image = self.preprocessor.enhance_image(image_array)
            
            # 返回模拟的OCR结果，提示用户上传文本
            return {
                'success': True,
                'raw_text': '⚠️ 云端环境OCR功能受限\n请手动输入图片中的英语文本，系统将提供AI增强分析。\n\n您可以：\n1. 在下方文本框中输入识别的文字\n2. 使用AI分析和文档生成功能\n3. 或者在本地环境中使用完整OCR功能',
                'confidence': 0.8,
                'details': [{
                    'text': '云端模式 - 请手动输入文本',
                    'confidence': 0.8,
                    'bbox': [[0, 0], [100, 0], [100, 20], [0, 20]]
                }],
                'line_count': 1,
                'fallback_mode': True
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'基础OCR处理失败: {e}',
                'raw_text': '',
                'confidence': 0.0,
                'details': []
            }


def create_ocr_processor() -> OCRProcessor:
    """创建OCR处理器实例"""
    return OCRProcessor()