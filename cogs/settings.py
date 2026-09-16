import discord
from discord import app_commands
from discord.ext import commands
from .common import has_permission,deny,load_data

class Settings(commands.Cog):
    def __init__(self,bot): self.bot=bot
    @app_commands.command(name="settings",description="⚙️💎 Server Settings")
    async def settings(self,i):
        if not has_permission(i.user,"settings"): return await deny(i,"settings")
        d=load_data().get(str(i.guild.id),{})
        e=discord.Embed(
            title="⚙️💎 A2Z SERVER SETTINGS",
            description=f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n💾 Persistent server configuration\n"
                        f"📦 **Configured features:** {len(d.get('settings',{}))}\n"
                        "💎 Custom emoji mapping supported in `data/settings.json`.\n"
                        "🔐 Permission data is stored per server.\n"
                        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            color=discord.Color.gold())
        await i.response.send_message(embed=e,ephemeral=True)
async def setup(bot): await bot.add_cog(Settings(bot))
