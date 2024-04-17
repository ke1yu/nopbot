import discord
from constants import Str_Dict_Keys
from lingual import get_locale

class EmbedHelp(discord.Embed):
  def __init__(self, language):
    self.color = 0x797979
    self.title = 'Help'
    self.type = 'rich'
    self.url = None
    self.description = None
    self.timestamp = None
    self.add_field(name="/mynoticenop", value=get_locale(language, Str_Dict_Keys.HELP_MY_NOTICE), inline=False)
    self.add_field(name="/vcnoticenop", value=get_locale(language, Str_Dict_Keys.HELP_VC_NOTICE), inline=False)
    self.add_field(name="/sendherenop", value=get_locale(language, Str_Dict_Keys.HELP_SEND_HERE), inline=False)
    self.add_field(name="/notifynamenop", value=get_locale(language, Str_Dict_Keys.HELP_NOTIFY_NAME), inline=False)
    self.add_field(name="/langnop", value=get_locale(language, Str_Dict_Keys.HELP_LANG), inline=False)
    self.add_field(name="Privacy Policy", value="https://www.utsuboublog.com/number-of-people-legal#Privacy-Policy")
    self.set_author(name="Keiyu", url="https://twitter.com/utsu_b0u", icon_url="https://pbs.twimg.com/profile_images/1635287134201614342/CDDMzL6C_400x400.png")