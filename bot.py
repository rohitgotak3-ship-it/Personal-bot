import discord
from discord import app_commands
from discord.ext import commands
import json, os, random
from pathlib import Path

BOT_TOKEN = os.getenv('DISCORD_TOKEN', 'PUT_YOUR_BOT_TOKEN_HERE')
OWNER_ID = 1433457392917676138
DATA_FILE = Path('lightness_data.json')
ACCESS_FILE = Path('main_dashboard_access.json')

E = {
    'crown':'<a:BS_crown:1549137817341268058>',
    'fire':'<a:Fire:1549138871537639507>',
    'diamond':'<a:diomond:1549139140803563644>',
    'arrow':'<a:Arrow_White:1549136782971379712>',
    'verify':'<a:INFAMOUS_Verify:1549136346902175754>',
    'bot':'<a:bot:1549139254712606830>',
    'star':'<a:star:1529777112796631141>',
    'purple':'<a:purple:1529777102100889602>',
    'ticket':'<a:ticket:1549136416250921060>',
}

DEFAULT_DATA = {'guilds': {}}

def load_json(path, default):
    try:
        with path.open('r', encoding='utf-8') as f: return json.load(f)
    except Exception: return default

def save_json(path, data):
    tmp = path.with_suffix(path.suffix+'.tmp')
    with tmp.open('w', encoding='utf-8') as f: json.dump(data, f, indent=2, ensure_ascii=False)
    tmp.replace(path)

DATA = load_json(DATA_FILE, DEFAULT_DATA)
ACCESS = set(int(x) for x in load_json(ACCESS_FILE, []))

def guild_cfg(gid):
    g = DATA.setdefault('guilds', {}).setdefault(str(gid), {})
    g.setdefault('welcome', {})
    g.setdefault('goodbye', {})
    g.setdefault('announcement', {})
    g.setdefault('ticket', {})
    g.setdefault('verify', {})
    return g

def is_owner(uid): return uid == OWNER_ID

def can_dashboard(uid): return is_owner(uid) or uid in ACCESS

async def deny(i):
    msg = f"{E['verify']} **ACCESS DENIED**\n{E['diamond']} You don't have LIGHTNESS Dashboard access."
    if i.response.is_done(): await i.followup.send(msg, ephemeral=True)
    else: await i.response.send_message(msg, ephemeral=True)

class BaseModal(discord.ui.Modal):
    pass

class ChannelMessageModal(discord.ui.Modal):
    def __init__(self, module):
        self.module = module
        super().__init__(title=f'LIGHTNESS • {module.upper()} SETUP')
        self.channel_id = discord.ui.TextInput(label='Channel ID', placeholder='Paste the channel ID', max_length=20)
        self.message = discord.ui.TextInput(label='Message', placeholder='Use {user}, {server}, {member_count}', style=discord.TextStyle.paragraph, required=False, max_length=1900)
        self.add_item(self.channel_id); self.add_item(self.message)
    async def on_submit(self, i):
        if not can_dashboard(i.user.id): return await deny(i)
        try: cid = int(str(self.channel_id.value).strip())
        except: return await i.response.send_message(f"{E['verify']} Invalid channel ID.", ephemeral=True)
        ch = i.guild.get_channel(cid)
        if not isinstance(ch, discord.TextChannel): return await i.response.send_message(f"{E['verify']} Text channel not found.", ephemeral=True)
        cfg = guild_cfg(i.guild.id)[self.module]
        cfg.update({'channel_id': cid, 'message': str(self.message.value).strip()})
        save_json(DATA_FILE, DATA)
        await i.response.send_message(f"{E['diamond']} **{self.module.title()} saved:** {ch.mention}", ephemeral=True)

class AnnouncementModal(discord.ui.Modal, title='LIGHTNESS • ANNOUNCEMENT'):
    message = discord.ui.TextInput(label='Announcement', style=discord.TextStyle.paragraph, max_length=1900)
    async def on_submit(self, i):
        if not can_dashboard(i.user.id): return await deny(i)
        cfg = guild_cfg(i.guild.id)['announcement']; cid = cfg.get('channel_id')
        if not cid: return await i.response.send_message(f"{E['verify']} Set Announcement channel first.", ephemeral=True)
        ch=i.guild.get_channel(int(cid))
        if not ch: return await i.response.send_message(f"{E['verify']} Saved channel no longer exists.", ephemeral=True)
        text = f"{E['crown']} **𝐀𝐍𝐍𝐎𝐔𝐍𝐂𝐄𝐌𝐄𝐍𝐓** {E['crown']}\n\n{E['fire']} {self.message.value}\n\n{E['diamond']} **LIGHTNESS OFFICIAL**"
        await ch.send(text)
        await i.response.send_message(f"{E['star']} Announcement sent to {ch.mention}.", ephemeral=True)

