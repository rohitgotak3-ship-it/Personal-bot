import discord
from discord import app_commands
from discord.ext import commands
from .common import has_permission, deny, load_data, save_data, EditModal, ProtectedView, x

PANELS = {
 "welcome": "WELCOME CONTROL PANEL",
 "goodbye": "GOODBYE CONTROL PANEL",
 "ticket": "TICKET CONTROL PANEL",
 "giveaway": "GIVEAWAY CONTROL PANEL",
 "announcement": "ANNOUNCEMENT CONTROL PANEL",
 "moderation": "MODERATION CONTROL PANEL",
}

class PanelView(ProtectedView):
    def __init__(self, feature):
        super().__init__(feature)
        self.add_item(discord.ui.Button(label="Test", style=discord.ButtonStyle.secondary, custom_id=f"{feature}:test"))
        self.add_item(discord.ui.Button(label="Edit", style=discord.ButtonStyle.primary, custom_id=f"{feature}:edit"))
        self.add_item(discord.ui.Button(label="Save", style=discord.ButtonStyle.success, custom_id=f"{feature}:save"))
        self.add_item(discord.ui.Button(label="Reset", style=discord.ButtonStyle.danger, custom_id=f"{feature}:reset"))
        self.add_item(discord.ui.Button(label="Publish", style=discord.ButtonStyle.success, custom_id=f"{feature}:publish", row=1))
        for child in self.children:
            child.callback = self._callback

    async def _callback(self, interaction):
        if not await self.interaction_check(interaction): return
        action = interaction.data.get("custom_id", "").split(":", 1)[1]
        data = load_data(); cfg = data.get(str(interaction.guild.id),{}).get("settings",{}).get(self.feature,{})
        if action == "test":
            msg = cfg.get("message") or f"{x('confuse')} No custom message saved yet."
            e = discord.Embed(title=f"{x('loading')} {self.feature.upper()} TEST", description=f"{x('butterfly')} **PREVIEW**\n\n{msg}", color=discord.Color.gold())
            if cfg.get("image"): e.set_image(url=cfg["image"])
            await interaction.response.send_message(embed=e, ephemeral=True); return
        if action == "edit":
            await interaction.response.send_modal(EditModal(self.feature)); return
        if action == "save":
            gd=data.setdefault(str(interaction.guild.id),{"permissions":{},"settings":{}}); gd["settings"].setdefault(self.feature,{})["enabled"]=True; save_data(data)
            await interaction.response.send_message(f"{x('verify')} {x('diamond')} **SAVED**", ephemeral=True); return
        if action == "reset":
            gd=data.setdefault(str(interaction.guild.id),{"permissions":{},"settings":{}}); gd["settings"][self.feature]={}; save_data(data)
            await interaction.response.send_message(f"{x('error')} {x('diamond')} **RESET**", ephemeral=True); return
        if action == "publish":
            await publish_feature(interaction, self.feature)

async def publish_feature(interaction, feature):
    data=load_data(); cfg=data.get(str(interaction.guild.id),{}).get("settings",{}).get(feature,{})
    if not cfg.get("message") and feature not in ("ticket","giveaway"):
        await interaction.response.send_message(f"{x('confuse')} Set a message first with Edit.", ephemeral=True); return
    cid=cfg.get("channel_id")
    channel=interaction.guild.get_channel(cid) if cid else interaction.channel
    if not channel or not hasattr(channel,"send"):
        await interaction.response.send_message(f"{x('error')} Set a valid Channel ID in Edit.", ephemeral=True); return
    if feature == "ticket":
        e=discord.Embed(title=f"{x('diamond')} TICKET SUPPORT",description=cfg.get("message") or f"{x('verify')} Open a ticket for support.",color=discord.Color.gold())
        await channel.send(embed=e, view=TicketView())
    else:
        e=discord.Embed(title=f"{x('diamond')} {feature.upper()}",description=cfg.get("message") or "",color=discord.Color.gold())
        if cfg.get("image"): e.set_image(url=cfg["image"])
        await channel.send(embed=e)
    await interaction.response.send_message(f"{x('verify')} {x('fire')} **PUBLISHED**", ephemeral=True)

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        b=discord.ui.Button(label="Open Ticket", style=discord.ButtonStyle.success, custom_id="lightness:ticket_open")
        b.callback=self.open_ticket
        self.add_item(b)
    async def open_ticket(self, interaction):
        data=load_data(); cfg=data.get(str(interaction.guild.id),{}).get("settings",{}).get("ticket",{})
        cat=None
        if cfg.get("category_id"): cat=interaction.guild.get_channel(cfg["category_id"])
        name=f"ticket-{interaction.user.name}"[:90]
        overwrites={interaction.guild.default_role:discord.PermissionOverwrite(view_channel=False),interaction.user:discord.PermissionOverwrite(view_channel=True,send_messages=True)}
        ch=await interaction.guild.create_text_channel(name, category=cat, overwrites=overwrites)
        await ch.send(f"{x('ticket')} {x('diamond')} <@{interaction.user.id}> Ticket created.")
        await interaction.response.send_message(f"{x('verify')} Ticket created: {ch.mention}",ephemeral=True)

class Panels(commands.Cog):
    def __init__(self,bot): self.bot=bot
    async def open_panel(self,i,feature):
        if not has_permission(i.user,feature): return await deny(i,feature)
        e=discord.Embed(title=f"{x('diamond')} {PANELS[feature]}",description=f"{x('loading')} **TEST** • **EDIT** • **SAVE** • **RESET** • **PUBLISH**\n\n{x('butterfly')} Edit lets you set message, image and channel ID.",color=discord.Color.gold())
        await i.response.send_message(embed=e,view=PanelView(feature),ephemeral=True)
    @app_commands.command(name="welcome",description="Welcome dashboard")
    async def welcome(self,i): await self.open_panel(i,"welcome")
    @app_commands.command(name="goodbye",description="Goodbye dashboard")
    async def goodbye(self,i): await self.open_panel(i,"goodbye")
    @app_commands.command(name="ticket",description="Ticket dashboard")
    async def ticket(self,i): await self.open_panel(i,"ticket")
    @app_commands.command(name="giveaway",description="Giveaway dashboard")
    async def giveaway(self,i): await self.open_panel(i,"giveaway")
    @app_commands.command(name="announcement",description="Announcement dashboard")
    async def announcement(self,i): await self.open_panel(i,"announcement")
    @app_commands.command(name="moderation",description="Moderation dashboard")
    async def moderation(self,i): await self.open_panel(i,"moderation")

async def setup(bot): await bot.add_cog(Panels(bot))
