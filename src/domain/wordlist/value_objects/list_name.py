"""名单名称值对象"""
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ListName:
    """名单名称值对象"""
    
    value: str
    
    def __post_init__(self):
        """初始化后验证"""
        if not self.value:
            raise ValueError("名单名称不能为空")
        
        if len(self.value) > 100:
            raise ValueError("名单名称长度不能超过100字符")
        
        if len(self.value.strip()) != len(self.value):
            raise ValueError("名单名称首尾不能包含空格")
    
    def __str__(self) -> str:
        return self.value
    
    @classmethod
    def create(cls, name: str) -> "ListName":
        """创建名单名称"""
        return cls(value=name.strip())