import discord
from discord.client import Client
from discord.ext import commands
from discord.ext import tasks
from discord import app_commands
import topgg
import dataclasses
import os
import sys
import psycopg2
from constants import DB_SETTING, Db_Keys, Str_Dict_Keys, Lang, On_Off
from lingual import get_locale
from help import EmbedHelp
from bean import Bean
from database import Database

database_keys = Db_Keys()
database_keys = dataclasses.asdict(database_keys)

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
  await update_database(g_id)

  try:
    g = Database.select(g_id)

    if member:
      if str(member.id) not in g[Db_Keys.NO_NOTICE_MEMBER]:
        lang = g[Db_Keys.LANGUAGE]
        name_notice = g[Db_Keys.NAME_NOTICE]

        if (before.channel != after.channel):
          if after.channel:
            # JOIN
            channel = after.channel
            key = Str_Dict_Keys.ALERT_NAME_JOIN

          else:
            # LEAVE
            channel = before.channel
            key = Str_Dict_Keys.ALERT_NAME_LEAVE
            
          channel_id = str(channel.id)

          if (str(member.id) not in g[Db_Keys.NO_NOTICE_MEMBER]) and (channel_id not in g[Db_Keys.NO_NOTICE_VC]):
            if channel_id in g[Db_Keys.ALERT_CHANNEL]:
              text_id = g[Db_Keys.ALERT_CHANNEL][channel_id]

            elif Str_Dict_Keys.DEFAULT in g[Db_Keys.ALERT_CHANNEL]:
              text_id = g[Db_Keys.ALERT_CHANNEL][Str_Dict_Keys.DEFAULT]
            
            else:
              text_id = ""

            alert_channel_list = [ch for ch in member.guild.text_channels if str(ch.id) == text_id]
            
            if alert_channel_list:
              alert_channel = alert_channel_list[0]
            else:
              alert_channel = member.guild.system_channel or member.guild.text_channels[0]

            msg = get_locale(lang, key if name_notice else Str_Dict_Keys.ALERT,
              member.display_name, channel.name, len(channel.members))
            await alert_channel.send(msg)

  except psycopg2.DatabaseError as e:
    print("on_voice_state_update", e)

@client.tree.command(name="mynoticenop", description="Turn on/off notifications about your entry and exit.")
@app_commands.choices(on_off=[
  app_commands.Choice(name=On_Off.On, value=On_Off.On),
  app_commands.Choice(name=On_Off.Off, value=On_Off.Off)
])
async def my_notice_command(interaction, on_off: app_commands.Choice[str]):
  g_id = str(interaction.guild_id)
  await update_database(g_id)

  try:
    g = Database.select(g_id)

    lang = g[Db_Keys.LANGUAGE]
    i_user_id = str(interaction.user.id)
    if on_off.value == On_Off.On:
      if i_user_id in g[Db_Keys.NO_NOTICE_MEMBER]:
        g[Db_Keys.NO_NOTICE_MEMBER].remove(i_user_id)
        Database.update(g_id, Db_Keys.NO_NOTICE_MEMBER, g[Db_Keys.NO_NOTICE_MEMBER])

      await interaction.response.send_message(get_locale(lang, Str_Dict_Keys.MY_NOTICE, i_user_id, On_Off.On), ephemeral=True)

    elif on_off.value == On_Off.Off:
      if i_user_id not in g[Db_Keys.NO_NOTICE_MEMBER]:
        g[Db_Keys.NO_NOTICE_MEMBER].append(i_user_id)
        Database.update(g_id, Db_Keys.NO_NOTICE_MEMBER, g[Db_Keys.NO_NOTICE_MEMBER])

      await interaction.response.send_message(get_locale(lang, Str_Dict_Keys.MY_NOTICE, i_user_id, On_Off.Off), ephemeral=True)
  
  except psycopg2.DatabaseError as e:
    print("my_notice_command", e)


