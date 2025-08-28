"""
AI视觉识别处理模块

基于智普AI GLM-4V-Flash的纯视觉识别系统
版本: v1.2.0 - 完全移除OCR依赖
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


class VisionProcessor:
    """基于GLM-4V-Flash的纯视觉识别处理器"""
    
    def __init__(self):
        print(f"[VisionProcessor] 初始化GLM-4V-Flash视觉处理器")
        self.ai_client = ZhipuAIClient()
        self.version = "v1.2.2"
        print(f"[VisionProcessor] 版本: {self.version} - 纯AI视觉识别")
    
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
        
        print(f"[VisionProcessor] 准备图像数据，输入类型: {type(image_input)}")
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
            temp_path = temp_file.name
        
        try:
            if isinstance(image_input, str):
                # 已经是文件路径
                print(f"[VisionProcessor] 使用现有文件路径: {image_input}")
                return image_input
            
            elif isinstance(image_input, bytes):
                # 字节数据
                print(f"[VisionProcessor] 处理字节数据，大小: {len(image_input)} bytes")
                image = Image.open(io.BytesIO(image_input))
                image.save(temp_path, 'JPEG')
                print(f"[VisionProcessor] 保存临时文件: {temp_path}")
                return temp_path
            
            elif isinstance(image_input, Image.Image):
                # PIL图像
                print(f"[VisionProcessor] 处理PIL图像，尺寸: {image_input.size}")
                image_input.save(temp_path, 'JPEG')
                print(f"[VisionProcessor] 保存临时文件: {temp_path}")
                return temp_path
            
            elif isinstance(image_input, np.ndarray):
                # numpy数组
                print(f"[VisionProcessor] 处理numpy数组，形状: {image_input.shape}")
                image = Image.fromarray(image_input)
                image.save(temp_path, 'JPEG')
                print(f"[VisionProcessor] 保存临时文件: {temp_path}")
                return temp_path
            
            else:
                error_msg = f"不支持的图像输入类型: {type(image_input)}"
                print(f"[VisionProcessor] 错误: {error_msg}")
                raise ValueError(error_msg)
                
        except Exception as e:
            # 清理临时文件
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                print(f"[VisionProcessor] 清理临时文件: {temp_path}")
            print(f"[VisionProcessor] 图像准备失败: {e}")
            raise e
    
    def process_image(self, image_input: Union[str, bytes, Image.Image, np.ndarray]) -> Dict:
        """
        使用GLM-4V-Flash处理图像并进行文字识别
        
        Args:
            image_input: 图像输入（文件路径、字节数据、PIL图像或numpy数组）
            
        Returns:
            视觉识别结果字典
        """
        temp_file = None
        
        print(f"[VisionProcessor] 开始处理图像")
        
        try:
            # 准备图像文件
            image_path = self._prepare_image(image_input)
            
            # 如果是临时文件，记录以便清理
            if not isinstance(image_input, str):
                temp_file = image_path
            
            print(f"[VisionProcessor] 调用GLM-4V-Flash进行视觉识别")
            
            # 使用GLM-4V-Flash进行视觉识别
            vision_result = self.ai_client.recognize_image_text(image_path, "英语教材内容")
            
            print(f"[VisionProcessor] GLM-4V-Flash处理完成，成功: {vision_result['success']}")
            
            # 转换为统一的结果格式
            if vision_result['success']:
                result = {
                    'success': True,
                    'raw_text': vision_result['raw_text'],
                    'confidence': vision_result['confidence'],
                    'details': vision_result.get('details', []),
                    'method': 'GLM-4V-Flash',
                    'version': self.version,
                    'vision_model': vision_result.get('vision_model', 'glm-4v-flash')
                }
                print(f"[VisionProcessor] 识别成功，文本长度: {len(result['raw_text'])}, 置信度: {result['confidence']}")
                return result
            else:
                result = {
                    'success': False,
                    'error': vision_result.get('error', '视觉识别失败'),
                    'raw_text': '',
                    'confidence': 0.0,
                    'details': [],
                    'version': self.version
                }
                print(f"[VisionProcessor] 识别失败: {result['error']}")
                return result
                
        except Exception as e:
            error_msg = f'图像处理失败: {e}'
            print(f"[VisionProcessor] 异常: {error_msg}")
            logging.error(f"GLM-4V-Flash处理失败: {e}")
            return {
                'success': False,
                'error': error_msg,
                'raw_text': '',
                'confidence': 0.0,
                'details': [],
                'version': self.version
            }
        
        finally:
            # 清理临时文件
            if temp_file and temp_file != image_input:
                try:
                    import os
                    if os.path.exists(temp_file):
                        os.unlink(temp_file)
                        print(f"[VisionProcessor] 清理临时文件: {temp_file}")
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
        print(f"[VisionProcessor] 开始批量处理，图像数量: {len(image_list)}")
        results = []
        total = len(image_list)
        
        for i, image_input in enumerate(image_list):
            print(f"[VisionProcessor] 处理第 {i+1}/{total} 个图像")
            
            # 处理单个图像
            result = self.process_image(image_input)
            result['index'] = i
            results.append(result)
            
            # 更新进度
            if progress_callback:
                progress_callback(i + 1, total)
        
        print(f"[VisionProcessor] 批量处理完成，成功: {sum(1 for r in results if r['success'])}/{total}")
        return results


@st.cache_resource
def create_vision_processor() -> VisionProcessor:
    """创建基于GLM-4V-Flash的视觉处理器实例"""
    print(f"[Factory] 创建VisionProcessor实例")
    return VisionProcessor()


# 保持向后兼容的函数名
@st.cache_resource
def create_ocr_processor() -> VisionProcessor:
    """创建视觉处理器实例（兼容旧版本接口）"""
    print(f"[Factory] 通过兼容接口创建VisionProcessor实例")
    return create_vision_processor()