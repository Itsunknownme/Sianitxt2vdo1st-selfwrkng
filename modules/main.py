import os
import sys
import asyncio
import requests
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, InputMediaPhoto

from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env

import globals
from html_handler import html_handler
from drm_handler import drm_handler
from text_handler import text_to_txt
from features import register_feature_handlers
from upgrade import register_upgrade_handlers
from commands import register_commands_handlers
from settings import register_settings_handlers
from broadcast import broadcast_handler, broadusers_handler
from authorisation import add_auth_user, list_auth_users, remove_auth_user
from youtube_handler import ytm_handler, y2t_handler, getcookies_handler, cookies_handler

# Load vars from environment
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER = int(os.getenv("OWNER"))
CREDIT = os.getenv("CREDIT", "UploaderBot")
AUTH_USERS = []
TOTAL_USERS = []
cookies_file_path = "cookies.json"

# Initialize bot
bot = Client(
    "bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Register handlers
register_feature_handlers(bot)
register_settings_handlers(bot)
register_upgrade_handlers(bot)
register_commands_handlers(bot)

# ================== START COMMAND ==================
@bot.on_message(filters.command("start"))
async def start(bot, m: Message):
    user_id = m.chat.id
    if user_id not in TOTAL_USERS:
        TOTAL_USERS.append(user_id)

    if m.chat.id in AUTH_USERS:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✨ Commands", callback_data="cmd_command")],
            [InlineKeyboardButton("💎 Features", callback_data="feat_command"), InlineKeyboardButton("⚙️ Settings", callback_data="setttings")],
            [InlineKeyboardButton("💳 Plans", callback_data="upgrade_command")],
        ])
        await bot.send_message(
            chat_id=m.chat.id,
            text=f"🌟 Welcome {m.from_user.first_name}! 🌟\n\nGreat! You are a premium member!\nUse ✨ Commands to get started 🌟",
            reply_markup=keyboard
        )
    else:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✨ Commands", callback_data="cmd_command")],
            [InlineKeyboardButton("💎 Features", callback_data="feat_command"), InlineKeyboardButton("⚙️ Settings", callback_data="setttings")],
            [InlineKeyboardButton("💳 Plans", callback_data="upgrade_command")],
        ])
        await bot.send_message(
            chat_id=m.chat.id,
            text=f"🎉 Welcome {m.from_user.first_name} to DRM Bot! 🎉\n\n"
                 f"You are currently using the free version. 🆓\n\n"
                 f"I'm here to make your life easier by downloading videos from your .txt file 📄 and uploading them directly to Telegram!\n\n"
                 f"Want to get started? Press /id",
            reply_markup=keyboard
        )

# ================== BACK TO MAIN MENU ==================
@bot.on_callback_query(filters.regex("back_to_main_menu"))
async def back_to_main_menu(client, callback_query):
    user_id = callback_query.from_user.id
    first_name = callback_query.from_user.first_name
    caption = f"✨ Welcome [{first_name}](tg://user?id={user_id}) in My uploader bot"
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✨ Commands", callback_data="cmd_command")],
        [InlineKeyboardButton("💎 Features", callback_data="feat_command"), InlineKeyboardButton("⚙️ Settings", callback_data="setttings")],
        [InlineKeyboardButton("💳 Plans", callback_data="upgrade_command")],
    ])
    await callback_query.message.edit_media(
        InputMediaPhoto(media="https://envs.sh/GVI.jpg", caption=caption),
        reply_markup=keyboard
    )
    await callback_query.answer()

# ================== ID COMMAND ==================
@bot.on_message(filters.command(["id"]))
async def id_command(client, message: Message):
    chat_id = message.chat.id
    text = f"<b>The ID of this chat is:</b>\n{chat_id}"
    await message.reply_text(text)

# ================== INFO COMMAND ==================
@bot.on_message(filters.private & filters.command(["info"]))
async def info(bot: Client, update: Message):
    text = (
        f"╭────────────────╮\n"
        f"│✨ Your Telegram Info✨ \n"
        f"├────────────────\n"
        f"├🔹Name : {update.from_user.first_name} {update.from_user.last_name if update.from_user.last_name else 'None'}\n"
        f"├🔹User ID : @{update.from_user.username}\n"
        f"├🔹TG ID : {update.from_user.id}\n"
        f"├🔹Profile : {update.from_user.mention}\n"
        f"╰────────────────╯"
    )
    await update.reply_text(text=text, disable_web_page_preview=True)

# ================== LOGS COMMAND ==================
@bot.on_message(filters.command(["logs"]))
async def send_logs(client: Client, m: Message):
    try:
        with open("logs.txt", "rb") as file:
            sent = await m.reply_text("📤 Sending you....")
            await m.reply_document(document=file)
            await sent.delete()
    except Exception as e:
        await m.reply_text(f"Error sending logs:\n<blockquote>{e}</blockquote>")

# ================== RESET BOT ==================
@bot.on_message(filters.command(["reset"]))
async def restart_handler(_, m):
    if m.chat.id != OWNER:
        return
    await m.reply_text("Bot is resetting...")
    os.execl(sys.executable, sys.executable, *sys.argv)

