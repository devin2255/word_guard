# 御言(WordGuard)

基于领域驱动设计(Domain-Driven Design)架构重构的文本内容风控系统。

## 🏗️ 架构概述

采用标准的DDD四层架构，遵循洋葱架构原则，确保依赖关系从外向内：

```
src/
├── domain/                    # 领域层（核心业务逻辑）
│   ├── wordlist/             # 名单聚合根
│   │   ├── entities/         # 领域实体：WordList
│   │   ├── value_objects/    # 值对象：ListName, RiskLevel
│   │   ├── repositories/     # 仓储接口
│   │   ├── services/         # 领域服务（跨聚合业务逻辑）
│   │   └── events/           # 领域事件：WordListCreated, WordListUpdated
│   └── app/                  # 应用聚合根
│       ├── entities/         # 领域实体：App
│       └── repositories/     # 仓储接口
├── application/              # 应用层（用例协调）
│   ├── commands/             # 命令：CreateWordList, UpdateWordList
│   ├── queries/              # 查询：GetWordList, GetWordLists
│   ├── handlers/             # CQRS处理器（命令/查询分离）
│   └── dto/                  # 数据传输对象
├── infrastructure/           # 基础设施层（技术实现）
│   ├── repositories/         # 仓储实现（Tortoise ORM适配）
│   └── database/             # 数据库模型（ORM映射）
├── interfaces/               # 接口层（外部交互）
│   ├── controllers/          # 控制器（API端点处理）
│   ├── routes/               # FastAPI路由配置
│   └── dependencies.py       # 依赖注入容器
├── shared/                   # 共享内核
│   ├── enums/                # 业务枚举（ListType, MatchRule, RiskType等）
│   ├── exceptions/           # 领域异常
│   └── events/               # 事件基础设施
└── config/                   # 配置管理
    ├── settings.py           # 应用设置
    ├── database.py           # 数据库配置
    └── aerich_config.py      # 数据库迁移配置
```

### 🎯 架构设计原则

1. **依赖倒置原则**: 内层不依赖外层，通过接口实现解耦
2. **单一职责原则**: 每层只负责自己的职责，边界清晰
3. **开闭原则**: 对扩展开放，对修改封闭
4. **领域驱动**: 代码结构反映业务概念和规则

## 🚀 快速开始

### 环境要求
- Python 3.7+
- MySQL 5.7+ / 8.0+
- Git

### 安装配置
```bash
# 克隆项目
git clone <repository-url>
cd word_guard

# 安装依赖
pip install -r requirements.txt

# 配置数据库
# 复制配置文件并修改数据库连接信息
cp src/config/.env.example src/config/.env

# 初始化数据库迁移
aerich init-db

# 运行迁移
aerich upgrade
```

### 启动应用
```bash
# 开发模式（自动重载）
python yuyan.py

# 生产模式
uvicorn src.main:app --host 0.0.0.0 --port 18000 --workers 4
```

### 开发工具
```bash
# 运行所有测试
pytest

# 运行测试并查看覆盖率
pytest --cov=src --cov-report=html

# 运行单元测试
pytest tests/unit/

# 运行集成测试
pytest tests/integration/

# 代码格式化（如果安装了black）
black src/ tests/

# 类型检查（如果安装了mypy）
mypy src/
```

### 访问地址
- **API文档**: http://localhost:18000/docs
- **系统信息**: http://localhost:18000/
- **健康检查**: http://localhost:18000/health

## 📊 API接口

### 请求格式
所有API遵循RESTful风格，使用JSON格式交换数据。

#### 通用头信息
```http
Content-Type: application/json
Accept: application/json
User-Agent: YourApp/1.0
```

#### 统一响应格式
```json
{
    "code": 200,
    "message": "success",
    "data": {},
    "timestamp": "2024-01-01T00:00:00Z"
}
```

#### HTTP状态码
- `200 OK`: 请求成功
- `201 Created`: 资源创建成功
- `400 Bad Request`: 请求参数错误
- `404 Not Found`: 资源不存在
- `422 Unprocessable Entity`: 数据验证失败
- `500 Internal Server Error`: 服务器内部错误

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

#### 领域层设计
1. **聚合根(Aggregate Root)**: 
   - `WordList`: 名单聚合根，封装名单相关业务规则
   - `App`: 应用聚合根，管理多租户应用

