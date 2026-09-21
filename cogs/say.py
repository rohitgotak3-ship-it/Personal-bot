import discord
from discord import app_commands
from discord.ext import commands
from .common import has_permission, deny, x

class Say(commands.Cog):
    def __init__(self,bot): self.bot=bot
    @app_commands.command(name="say",description="Send a message through LIGHTNESS")
    @app_commands.describe(message="Message to send",channel="Optional target channel")
    async def say(self,i,message:str,channel:discord.TextChannel|None=None):
        if not has_permission(i.user,"say"): return await deny(i,"say")
        target=channel or i.channel
        await target.send(message)
        await i.response.send_message(f"{x('verify')} {x('diamond')} **MESSAGE SENT**",ephemeral=True)
async def setup(bot): await bot.add_cog(Say(bot))
