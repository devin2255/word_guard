"""风险等级值对象"""
from dataclasses import dataclass
from src.shared.enums.list_enums import RiskTypeEnum


@dataclass(frozen=True)
class RiskLevel:
    """风险等级值对象"""
    
    risk_type: RiskTypeEnum
    
    @property
    def is_high_risk(self) -> bool:
        """是否高风险"""
        return self.risk_type in [
            RiskTypeEnum.BLACK_ACCOUNT,
            RiskTypeEnum.BLACK_IP,
            RiskTypeEnum.HIGH_RISK_ACCOUNT,
            RiskTypeEnum.HIGH_RISK_IP,
            RiskTypeEnum.PROHIBIT,
            RiskTypeEnum.POLITICS,
            RiskTypeEnum.PORN,
            RiskTypeEnum.ABUSE
        ]
    
    @property
    def description(self) -> str:
        """风险描述"""
        return RiskTypeEnum.desc(self.risk_type)
    
    @classmethod
    def create_normal(cls) -> "RiskLevel":
        """创建正常风险等级"""
        return cls(risk_type=RiskTypeEnum.NORMAL)
    
    @classmethod
    def create_high_risk(cls, risk_type: RiskTypeEnum) -> "RiskLevel":
        """创建高风险等级"""
        return cls(risk_type=risk_type)