2. **实体(Entity)**: 
   - 具有唯一标识的业务对象
   - 封装业务规则和不变性约束
   - 支持领域事件发布

3. **值对象(Value Object)**: 
   - `ListName`: 名单名称，包含长度和格式验证
   - `RiskLevel`: 风险等级，封装风险分类逻辑
   - 不可变对象，通过值比较相等性

4. **仓储(Repository)**: 
   - 抽象数据访问接口
   - 隐藏数据持久化细节
   - 支持领域查询语言

5. **领域服务(Domain Service)**: 
   - 处理跨聚合的业务逻辑
   - 无状态的纯业务计算

6. **领域事件(Domain Event)**: 
   - `WordListCreatedEvent`: 名单创建事件
   - `WordListUpdatedEvent`: 名单更新事件
   - 支持事件驱动架构

#### CQRS模式
- **命令(Commands)**: 
  - `CreateWordListCommand`: 创建名单命令
  - `UpdateWordListCommand`: 更新名单命令
  - 封装修改操作的输入参数

- **查询(Queries)**: 
  - `GetWordListQuery`: 获取单个名单查询
  - `GetWordListsQuery`: 获取名单列表查询
  - 专门的读模型，优化查询性能

- **处理器(Handlers)**: 
  - 命令处理器：处理业务逻辑，产生副作用
  - 查询处理器：纯读操作，无副作用
  - 实现命令查询职责分离

#### 软删除机制
- **审计支持**: 所有实体继承`BaseModel`，自动记录创建时间、更新时间、删除时间
- **审计用户**: 记录创建人、更新人、删除人信息
- **逻辑删除**: 通过`delete_time`字段实现软删除，保留历史数据
- **自动过滤**: 仓储层自动过滤已删除记录

#### 业务规则封装
- **18种语言支持**: 从中文、英文到土耳其语的全球化支持
- **13种风险类型**: 涵盖涉政、色情、辱骂、广告等完整风险分类体系
- **7种匹配规则**: 支持文本、昵称、IP、账号、角色ID、设备指纹等多维度匹配
- **类型安全**: 使用IntEnum确保枚举值的类型安全和描述信息

## 📋 数据库设计

### 数据模型架构

#### BaseModel 基础模型
所有实体继承的基础模型，提供统一的审计字段：
```python
class BaseModel(models.Model):
    create_time = fields.DatetimeField(auto_now_add=True)
    update_time = fields.DatetimeField(auto_now=True)
    delete_time = fields.DatetimeField(null=True)  # 软删除
    create_by = fields.CharField(max_length=50, null=True)
    update_by = fields.CharField(max_length=50, null=True)
    delete_by = fields.CharField(max_length=50, null=True)
```

#### WordListModel (名单表)
核心业务实体，存储内容过滤规则：

| 字段 | 类型 | 说明 | 枚举值 |
|------|------|------|---------|
| `id` | int | 自增主键 | - |
| `list_name` | varchar(100) | 名单名称 | - |
| `list_type` | int | 名单类型 | 0-白名单, 1-忽略名单, 2-黑名单 |
| `match_rule` | int | 匹配规则 | 0-文本+昵称, 1-文本, 2-昵称, 3-IP, 4-账号, 5-角色ID, 6-设备指纹 |
| `suggestion` | int | 处置建议 | 0-拒绝, 1-通过, 2-审核 |
| `risk_type` | int | 风险类型 | 0-正常, 100-涉政, 200-色情, 300-辱骂, 400-广告, 500-无意义, 600-违禁, 700-其他, 800-黑账号, 900-黑IP, 810-高危账号, 910-高危IP, 1000-自定义 |
| `status` | int | 状态 | 0-禁用, 1-启用 |
| `language` | int | 语种 | 0-全部, 1-简中, 2-繁中, 3-英文, ... 17-其他 |

#### AppModel (应用表)
多租户应用管理：

| 字段 | 类型 | 说明 | 约束 |
|------|------|------|---------|
| `id` | int | 自增主键 | PK |
| `app_name` | varchar(100) | 应用名称 | NOT NULL |
| `app_id` | varchar(50) | 应用唯一标识 | UNIQUE |
| `username` | varchar(50) | 负责人 | NULL |

