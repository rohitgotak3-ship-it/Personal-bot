import discord
from discord import app_commands
from discord.ext import commands
from .common import has_permission, deny, get_custom_emoji, ProtectedView

FEATURES = [
    ("welcome","👋","Welcome"),
    ("goodbye","🚪","Goodbye"),
    ("ticket","🎫","Ticket"),
    ("giveaway","🎁","Giveaway"),
    ("announcement","📢","Announcement"),
    ("serverinfo","🏰","Server Info"),
    ("moderation","🛡️","Moderation"),
    ("permissions","🔐","Permissions"),
    ("help","❓","Help"),
    ("settings","⚙️","Settings")
]

class Select(discord.ui.Select):
    def __init__(self):
        super().__init__(
            placeholder="💎✨ Select a dashboard...",
            options=[discord.SelectOption(label=l, value=k, emoji=e)
                     for k,e,l in FEATURES]
        )
    async def callback(self, interaction):
        k = self.values[0]
        if not has_permission(interaction.user, k):
            return await deny(interaction, k)
        await interaction.response.send_message(
            f"💎✨ **{k.title()} Dashboard** unlocked!\n"
            f"Use `/{k}` to open its dedicated control panel.",
            ephemeral=True
        )

class View(ProtectedView):
    def __init__(self):
        super().__init__("dashboard")
        self.add_item(Select())

class Dashboard(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="dashboard", description="💎🧭 Open PRO A2Z Control Center")
    async def dashboard(self, interaction):
        if not has_permission(interaction.user, "dashboard"):
            return await deny(interaction, "dashboard")
        g = interaction.guild
        e = discord.Embed(
            title=f"{get_custom_emoji(g,'diamond')} 👑 PRO A2Z CONTROL CENTER",
            description=(
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "⚡ **ONE PANEL • EVERY SYSTEM**\n\n"
                "👋 Welcome • 🚪 Goodbye • 🎫 Tickets\n"
                "🎁 Giveaways • 📢 Announcements\n"
                "🏰 Server Info • 🛡️ Moderation\n"
                "🔐 Permissions • ❓ Help • ⚙️ Settings\n\n"
                "🧪 **TEST** → 👀 **PREVIEW** → ✏️ **EDIT**\n"
                "💾 **SAVE** → 🚀 **PUBLISH**\n\n"
                "💎 Uses your server's custom emojis when available.\n"
                "🔒 Permission checks are active on every protected system.\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            ),
            color=discord.Color.gold()
        )
        if g.icon: e.set_thumbnail(url=g.icon.url)
        e.set_footer(text="👑 PRO A2Z / LIGHTNESS • Official Control Center")
        await interaction.response.send_message(embed=e, view=View(), ephemeral=True)

async def setup(bot):
    await bot.add_cog(Dashboard(bot))