@client.tree.command(name="vcnoticenop", description="Select the voice or stage channel to turn notifications on/off.")
@app_commands.choices(on_off=[
  app_commands.Choice(name=On_Off.On, value=On_Off.On),
  app_commands.Choice(name=On_Off.Off, value=On_Off.Off)
])
async def vc_notice_command(interaction, on_off: app_commands.Choice[str], channel: discord.VoiceChannel | discord.StageChannel):
  g_id = str(interaction.guild_id)
  await update_database(g_id)
  
  try:
    g = Database.select(g_id)
    lang = g[Db_Keys.LANGUAGE]

    if interaction.permissions.administrator:
      if channel:
        channel_id = str(channel.id)
        if on_off.value == On_Off.On:
          if channel_id in g[Db_Keys.NO_NOTICE_VC]:
            g[Db_Keys.NO_NOTICE_VC].remove(channel_id)
            Database.update(g_id, Db_Keys.NO_NOTICE_VC, g[Db_Keys.NO_NOTICE_VC])

          await interaction.response.send_message(get_locale(lang, Str_Dict_Keys.VC_CHANGED, channel.name, On_Off.On))

        elif on_off.value == On_Off.Off:
          if channel_id not in g[Db_Keys.NO_NOTICE_VC]:
            g[Db_Keys.NO_NOTICE_VC].append(channel_id)
            Database.update(g_id, Db_Keys.NO_NOTICE_VC, g[Db_Keys.NO_NOTICE_VC])

          await interaction.response.send_message(get_locale(lang, Str_Dict_Keys.VC_CHANGED, channel.name, On_Off.Off))
      else:
        await interaction.response.send_message(get_locale(lang, Str_Dict_Keys.NO_CHANNEL), ephemeral=True)
    else:
      await interaction.response.send_message(get_locale(lang, Str_Dict_Keys.NO_PERMISSIONS), ephemeral=True)
      
  except psycopg2.DatabaseError as e:
    print("vc_notice_command", e)

@client.tree.command(name="sendherenop", description="Notifications of selected VC will be on the text channel where this command is entered.")
async def send_here_command(interaction, vc: str):
  g_id = str(interaction.guild_id)
  await update_database(g_id)
  
  try:
    g = Database.select(g_id)

    lang = g[Db_Keys.LANGUAGE]

    if interaction.permissions.administrator:
      channel_id = str(interaction.channel_id)
      text_name = get_locale(lang, Str_Dict_Keys.BRACKET, interaction.channel.name)

      if vc in [Str_Dict_Keys.ALL, Str_Dict_Keys.DEFAULT]:
        if vc == Str_Dict_Keys.ALL:
          g[Db_Keys.ALERT_CHANNEL].clear()

        g[Db_Keys.ALERT_CHANNEL][Str_Dict_Keys.DEFAULT] = channel_id

        await interaction.response.send_message(get_locale(lang, Str_Dict_Keys.SEND_HERE, get_locale(lang, vc), text_name))

      else:
        g[Db_Keys.ALERT_CHANNEL][vc] = channel_id
        Database.update(g_id, Db_Keys.ALERT_CHANNEL, g[Db_Keys.ALERT_CHANNEL])

        ch_name = get_locale(lang, Str_Dict_Keys.BRACKET, interaction.guild.get_channel(int(vc)).name)

        await interaction.response.send_message(get_locale(lang, Str_Dict_Keys.SEND_HERE, ch_name, text_name))

    else:
      await interaction.response.send_message(get_locale(lang, Str_Dict_Keys.NO_PERMISSIONS), ephemeral=True)

  except psycopg2.DatabaseError as e:
    print("send_here_command", e)


@send_here_command.autocomplete("vc")
async def autocomplete_vc(interaction: discord.Interaction, current: str):
  g_id = str(interaction.guild_id)

  await update_database(g_id)
  
  choices = []

  try:
    g = Database.select(g_id)
    lang = g[Db_Keys.LANGUAGE]
    choices = [
      app_commands.Choice(name=get_locale(lang, Str_Dict_Keys.ALL), value=Str_Dict_Keys.ALL),
      app_commands.Choice(name=get_locale(lang, Str_Dict_Keys.DEFAULT), value=Str_Dict_Keys.DEFAULT)
    ]

    if interaction.guild:
      vcs = interaction.guild.voice_channels + interaction.guild.stage_channels

      for vc in vcs:
        if current.lower() in vc.name.lower():
          choices.append(app_commands.Choice(name=vc.name, value=str(vc.id)))

  except psycopg2.DatabaseError as e:
    print("autocomplete_vc", e)

  return choices[:25]

