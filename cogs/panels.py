import discord
from discord import app_commands
from discord.ext import commands
from .common import has_permission, deny, load_data, save_data, EditModal, ProtectedView, get_custom_emoji

PANELS = {
 "welcome":("👋","WELCOME CONTROL PANEL","🟢 Enable/Disable\n📢 Channel\n✍️ Message\n🖼️ Image/Banner\n🧩 Variables\n🎨 Embed Style"),
 "goodbye":("🚪","GOODBYE CONTROL PANEL","🟢 Enable/Disable\n📢 Channel\n💬 Goodbye Message\n🖼️ Image/Banner\n🧩 Variables\n🎨 Embed Style"),
 "ticket":("🎫","TICKET COMMAND CENTER","🎫 Panel Message\n📂 Category\n🛡️ Support Role\n🖼️ Panel Image\n🔘 Button Editor\n🔒 Ticket Permissions"),
 "giveaway":("🎁","GIVEAWAY COMMAND CENTER","🎁 Prize\n🏆 Winners\n⏱️ Duration\n📢 Channel\n🖼️ Giveaway Image\n🔘 Enter Button\n🔄 Reroll"),
 "announcement":("📢","ANNOUNCEMENT CONTROL CENTER","📢 Channel\n✨ Title\n📝 Description\n🖼️ Image/Banner\n🔗 Buttons\n👤 Author\n🎨 Embed Style"),
 "moderation":("🛡️","MODERATION CONTROL PANEL","🔨 Ban\n👢 Kick\n🔇 Timeout\n⚠️ Warn\n🧹 Purge\n🔒 Protected Controls")
}

class PanelView(ProtectedView):
    def __init__(self, feature):
        super().__init__(feature)
        self.feature = feature

    @discord.ui.button(label="🧪 Test", style=discord.ButtonStyle.secondary)
    async def test(self, interaction, button):
        cfg = load_data().get(str(interaction.guild.id),{}).get("settings",{}).get(self.feature,{})
        msg = cfg.get("message") or "✨ No custom message saved yet."
        e = discord.Embed(
            title=f"🧪💎 {self.feature.upper()} TEST PREVIEW",
            description=f"👀 **Live Preview**\n\n{msg}\n\n━━━━━━━━━━━━━━━━━━\n🧪 TEST ONLY",
            color=discord.Color.gold()
        )
        if cfg.get("image"):
            e.set_image(url=cfg["image"])
        await interaction.response.send_message(embed=e, ephemeral=True)

    @discord.ui.button(label="✏️ Edit", style=discord.ButtonStyle.primary)
    async def edit(self, interaction, button):
        await interaction.response.send_modal(EditModal(self.feature))

    @discord.ui.button(label="💾 Save", style=discord.ButtonStyle.success)
    async def save(self, interaction, button):
        data=load_data()
        gd=data.setdefault(str(interaction.guild.id),{"permissions":{},"settings":{},"emoji_map":{}})
        gd["settings"].setdefault(self.feature,{})["enabled"]=True
        save_data(data)
        await interaction.response.send_message(
            f"✅💎 **{self.feature.title()} configuration saved!**", ephemeral=True)

    @discord.ui.button(label="🔄 Reset", style=discord.ButtonStyle.danger)
    async def reset(self, interaction, button):
        data=load_data()
        gd=data.setdefault(str(interaction.guild.id),{"permissions":{},"settings":{},"emoji_map":{}})
        gd["settings"][self.feature]={}
        save_data(data)
        await interaction.response.send_message(
            f"🔄💎 **{self.feature.title()} reset.**", ephemeral=True)

    @discord.ui.button(label="🚀 Publish", style=discord.ButtonStyle.success, row=1)
    async def publish(self, interaction, button):
        await interaction.response.send_message(
            f"🚀✨ **{self.feature.title()} is ready to publish.**\n"
            "Configure and test it first.", ephemeral=True)

class Panels(commands.Cog):
    def __init__(self, bot): self.bot=bot

    async def open_panel(self, interaction, feature):
        if not has_permission(interaction.user, feature):
            return await deny(interaction, feature)
        emoji,title,items=PANELS[feature]
        e=discord.Embed(
            title=f"{get_custom_emoji(interaction.guild,feature if feature in ('welcome','goodbye','ticket','giveaway','announcement','moderation') else 'diamond')} 💎 {title}",
            description=(
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"{items}\n\n"
                "🧪 **TEST** → 👀 **PREVIEW** → ✏️ **EDIT**\n"
                "💾 **SAVE** → 🚀 **PUBLISH**\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            ),
            color=discord.Color.gold()
        )
        await interaction.response.send_message(embed=e,view=PanelView(feature),ephemeral=True)

    @app_commands.command(name="welcome", description="👋💎 Welcome Dashboard")
    async def welcome(self, i): await self.open_panel(i,"welcome")
    @app_commands.command(name="goodbye", description="🚪💎 Goodbye Dashboard")
    async def goodbye(self, i): await self.open_panel(i,"goodbye")
    @app_commands.command(name="ticket", description="🎫💎 Ticket Dashboard")
    async def ticket(self, i): await self.open_panel(i,"ticket")
    @app_commands.command(name="giveaway", description="🎁💎 Giveaway Dashboard")
    async def giveaway(self, i): await self.open_panel(i,"giveaway")
    @app_commands.command(name="announcement", description="📢💎 Announcement Dashboard")
    async def announcement(self, i): await self.open_panel(i,"announcement")
    @app_commands.command(name="moderation", description="🛡️💎 Moderation Dashboard")
    async def moderation(self, i): await self.open_panel(i,"moderation")

async def setup(bot):
    await bot.add_cog(Panels(bot))
