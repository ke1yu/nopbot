import discord
from discord import app_commands
import topgg
import dataclasses
import os
from replit import db
# from datetime import datetime, timedelta
from constants import DB_SETTING, Db_Keys, Lang, Str_Dict_Keys
from lingual import get_locale
from help import EmbedHelp
from keep_alive import keep_alive

database_keys = Db_Keys()
database_keys = dataclasses.asdict(database_keys)

default_dict = {
  Db_Keys.NO_NOTICE_MEMBER: [],
  Db_Keys.NO_NOTICE_VC: [],
  Db_Keys.ALERT_CHANNEL: None,
  Db_Keys.NAME_NOTICE: True,
  Db_Keys.LANGUAGE: Lang.EN,
}

embed_help = {
  Lang.JP : EmbedHelp(Lang.JP),
  Lang.EN : EmbedHelp(Lang.EN)
}

class MyClient(discord.Client):
  def __init__(self, *, intents: discord.Intents):
    activity = discord.Game(name="/helpnop")
    super().__init__(intents=intents, activity=activity, status=discord.Status.online)
    self.tree = app_commands.CommandTree(self)

  async def setup_hook(self):
    # This copies the global commands over to your guild.
    # サーバー数
    # guild_count = len(client.guilds)
    # f文字列(フォーマット済み文字列リテラル)は、Python3.6からの機能です。
    # game = discord.Game(f'{guild_count} servers')
    for g in self.guilds:
      g_id = str(g.id)
      if db[DB_SETTING].get(g_id, 'NO') == 'NO':
        db[DB_SETTING][g_id] = default_dict
      for key in database_keys.values():
        if db[DB_SETTING][g_id].get(key, 'NO') == 'NO':
          db[DB_SETTING][g_id][key] = default_dict[key]
    # self.tree.copy_global_to(guild=MY_GUILD)
    dbl_token = os.environ['DBL_TOKEN']
    self.topggpy = topgg.DBLClient(client, dbl_token, autopost=True, post_shard_count=True)
    await self.tree.sync()

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
# intents.message_content = True
client = MyClient(intents=intents)

@client.event
async def on_voice_state_update(member, before, after):
  g_id = str(member.guild.id)
  g = db[DB_SETTING][g_id]
  if member:
    if member.id not in g[Db_Keys.NO_NOTICE_MEMBER]:
      lang = g[Db_Keys.LANGUAGE]
      name_notice = g[Db_Keys.NAME_NOTICE]
      if g[Db_Keys.ALERT_CHANNEL] == None:
        alert_channel = member.guild.system_channel
      else:
        alert_channel = [
          ch for ch in member.guild.text_channels
          if ch.id == g[Db_Keys.ALERT_CHANNEL]
        ]
        if alert_channel:
          alert_channel = alert_channel[0]
        else:
          alert_channel = member.guild.system_channel
    
      if (before.channel != after.channel):
        if after.channel:
          if name_notice:
            msg = get_locale(lang, Str_Dict_Keys.ALERT_NAME_JOIN, member.display_name, after.channel.name, len(after.channel.members))
          else:
            msg = get_locale(lang, Str_Dict_Keys.ALERT, after.channel.name, len(after.channel.members))
          if after.channel.id not in g[Db_Keys.NO_NOTICE_VC]:
            await alert_channel.send(msg)
        else:
          if name_notice:
            msg = get_locale(lang, Str_Dict_Keys.ALERT_NAME_LEAVE, member.display_name, before.channel.name, len(before.channel.members))
          else:
            msg = get_locale(lang, Str_Dict_Keys.ALERT, before.channel.name, len(before.channel.members))
          if before.channel.id not in g[Db_Keys.NO_NOTICE_VC]:
            await alert_channel.send(msg)


@client.tree.command(name="mynoticenop", description="Turn on/off notifications about your entry and exit.")
@app_commands.choices(on_off=[
  app_commands.Choice(name="On", value="on"),
  app_commands.Choice(name="Off", value="off")
])
async def my_notice_command(interaction, on_off: app_commands.Choice[str]):
  g_id = str(interaction.guild_id)
  g = db[DB_SETTING][g_id]
  lang = g[Db_Keys.LANGUAGE]
  i_user_id = interaction.user.id
  if on_off.value == 'on':
    if i_user_id in g[Db_Keys.NO_NOTICE_MEMBER]:
      db[DB_SETTING][g_id][Db_Keys.NO_NOTICE_MEMBER].remove(i_user_id)
    await interaction.response.send_message(get_locale(lang, Str_Dict_Keys.MY_NOTICE, interaction.user.id, 'ON'), ephemeral=True)
  elif on_off.value == 'off':
    if i_user_id not in g[Db_Keys.NO_NOTICE_MEMBER]:
      db[DB_SETTING][g_id][Db_Keys.NO_NOTICE_MEMBER].append(i_user_id)
    await interaction.response.send_message(get_locale(lang, Str_Dict_Keys.MY_NOTICE, interaction.user.id, 'OFF'), ephemeral=True)

