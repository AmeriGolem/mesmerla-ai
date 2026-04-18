import discord
from core.llm import load_model
from text_convo import text_conversation

# ----------------------
# CONFIG
# ----------------------
TOKEN = "YOUR_DISCORD_BOT_TOKEN"  # <--- put your bot token here
PERSONALITY = "Mesmerla"
MODE = "reflective"  # or "concise", "passionate"
VERBOSE = False

# ----------------------
# LOAD MODEL
# ----------------------
model_path = r"C:\Users\aberl\Desktop\Projet Code\Mesmerla_AI\AI-ssistant\models\Nous-Hermes-2-Mistral-7B-DPO.Q4_0.gguf"  # adjust if needed
llm = load_model(model_path)

# ----------------------
# DISCORD CLIENT
# ----------------------
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

client = discord.Client(intents=intents)

# ----------------------
# EVENTS
# ----------------------
@client.event
async def on_ready():
    print(f"✅ Mesmerla is online as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return  # Ignore herself

    # Optional: Only reply if mentioned
    if client.user in message.mentions:
        user_input = message.content.replace(f"<@{client.user.id}>", "").strip()

        reply = text_conversation(
            llm,
            user_input,
            personality=PERSONALITY,
            mode=MODE,
            verbose=VERBOSE
        )

        await message.channel.send(reply)

# ----------------------
# RUN
# ----------------------
client.run(TOKEN)
