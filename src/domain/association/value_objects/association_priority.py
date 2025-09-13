"""关联优先级值对象"""
from dataclasses import dataclass
from src.shared.exceptions.domain_exceptions import AssociationValidationError


@dataclass(frozen=True)
class AssociationPriority:
    """关联优先级值对象"""
    
    value: int
    
    # 预定义优先级常量
    LOW = -10
    NORMAL = 0
    HIGH = 10
    CRITICAL = 50
    
    def __post_init__(self):
        """初始化后验证"""
        if not isinstance(self.value, int):
            raise AssociationValidationError("priority", self.value, "优先级必须是整数")
        
        if self.value < -100 or self.value > 100:
            raise AssociationValidationError(
                "priority", self.value, "优先级必须在-100到100之间"
            )
    
    @classmethod
    def create_low(cls) -> "AssociationPriority":
        """创建低优先级"""
        return cls(cls.LOW)
    
    @classmethod
    def create_normal(cls) -> "AssociationPriority":
        """创建普通优先级"""
        return cls(cls.NORMAL)
    
    @classmethod
    def create_high(cls) -> "AssociationPriority":
        """创建高优先级"""
        return cls(cls.HIGH)
    
    @classmethod
    def create_critical(cls) -> "AssociationPriority":
        """创建关键优先级"""
        return cls(cls.CRITICAL)
    
    def is_higher_than(self, other: "AssociationPriority") -> bool:
        """是否比另一个优先级高"""
        return self.value > other.value
    
    def is_lower_than(self, other: "AssociationPriority") -> bool:
        """是否比另一个优先级低"""
        return self.value < other.value
    
    def is_equal_to(self, other: "AssociationPriority") -> bool:
        """是否与另一个优先级相等"""
        return self.value == other.value
    
    def get_level_description(self) -> str:
        """获取优先级等级描述"""
        if self.value >= self.CRITICAL:
            return "关键"
        elif self.value >= self.HIGH:
            return "高"
        elif self.value >= self.NORMAL:
            return "普通"
        elif self.value >= self.LOW:
            return "低"
        else:
            return "极低"
    
    def __str__(self) -> str:
        return f"{self.value}({self.get_level_description()})"
    
    def __repr__(self) -> str:
        return f"AssociationPriority(value={self.value})"