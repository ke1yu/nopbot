import json
from lingual import Lang
from constants import Num


class Bean:
	def __init__(self, guild_id):
		self.guild_id = guild_id
		self.no_notice_member = []
		self.no_notice_vc = []
		self.alert_channel = {}
		self.name_notice = True
		self.language  = Lang.EN
	
	def get_tuple(self):
		return (
			self.guild_id,
			self.no_notice_member,
			self.no_notice_vc,
			json.dumps(self.alert_channel),
			self.name_notice,
			self.language
		)