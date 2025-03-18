import discord
from together import Together
import os
from dotenv import load_dotenv
import json

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
TOGETHER_MODEL_NAME = os.getenv("TOGETHER_MODEL_NAME", "your_ai_model")

ALLOWED_CHANNELS = [your_channel_id_here]

if not DISCORD_BOT_TOKEN or not TOGETHER_API_KEY:
    raise ValueError("🚨 Missing required environment variables! Check your .env file.")

os.environ["TOGETHER_API_KEY"] = TOGETHER_API_KEY

CHAT_HISTORY_FILE = "chat_history.json"
CHAT_HISTORY_BACKUP_FILE = "chat_history_backup.json"

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
together_client = Together()

TOKEN_LIMIT = 8193

def count_tokens(text):
    return len(text.split())

def get_max_new_tokens(history):
    total_input_tokens = sum(count_tokens(msg["content"]) for msg in history)
    max_allowed_tokens = TOKEN_LIMIT - total_input_tokens
    return max(100, min(max_allowed_tokens, 1024))

def truncate_history(history):
    total_tokens = sum(count_tokens(msg["content"]) for msg in history)
    
    while total_tokens > (TOKEN_LIMIT - 100) and len(history) > 1:
        removed = history.pop(0)
        total_tokens -= count_tokens(removed["content"])
    
    return history

def load_chat_history():
    if not os.path.exists(CHAT_HISTORY_FILE):
        return []
    with open(CHAT_HISTORY_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)
        if isinstance(data, list):
            return data
        else:
            return []

def save_chat_history(history):
    with open(CHAT_HISTORY_FILE, "w", encoding="utf-8") as file:
        json.dump(history, file, indent=4, ensure_ascii=False)

def load_chat_history_backup():
    if not os.path.exists(CHAT_HISTORY_BACKUP_FILE):
        return []  # Return empty list if backup doesn't exist
    with open(CHAT_HISTORY_BACKUP_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)
        if isinstance(data, list):
            return data
        else:
            return []

def append_chat_history_backup(history):
    """Append new history to the backup file."""
    current_backup = load_chat_history_backup()
    current_backup.extend(history)
    with open(CHAT_HISTORY_BACKUP_FILE, "w", encoding="utf-8") as file:
        json.dump(current_backup, file, indent=4, ensure_ascii=False)

chat_history = load_chat_history()

@client.event
async def on_ready():
    print(f"✅ Bot is online as {client.user}")
    print(f"🔹 Allowed Channels: {ALLOWED_CHANNELS}")
    await client.change_presence(status=discord.Status.online, activity=discord.Game("Playing ! command"))

@client.event
async def on_message(message):
    global chat_history

    if message.author == client.user:
        return

    channel_id = message.channel.id
    print(f"📩 Received message in {channel_id}: {message.content}")

    if channel_id not in ALLOWED_CHANNELS:
        print(f"❌ Ignored message from {channel_id} (Not in allowed channels: {ALLOWED_CHANNELS})")
        return

    if message.content.strip().lower() == "!clean":
        if message.author.guild_permissions.administrator:
            chat_history.clear()
            save_chat_history(chat_history)
            await message.channel.send("✅ Chat history has been cleared.")
        else:
            await message.channel.send("❌ You do not have permission to use this command.")
        return

    if message.content.strip().lower() == "!restore":
        backup_history = load_chat_history_backup()
        if backup_history:
            chat_history = backup_history
            save_chat_history(chat_history)
            await message.channel.send("✅ Chat history has been restored.")
        else:
            await message.channel.send("❌ No backup found to restore history.")
        return
    
    if message.content.strip().lower() == "!save":
        append_chat_history_backup(chat_history)
        await message.channel.send("✅ Chat history has been saved as a backup.")

    print(f"✅ Processing message in allowed channel {channel_id}")

    user_input = message.content.strip()
    if not user_input:
        return

    append_chat_history_backup(chat_history)

    chat_history.append({"role": "user", "content": user_input})

    chat_history = truncate_history(chat_history)

    max_tokens = get_max_new_tokens(chat_history)

    if max_tokens < 100:
        await message.channel.send("⚠️ Not enough token space left for response. Try a shorter message.")
        return

    try:
        response = together_client.chat.completions.create(
            model=TOGETHER_MODEL_NAME,
            messages=chat_history,
            max_tokens=max_tokens,
        )

        if response and response.choices:
            answer = response.choices[0].message.content.strip()
        else:
            answer = "⚠️ I couldn't generate a response. Try again."

        chat_history.append({"role": "assistant", "content": answer})
        save_chat_history(chat_history)

        await message.channel.send(answer)

    except Exception as e:
        print(f"❌ API Error: {str(e)}")
        await message.channel.send(f"❌ API Error: {str(e)}")

client.run(DISCORD_BOT_TOKEN)