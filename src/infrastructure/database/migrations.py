"""数据库迁移管理脚本"""
import os
import sys
import asyncio
from tortoise import Tortoise
from aerich import Command


async def init_db():
    """初始化数据库迁移"""
    try:
        command = Command(tortoise_config="src.config.aerich_config.TORTOISE_ORM", app="models")
        await command.init()
        print("✅ 数据库迁移初始化完成")
    except Exception as e:
        print(f"❌ 初始化失败: {e}")


async def init_migrate():
    """创建初始迁移"""
    try:
        command = Command(tortoise_config="src.config.aerich_config.TORTOISE_ORM", app="models")
        await command.init_db(safe=True)
        print("✅ 数据库初始化完成")
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")


async def create_migration(name: str = None):
    """创建新的迁移"""
    try:
        command = Command(tortoise_config="src.config.aerich_config.TORTOISE_ORM", app="models")
        await command.migrate(name)
        print(f"✅ 迁移创建完成: {name or 'auto_migration'}")
    except Exception as e:
        print(f"❌ 创建迁移失败: {e}")


async def apply_migrations():
    """应用迁移"""
    try:
        command = Command(tortoise_config="src.config.aerich_config.TORTOISE_ORM", app="models")
        await command.upgrade()
        print("✅ 迁移应用完成")
    except Exception as e:
        print(f"❌ 应用迁移失败: {e}")


async def rollback_migration():
    """回滚迁移"""
    try:
        command = Command(tortoise_config="src.config.aerich_config.TORTOISE_ORM", app="models")
        await command.downgrade()
        print("✅ 迁移回滚完成")
    except Exception as e:
        print(f"❌ 回滚失败: {e}")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python migrations.py [init|init_db|migrate|upgrade|downgrade]")
        print()
        print("命令:")
        print("  init      - 初始化aerich")
        print("  init_db   - 初始化数据库")
        print("  migrate   - 创建新迁移 (可选: migration_name)")
        print("  upgrade   - 应用迁移")
        print("  downgrade - 回滚迁移")
        return

    command = sys.argv[1]
    
    if command == "init":
        asyncio.run(init_db())
    elif command == "init_db":
        asyncio.run(init_migrate())
    elif command == "migrate":
        name = sys.argv[2] if len(sys.argv) > 2 else None
        asyncio.run(create_migration(name))
    elif command == "upgrade":
        asyncio.run(apply_migrations())
    elif command == "downgrade":
        asyncio.run(rollback_migration())
    else:
        print(f"❌ 未知命令: {command}")


if __name__ == "__main__":
    main()