class TicketSetupModal(discord.ui.Modal, title='LIGHTNESS • TICKET SETUP'):
    category_id = discord.ui.TextInput(label='Category ID', placeholder='Category where tickets will be created')
    panel_channel_id = discord.ui.TextInput(label='Panel Channel ID', placeholder='Channel for the ticket panel')
    async def on_submit(self, i):
        if not can_dashboard(i.user.id): return await deny(i)
        try: catid=int(str(self.category_id.value)); chid=int(str(self.panel_channel_id.value))
        except: return await i.response.send_message(f"{E['verify']} Invalid ID.", ephemeral=True)
        cat=i.guild.get_channel(catid); ch=i.guild.get_channel(chid)
        if not isinstance(cat, discord.CategoryChannel) or not isinstance(ch, discord.TextChannel):
            return await i.response.send_message(f"{E['verify']} Category or text channel not found.", ephemeral=True)
        guild_cfg(i.guild.id)['ticket']={'category_id':catid,'panel_channel_id':chid}
        save_json(DATA_FILE, DATA)
        await ch.send(f"{E['ticket']} **𝐓𝐈𝐂𝐊𝐄𝐓 𝐒𝐔𝐏𝐏𝐎𝐑𝐓** {E['ticket']}\n{E['diamond']} Press the button below to create a private ticket.", view=TicketPanelView())
        await i.response.send_message(f"{E['crown']} Ticket panel published in {ch.mention}.", ephemeral=True)

class TicketPanelView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label='CREATE TICKET', style=discord.ButtonStyle.primary, custom_id='lightness:create_ticket')
    async def create(self, i, b):
        cfg=guild_cfg(i.guild.id)['ticket']; cat=i.guild.get_channel(int(cfg.get('category_id',0))) if cfg.get('category_id') else None
        if not isinstance(cat, discord.CategoryChannel): return await i.response.send_message(f"{E['verify']} Ticket system is not configured.", ephemeral=True)
        overwrites={i.guild.default_role: discord.PermissionOverwrite(view_channel=False), i.user: discord.PermissionOverwrite(view_channel=True, send_messages=True), i.guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)}
        ch=await i.guild.create_text_channel(f'ticket-{i.user.name}'.lower()[:90], category=cat, overwrites=overwrites)
        await ch.send(f"{E['ticket']} {i.user.mention} **Ticket created.**\n{E['diamond']} Staff will assist you here.", view=CloseTicketView())
        await i.response.send_message(f"{E['star']} Ticket created: {ch.mention}", ephemeral=True)

class CloseTicketView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label='CLOSE TICKET', style=discord.ButtonStyle.danger, custom_id='lightness:close_ticket')
    async def close(self, i,b):
        await i.response.send_message(f"{E['fire']} Closing ticket...", ephemeral=True)
        await i.channel.delete(reason=f'Closed by {i.user}')

