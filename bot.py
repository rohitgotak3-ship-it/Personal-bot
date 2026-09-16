import os, asyncio, discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN=os.getenv("DISCORD_TOKEN")
if not TOKEN: raise RuntimeError("DISCORD_TOKEN is missing in .env")

intents=discord.Intents.default()
intents.members=True
intents.message_content=True

bot=commands.Bot(command_prefix="!",intents=intents)

EXTENSIONS=[
 "cogs.dashboard","cogs.panels","cogs.serverinfo",
 "cogs.permissions","cogs.help","cogs.settings"
]

@bot.event
async def on_ready():
    print(f"💎 Logged in as {bot.user} ({bot.user.id})")
    try:
        synced=await bot.tree.sync()
        print(f"✨ Synced {len(synced)} slash commands.")
    except Exception as e:
        print("❌ Sync error:",e)

async def main():
    for ext in EXTENSIONS:
        try:
            await bot.load_extension(ext)
            print("✅ Loaded",ext)
        except Exception as e:
            print("❌ Failed",ext,e)
    await bot.start(TOKEN)

if __name__=="__main__":
    asyncio.run(main())
