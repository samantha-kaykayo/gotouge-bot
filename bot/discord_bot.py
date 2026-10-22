
import discord
from discord import app_commands
from discord.ext.commands import Bot
import os
from bot.core import bot, quotes_col, channels_col, db
from .roles import has_role
from bot.scheduler import send_daily_quote, start_daily_loop
import random

tree = bot.tree

TOS_LINK = "https://docs.google.com/document/d/1yCpt6N_FHItkYI6aNMNURUIbe_uyIywIs7Sxk1CXAfM/edit?usp=sharing"
PRIVACY_LINK = "https://docs.google.com/document/d/1BBAK0UjKXDbxpWLAHZ2GHGL2HBs9vx6obMRLM-qXFR8/edit?usp=sharing"

@bot.event
async def on_ready():
    await tree.sync()
    print(f"Bot connected as {bot.user}")
    start_daily_loop(bot)

@tree.command(name="addquote")
@app_commands.describe(text="Quote", image="Image URL")
async def addquote(interaction: discord.Interaction, text: str, image: str = None):
    if not await has_role(interaction):
        await interaction.response.send_message("No permission.", ephemeral=True)
        return
    quotes_col.insert_one({"text": text, "image": image})
    await interaction.response.send_message("✅ Quote added.")

@tree.command(name="settime")
@app_commands.describe(time="Format HH:MM in 24-hour UTC time")
async def settime(interaction: discord.Interaction, time: str):
    if not await has_role(interaction):
        await interaction.response.send_message("No permission.", ephemeral=True)
        return

    try:
        hour, minute = map(int, time.split(":"))
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError

        db['settings'].update_one(
            {"_id": "global_settings"},
            {"$set": {"daily_time": f"{hour:02}:{minute:02}"}},
            upsert=True
        )

        await interaction.response.send_message(f"⏰ Daily quote time set to {hour:02}:{minute:02} UTC!")

    except Exception:
        await interaction.response.send_message("❌ Invalid time format. Please use HH:MM (24-hour UTC).", ephemeral=True)

@tree.command(name="addchannel")
@app_commands.describe(channel="Select the channel to add")
async def addchannel(interaction: discord.Interaction, channel: discord.TextChannel):
    if not await has_role(interaction):
        await interaction.response.send_message("No permission.", ephemeral=True)
        return
    channels_col.update_one(
        {"channel_id": channel.id},
        {"$set": {"channel_id": channel.id}},
        upsert=True
    )
    await interaction.response.send_message(f"✅ {channel.mention} has been added for daily quotes!")

@tree.command(name="removechannel")
@app_commands.describe(channel="Select the channel to remove")
async def removechannel(interaction: discord.Interaction, channel: discord.TextChannel):
    if not await has_role(interaction):
        await interaction.response.send_message("No permission.", ephemeral=True)
        return
    result = channels_col.delete_one({"channel_id": channel.id})
    if result.deleted_count > 0:
        await interaction.response.send_message(f"🗑️ {channel.mention} removed from daily quotes.")
    else:
        await interaction.response.send_message(f"⚠️ {channel.mention} was not registered.")

@tree.command(name="listchannels")
async def listchannels(interaction: discord.Interaction):
    if not await has_role(interaction):
        await interaction.response.send_message("No permission.", ephemeral=True)
        return
    channels = list(channels_col.find())
    if not channels:
        await interaction.response.send_message("❌ No channels have been added yet.", ephemeral=True)
        return
    mentions = []
    for ch in channels:
        chan = interaction.guild.get_channel(ch["channel_id"])
        if chan:
            mentions.append(chan.mention)
        else:
            mentions.append(f"Missing channel ID: {ch['channel_id']}")
    await interaction.response.send_message("\n".join(mentions), ephemeral=True)

@tree.command(name="tos")
async def tos(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📜 Terms of Service",
        description=f"View our Terms of Service [here]({TOS_LINK}).",
        color=0x00BFFF
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="privacy")
async def privacy(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🔒 Privacy Policy",
        description=f"View our Privacy Policy [here]({PRIVACY_LINK}).",
        color=0x00BFFF
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="testsend")
async def testsend(interaction: discord.Interaction):
    if not await has_role(interaction):
        await interaction.response.send_message("No permission.", ephemeral=True)
        return
    await send_daily_quote()
    await interaction.response.send_message("✅ Test quote sent.")

@tree.command(name="viewtime")
async def viewtime(interaction: discord.Interaction):
    if not await has_role(interaction):
        await interaction.response.send_message("No permission.", ephemeral=True)
        return
    settings = db['settings'].find_one({"_id": "global_settings"})
    if settings and settings.get("daily_time"):
        await interaction.response.send_message(f"📆 Daily quote time is set to **{settings['daily_time']} UTC**", ephemeral=True)
    else:
        await interaction.response.send_message("⚠️ No daily time has been set yet.", ephemeral=True)

def start_discord_bot():
    bot.run(os.getenv("DISCORD_TOKEN"))