@client.tree.command(name="notifynamenop", description="Turn display of user names in notifications on/off.")
@app_commands.choices(display_name=[
  app_commands.Choice(name=On_Off.On, value=On_Off.On),
  app_commands.Choice(name=On_Off.Off, value=On_Off.Off)
])
async def notice_type_command(interaction, display_name: app_commands.Choice[str]):
  g_id = str(interaction.guild_id)
  await update_database(g_id)

  try:
    g = Database.select(g_id)

    lang = g[Db_Keys.LANGUAGE]
    if interaction.permissions.administrator:
      if display_name.value == On_Off.On:
        g[Db_Keys.NAME_NOTICE] = True
        Database.update(g_id, Db_Keys.NAME_NOTICE, g[Db_Keys.NAME_NOTICE])

        await interaction.response.send_message(get_locale(lang, Str_Dict_Keys.NOTICE_TYPE_CHANGED, On_Off.On))
      elif display_name.value == On_Off.Off:
        g[Db_Keys.NAME_NOTICE] = False
        Database.update(g_id, Db_Keys.NAME_NOTICE, g[Db_Keys.NAME_NOTICE])

        await interaction.response.send_message(get_locale(lang, Str_Dict_Keys.NOTICE_TYPE_CHANGED, On_Off.Off))
    else:
      await interaction.response.send_message(get_locale(lang, Str_Dict_Keys.NO_PERMISSIONS), ephemeral=True)
  except psycopg2.DatabaseError as e:
    print("notice_type_command", e)

@client.tree.command(name="langnop", description="Switch languages.")
@app_commands.choices(language=[
  app_commands.Choice(name="日本語", value=Lang.JP),
  app_commands.Choice(name="English", value=Lang.EN)
])
async def lang_command(interaction, language: app_commands.Choice[str]):
  g_id = str(interaction.guild_id)
  await update_database(g_id)

  try:
    g = Database.select(g_id)
    
    if interaction.permissions.administrator:
      g[Db_Keys.LANGUAGE] = language.value
      Database.update(g_id, Db_Keys.LANGUAGE, g[Db_Keys.LANGUAGE])

      await interaction.response.send_message(get_locale(language.value, Str_Dict_Keys.LANG_CHANGED, interaction.channel.name))
    
    else:
      await interaction.response.send_message(get_locale(g[Db_Keys.LANGUAGE], Str_Dict_Keys.NO_PERMISSIONS), ephemeral=True)
  except psycopg2.DatabaseError as e:
    print("lang_command", e)

@client.tree.command(name="helpnop", description="Display help.")
async def help_command(interaction):
  g_id = str(interaction.guild_id)
  await update_database(g_id)

  try:
    lang = Database.select(g_id)[Db_Keys.LANGUAGE]

    await interaction.response.send_message(embed=EmbedHelp(lang), ephemeral=True)
  except psycopg2.DatabaseError as e:
    print("help_command", e)

@client.event
async def on_guild_join(guild):
  try:
    Database.insert(Bean(str(guild.id)))
  except psycopg2.DatabaseError as e:
    print("on_guild_join", e)

@client.event
async def on_guild_remove(guild):
  if guild:
    g_id = str(guild.id)
    try:
      Database.delete(g_id)
    except psycopg2.DatabaseError as e:
      print("on_guild_remove", e)

@client.event
async def on_member_remove(member):
  if member:
    g_id = str(member.guild.id)
    await update_database(g_id)

    try:
      g = Database.select(g_id)

      member_id = str(member.id)
      if member_id in g[Db_Keys.NO_NOTICE_MEMBER]:
        g[Db_Keys.NO_NOTICE_MEMBER].remove(member_id)

        Database.update(g_id, Db_Keys.NO_NOTICE_MEMBER, g[Db_Keys.NO_NOTICE_MEMBER])
    except psycopg2.DatabaseError as e:
      print("on_member_remove", e)


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

async def update_database(g_id):
  if not Database.select(g_id):
    Database.insert(Bean(g_id))

# @tasks.loop(minutes = 10)
# async def call_update_database():
#   print("Update started")

#   for g in client.guilds:
#     g_id = str(g.id)
#     await update_database(g_id)

#   print("Database updated")

my_secret = os.environ['DISCORD_TOKEN']

client.run(my_secret)