class MainView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    async def check(self,i):
        if not can_dashboard(i.user.id): await deny(i); return False
        return True
    @discord.ui.button(label='WELCOME', style=discord.ButtonStyle.success, custom_id='lightness:welcome')
    async def welcome(self,i,b):
        if await self.check(i): await i.response.send_modal(ChannelMessageModal('welcome'))
    @discord.ui.button(label='GOODBYE', style=discord.ButtonStyle.danger, custom_id='lightness:goodbye')
    async def goodbye(self,i,b):
        if await self.check(i): await i.response.send_modal(ChannelMessageModal('goodbye'))
    @discord.ui.button(label='ANNOUNCEMENT', style=discord.ButtonStyle.primary, custom_id='lightness:announcement')
    async def announcement(self,i,b):
        if await self.check(i): await i.response.send_modal(AnnouncementModal())
    @discord.ui.button(label='TICKET', style=discord.ButtonStyle.secondary, custom_id='lightness:ticket')
    async def ticket(self,i,b):
        if await self.check(i): await i.response.send_modal(TicketSetupModal())
    @discord.ui.button(label='SERVER INFO', style=discord.ButtonStyle.secondary, custom_id='lightness:server_info')
    async def info(self,i,b):
        if not await self.check(i): return
        g=i.guild
        em=discord.Embed(title=f"{E['crown']} 𝐒𝐄𝐑𝐕𝐄𝐑 𝐈𝐍𝐅𝐎 {E['crown']}", description=f"{E['diamond']} **{g.name}**\n\n{E['star']} Members: **{g.member_count}**\n{E['verify']} Owner: <@{g.owner_id}>\n{E['bot']} ID: `{g.id}`", color=discord.Color.blurple())
        await i.response.send_message(embed=em, ephemeral=True)
    @discord.ui.button(label='VERIFY', style=discord.ButtonStyle.secondary, custom_id='lightness:verify')
    async def verify(self,i,b):
        if not await self.check(i): return
        await i.response.send_message(f"{E['verify']} Verify setup can be configured with `/verify-setup`.", ephemeral=True)

class AdminView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label='GIVE ACCESS', style=discord.ButtonStyle.success, custom_id='lightness:give_access')
    async def give(self,i,b):
        if not is_owner(i.user.id): return await deny(i)
        await i.response.send_modal(AccessModal(True))
    @discord.ui.button(label='REMOVE ACCESS', style=discord.ButtonStyle.danger, custom_id='lightness:remove_access')
    async def remove(self,i,b):
        if not is_owner(i.user.id): return await deny(i)
        await i.response.send_modal(AccessModal(False))
    @discord.ui.button(label='ACCESS LIST', style=discord.ButtonStyle.primary, custom_id='lightness:access_list')
    async def listing(self,i,b):
        if not is_owner(i.user.id): return await deny(i)
        txt='\n'.join(f'{E["arrow"]} <@{x}>' for x in sorted(ACCESS)) or 'No users added.'
        await i.response.send_message(f'{E["crown"]} **MAIN ACCESS**\n{txt}', ephemeral=True)

class AccessModal(discord.ui.Modal):
    def __init__(self, add):
        self.adding=add; super().__init__(title='LIGHTNESS • GIVE ACCESS' if add else 'LIGHTNESS • REMOVE ACCESS')
        self.uid=discord.ui.TextInput(label='Discord User ID', max_length=20); self.add_item(self.uid)
    async def on_submit(self,i):
        if not is_owner(i.user.id): return await deny(i)
        try: uid=int(str(self.uid.value).strip())
        except: return await i.response.send_message(f'{E["verify"]} Invalid ID.',ephemeral=True)
        if self.adding: ACCESS.add(uid)
        else: ACCESS.discard(uid)
        save_json(ACCESS_FILE, sorted(ACCESS))
        await i.response.send_message(f'{E["diamond"]} Access {"granted" if self.adding else "removed"} for <@{uid}>.',ephemeral=True)

class Bot(commands.Bot):
    def __init__(self):
        intents=discord.Intents.default(); intents.members=True; intents.guilds=True; intents.message_content=True
        super().__init__(command_prefix='!', intents=intents, help_command=None)
    async def setup_hook(self):
        self.add_view(MainView()); self.add_view(AdminView()); self.add_view(TicketPanelView()); self.add_view(CloseTicketView())
        await self.tree.sync()

bot=Bot()

@bot.tree.command(name='dashboard', description='Open the LIGHTNESS Main Dashboard')
async def dashboard(i):
    if not can_dashboard(i.user.id): return await deny(i)
    em=discord.Embed(title=f'{E["crown"]} 𝐋𝐈𝐆𝐇𝐓𝐍𝐄𝐒𝐒 • 𝐌𝐀𝐈𝐍 𝐃𝐀𝐒𝐇𝐁𝐎𝐀𝐑𝐃 {E["crown"]}', description=f'{E["diamond"]} Select a module below to configure your server.\n\n{E["verify"]} Premium LIGHTNESS controls', color=discord.Color.blurple())
    await i.response.send_message(embed=em,view=MainView(),ephemeral=True)

