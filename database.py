import psycopg2
import psycopg2.extras
import os
from constants import DB_SETTING

class Database:
    DATABASE_URL = os.environ.get("DATABASE_URL")

    @classmethod
    def select(cls, guild_id):
        with psycopg2.connect(cls.DATABASE_URL) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute(
                    f"SELECT * FROM {DB_SETTING} WHERE guild_id = %s",
                    (guild_id,)
                )
                result = cur.fetchone()
        return dict(result) if result else {}

    @classmethod
    def insert(cls, bean):
        bean_tuple = bean.get_tuple()
        placeholders = ", ".join(["%s"] * len(bean_tuple))
        
        with psycopg2.connect(cls.DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"INSERT INTO {DB_SETTING} VALUES ({placeholders})",
                    bean_tuple
                )

    @classmethod
    def update(cls, guild_id, col, value):
        with psycopg2.connect(cls.DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"UPDATE {DB_SETTING} SET {col} = %s WHERE guild_id = %s",
                    (value, guild_id)
                )

    @classmethod
    def delete(cls, guild_id):
        with psycopg2.connect(cls.DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"DELETE FROM {DB_SETTING} WHERE guild_id = %s",
                    (guild_id,)
                )
