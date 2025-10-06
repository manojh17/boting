import asyncio
import json
import logging
import threading
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import aiohttp  # async HTTP client

# ----------------------------- CONFIG -----------------------------
API_ID = 12854871
API_HASH = "22243531d2908439e7935c1d8c5966e1"
BOT_TOKEN = "8314102530:AAEFPObpBXhha3WG97B39XMuTKltemx0T-U"
PRIVATE_CHANNEL_ID = -1002949423579
CACHE_FILE = "episode_cache.json"
AUTO_DELETE_SECONDS = 3600
SELF_PING_INTERVAL = 600
SELF_URL = "https://boting-77os.onrender.com"  # Replace with your Render URL

# ---------------------------- LOGGING ----------------------------
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# --------------------------- FLASK -------------------------------
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is alive! 🚀"

def run_flask():
    app.run(host="0.0.0.0", port=5304)

# --------------------------- PYROGRAM BOT ------------------------
bot = Client(
    "episode_bot",            # session name
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workdir="/tmp"            # Render free-tier writable folder
)


try:
    with open(CACHE_FILE, "r") as f:
        episode_cache = json.load(f)
except FileNotFoundError:
    episode_cache = {}

def save_cache():
    with open(CACHE_FILE, "w") as f:
        json.dump(episode_cache, f)
    logging.info("Episode cache saved.")

def build_episode_buttons():
    if not episode_cache:
        return None
    buttons = [[InlineKeyboardButton(ep, callback_data=ep)] for ep in sorted(episode_cache.keys())]
    return InlineKeyboardMarkup(buttons)

@bot.on_message(filters.chat(PRIVATE_CHANNEL_ID))
async def handle_new_episode(client, message):
    ep_text = message.text or message.caption or ""
    if "S9EP" in ep_text.upper():
        ep_name = next((word for word in ep_text.split() if "S9EP" in word.upper()), None)
        if ep_name and ep_name not in episode_cache:
            episode_cache[ep_name] = message.id
            save_cache()
            logging.info(f"New episode cached: {ep_name} (ID: {message.id})")

@bot.on_message(filters.private & filters.command("start"))
async def start_command(client, message):
    buttons = build_episode_buttons()
    if buttons:
        await message.reply_text("Select an episode to receive:", reply_markup=buttons)
    else:
        await message.reply_text("No episodes available yet. Please wait.")

@bot.on_message(filters.private & filters.command("refresh"))
async def refresh_command(client, message):
    buttons = build_episode_buttons()
    if buttons:
        await message.reply_text("Episode list refreshed:", reply_markup=buttons)
    else:
        await message.reply_text("No episodes available to refresh.")

@bot.on_callback_query()
async def handle_episode_button(client, callback_query):
    ep_name = callback_query.data
    user_id = callback_query.from_user.id

    if ep_name not in episode_cache:
        await callback_query.answer("Episode not found.", show_alert=True)
        return

    try:
        forwarded_msg = await bot.forward_messages(
            chat_id=user_id,
            from_chat_id=PRIVATE_CHANNEL_ID,
            message_ids=episode_cache[ep_name]
        )
        await callback_query.answer()

        async def delete_and_notify():
            await asyncio.sleep(AUTO_DELETE_SECONDS)
            try:
                await bot.delete_messages(user_id, forwarded_msg.id)
                await bot.send_message(user_id, f"⏰ The episode {ep_name} has been deleted after 1 hour.")
            except Exception as e:
                logging.warning(f"Failed to auto-delete message: {e}")

        asyncio.create_task(delete_and_notify())
    except Exception as e:
        logging.error(f"Failed to forward episode {ep_name}: {e}")
        await callback_query.answer("Failed to send episode.", show_alert=True)

# --------------------------- SELF PING ----------------------------
async def keep_alive():
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(SELF_URL) as resp:
                    logging.info(f"Pinged self, status: {resp.status}")
            except Exception as e:
                logging.warning(f"Self-ping failed: {e}")
            await asyncio.sleep(SELF_PING_INTERVAL)

# --------------------------- RUN EVERYTHING ----------------------
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    # Start bot and self-ping tasks
    loop.create_task(bot.start())  # ✅ coroutine
    loop.create_task(keep_alive())  # ✅ coroutine
    logging.info("Bot started and self-ping task running...")

    # Run Flask in separate thread so it doesn't block asyncio loop
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    # Keep asyncio loop alive
    loop.run_forever()