@bot.tree.command(name='admin-dashboard', description='Owner-only access dashboard')
async def admin_dashboard(i):
    if not is_owner(i.user.id): return await deny(i)
    em=discord.Embed(title=f'{E["crown"]} 𝐋𝐈𝐆𝐇𝐓𝐍𝐄𝐒𝐒 • 𝐀𝐃𝐌𝐈𝐍 {E["crown"]}', description=f'{E["verify"]} Owner only\n\n{E["diamond"]} Manage Main Dashboard access.', color=discord.Color.gold())
    await i.response.send_message(embed=em,view=AdminView(),ephemeral=True)

@bot.tree.command(name='op', description='Open LIGHTNESS OP Maker')
async def op(i):
    if not can_dashboard(i.user.id): return await deny(i)
    await i.response.send_message(f'{E["crown"]} **LIGHTNESS • OP MAKER**\n{E["diamond"]} Use `/op-message` or `/op-image`.',ephemeral=True)

@bot.tree.command(name='op-message', description='Create a formatted LIGHTNESS OP message')
@app_commands.describe(text='Your raw text')
async def op_message(i,text:str):
    if not can_dashboard(i.user.id): return await deny(i)
    emojis=list(E.values()); random.shuffle(emojis)
    lines=[x.strip() for x in text.splitlines() if x.strip()] or [text]
    out=f'{emojis[0]} **𝐋𝐈𝐆𝐇𝐓𝐍𝐄𝐒𝐒 • 𝐎𝐏** {emojis[1]}\n\n'
    for n,line in enumerate(lines): out += f'{emojis[(n+2)%len(emojis)]} **{line}**\n'
    out += f'\n{emojis[-1]} **𝐋𝐈𝐆𝐇𝐓𝐍𝐄𝐒𝐒 𝐎𝐅𝐅𝐈𝐂𝐈𝐀𝐋**'
    chunks=[out[i:i+1900] for i in range(0,len(out),1900)]
    for c in chunks: await i.channel.send(c)
    await i.response.send_message(f'{E["star"]} OP sent.',ephemeral=True)

@bot.tree.command(name='op-image', description='Create an OP image post')
@app_commands.describe(image_url='Direct image URL', caption='Optional caption')
async def op_image(i,image_url:str,caption:str=''):
    if not can_dashboard(i.user.id): return await deny(i)
    em=discord.Embed(title=f'{E["crown"]} 𝐋𝐈𝐆𝐇𝐓𝐍𝐄𝐒𝐒 • 𝐎𝐏 {E["crown"]}', description=(f'{E["fire"]} {caption}' if caption else f'{E["diamond"]} 𝐎𝐏 𝐈𝐌𝐀𝐆𝐄'), color=discord.Color.blurple())
    em.set_image(url=image_url); em.set_footer(text='LIGHTNESS OFFICIAL')
    await i.channel.send(embed=em); await i.response.send_message(f'{E["star"]} Image OP sent.',ephemeral=True)

@bot.event
async def on_member_join(member):
    cfg=guild_cfg(member.guild.id)['welcome']; cid=cfg.get('channel_id')
    if not cid: return
    ch=member.guild.get_channel(int(cid))
    if ch:
        msg=cfg.get('message') or f'{E["crown"]} Welcome {member.mention} to **{member.guild.name}**! {E["diamond"]}'
        await ch.send(msg.replace('{user}',member.mention).replace('{server}',member.guild.name).replace('{member_count}',str(member.guild.member_count)))

@bot.event
async def on_member_remove(member):
    cfg=guild_cfg(member.guild.id)['goodbye']; cid=cfg.get('channel_id')
    if not cid: return
    ch=member.guild.get_channel(int(cid))
    if ch:
        msg=cfg.get('message') or f'{E["fire"]} {member.mention} has left **{member.guild.name}**. {E["diamond"]}'
        await ch.send(msg.replace('{user}',member.mention).replace('{server}',member.guild.name).replace('{member_count}',str(member.guild.member_count)))

@bot.event
async def on_ready(): print(f'LIGHTNESS online as {bot.user} ({bot.user.id})')

if BOT_TOKEN == 'PUT_YOUR_BOT_TOKEN_HERE': print('Set DISCORD_TOKEN in Railway Variables.')
else: bot.run(BOT_TOKEN)
