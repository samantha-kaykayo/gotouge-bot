
import random
import discord
import datetime
from discord.ext import tasks
from bot.core import quotes_col, channels_col, db

@tasks.loop(minutes=1)
async def daily_loop(bot):
    now = datetime.datetime.utcnow().strftime("%H:%M")
    settings = db['settings'].find_one({"_id": "global_settings"})
    scheduled_time = settings.get("daily_time") if settings else None

    if scheduled_time == now:
        await send_daily_quote(bot)

async def send_daily_quote(bot):
    try:
        quotes = list(quotes_col.find())
        if not quotes:
            print("No quotes found.")
            return

        quote = random.choice(quotes)
        settings = db['settings'].find_one({"_id": "global_settings"})
        fallback_image = settings.get("fallback_image") if settings else None
        image_url = quote.get("image") or fallback_image

        embed = discord.Embed(
            title="🌸 Quote of the Day",
            description=quote["text"],
            color=discord.Color.pink()
        )

        if image_url:
            embed.set_thumbnail(url=image_url)

        channels = list(channels_col.find())
        if not channels:
            print("No channels configured.")
            return

        for ch in channels:
            channel = bot.get_channel(ch["channel_id"])
            if channel:
                await channel.send(embed=embed)
            else:
                print(f"Channel ID {ch['channel_id']} not found.")

    except Exception as e:
        print(f"Error sending daily quote: {e}")

def start_daily_loop(bot):
    if not daily_loop.is_running():
        daily_loop.start(bot)
