import discord
from together import Together
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
TOGETHER_MODEL_NAME = os.getenv("TOGETHER_MODEL_NAME", "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free")
ALLOWED_CHANNEL_ID = int(os.getenv("ALLOWED_CHANNEL_ID", "0"))

if not DISCORD_BOT_TOKEN or not TOGETHER_API_KEY or not ALLOWED_CHANNEL_ID:
    raise ValueError("🚨 Missing required environment variables! Check your .env file.")

os.environ["TOGETHER_API_KEY"] = TOGETHER_API_KEY

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
together_client = Together()

@client.event
async def on_ready():
    print(f"✅ Bot is online as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.channel.id != ALLOWED_CHANNEL_ID:
        print(f"🚫 Ignoring message from unauthorized channel: {message.channel.id}")
        return

    print(f"📩 Received message: '{message.content}' from {message.author}")

    user_input = message.content.strip()
    if not user_input:
        print("🚨 Message was empty after stripping. Ignoring.")
        return

    async def send_long_message(channel, text):
        """Splits long messages into multiple 2000-character chunks and sends them sequentially."""
        chunk_size = 2000
        for i in range(0, len(text), chunk_size):
            await channel.send(text[i:i+chunk_size])

    try:
        response = together_client.chat.completions.create(
            model=TOGETHER_MODEL_NAME,
            messages=[{"role": "user", "content": user_input}],
        )

        print(f"📜 Full API Response: {response}")

        if response and response.choices:
            answer = response.choices[0].message.content.strip()
        else:
            answer = "Sorry, I couldn't generate a response."

        print(f"🤖 Bot Response: {answer}")
        await send_long_message(message.channel, answer)

    except Exception as e:
        error_msg = f"❌ API Error: {str(e)}"
        print(error_msg)
        await send_long_message(message.channel, error_msg)

client.run(DISCORD_BOT_TOKEN)