# ================== STOP COMMAND ==================
@bot.on_message(filters.command("stop") & filters.private)
async def cancel_handler(client: Client, m: Message):
    if m.chat.id not in AUTH_USERS:
        await bot.send_message(
            m.chat.id, 
            f"<b>Oopss! You are not a Premium member</b>\n"
            f"Use /upgrade to get your plan."
        )
    else:
        if globals.processing_request:
            globals.cancel_requested = True
            await m.delete()
            cancel_message = await m.reply_text("🚦 Process cancel request received. Stopping after current process...")
            await asyncio.sleep(30)
            await cancel_message.delete()
        else:
            await m.reply_text("⚡ No active process to cancel.")

# ================== AUTH COMMANDS ==================
@bot.on_message(filters.command("addauth") & filters.private)
async def call_add_auth_user(client: Client, message: Message):
    await add_auth_user(client, message)

@bot.on_message(filters.command("users") & filters.private)
async def call_list_auth_users(client: Client, message: Message):
    await list_auth_users(client, message)

@bot.on_message(filters.command("rmauth") & filters.private)
async def call_remove_auth_user(client: Client, message: Message):
    await remove_auth_user(client, message)

# ================== BROADCAST COMMANDS ==================
@bot.on_message(filters.command("broadcast") & filters.private)
async def call_broadcast_handler(client: Client, message: Message):
    await broadcast_handler(client, message)

@bot.on_message(filters.command("broadusers") & filters.private)
async def call_broadusers_handler(client: Client, message: Message):
    await broadusers_handler(client, message)

# ================== YOUTUBE & FILE HANDLERS ==================
@bot.on_message(filters.command("cookies") & filters.private)
async def call_cookies_handler(client: Client, m: Message):
    await cookies_handler(client, m)

@bot.on_message(filters.command(["t2t"]))
async def call_text_to_txt(bot: Client, m: Message):
    await text_to_txt(bot, m)

@bot.on_message(filters.command(["y2t"]))
async def call_y2t_handler(bot: Client, m: Message):
    await y2t_handler(bot, m)

@bot.on_message(filters.command(["ytm"]))
async def call_ytm_handler(bot: Client, m: Message):
    await ytm_handler(bot, m)

@bot.on_message(filters.command("getcookies") & filters.private)
async def call_getcookies_handler(client: Client, m: Message):
    await getcookies_handler(client, m)

@bot.on_message(filters.command(["t2h"]))
async def call_html_handler(bot: Client, message: Message):
    await html_handler(bot, message)

@bot.on_message(filters.private & (filters.document | filters.text))
async def call_drm_handler(bot: Client, m: Message):
    await drm_handler(bot, m)
    
@bot.on_message(filters.command(["h2t"]))
async def call_html_to_txt_handler(bot: Client, message: Message):
    # This calls the new function defined in html_handler.py
    await html_to_txt_handler(bot, message) 
# --- END NEW H2T HANDLER ---
    
#.....,.....,.......,...,.......,.....,.....,.....,.......,...,.......,.....,
@bot.on_message(filters.private & (filters.document | filters.text))
async def call_drm_handler(bot: Client, m: Message):
    await drm_handler(bot, m)

from pyrogram import filters
from html_handler import html_to_txt_handler

app = Client("my_bot")  # adjust to your session

# Command: reply to an HTML file with /h2t
@app.on_message(filters.command("h2t") & filters.reply)
async def _h2t(client, message):
    await html_to_txt_handler(client, message)



# ================== BOT COMMANDS ==================
def reset_and_set_commands():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setMyCommands"
    commands = [
        {"command": "start", "description": "✅ Check Alive the Bot"},
        {"command": "stop", "description": "🚫 Stop the ongoing process"},
        {"command": "id", "description": "🆔 Get Your ID"},
        {"command": "info", "description": "ℹ️ Check Your Information"},
        {"command": "cookies", "description": "📁 Upload YT Cookies"},
        {"command": "y2t", "description": "🔪 YouTube → .txt Converter"},
        {"command": "ytm", "description": "🎶 YouTube → .mp3 downloader"},
        {"command": "t2t", "description": "📟 Text → .txt Generator"},
        {"command": "t2h", "description": "🌐 .txt → .html Converter"},
        {"command": "h2t", "description": "🦥 .html → .txt Converter"},
        {"command": "logs", "description": "👁️ View Bot Activity"},
        {"command": "broadcast", "description": "📢 Broadcast to All Users"},
        {"command": "broadusers", "description": "👨‍❤️‍👨 All Broadcasting Users"},
        {"command": "addauth", "description": "▶️ Add Authorisation"},
        {"command": "rmauth", "description": "⏸️ Remove Authorisation "},
        {"command": "users", "description": "👨‍👨‍👧‍👦 All Premium Users"},
        {"command": "reset", "description": "✅ Reset the Bot"}
    ]
    requests.post(url, json={"commands": commands})

# ================== START BOT ==================
if __name__ == "__main__":
    # 1. Set commands (uses 'requests' library)
    reset_and_set_commands()
    
    # 2. FIX: Send the startup notification directly using 'requests'
    # This replaces the undefined 'notify_owner()' call.
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": OWNER,
        "text": "✅ Bot has successfully started!\nOwner ID: `{}`".format(OWNER)
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        # Fails silently if Telegram API is unreachable, but allows bot to start
        print(f"Warning: Failed to send startup notification via requests: {e}")
        
    # 3. Start the bot (Blocking call that runs forever)
    bot.run()

