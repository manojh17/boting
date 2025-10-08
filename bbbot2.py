# import asyncio
# import json
# import logging
# from pyrogram import Client, filters
# from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# # ----------------------------- CONFIG -----------------------------
# API_ID = 12854871
# API_HASH = "22243531d2908439e7935c1d8c5966e1"
# BOT_TOKEN = "8314102530:AAEFPObpBXhha3WG97B39XMuTKltemx0T-U"
# PRIVATE_CHANNEL_ID = -1002949423579
# CACHE_FILE = "episode_cache.json"
# AUTO_DELETE_SECONDS = 3600  # 1 hour

# # ---------------------------- LOGGING ----------------------------
# logging.basicConfig(
#     format="%(asctime)s - %(levelname)s - %(message)s",
#     level=logging.INFO
# )

# # --------------------------- INITIALIZE --------------------------
# bot = Client("episode_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# # Load existing cache or initialize empty
# try:
#     with open(CACHE_FILE, "r") as f:
#         episode_cache = json.load(f)
# except FileNotFoundError:
#     episode_cache = {}

# # ------------------------ HELPER FUNCTIONS ------------------------
# def save_cache():
#     """Save the current episode cache to a JSON file."""
#     with open(CACHE_FILE, "w") as f:
#         json.dump(episode_cache, f)
#     logging.info("Episode cache saved.")

# def build_episode_buttons():
#     """Build inline keyboard buttons from cached episodes."""
#     if not episode_cache:
#         return None
#     buttons = []
#     for ep_name in sorted(episode_cache.keys()):
#         buttons.append([InlineKeyboardButton(ep_name, callback_data=ep_name)])
#     return InlineKeyboardMarkup(buttons)

# async def auto_delete_message(chat_id, message_id):
#     """Delete a message after a certain delay."""
#     await asyncio.sleep(AUTO_DELETE_SECONDS)
#     try:
#         await bot.delete_messages(chat_id, message_id)
#         logging.info(f"Auto-deleted message {message_id} in chat {chat_id}")
#     except Exception as e:
#         logging.warning(f"Failed to auto-delete message {message_id}: {e}")

# # ------------------------ CHANNEL LISTENER ------------------------
# @bot.on_message(filters.chat(PRIVATE_CHANNEL_ID))
# async def handle_new_episode(client, message):
#     """Listen for new episodes and cache them."""
#     ep_text = message.text or message.caption or ""
#     if "S9EP" in ep_text.upper():
#         # Extract episode name
#         ep_name = next((word for word in ep_text.split() if "S9EP" in word.upper()), None)
#         if ep_name and ep_name not in episode_cache:
#             episode_cache[ep_name] = message.id  # <-- updated for Pyrogram v2+
#             save_cache()
#             logging.info(f"New episode cached: {ep_name} (ID: {message.id})")

# # ------------------------ COMMANDS ------------------------
# @bot.on_message(filters.private & filters.command("start"))
# async def start_command(client, message):
#     """Send episode selection buttons."""
#     buttons = build_episode_buttons()
#     if buttons:
#         await message.reply_text("Select an episode to receive:", reply_markup=buttons)
#     else:
#         await message.reply_text("No episodes available yet. Please wait for new releases.")

# @bot.on_message(filters.private & filters.command("refresh"))
# async def refresh_command(client, message):
#     """Refresh the inline buttons."""
#     buttons = build_episode_buttons()
#     if buttons:
#         await message.reply_text("Episode list refreshed:", reply_markup=buttons)
#     else:
#         await message.reply_text("No episodes available to refresh.")

# # ------------------------ CALLBACK HANDLER ------------------------
# @bot.on_callback_query()
# async def handle_episode_button(client, callback_query):
#     ep_name = callback_query.data
#     user_id = callback_query.from_user.id

#     if ep_name not in episode_cache:
#         await callback_query.answer("Episode not found or expired.", show_alert=True)
#         return

#     try:
#         # Forward the message from private channel
#         forwarded_msg = await bot.forward_messages(
#             chat_id=user_id,
#             from_chat_id=PRIVATE_CHANNEL_ID,
#             message_ids=episode_cache[ep_name]
#         )
#         await callback_query.answer()  # Acknowledge the button click
#         # Auto-delete after 1 hour
#         asyncio.create_task(auto_delete_message(user_id, forwarded_msg.id))  # <-- updated for Pyrogram v2+
#     except Exception as e:
#         logging.error(f"Failed to forward episode {ep_name}: {e}")
#         await callback_query.answer("Failed to send episode.", show_alert=True)

# # ------------------------ RUN BOT ------------------------
# if __name__ == "__main__":
#     logging.info("Bot started. Listening for new episodes...")
#     bot.run()

