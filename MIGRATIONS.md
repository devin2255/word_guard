# 数据库迁移管理指南

使用Aerich管理YuYan项目的数据库迁移。

## 快速开始

### 1. 安装和初始化

```bash
# 方法1: 使用设置脚本（推荐）
python setup_migrations.py

# 方法2: 手动设置
pip install aerich==0.7.4
aerich init -t src.config.aerich_config.TORTOISE_ORM
aerich init-db
```

### 2. 创建迁移

```bash
# 自动检测模型变更并创建迁移
aerich migrate

# 创建具名迁移
aerich migrate remove_risk_severity

# 使用便捷脚本
python migrations.py migrate remove_risk_severity
```

### 3. 应用迁移

```bash
# 应用所有未应用的迁移
aerich upgrade

# 使用便捷脚本
python migrations.py upgrade
```

### 4. 回滚迁移

```bash
# 回滚最后一个迁移
aerich downgrade

# 使用便捷脚本
python migrations.py downgrade
```

## 目录结构

```
YuYan/
├── migrations/                 # 迁移文件目录
│   └── models/                # models应用的迁移
│       ├── 0_initial.py       # 初始迁移
│       └── 1_remove_risk_severity.py
├── pyproject.toml             # Aerich配置
├── migrations.py              # 迁移管理脚本
└── setup_migrations.py       # 安装设置脚本
```

## 常用命令

| 命令 | 说明 |
|------|------|
| `aerich init` | 初始化aerich配置 |
| `aerich init-db` | 初始化数据库，创建aerich元数据表 |
| `aerich migrate [name]` | 检测模型变更，创建迁移文件 |
| `aerich upgrade` | 应用所有未应用的迁移 |
| `aerich downgrade` | 回滚最后一次迁移 |
| `aerich history` | 查看迁移历史 |
| `aerich heads` | 显示当前迁移状态 |

## 配置文件

### pyproject.toml
```toml
[tool.aerich]
tortoise_orm = "src.config.aerich_config.TORTOISE_ORM"
location = "./migrations"
src_folder = "./."
```

### aerich_config.py
```python
TORTOISE_ORM = {
    "connections": {
        "default": "mysql://root:2255@127.0.0.1:3306/yuyan"
    },
    "apps": {
        "models": {
            "models": [
                "src.infrastructure.database.models",
                "aerich.models"
            ],
            "default_connection": "default",
        },
    },
}
```

## 最佳实践

### 1. 开发流程
1. 修改模型 (`src/infrastructure/database/models.py`)
2. 创建迁移：`aerich migrate descriptive_name`
3. 检查生成的迁移文件
4. 应用迁移：`aerich upgrade`
5. 测试新的数据库结构

### 2. 迁移命名
- 使用描述性名称：`remove_risk_severity`
- 使用动词开头：`add_user_table`, `update_wordlist_schema`
- 避免空格和特殊字符

### 3. 团队协作
- 迁移文件要提交到版本控制
- 部署前先在开发环境测试迁移
- 生产环境部署时先备份数据库

### 4. 回滚准备
- 重要变更前备份数据库
- 测试回滚流程
- 准备数据修复脚本

## 故障排除

### 1. 迁移冲突
```bash
# 查看当前状态
aerich heads

# 重置到特定版本
aerich downgrade
aerich upgrade
```

### 2. 模型不同步
```bash
# 强制创建迁移
aerich migrate --name force_sync
```

### 3. 初始化问题
```bash
# 删除migrations目录重新开始
rm -rf migrations
aerich init -t src.config.aerich_config.TORTOISE_ORM
aerich init-db
```

## 生产环境注意事项

1. **备份数据**：迁移前务必备份生产数据库
2. **测试迁移**：在预生产环境先测试
3. **停机时间**：大型迁移可能需要维护窗口
4. **监控检查**：迁移后检查应用功能
5. **回滚准备**：准备快速回滚方案

## 示例：移除risk_severity字段

```bash
# 1. 修改模型文件（已完成）
# 2. 创建迁移
aerich migrate remove_risk_severity

# 3. 查看生成的迁移文件
cat migrations/models/1_remove_risk_severity.py

# 4. 应用迁移
aerich upgrade

# 5. 验证变更
# 检查数据库表结构是否正确
```