@client.tree.command(name="vcnoticenop", description="Enter ID of the voice channel to turn notifications on/off.")
@app_commands.choices(on_off=[
  app_commands.Choice(name="On", value="on"),
  app_commands.Choice(name="Off", value="off")
])
async def vc_notice_command(interaction, on_off: app_commands.Choice[str], channel_id : str):
  g_id = str(interaction.guild_id)
  g = db[DB_SETTING][g_id]
  lang = g[Db_Keys.LANGUAGE]
  if interaction.permissions.administrator:
    if channel_id.isdecimal():
      channel_id = int(channel_id)
      ch = [ch for ch in interaction.guild.voice_channels if ch.id == channel_id]
      if ch:
        ch = ch[0]
        if on_off.value == 'on':
          if channel_id in g[Db_Keys.NO_NOTICE_VC]:
            db[DB_SETTING][g_id][Db_Keys.NO_NOTICE_VC].remove(channel_id)
          await interaction.response.send_message(get_locale(lang, Str_Dict_Keys.VC_CHANGED, ch.name, 'ON'))
        elif on_off.value == 'off':
          if channel_id not in g[Db_Keys.NO_NOTICE_VC]:
            db[DB_SETTING][g_id][Db_Keys.NO_NOTICE_VC].append(channel_id)
            await interaction.response.send_message(get_locale(lang, Str_Dict_Keys.VC_CHANGED, ch.name, 'OFF'))
      else:
        await interaction.response.send_message(get_locale(lang, Str_Dict_Keys.NO_CHANNEL), ephemeral=True)
    else:
      await interaction.response.send_message(get_locale(lang, Str_Dict_Keys.NOT_INTEGER), ephemeral=True)
  else:
    await interaction.response.send_message(get_locale(lang, Str_Dict_Keys.NO_PERMISSIONS), ephemeral=True)

  
@client.tree.command(name="sendherenop", description="Notifications will be on the text channel where this command is entered.")
async def send_here_command(interaction):
  g_id = str(interaction.guild_id)
  lang = db[DB_SETTING][g_id][Db_Keys.LANGUAGE]
  if interaction.permissions.administrator:
    db[DB_SETTING][g_id][Db_Keys.ALERT_CHANNEL] = interaction.channel_id
    await interaction.response.send_message(get_locale(lang, Str_Dict_Keys.SEND_HERE, interaction.channel.name))
  else:
    await interaction.response.send_message(get_locale(lang, Str_Dict_Keys.NO_PERMISSIONS), ephemeral=True)


@client.tree.command(name="notifynamenop", description="Turn display of user names in notifications on/off.")
@app_commands.choices(display_name=[
  app_commands.Choice(name="On", value="on"),
  app_commands.Choice(name="Off", value="off")
])
async def notice_type_command(interaction, display_name: app_commands.Choice[str]):
  g_id = str(interaction.guild_id)
  lang = db[DB_SETTING][g_id][Db_Keys.LANGUAGE]
  if interaction.permissions.administrator:
    if display_name.value == "on":
      db[DB_SETTING][g_id][Db_Keys.NAME_NOTICE] = True
      await interaction.response.send_message(get_locale(lang, Str_Dict_Keys.NOTICE_TYPE_CHANGED, 'ON'))
    elif display_name.value == "off":
      db[DB_SETTING][g_id][Db_Keys.NAME_NOTICE] = False
      await interaction.response.send_message(get_locale(lang, Str_Dict_Keys.NOTICE_TYPE_CHANGED, 'OFF'))
  else:
    await interaction.response.send_message(get_locale(lang, Str_Dict_Keys.NO_PERMISSIONS), ephemeral=True)


@client.tree.command(name="langnop", description="Switch languages.")
@app_commands.choices(language=[
  app_commands.Choice(name="日本語", value=Lang.JP),
  app_commands.Choice(name="English", value=Lang.EN)
])
async def lang_command(interaction, language: app_commands.Choice[str]):
  g_id = str(interaction.guild_id)
  if interaction.permissions.administrator:
    db[DB_SETTING][g_id][Db_Keys.LANGUAGE] = language.value
    await interaction.response.send_message(get_locale(language.value, Str_Dict_Keys.LANG_CHANGED, interaction.channel.name))
  else:
    await interaction.response.send_message(get_locale(db[DB_SETTING][g_id][Db_Keys.LANGUAGE], Str_Dict_Keys.NO_PERMISSIONS), ephemeral=True)


@client.tree.command(name="helpnop", description="Display help.")
async def help_command(interaction):
  g_id = str(interaction.guild_id)
  lang = db[DB_SETTING][g_id][Db_Keys.LANGUAGE]
  await interaction.response.send_message(embed=embed_help[lang], ephemeral=True)


# @client.tree.command(name="countnop", description="Count the number of servers where this bot is installed.")
# async def count_command(interaction):
#   await interaction.response.send_message(str(len(client.guilds)) + " servers", ephemeral=True)


@client.event
async def on_guild_join(guild):
  db[DB_SETTING][str(guild.id)] = default_dict

@client.event
async def on_guild_remove(guild):
  if guild:
    g_id = str(guild.id)
    db[DB_SETTING].pop(g_id, "Not Found")

@client.event
async def on_member_remove(member):
  if member:
    g_id = str(member.guild.id)
    if member.id in db[DB_SETTING][g_id][Db_Keys.NO_NOTICE_MEMBER]:
      db[DB_SETTING][g_id][Db_Keys.NO_NOTICE_MEMBER].remove(member.id)

@client.event
async def on_autopost_success():
  print(
      f"Posted server count ({client.topggpy.guild_count}), shard count ({client.shard_count})"
  )

keep_alive()
my_secret = os.environ['DISCORD_TOKEN']

try:
  client.run(my_secret)
except discord.errors.HTTPException:
  print("\n\n\nBLOCKED BY RATE LIMITS\nRESTARTING NOW\n\n\n")
  os.system("python restarter.py")
  os.system('kill 1')