import asyncio
import json
import logging
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# ----------------------------- CONFIG -----------------------------
API_ID = 12854871
API_HASH = "22243531d2908439e7935c1d8c5966e1"
BOT_TOKEN = "8314102530:AAEFPObpBXhha3WG97B39XMuTKltemx0T-U"
PRIVATE_CHANNEL_ID = -1002949423579
CACHE_FILE = "episode_cache.json"
AUTO_DELETE_SECONDS = 3600  # 1 hour

# ---------------------------- LOGGING ----------------------------
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# --------------------------- INITIALIZE --------------------------
bot = Client("episode_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Load existing cache or initialize empty
try:
    with open(CACHE_FILE, "r") as f:
        episode_cache = json.load(f)
except FileNotFoundError:
    episode_cache = {}

# ------------------------ HELPER FUNCTIONS ------------------------
def save_cache():
    """Save the current episode cache to a JSON file."""
    with open(CACHE_FILE, "w") as f:
        json.dump(episode_cache, f, indent=4)
    logging.info("Episode cache saved.")

def build_episode_buttons():
    """Build inline keyboard buttons from cached episodes."""
    if not episode_cache:
        return None
    buttons = []
    for ep_name in sorted(episode_cache.keys()):
        buttons.append([InlineKeyboardButton(ep_name, callback_data=ep_name)])
    return InlineKeyboardMarkup(buttons)

# ------------------------ CHANNEL LISTENER ------------------------
@bot.on_message(filters.chat(PRIVATE_CHANNEL_ID))
async def handle_new_episode(client, message):
    """Listen for new episodes and cache them."""
    ep_text = message.text or message.caption or ""
    if "S9EP" in ep_text.upper():
        # Extract episode name
        ep_name = next((word for word in ep_text.split() if "S9EP" in word.upper()), None)
        if ep_name:
            # If episode already exists, append the new message ID
            if ep_name in episode_cache:
                if isinstance(episode_cache[ep_name], list):
                    if message.id not in episode_cache[ep_name]:
                        episode_cache[ep_name].append(message.id)
                else:
                    # Convert single value to list
                    episode_cache[ep_name] = [episode_cache[ep_name], message.id]
            else:
                # First message for this episode
                episode_cache[ep_name] = [message.id]

            save_cache()
            logging.info(f"Episode cached: {ep_name} (IDs: {episode_cache[ep_name]})")

# ------------------------ COMMANDS ------------------------
@bot.on_message(filters.private & filters.command("start"))
async def start_command(client, message):
    """Send episode selection buttons."""
    buttons = build_episode_buttons()
    if buttons:
        await message.reply_text("Select an episode to receive:", reply_markup=buttons)
    else:
        await message.reply_text("No episodes available yet. Please wait for new releases.")

@bot.on_message(filters.private & filters.command("refresh"))
async def refresh_command(client, message):
    """Refresh the inline buttons."""
    buttons = build_episode_buttons()
    if buttons:
        await message.reply_text("Episode list refreshed:", reply_markup=buttons)
    else:
        await message.reply_text("No episodes available to refresh.")

# ------------------------ CALLBACK HANDLER ------------------------
@bot.on_callback_query()
async def handle_episode_button(client, callback_query):
    ep_name = callback_query.data
    user_id = callback_query.from_user.id

    if ep_name not in episode_cache:
        await callback_query.answer("Episode not found or expired.", show_alert=True)
        return

    try:
        # Forward the message from private channel
        forwarded_msg = await bot.forward_messages(
            chat_id=user_id,
            from_chat_id=PRIVATE_CHANNEL_ID,
            message_ids=episode_cache[ep_name]
        )
        await callback_query.answer()  # Acknowledge the button click

        # Auto-delete after 1 hour and notify user
        async def delete_and_notify():
            await asyncio.sleep(AUTO_DELETE_SECONDS)
            try:
                await bot.delete_messages(user_id, forwarded_msg.id)
                logging.info(f"Auto-deleted message {forwarded_msg.id} in chat {user_id}")
                # Notify user
                await bot.send_message(user_id, f"⏰ The episode {ep_name} has been deleted after 1 hour.")
            except Exception as e:
                logging.warning(f"Failed to auto-delete message {forwarded_msg.id}: {e}")

        asyncio.create_task(delete_and_notify())

    except Exception as e:
        logging.error(f"Failed to forward episode {ep_name}: {e}")
        await callback_query.answer("Failed to send episode.", show_alert=True)

# ------------------------ RUN BOT ------------------------
if __name__ == "__main__":
    logging.info("Bot started. Listening for new episodes...")
    bot.run()

