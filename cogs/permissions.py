import discord
from discord import app_commands
from discord.ext import commands
from .common import OWNER_ID,is_admin,deny,load_data,save_data

FEATURES=["dashboard","welcome","goodbye","ticket","giveaway","announcement","serverinfo","moderation","permissions","help","settings"]

class GrantModal(discord.ui.Modal):
    def __init__(self,feature):
        super().__init__(title=f"🔐 Grant {feature.title()} Access")
        self.feature=feature
        self.role=discord.ui.TextInput(label="🎭 Role ID (optional)",required=False,max_length=25)
        self.user=discord.ui.TextInput(label="👤 User ID (optional)",required=False,max_length=25)
        self.add_item(self.role); self.add_item(self.user)
    async def on_submit(self,i):
        if not is_admin(i.user): return await deny(i,"permissions")
        data=load_data()
        gd=data.setdefault(str(i.guild.id),{"permissions":{},"settings":{},"emoji_map":{}})
        p=gd["permissions"].setdefault(self.feature,{"roles":[],"users":[]})
        if self.role.value.strip().isdigit():
            rid=int(self.role.value.strip())
            if rid not in p["roles"]: p["roles"].append(rid)
        if self.user.value.strip().isdigit():
            uid=int(self.user.value.strip())
            if uid not in p["users"]: p["users"].append(uid)
        save_data(data)
        await i.response.send_message(
            f"✅💎 **{self.feature.title()} permission saved!**",ephemeral=True)

class Select(discord.ui.Select):
    def __init__(self):
        super().__init__(
            placeholder="🔐 Select a protected feature...",
            options=[discord.SelectOption(label=x.title(),value=x) for x in FEATURES])
    async def callback(self,i):
        if not is_admin(i.user): return await deny(i,"permissions")
        await i.response.send_modal(GrantModal(self.values[0]))

class View(discord.ui.View):
    def __init__(self): super().__init__(timeout=300); self.add_item(Select())

class Permissions(commands.Cog):
    def __init__(self,bot): self.bot=bot
    @app_commands.command(name="permissions",description="🔐💎 Permission Center")
    async def permissions(self,i):
        if not is_admin(i.user): return await deny(i,"permissions")
        e=discord.Embed(
            title="🔐💎 A2Z PERMISSION CENTER",
            description=(
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "👑 **Bot Owner:** Full Access\n"
                "🛡️ **Server Administrator:** Full Access\n"
                "👥 **Members:** No access unless granted\n\n"
                "🎭 Grant by Role\n👤 Grant by User\n\n"
                "🔒 Every protected command and dashboard checks permission.\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"),
            color=discord.Color.gold())
        await i.response.send_message(embed=e,view=View(),ephemeral=True)

async def setup(bot): await bot.add_cog(Permissions(bot))
