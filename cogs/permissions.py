import discord
from discord import app_commands
from discord.ext import commands
from .common import OWNER_ID, is_master, deny, load_data, save_data, x, has_permission

FEATURES=["dashboard","welcome","goodbye","ticket","giveaway","announcement","serverinfo","moderation","permissions","help","settings","say"]

class GrantModal(discord.ui.Modal):
    def __init__(self,feature):
        super().__init__(title=f"Grant {feature.title()} Access"); self.feature=feature
        self.role=discord.ui.TextInput(label="Role ID (optional)",required=False,max_length=25)
        self.user=discord.ui.TextInput(label="User ID (optional)",required=False,max_length=25)
        self.add_item(self.role); self.add_item(self.user)
    async def on_submit(self,i):
        if not is_master(i.user): return await deny(i,"permissions")
        data=load_data(); gd=data.setdefault(str(i.guild.id),{"permissions":{},"settings":{}}); p=gd["permissions"].setdefault(self.feature,{"roles":[],"users":[]})
        if self.role.value.strip().isdigit():
            rid=int(self.role.value.strip()); p["roles"] = list(dict.fromkeys(p["roles"]+[rid]))
        if self.user.value.strip().isdigit():
            uid=int(self.user.value.strip()); p["users"] = list(dict.fromkeys(p["users"]+[uid]))
        save_data(data); await i.response.send_message(f"{x('verify')} {x('diamond')} **PERMISSION SAVED**",ephemeral=True)

class Select(discord.ui.Select):
    def __init__(self): super().__init__(placeholder="Select protected feature",options=[discord.SelectOption(label=f.title(),value=f) for f in FEATURES])
    async def callback(self,i):
        if not is_master(i.user): return await deny(i,"permissions")
        await i.response.send_modal(GrantModal(self.values[0]))

class View(discord.ui.View):
    def __init__(self): super().__init__(timeout=900); self.add_item(Select())

class Permissions(commands.Cog):
    def __init__(self,bot): self.bot=bot
    @app_commands.command(name="permissions",description="Permission center")
    async def permissions(self,i):
        if not is_master(i.user): return await deny(i,"permissions")
        e=discord.Embed(title=f"{x('verify')} {x('diamond')} PERMISSION CENTER",description=f"{x('crown')} **ONLY MASTER ID HAS UNRESTRICTED ACCESS**\n`{OWNER_ID}`\n\n{x('shield')} Server owner/admin roles do NOT automatically bypass protection.\n{x('arrow')} Select a feature and grant a user or role explicitly.",color=discord.Color.gold())
        await i.response.send_message(embed=e,view=View(),ephemeral=True)
async def setup(bot): await bot.add_cog(Permissions(bot))
