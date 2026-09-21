import discord
from discord.ext import commands
from .common import load_data, x

async def send_configured(guild, feature, member):
    cfg=load_data().get(str(guild.id),{}).get("settings",{}).get(feature,{})
    if not cfg.get("enabled") or not cfg.get("message"): return
    cid=cfg.get("channel_id")
    channel=guild.get_channel(cid) if cid else None
    if not channel: return
    msg=cfg["message"].replace("{user}",member.mention).replace("{username}",member.name).replace("{server}",guild.name)
    e=discord.Embed(description=msg,color=discord.Color.gold())
    if cfg.get("image"): e.set_image(url=cfg["image"])
    await channel.send(embed=e)

class Events(commands.Cog):
    def __init__(self,bot): self.bot=bot
    @commands.Cog.listener()
    async def on_member_join(self,member):
        try: await send_configured(member.guild,"welcome",member)
        except Exception as e: print("welcome error:",e)
    @commands.Cog.listener()
    async def on_member_remove(self,member):
        try: await send_configured(member.guild,"goodbye",member)
        except Exception as e: print("goodbye error:",e)
async def setup(bot): await bot.add_cog(Events(bot))
