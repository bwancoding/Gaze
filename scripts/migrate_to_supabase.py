#!/usr/bin/env python3
"""
WRHITW SQLite → Supabase PostgreSQL 迁移脚本

使用方法:
    python migrate_to_supabase.py --sqlite ./wrhitw.db --supabase-url "postgresql://..."

依赖:
    pip install sqlite3 asyncpg python-dotenv
"""

import asyncio
import argparse
import sqlite3
import asyncpg
import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()


class SQLiteToSupabaseMigrator:
    """SQLite 到 Supabase PostgreSQL 迁移器"""

    # 表映射：SQLite 表名 → PostgreSQL 表名
    TABLES = [
        'sources',
        'events',
        'event_sources',
        'ai_summaries',
        'users',
        'reading_history',
        'bookmarks',
        'stakeholder_types',
        'stakeholders',
        'event_stakeholders',
        'stakeholder_verifications',
        'user_stakeholder_roles',
        'user_personas',
        'event_stakeholder_verifications',
        'comments',
        'comment_votes',
    ]

    # 需要转换 TEXT 字段为 UUID 数组的字段
    UUID_ARRAY_FIELDS = {
        'ai_summaries': ['left_sources', 'center_sources', 'right_sources'],
        'users': ['preferred_categories'],
        'events': ['tags'],
    }

    def __init__(self, sqlite_path: str, supabase_url: str):
        self.sqlite_path = sqlite_path
        self.supabase_url = supabase_url
        self.sqlite_conn: Optional[sqlite3.Connection] = None
        self.pg_conn: Optional[asyncpg.Connection] = None

    async def connect(self):
        """建立数据库连接"""
        print(f"📦 连接 SQLite: {self.sqlite_path}")
        self.sqlite_conn = sqlite3.connect(self.sqlite_path)
        self.sqlite_conn.row_factory = sqlite3.Row

        print(f"📦 连接 Supabase PostgreSQL")
        self.pg_conn = await asyncpg.connect(self.supabase_url)
        print("✅ 数据库连接成功")

    async def close(self):
        """关闭数据库连接"""
        if self.sqlite_conn:
            self.sqlite_conn.close()
        if self.pg_conn:
            await self.pg_conn.close()
        print("✅ 数据库连接已关闭")

    def _convert_value(self, value: Any, table: str, column: str) -> Any:
        """转换字段值以适配 PostgreSQL"""
        if value is None:
            return None

        # 处理 UUID 数组字段（SQLite 存储为 JSON 字符串或逗号分隔）
        if table in self.UUID_ARRAY_FIELDS and column in self.UUID_ARRAY_FIELDS[table]:
            if isinstance(value, str):
                try:
                    # 尝试解析 JSON
                    parsed = json.loads(value)
                    if isinstance(parsed, list):
                        return parsed
                except json.JSONDecodeError:
                    # 尝试逗号分隔
                    if value.strip():
                        return [v.strip() for v in value.split(',')]
            return value

        # 处理布尔值（SQLite 使用 0/1）
        if isinstance(value, int) and value in (0, 1):
            # 检查是否是布尔列
            return bool(value)

        # 处理日期时间
        if isinstance(value, str):
            # SQLite 的 DATETIME 通常是字符串
            try:
                # 尝试解析为标准格式
                if 'T' in value or value.endswith('Z'):
                    return value  # 已经是 ISO 格式
            except Exception:
                pass

        return value

    def _row_to_dict(self, row: sqlite3.Row, table: str) -> Dict[str, Any]:
        """将 SQLite 行转换为 PostgreSQL 兼容的字典"""
        result = {}
        for key in row.keys():
            value = row[key]
            result[key] = self._convert_value(value, table, key)
        return result

    async def get_table_columns(self, table: str) -> List[str]:
        """获取 PostgreSQL 表的列名"""
        query = """
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = $1 
            ORDER BY ordinal_position
        """
        rows = await self.pg_conn.fetch(query, table)
        return [row['column_name'] for row in rows]

    async def migrate_table(self, table: str) -> int:
        """迁移单个表"""
        print(f"\n📊 迁移表：{table}")

        # 获取 SQLite 数据
        cursor = self.sqlite_conn.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()

        if not rows:
            print(f"  ⚠️  表 {table} 为空，跳过")
            return 0

        print(f"  📝 找到 {len(rows)} 条记录")

        # 获取 PostgreSQL 表列
        pg_columns = await self.get_table_columns(table)
        
        # 过滤掉 PostgreSQL 表中不存在的列
        sqlite_columns = [desc[0] for desc in cursor.description]
        valid_columns = [col for col in sqlite_columns if col in pg_columns]

        if len(valid_columns) != len(sqlite_columns):
            missing = set(sqlite_columns) - set(pg_columns)
            print(f"  ⚠️  跳过 {len(missing)} 个不兼容的列：{missing}")

        # 批量插入
        batch_size = 100
        inserted = 0

        for i in range(0, len(rows), batch_size):
            batch = rows[i:i + batch_size]
            
            # 构建插入语句
            placeholders = ', '.join([f'${j+1}' for j in range(len(valid_columns))])
            columns_str = ', '.join(valid_columns)
            insert_query = f"""
                INSERT INTO {table} ({columns_str})
                VALUES ({placeholders})
                ON CONFLICT DO NOTHING
            """

            # 准备数据
            values = []
            for row in batch:
                row_dict = self._row_to_dict(row, table)
                row_values = [row_dict.get(col) for col in valid_columns]
                values.append(row_values)

            # 批量插入
            try:
                await self.pg_conn.executemany(insert_query, values)
                inserted += len(batch)
                print(f"  ✅ 已插入 {inserted}/{len(rows)} 条记录")
            except Exception as e:
                print(f"  ❌ 插入失败：{e}")
                # 尝试逐条插入以定位问题
                for row in batch:
                    row_dict = self._row_to_dict(row, table)
                    row_values = [row_dict.get(col) for col in valid_columns]
                    try:
                        await self.pg_conn.execute(insert_query, *row_values)
                        inserted += 1
                    except Exception as inner_e:
                        print(f"    ⚠️  跳过单条记录：{inner_e}")

        return inserted

    async def verify_migration(self) -> bool:
        """验证迁移结果"""
        print("\n🔍 验证迁移结果...")
        
        all_ok = True
        for table in self.TABLES:
            sqlite_count = self.sqlite_conn.execute(
                f"SELECT COUNT(*) as cnt FROM {table}"
            ).fetchone()['cnt']
            
            pg_row = await self.pg_conn.fetchrow(
                f"SELECT COUNT(*) as cnt FROM {table}"
            )
            pg_count = pg_row['cnt'] if pg_row else 0

            status = "✅" if sqlite_count == pg_count else "⚠️"
            if sqlite_count != pg_count:
                all_ok = False
            
            print(f"  {status} {table}: SQLite={sqlite_count}, PostgreSQL={pg_count}")

        return all_ok

    async def reset_sequences(self):
        """重置 PostgreSQL 序列（确保 UUID 生成不冲突）"""
        print("\n🔄 重置序列...")
        
        # PostgreSQL 使用 uuid_generate_v4()，不需要重置序列
        # 但我们可以验证扩展已启用
        result = await self.pg_conn.fetchval(
            "SELECT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'uuid-ossp')"
        )
        
        if result:
            print("  ✅ uuid-ossp 扩展已启用")
        else:
            print("  ⚠️  uuid-ossp 扩展未启用，需要先运行：CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";")

    async def migrate(self) -> bool:
        """执行完整迁移"""
        print("=" * 60)
        print("WRHITW SQLite → Supabase PostgreSQL 迁移")
        print("=" * 60)

        try:
            await self.connect()
            
            total_inserted = 0
            for table in self.TABLES:
                count = await self.migrate_table(table)
                total_inserted += count

            await self.reset_sequences()
            
            print("\n" + "=" * 60)
            print(f"迁移完成！共插入 {total_inserted} 条记录")
            print("=" * 60)

            # 验证
            verification_ok = await self.verify_migration()
            
            return verification_ok

        except Exception as e:
            print(f"\n❌ 迁移失败：{e}")
            import traceback
            traceback.print_exc()
            return False

        finally:
            await self.close()


async def main():
    parser = argparse.ArgumentParser(
        description='WRHITW SQLite → Supabase PostgreSQL 迁移工具'
    )
    parser.add_argument(
        '--sqlite', 
        default='./wrhitw.db',
        help='SQLite 数据库路径 (默认：./wrhitw.db)'
    )
    parser.add_argument(
        '--supabase-url',
        default=os.getenv('SUPABASE_DATABASE_URL'),
        help='Supabase PostgreSQL 连接 URL (或设置 SUPABASE_DATABASE_URL 环境变量)'
    )
    parser.add_argument(
        '--verify-only',
        action='store_true',
        help='仅验证迁移结果，不执行迁移'
    )

    args = parser.parse_args()

    if not args.supabase_url:
        print("❌ 错误：请提供 --supabase-url 或设置 SUPABASE_DATABASE_URL 环境变量")
        print("\n示例:")
        print('  export SUPABASE_DATABASE_URL="postgresql://postgres:password@db.xxx.supabase.co:5432/postgres"')
        print('  python migrate_to_supabase.py --sqlite ./wrhitw.db')
        return 1

    # 检查 SQLite 文件
    if not os.path.exists(args.sqlite):
        print(f"❌ 错误：SQLite 文件不存在：{args.sqlite}")
        return 1

    migrator = SQLiteToSupabaseMigrator(args.sqlite, args.supabase_url)
    
    if args.verify_only:
        await migrator.connect()
        ok = await migrator.verify_migration()
        await migrator.close()
        return 0 if ok else 1
    else:
        ok = await migrator.migrate()
        return 0 if ok else 1


if __name__ == '__main__':
    exit_code = asyncio.run(main())
    exit(exit_code)
