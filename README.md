# 御言(WordGuard)

基于领域驱动设计(Domain-Driven Design)架构重构的文本内容风控系统。

## 🏗️ 架构概述

采用标准的DDD四层架构：

```
src/
├── domain/                    # 领域层（核心业务逻辑）
│   ├── wordlist/             # 名单聚合
│   │   ├── entities/         # 实体
│   │   ├── value_objects/    # 值对象
│   │   ├── repositories/     # 仓储接口
│   │   ├── services/         # 领域服务
│   │   └── events/           # 领域事件
│   └── app/                  # 应用聚合
├── application/              # 应用层（用例协调）
│   ├── commands/             # 命令
│   ├── queries/              # 查询
│   ├── handlers/             # 处理器
│   └── dto/                  # 数据传输对象
├── infrastructure/           # 基础设施层（技术实现）
│   ├── repositories/         # 仓储实现
│   └── database/             # 数据库模型
├── interfaces/               # 接口层（外部交互）
│   ├── controllers/          # 控制器
│   ├── routes/               # 路由
│   └── dependencies.py       # 依赖注入
├── shared/                   # 共享内核
│   ├── enums/                # 业务枚举
│   ├── exceptions/           # 领域异常
│   └── events/               # 事件基础
└── config/                   # 配置
```

## 🚀 快速开始

### 安装依赖
```bash
pip install -r requirements.txt
```

### 启动DDD重构版
```bash
python yuyan.py
```

### 访问文档
- API文档: http://localhost:18000/docs
- 系统信息: http://localhost:18000/

## 📊 API接口

### 名单管理 (/v1/wordlist)
- `POST /v1/wordlist` - 创建名单
- `GET /v1/wordlist` - 获取名单列表
- `GET /v1/wordlist/{id}` - 获取名单详情
- `PUT /v1/wordlist/{id}` - 更新名单
- `DELETE /v1/wordlist/{id}` - 删除名单

### 应用管理 (/v1/app)
- `POST /v1/app` - 创建应用
- `GET /v1/app` - 获取应用列表
- `GET /v1/app/by-id/{id}` - 根据数据库ID获取应用
- `GET /v1/app/by-app-id/{app_id}` - 根据应用ID获取应用

## 🔧 核心特性

### DDD模式实现

1. **实体(Entity)**: WordList、App等核心业务对象
2. **值对象(Value Object)**: ListName、RiskLevel等不可变对象
3. **聚合根(Aggregate Root)**: WordList作为名单聚合的根
4. **仓储(Repository)**: 封装数据访问逻辑
5. **领域服务(Domain Service)**: 跨聚合的业务逻辑
6. **领域事件(Domain Event)**: WordListCreated、WordListUpdated等

### CQRS模式
- **命令**: CreateWordListCommand、UpdateWordListCommand等
- **查询**: GetWordListQuery、GetWordListsQuery等
- **处理器**: 分离命令和查询的处理逻辑

### 软删除机制
- 所有实体支持软删除
- 自动过滤已删除记录
- 完整的审计日志(创建人、更新人、删除人)

### 业务规则封装
- 17+种语言支持
- 13种风险类型分类
- 6种匹配规则
- 完整的枚举体系

## 📋 数据库模型

### WordListModel (wordlist表)
- id: 主键
- list_name: 名单名称
- list_type: 名单类型(白名单/黑名单/忽略名单)
- match_rule: 匹配规则(文本/IP/账号等)
- suggestion: 处置建议(通过/拒绝/审核)
- risk_type: 风险类型
- status: 状态(启用/禁用)
- language: 支持语种

### AppModel (app表)
- id: 主键
- app_name: 应用名称
- app_id: 应用唯一标识
- username: 负责人

## 🎯 设计优势

1. **高内聚低耦合**: 业务逻辑集中，依赖清晰
2. **易于扩展**: 新增聚合、实体、值对象都很简单
3. **业务导向**: 代码结构反映业务概念
4. **测试友好**: 纯函数、依赖注入便于单元测试
5. **维护性强**: 修改影响范围小，bug定位准确
6. **团队协作**: 不同层次可以并行开发

## 🔮 扩展计划

- [ ] 添加名单详情聚合
- [ ] 实现策略引擎模块
- [ ] 集成AI检测服务
- [ ] 添加事件溯源
- [ ] 实现缓存层
- [ ] 微服务拆分
