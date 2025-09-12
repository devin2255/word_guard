# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 在此代码仓库中工作时提供指导。

## 项目概述

御言(YuYan)是一个专为用户生成内容(UGC)设计的文本内容风控系统。它提供智能过滤、名单管理和多语言文本内容风险分类功能。

**技术栈:**
- FastAPI (异步Web框架)
- Tortoise ORM (异步ORM)  
- MySQL (数据库)
- Uvicorn (ASGI服务器)
- Python 3.7+

## 开发命令

### 运行应用
```bash
# 开发模式
python yuyan.py

# 生产模式  
uvicorn yuyan:app --host 0.0.0.0 --port 18000
```

### 数据库
- 应用使用 Tortoise ORM，支持自动生成数据库表结构
- 数据库连接通过 `app/config/` 中的环境变量配置
- 模型支持软删除（通过 `delete_time` 字段实现逻辑删除）

## 系统架构

### 项目结构
```
app/
├── __init__.py          # 应用工厂，支持自动注册
├── api/v1/             # API路由（版本化管理）
├── config/             # 环境配置和常量  
├── libs/enums.py       # 业务枚举定义
├── models/             # 数据模型（继承BaseModel）
└── validators/         # Pydantic请求验证
```

### 核心设计模式

**应用工厂模式**: `app/__init__.py` 中的 `create_app()` 自动完成:
- 从 `app/models/` 目录动态加载模型
- 注册 `app/api/v1/` 中的API路由
- 配置数据库并自动生成表结构
- 设置CORS跨域中间件

**BaseModel模式**: 所有模型继承自 `app/models/base.BaseModel`，提供:
- 软删除功能（`delete_time` 字段）
- 自动时间戳（`create_time`, `update_time`）
- 审计字段（`create_by`, `update_by`, `delete_by`）
- JSON序列化及字段过滤
- 自动排除软删除记录的查询方法

**API版本管理**: 所有路由以 `/v1/` 为前缀，按模块组织:
- `/v1/app` - 应用管理
- `/v1/wordlist` - 名单管理

## 核心业务逻辑

### 枚举类型 (app/libs/enums.py)
定义系统行为的关键业务枚举:

- **ListTypeEnum**: 白名单(0), 忽略名单(1), 黑名单(2)
- **MatchRuleEnum**: 文本加昵称(0), 文本(1), 昵称(2), IP(3), 账号(4), 角色ID(5), 设备指纹(6)
- **RiskTypeEnum**: 内容风险分类（正常、涉政、色情、辱骂、广告等）
- **LanguageEnum**: 17+种支持语言（中文、英文、德文等）
- **SwitchEnum**: 开(1)/关(0) 功能开关

### 模型关系
- **WordList**: 内容过滤规则的主要实体
- **App**: 多租户支持的应用注册表
- **ListDetail**: 名单的详细内容条目

### 查询模式
所有模型自动过滤软删除记录:
```python
# 以下方法自动排除已删除记录
await Model.get(**kwargs)
await Model.query_all(**kwargs)

# 软删除
await instance.delete(delete_by="username")

# 硬删除  
await instance.hard_delete()
```

## 配置管理

环境变量加载来源:
- `app/config/product.env` (生产环境)
- `app/config/test.env` (测试环境)

`app/config/__init__.py` 中的关键设置:
- `DATABASE_URL`: MySQL连接字符串
- `APP_NAME`: 应用显示名称
- `APP_ENV`: 环境标识符

## API文档

运行应用时，FastAPI在 `/docs` 自动生成OpenAPI文档。API遵循RESTful约定，使用合适的HTTP状态码和Pydantic验证。

## 重要说明

- 所有数据库操作使用 Tortoise ORM 异步方式
- 模型使用驼峰命名转下划线的表名转换
- 枚举字段同时支持整数值和字符串描述
- 系统支持17+种语言的国际化内容审核
- CORS配置为允许所有来源（生产环境需调整）