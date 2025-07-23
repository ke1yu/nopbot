import psycopg
import os
from constants import DB_SETTING

class Database:
	DATABASE_URL = os.environ.get("DATABASE_URL")

	@classmethod
	def select(cls, guild_id):
		with psycopg.connect(cls.DATABASE_URL, row_factory=psycopg.rows.dict_row) as conn:
			with conn.cursor() as cur:
				cur.execute(
					"SELECT FROM " + DB_SETTING + " WHERE guild_id = %s",
					(guild_id)
				)

				result = cur.fetch_one()
		
		return result

	# @classmethod
	# def select(cls, guild_id, col, val):
	# 	with psycopg.connect(cls.DATABASE_URL, row_factory=psycopg.rows.dict_row) as conn:
	# 		with conn.cursor() as cur:
	# 			cur.execute(
	# 				"SELECT FROM " + DB_SETTING + " WHERE guild_id = %s AND %s = %s",
	# 				(guild_id, col, val)
	# 			)

	# 			result = cur.fetch_one()
		
	# 	return result

	@classmethod
	def insert(cls, bean):
		bean_tuple = bean.get_tuple()
		percent_s = ", ".join(["%s"] * len(bean_tuple))

		with psycopg.connect(cls.DATABASE_URL) as conn:
			with conn.cursor() as cur:
				cur.execute(
					"INSERT INTO " + DB_SETTING + " VALUES (" + percent_s + ")",
					bean_tuple
				)
	
	@classmethod
	def update(cls, guild_id, col, value):
		with psycopg.connect(cls.DATABASE_URL) as conn:
			with conn.cursor() as cur:
				cur.execute(
					"UPDATE " + DB_SETTING + " SET %s = ",
					(guild_id)
				)

	@classmethod
	def delete(cls, guild_id):
		with psycopg.connect(cls.DATABASE_URL) as conn:
			with conn.cursor() as cur:
				cur.execute(
					"DELETE * FROM " + DB_SETTING + " WHERE guild_id = %s",
					(guild_id)
				)