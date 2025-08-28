"""
配置管理模块
"""

import yaml
import streamlit as st
import os
from pathlib import Path
from typing import Any, Dict, Optional


class Config:
    """配置管理类"""
    
    def __init__(self, config_path: str = "config/app_config.yaml"):
        self.config_path = Path(config_path)
        self._config = self._load_config()
        self._load_secrets()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            else:
                return self._get_default_config()
        except yaml.YAMLError as e:
            st.error(f"配置文件解析错误: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "app": {
                "name": "English Learning Assistant",
                "version": "1.1.0",
                "debug": False
            },
            "ocr": {
                "engine": "paddleocr",
                "version": "3.1.0",
                "languages": ["ch", "en"],
                "use_gpu": False,
                "confidence_threshold": 0.8,
                "angle_classification": True,
                "enable_mkldnn": True,
                "ai_enhanced": True
            },
            "ai": {
                "provider": "zhipu",
                "model": "glm-4-flash",
                "base_url": "https://open.bigmodel.cn/api/paas/v4/chat/completions",
                "temperature": 0.7,
                "top_p": 0.8,
                "max_tokens": 2000,
                "timeout": 30,
                "retry_times": 3
            },
            "processing": {
                "batch_size": 5,
                "max_workers": 3,
                "max_file_size": 10,
                "supported_formats": ["jpg", "jpeg", "png", "bmp"]
            },
            "paths": {
                "output_base": "./output",
                "cache_dir": "./cache",
                "temp_dir": "./temp",
                "log_dir": "./logs"
            }
        }
    
    def _load_secrets(self):
        """加载密钥配置 (项目特定命名)"""
        api_key = None
        
        try:
            # 优先使用Streamlit secrets (项目特定名称)
            api_key = st.secrets.get("api", {}).get("ENGLISH_LEARNING_ZHIPU_API_KEY")
        except (KeyError, FileNotFoundError, AttributeError):
            pass
            
        if not api_key:
            # 回退到环境变量 (项目特定名称)
            api_key = os.getenv("ENGLISH_LEARNING_ZHIPU_API_KEY")
            
        if not api_key:
            # 兼容旧版本环境变量名
            api_key = os.getenv("ZHIPU_API_KEY")
        
        # Debug: 输出调试信息
        print(f"DEBUG - API Key found: {bool(api_key)}")
        if api_key:
            print(f"DEBUG - API Key length: {len(api_key)}")
            print(f"DEBUG - API Key prefix: {api_key[:8]}...")
        
        if api_key:
            self._config.setdefault("ai", {})["api_key"] = api_key
        else:
            st.warning("⚠️ 未找到AI API密钥 (ENGLISH_LEARNING_ZHIPU_API_KEY)，部分功能可能无法使用")
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key_path: 配置路径，如 'ai.model'
            default: 默认值
            
        Returns:
            配置值
        """
        keys = key_path.split('.')
        value = self._config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
                
        return value
    
    def has_api_key(self) -> bool:
        """检查是否配置了API密钥"""
        return bool(self.get("ai.api_key"))
    
    def get_api_key(self) -> Optional[str]:
        """获取API密钥"""
        return self.get("ai.api_key")


# 全局配置实例
config = Config()