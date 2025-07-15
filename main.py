import discord
from discord.client import Client
from discord.ext import commands
from discord.ext import tasks
from discord import app_commands
import topgg
import dataclasses
import os
import copy
from replit import db
from constants import DB_SETTING, Db_Keys, Lang, Str_Dict_Keys
from lingual import get_locale
from help import EmbedHelp
from keep_alive import keep_alive

database_keys = Db_Keys()
database_keys = dataclasses.asdict(database_keys)

default_dict = {
  Db_Keys.NO_NOTICE_MEMBER: [],
  Db_Keys.NO_NOTICE_VC: [],
  Db_Keys.ALERT_CHANNEL: {},
  Db_Keys.NAME_NOTICE: True,
  Db_Keys.LANGUAGE: Lang.EN,
}

embed_help = {
  Lang.JP : EmbedHelp(Lang.JP),
  Lang.EN : EmbedHelp(Lang.EN)
}

class MyClient(Client):
  def __init__(self, *, intents: discord.Intents):
    activity = discord.Game(name="/helpnop")
    super().__init__(intents=intents, activity=activity, status=discord.Status.online)
    self.tree = app_commands.CommandTree(self)

  async def setup_hook(self):
    dbl_token = os.environ['DBL_TOKEN']
    self.topggpy = topgg.DBLClient(
      self,
      dbl_token,
      autopost=True,
      post_shard_count=True
    )
    await self.tree.sync()

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
client = MyClient(intents=intents)

@client.event
async def on_voice_state_update(member, before, after):
  g_id = str(member.guild.id)
  g = db[DB_SETTING][g_id]
  if member:
    if str(member.id) not in g[Db_Keys.NO_NOTICE_MEMBER]:
      lang = g[Db_Keys.LANGUAGE]
      name_notice = g[Db_Keys.NAME_NOTICE]

      if (before.channel != after.channel):
        if after.channel:
          # JOIN
          channel = after.channel
          channel_id = str(channel.id)
          if str(member.id) not in g[Db_Keys.NO_NOTICE_MEMBER] and channel_id not in g[Db_Keys.NO_NOTICE_VC]:
            alert_channel = member.guild.system_channel or member.guild.text_channels[0]
            if channel_id in g[Db_Keys.ALERT_CHANNEL]:
              alert_channel_list = [ch for ch in member.guild.text_channels if str(ch.id) == g[Db_Keys.ALERT_CHANNEL][channel_id]]
              if alert_channel_list:
                alert_channel = alert_channel_list[0]
            msg = get_locale(lang, Str_Dict_Keys.ALERT_NAME_JOIN if name_notice else Str_Dict_Keys.ALERT,
                             member.display_name, channel.name, len(channel.members))
            await alert_channel.send(msg)

        elif before.channel:
          # LEAVE
          channel = before.channel
          channel_id = str(channel.id)
          if str(member.id) not in g[Db_Keys.NO_NOTICE_MEMBER] and channel_id not in g[Db_Keys.NO_NOTICE_VC]:
            alert_channel = member.guild.system_channel
            if channel_id in g[Db_Keys.ALERT_CHANNEL]:
              alert_channel_list = [ch for ch in member.guild.text_channels if str(ch.id) == g[Db_Keys.ALERT_CHANNEL][channel_id]]
              if alert_channel_list:
                alert_channel = alert_channel_list[0]
            msg = get_locale(lang, Str_Dict_Keys.ALERT_NAME_LEAVE if name_notice else Str_Dict_Keys.ALERT,
                             member.display_name, channel.name, len(channel.members))
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
  i_user_id = str(interaction.user.id)
  if on_off.value == 'on':
    if i_user_id in g[Db_Keys.NO_NOTICE_MEMBER]:
      db[DB_SETTING][g_id][Db_Keys.NO_NOTICE_MEMBER].remove(i_user_id)
    await interaction.response.send_message(get_locale(lang, Str_Dict_Keys.MY_NOTICE, i_user_id, 'ON'), ephemeral=True)
  elif on_off.value == 'off':
    if i_user_id not in g[Db_Keys.NO_NOTICE_MEMBER]:
      db[DB_SETTING][g_id][Db_Keys.NO_NOTICE_MEMBER].append(i_user_id)
    await interaction.response.send_message(get_locale(lang, Str_Dict_Keys.MY_NOTICE, i_user_id, 'OFF'), ephemeral=True)


