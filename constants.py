import dataclasses


DB_SETTING = "setting"


# dict keys
@dataclasses.dataclass(frozen=True)
class Db_Keys:
  NO_NOTICE_MEMBER = "no_notice_member"
  NO_NOTICE_VC = "no_notice_vc"
  ALERT_CHANNEL = "alert_channel"
  NAME_NOTICE = "name_notice"
  THRESHOLD = "threshold"
  LANGUAGE = "language"

# string dict keys
@dataclasses.dataclass(frozen=True)
class Str_Dict_Keys:
  ALL = "__all__"
  DEFAULT = "__default__"
  ALERT = "alert"
  ALERT_NAME_JOIN = "alert_name_join"
  ALERT_NAME_LEAVE = "alert_name_leave"
  MY_NOTICE = "my_notice"
  SEND_HERE = "send_here"
  LANG_CHANGED = "lang_changed"
  VC_CHANGED = "vc_changed"
  NOTICE_TYPE_CHANGED = "notice_type_changed"
  NOT_INTEGER = "not_integer"
  NO_CHANNEL = "no_channel"
  NO_PERMISSIONS = "no_permissions"
  HELP_MY_NOTICE = "help_my_notice"
  HELP_VC_NOTICE = "help_vc_notice"
  HELP_SEND_HERE = "help_send_here"
  HELP_NOTIFY_NAME = "help_notify_name"
  HELP_LANG = "help_lang"


# language
@dataclasses.dataclass(frozen=True)
class Lang:
  JP = "jp"
  EN = "en"

# numbers
@dataclasses.dataclass(frozen=True)
class Num:
  MAX_THRESHOLD = 250000