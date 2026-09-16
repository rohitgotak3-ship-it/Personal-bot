import discord
from discord import app_commands
from discord.ext import commands
from .common import has_permission,deny

class Help(commands.Cog):
    def __init__(self,bot): self.bot=bot
    @app_commands.command(name="help",description="❓💎 Premium Help Center")
    async def help(self,i):
        if not has_permission(i.user,"help"): return await deny(i,"help")
        e=discord.Embed(
            title="❓💎 PREMIUM A2Z HELP CENTER",
            description=(
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "🧭 Dashboard — all control panels\n"
                "👋 Welcome — welcome setup\n🚪 Goodbye — goodbye setup\n"
                "🎫 Ticket — ticket setup\n🎁 Giveaway — giveaway setup\n"
                "📢 Announcement — announcement setup\n🏰 Server Info — A2Z server info\n"
                "🛡️ Moderation — protected moderation\n🔐 Permissions — user/role access\n"
                "⚙️ Settings — server settings\n\n"
                "🧪 TEST • 👀 PREVIEW • ✏️ EDIT • 💾 SAVE • 🚀 PUBLISH\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"),
            color=discord.Color.gold())
        await i.response.send_message(embed=e,ephemeral=True)
async def setup(bot): await bot.add_cog(Help(bot))