@client.tree.command(name="vcnoticenop", description="Select the voice or stage channel to turn notifications on/off.")
@app_commands.choices(on_off=[
  app_commands.Choice(name="On", value="on"),
  app_commands.Choice(name="Off", value="off")
])
async def vc_notice_command(interaction, on_off: app_commands.Choice[str], channel: discord.VoiceChannel | discord.StageChannel):
  g_id = str(interaction.guild_id)
  g = db[DB_SETTING][g_id]
  lang = g[Db_Keys.LANGUAGE]

  if interaction.permissions.administrator:
    if channel:
      channel_id = str(channel.id)
      if on_off.value == 'on':
        if channel_id in g[Db_Keys.NO_NOTICE_VC]:
          db[DB_SETTING][g_id][Db_Keys.NO_NOTICE_VC].remove(channel_id)
        await interaction.response.send_message(get_locale(lang, Str_Dict_Keys.VC_CHANGED, channel.name, 'ON'))
      elif on_off.value == 'off':
        if channel_id not in g[Db_Keys.NO_NOTICE_VC]:
          db[DB_SETTING][g_id][Db_Keys.NO_NOTICE_VC].append(channel_id)
          await interaction.response.send_message(get_locale(lang, Str_Dict_Keys.VC_CHANGED, channel.name, 'OFF'))
    else:
      await interaction.response.send_message(get_locale(lang, Str_Dict_Keys.NO_CHANNEL), ephemeral=True)
  else:
    await interaction.response.send_message(get_locale(lang, Str_Dict_Keys.NO_PERMISSIONS), ephemeral=True)


@client.tree.command(name="sendherenop", description="Notifications of selected VC will be on the text channel where this command is entered.")
async def send_here_command(interaction, vc: str):
  g_id = str(interaction.guild_id)
  lang = db[DB_SETTING][g_id][Db_Keys.LANGUAGE]

  if interaction.permissions.administrator:
    channel_id = str(interaction.channel_id)
    if vc == Str_Dict_Keys.DEFAULT:
      db[DB_SETTING][g_id][Db_Keys.ALERT_CHANNEL].clear()
      db[DB_SETTING][g_id][Db_Keys.ALERT_CHANNEL][Str_Dict_Keys.DEFAULT] = channel_id
      await interaction.response.send_message(get_locale(lang, Str_Dict_Keys.SEND_HERE, get_locale(lang, Str_Dict_Keys.DEFAULT)))
    else:
      db[DB_SETTING][g_id][Db_Keys.ALERT_CHANNEL][vc] = channel_id
      await interaction.response.send_message(get_locale(lang, Str_Dict_Keys.SEND_HERE, get_locale(lang, vc)))

  else:
    await interaction.response.send_message(get_locale(lang, Str_Dict_Keys.NO_PERMISSIONS), ephemeral=True)


@send_here_command.autocomplete("vc")
async def autocomplete_vc(interaction: discord.Interaction, current: str):
    g_id = str(interaction.guild_id)
    lang = db[DB_SETTING][g_id][Db_Keys.LANGUAGE]

    choices = [app_commands.Choice(name=get_locale(lang, Str_Dict_Keys.DEFAULT), value=Str_Dict_Keys.DEFAULT)]

    if interaction.guild:
      vcs = interaction.guild.voice_channels + interaction.guild.stage_channels
      for vc in vcs:
          if current.lower() in vc.name.lower():
              choices.append(app_commands.Choice(name=vc.name, value=str(vc.id)))

    return choices[:25]


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


@client.event
async def on_guild_join(guild):
  db[DB_SETTING][str(guild.id)] = copy.deepcopy(default_dict)

@client.event
async def on_guild_remove(guild):
  if guild:
    g_id = str(guild.id)
    db[DB_SETTING].pop(g_id, "Not Found")

@client.event
async def on_member_remove(member):
  if member:
    g_id = str(member.guild.id)
    member_id = str(member.id)
    if member_id in db[DB_SETTING][g_id][Db_Keys.NO_NOTICE_MEMBER]:
      db[DB_SETTING][g_id][Db_Keys.NO_NOTICE_MEMBER].remove(member_id)

@client.event
async def on_autopost_success():
  print(
      f"Posted server count ({client.topggpy.guild_count}), shard count ({client.shard_count})"
  )

@client.event
async def on_autopost_error(exception):
  print(
    f"Server count error due to {exception}"
  )

async def update_database():
  print("Update started")
  for g in client.guilds:
    g_id = str(g.id)
    if db[DB_SETTING].get(g_id, 'NO') == 'NO':
      print(g_id)
      db[DB_SETTING][g_id] = default_dict
    for key in database_keys.values():
      if db[DB_SETTING][g_id].get(key, 'NO') == 'NO':
        db[DB_SETTING][g_id][key] = default_dict[key]
  print("Database updated")


@tasks.loop(minutes = 10)
async def call_update_database():
  await update_database()

keep_alive()
my_secret = os.environ['DISCORD_TOKEN']

try:
  client.run(my_secret)
except discord.errors.HTTPException:
  print("\n\n\nBLOCKED BY RATE LIMITS\nRESTARTING NOW\n\n\n")
  os.system("python restarter.py")
  os.system('kill 1')