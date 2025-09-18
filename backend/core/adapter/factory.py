from typing import Dict, Any
from .base import BaseAdapter
from .dify_adapter import DifyAdapter

class AdapterFactory:
    """适配器工厂类"""
    
    _adapters = {
        "dify": DifyAdapter,
        # 可以在这里添加其他平台适配器
        # "n8n": N8nAdapter,
        # "coze": CozeAdapter,
        # "custom": CustomAdapter
    }
    
    @classmethod
    def register_adapter(cls, name: str, adapter_class):
        """注册新的适配器"""
        cls._adapters[name] = adapter_class
    
    @classmethod
    def create_adapter(cls, adapter_type: str, config: Dict[str, Any]) -> BaseAdapter:
        """创建适配器实例"""
        adapter_class = cls._adapters.get(adapter_type)
        if not adapter_class:
            raise ValueError(f"Unsupported adapter type: {adapter_type}")
        
        return adapter_class(config)
    
    @classmethod
    def get_supported_adapters(cls) -> list:
        """获取支持的适配器列表"""
        return list(cls._adapters.keys())