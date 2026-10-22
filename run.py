from bot.discord_bot import start_discord_bot
from web.routes import start_flask_server
import threading

threading.Thread(target=start_flask_server).start()
start_discord_bot()