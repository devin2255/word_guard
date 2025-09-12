from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `app` (
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `delete_time` DATETIME(6) COMMENT '删除时间',
    `create_by` VARCHAR(50) COMMENT '创建人',
    `update_by` VARCHAR(50) COMMENT '更新人',
    `delete_by` VARCHAR(50) COMMENT '删除人',
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT COMMENT '自增主键',
    `app_name` VARCHAR(100) NOT NULL COMMENT '应用名称',
    `app_id` VARCHAR(50) NOT NULL UNIQUE COMMENT '应用唯一标识',
    `username` VARCHAR(50) COMMENT '负责人'
) CHARACTER SET utf8mb4 COMMENT='应用数据库模型';
CREATE TABLE IF NOT EXISTS `wordlist` (
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `delete_time` DATETIME(6) COMMENT '删除时间',
    `create_by` VARCHAR(50) COMMENT '创建人',
    `update_by` VARCHAR(50) COMMENT '更新人',
    `delete_by` VARCHAR(50) COMMENT '删除人',
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT COMMENT '自增主键',
    `list_name` VARCHAR(100) NOT NULL COMMENT '名单名称',
    `list_type` SMALLINT NOT NULL COMMENT '名单类型',
    `match_rule` SMALLINT NOT NULL COMMENT '匹配规则',
    `suggestion` SMALLINT NOT NULL COMMENT '处置建议',
    `risk_type` SMALLINT NOT NULL COMMENT '风险类型',
    `status` SMALLINT NOT NULL COMMENT '状态' DEFAULT 1,
    `language` SMALLINT NOT NULL COMMENT '语种' DEFAULT 0
) CHARACTER SET utf8mb4 COMMENT='名单数据库模型';
CREATE TABLE IF NOT EXISTS `aerich` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `version` VARCHAR(255) NOT NULL,
    `app` VARCHAR(100) NOT NULL,
    `content` JSON NOT NULL
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
