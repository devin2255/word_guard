from enum import IntEnum as _IntEnum


class IntEnum(_IntEnum):
    """
    Enum where members are also (and must be) ints
    """

    @classmethod
    def values(cls):
        return [member.value for member in cls]


class ListTypeEnum(IntEnum):
    """名单类型枚举"""
    WHITELIST = 0    # 白名单
    IGNORELIST = 1   # 忽略名单  
    BLACKLIST = 2    # 黑名单

    @classmethod
    def desc(cls, status):
        key_map = {
            cls.WHITELIST: '白名单',
            cls.IGNORELIST: '忽略名单',
            cls.BLACKLIST: '黑名单',
        }
        return key_map[status]


class MatchRuleEnum(IntEnum):
    """
    名单匹配规则: 0-文本加昵称 | 1-文本 | 2-昵称 | 3-IP | 4-account | 5-role_id | 6-fingerprint
    """
    TEXT_AND_NAME = 0
    TEXT = 1
    NICKNAME = 2
    IP = 3
    ACCOUNT = 4
    ROLE_ID = 5
    FINGERPRINT = 6

    @classmethod
    def desc(cls, status):
        key_map = {
            cls.TEXT_AND_NAME.value: ['text', 'nickname'],
            cls.TEXT.value: ['text'],
            cls.NICKNAME.value: ['nickname'],
            cls.IP.value: ['ip'],
            cls.ACCOUNT.value: ['account'],
            cls.ROLE_ID.value: ['role_id'],
            cls.FINGERPRINT.value: ['fingerprint'],
        }
        return key_map[status]


class ListSuggestEnum(IntEnum):
    """名单处置建议"""
    REJECT = 0   # 拒绝
    PASS = 1     # 通过
    REVIEW = 2   # 审核

    @classmethod
    def desc(cls, status):
        key_map = {
            cls.REJECT: '拒绝',
            cls.PASS: '通过',
            cls.REVIEW: '审核'
        }
        return key_map[status]


class RiskTypeEnum(IntEnum):
    """
    名单风险类型: 0-正常 | 100-涉政 | 200-色情 | 300-辱骂 | 400-广告 | 500-无意义 | 600-违禁 | 700-其他 | 800-黑账号 | 900-黑IP | 810-高危账号 | 910-高危IP | 1000-自定义
    """
    NORMAL = 0
    POLITICS = 100
    PORN = 200
    ABUSE = 300
    AD = 400
    MEANINGLESS = 500
    PROHIBIT = 600
    OTHER = 700
    BLACK_ACCOUNT = 800
    BLACK_IP = 900
    HIGH_RISK_ACCOUNT = 810
    HIGH_RISK_IP = 910
    CUSTOM = 1000

    @classmethod
    def desc(cls, status):
        key_map = {
            cls.NORMAL.value: "正常",
            cls.POLITICS.value: "涉政",
            cls.PORN.value: "色情",
            cls.ABUSE.value: "辱骂",
            cls.AD.value: "广告",
            cls.MEANINGLESS.value: "无意义",
            cls.PROHIBIT.value: "违禁",
            cls.OTHER.value: "其他",
            cls.BLACK_ACCOUNT.value: "黑账号",
            cls.BLACK_IP.value: "黑IP",
            cls.HIGH_RISK_ACCOUNT.value: "高危账号",
            cls.HIGH_RISK_IP.value: "高危IP",
            cls.CUSTOM.value: "自定义",
        }
        return key_map[status]


class SwitchEnum(IntEnum):
    """开关状态"""
    OFF = 0  # 关闭
    ON = 1   # 打开

    @classmethod
    def desc(cls, status):
        key_map = {
            cls.OFF: '关闭',
            cls.ON: '打开'
        }
        return key_map[status]


class LanguageEnum(IntEnum):
    """语种"""
    ALL = 0      # 全部语种
    ZH = 1       # 简体中文
    ZH_TW = 2    # 繁体中文
    EN = 3       # 英语
    DE = 4       # 德语
    ES = 5       # 西班牙语
    JA = 6       # 日语
    IT = 7       # 意大利语
    FIL = 8      # 菲律宾语
    RU = 9       # 俄语
    PT = 10      # 葡萄牙语
    FR = 11      # 法语
    KO = 12      # 韩语
    PL = 13      # 波兰语
    ID = 14      # 印尼语
    TH = 15      # 泰语
    TR = 16      # 土耳其语
    OTHER = 17   # 其他

    @classmethod
    def desc(cls, status):
        key_map = {
            cls.ALL: '全部语种',
            cls.ZH: '简体中文',
            cls.ZH_TW: '繁体中文',
            cls.EN: '英语',
            cls.DE: '德语',
            cls.ES: '西班牙语',
            cls.JA: '日语',
            cls.IT: '意大利语',
            cls.FIL: '菲律宾语',
            cls.RU: '俄语',
            cls.PT: '葡萄牙语',
            cls.FR: '法语',
            cls.KO: '韩语',
            cls.PL: '波兰语',
            cls.ID: '印尼语',
            cls.TH: '泰语',
            cls.TR: '土耳其语',
            cls.OTHER: '其他'
        }
        return key_map[status]