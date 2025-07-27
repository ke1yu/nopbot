from replit import db
from constants import DB_SETTING, Db_Keys, Str_Dict_Keys

print(db[DB_SETTING].keys())

for key in db[DB_SETTING]:
  guild_data = db[DB_SETTING][key]

  # alert_channel: None または dictであることを想定
  value = guild_data.get(Db_Keys.ALERT_CHANNEL)
  if isinstance(value, int):
    db[DB_SETTING][key][Db_Keys.ALERT_CHANNEL] = {Str_Dict_Keys.DEFAULT: str(value)}

  # no_notice_vc: List[int] → List[str]
  vc_list = guild_data.get(Db_Keys.NO_NOTICE_VC, [])
  if isinstance(vc_list, list):
    db[DB_SETTING][key][Db_Keys.NO_NOTICE_VC] = [str(vc) for vc in vc_list]

  # no_notice_member: List[int] → List[str]
  member_list = guild_data.get(Db_Keys.NO_NOTICE_MEMBER, [])
  if isinstance(member_list, list):
    db[DB_SETTING][key][Db_Keys.NO_NOTICE_MEMBER] = [str(member) for member in member_list]