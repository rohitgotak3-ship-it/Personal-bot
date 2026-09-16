import discord
from discord import app_commands
from discord.ext import commands
from .common import has_permission, deny

class ServerInfo(commands.Cog):
    def __init__(self, bot): self.bot=bot

    @app_commands.command(name="serverinfo", description="🏰💎 A2Z Server Information")
    async def serverinfo(self, i):
        if not has_permission(i.user,"serverinfo"):
            return await deny(i,"serverinfo")
        g=i.guild
        humans=sum(1 for m in g.members if not m.bot)
        bots=sum(1 for m in g.members if m.bot)
        e=discord.Embed(
            title="🏰💎 A2Z SERVER INFORMATION",
            description="━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n✨ **COMPLETE A2Z SERVER OVERVIEW**\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            color=discord.Color.gold()
        )
        e.add_field(name="👑 SERVER IDENTITY",
            value=f"✨ **Name:** {g.name}\n👑 **Owner:** {g.owner.mention if g.owner else 'Unknown'}\n"
                  f"🆔 **ID:** `{g.id}`\n📅 **Created:** <t:{int(g.created_at.timestamp())}:F>\n"
                  f"⏳ **Age:** <t:{int(g.created_at.timestamp())}:R>",inline=False)
        e.add_field(name="👥 COMMUNITY",
            value=f"👤 **Members:** {g.member_count}\n🧑 **Humans:** {humans}\n🤖 **Bots:** {bots}\n"
                  f"🚀 **Boosts:** {g.premium_subscription_count or 0}\n💎 **Boost Level:** {g.premium_tier}")
        e.add_field(name="📚 STRUCTURE",
            value=f"📂 **Categories:** {sum(isinstance(c,discord.CategoryChannel) for c in g.channels)}\n"
                  f"💬 **Text:** {len(g.text_channels)}\n🔊 **Voice:** {len(g.voice_channels)}\n"
                  f"🎭 **Roles:** {len(g.roles)}\n😀 **Emojis:** {len(g.emojis)}")
        e.add_field(name="🛡️ SECURITY",
            value=f"🔐 **Verification:** {g.verification_level.name.title()}\n"
                  f"⚡ **2FA:** {'Enabled' if g.mfa_level else 'Disabled'}")
        if g.icon: e.set_thumbnail(url=g.icon.url)
        e.set_footer(text="💎 PRO A2Z / LIGHTNESS • A2Z Server Intelligence")
        await i.response.send_message(embed=e)

async def setup(bot): await bot.add_cog(ServerInfo(bot))