### 数据库迁移
```bash
# 初始化迁移环境
aerich init-db

# 生成迁移文件
aerich migrate --name="add_new_field"

# 应用迁移
aerich upgrade

# 回滚迁移
aerich downgrade

# 查看迁移历史
aerich history
```

## 🎯 设计优势

### 架构优势
1. **高内聚低耦合**: 
   - 业务逻辑集中在领域层，减少散列
   - 层间依赖清晰，遵循依赖倒置原则

2. **易于扩展**: 
   - 新增聚合根只需添加对应目录结构
   - 值对象和实体独立封装，互不影响
   - CQRS模式支持读写分离优化

3. **业务导向**: 
   - 代码结构直接反映业务概念
   - 领域专家可以直接理解代码结构
   - 业务规则在领域层集中管理

4. **测试友好**: 
   - 领域实体是纯函数，无副作用
   - 依赖注入便于模拟mock对象
   - 层次分明便于针对性测试

5. **维护性强**: 
   - 单一职责原则，修改影响范围小
   - 明确的错误边界和异常处理
   - 代码结构清晰，bug定位准确

6. **团队协作**: 
   - 不同层次可以并行开发
   - 接口定义明确，减少沟通成本
   - 代码复用性高，减少重复开发

### 技术优势
- **异步高性能**: FastAPI + Tortoise ORM 全异步栈
- **类型安全**: Python 3.7+ 类型提示 + Pydantic 数据验证
- **API文档**: OpenAPI 3.0 自动生成交互式文档
- **数据库迁移**: Aerich 提供版本化数据库管理
- **软删除**: 保留历史数据，支持数据恢复

## 🛠️ 开发指南

### 代码组织原则
1. **遵循命名约定**: 
   - 文件名使用snake_case
   - 类名使用PascalCase
   - 函数名使用snake_case

2. **层次依赖规则**:
   ```
   interfaces -> application -> domain <- infrastructure
                                ^
                            shared (enums, exceptions)
   ```

3. **新增聚合根步骤**:
   ```bash
   mkdir -p src/domain/{aggregate_name}/{entities,value_objects,repositories,services,events}
   mkdir -p src/application/{commands,queries,handlers,dto}
   mkdir -p src/infrastructure/repositories
   mkdir -p src/interfaces/{controllers,routes}
   ```

### 测试策略
- **单元测试**: 测试领域实体和值对象的业务逻辑
- **集成测试**: 测试应用层到数据库的完整流程
- **API测试**: 使用FastAPI TestClient测试HTTP接口

### 部署建议
```bash
# Docker 部署
docker build -t wordguard .
docker run -d -p 18000:18000 --name wordguard-app wordguard

# 使用 Docker Compose
docker-compose up -d

# 生产环境运行
uvicorn src.main:app --host 0.0.0.0 --port 18000 --workers 4 --access-log
```

## 🔮 路线图

### 短期目标 (1-2个月)
- [ ] **测试覆盖率提升**: 单元测试覆盖率达到 90%+
- [ ] **API 性能优化**: 添加请求限流和缓存机制
- [ ] **数据验证增强**: 完善Pydantic数据模型验证
- [ ] **日志监控**: 集成结构化日志和指标监控

### 中期目标 (3-6个月)
- [ ] **名单详情聚合**: 实现名单内容管理聚合
- [ ] **策略引擎**: 实现可配置的内容过滤策略
- [ ] **事件驱动架构**: 实现领域事件发布订阅
- [ ] **搜索功能**: 集成Elasticsearch实现高级搜索

### 长期目标 (6-12个月)
- [ ] **AI检测集成**: 集成机器学习模型进行内容理解
- [ ] **实时流处理**: 实现流式数据处理管道
- [ ] **微服务拆分**: 按业务领域拆分为微服务
- [ ] **多租户增强**: 实现数据隔离和权限管理
- [ ] **云原生支持**: 支持Kubernetes部署和服务网格

### 技术升级计划
- [ ] **数据库优化**: 添加读写分离和分库分表
- [ ] **缓存策略**: Redis 多级缓存和热点数据预热
- [ ] **消息队列**: RabbitMQ/Kafka 异步任务处理
- [ ] **配置中心**: 动态配置管理和热更新
