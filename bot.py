import os, json, asyncio, re
from pathlib import Path
from datetime import datetime
import discord
from discord import app_commands
from discord.ext import commands

TOKEN = os.getenv('DISCORD_TOKEN', '').strip()
MASTER_ID = 1433457392917676138
SERVER_ID = 1552614362701627432
DEFAULT_ANNOUNCEMENT_CHANNEL = 1552615643210322000
DEFAULT_INFO_CHANNEL = 1552616143158780004
DEFAULT_RULES_CHANNEL = 1552617506923880449
DEFAULT_CHAT_CHANNEL = 1552626851145584640
DEFAULT_VERIFY_CHANNEL = 1552662728244592763
DATA_FILE = Path('lightness_data.json')

if DATA_FILE.exists():
    try: DATA = json.loads(DATA_FILE.read_text())
    except Exception: DATA = {}
else: DATA = {}
DATA.setdefault('users', [])
DATA.setdefault('roles', [])
DATA.setdefault('verify_role', 0)
DATA.setdefault('announcement', {'title':'', 'description':'', 'image':'', 'channel':DEFAULT_ANNOUNCEMENT_CHANNEL})
DATA.setdefault('welcome', {'enabled':False,'channel':0,'title':'🩸 𝐈𝐍𝐃𝐈𝐀𝐍 𝐁𝐋𝐎𝐎𝐃 𝐌𝐎𝐎𝐍 𝐒𝟏 🩸','description':'<a:BS_crown:1549137817341268058> **𝐖𝐄𝐋𝐂𝐎𝐌𝐄 {user_mention}!**\n<a:Fire:1549138871537639507> **𝐖𝐄𝐋𝐂𝐎𝐌𝐄 𝐓𝐎 {server_name}**','image':''})
DATA.setdefault('goodbye', {'enabled':False,'channel':0,'title':'𝐆𝐎𝐎𝐃𝐁𝐘𝐄 {user_name}','description':'<a:Fire:1549138871537639507> **𝐖𝐄\'𝐋𝐋 𝐌𝐈𝐒𝐒 𝐘𝐎𝐔!**\n<a:Arrow_White:1549136782971379712> **𝐌𝐄𝐌𝐁𝐄𝐑𝐒 𝐋𝐄𝐅𝐓:** {member_count}','image':''})
DATA.setdefault('ticket', {'enabled':False,'channel':0,'category':0,'title':'🎫 𝐓𝐈𝐂𝐊𝐄𝐓 𝐒𝐔𝐏𝐏𝐎𝐑𝐓','description':'Open a ticket using the buttons below.','image':'','buttons':[{'label':'BUY','emoji':'🎫','style':'green'},{'label':'REPORT','emoji':'⚠️','style':'red'},{'label':'SUPPORT','emoji':'🛠️','style':'blue'}]})

def save():
    DATA_FILE.write_text(json.dumps(DATA, indent=2, ensure_ascii=False))

def e(name,eid): return f'<a:{name}:{eid}>'
ARROW=e('Arrow_White',1549136782971379712); CROWN=e('BS_crown',1549137817341268058); BUTTERFLY=e('CH_Butterfly',1549136722686644336); FIRE=e('Fire',1549138871537639507); VERIFY=e('INFAMOUS_Verify',1549136346902175754); ERROR=e('error',1549136020094717982); BOT=e('bot',1549139254712606830); HAMMER=e('hammer_time',1549138507539288126); DIAMOND=e('diomond',1549139140803563644); DOT=e('dot',1549136875283816608)

intents=discord.Intents.default(); intents.members=True; intents.guilds=True
bot=commands.Bot(command_prefix='!', intents=intents)

def is_master(i): return i.user.id==MASTER_ID

def allowed(uid, interaction):
    if uid==MASTER_ID: return True
    if uid in DATA['users']: return True
    return bool({r.id for r in getattr(interaction.user,'roles',[])} & set(DATA['roles']))

def render(text, member=None, guild=None):
    guild=guild or getattr(member,'guild',None)
    vals={'user_mention':member.mention if member else '', 'display_name':member.display_name if member else '', 'user_name':member.name if member else '', 'user_id':str(member.id) if member else '', 'server_name':guild.name if guild else '', 'server_id':str(guild.id) if guild else '', 'member_count':str(guild.member_count if guild else 0), 'member_count_ordinal':ordinal(guild.member_count if guild else 0), 'join_date':member.joined_at.strftime('%d/%m/%Y %H:%M') if member and member.joined_at else '', 'creation_date':member.created_at.strftime('%d/%m/%Y %H:%M') if member else ''}
    for k,v in vals.items(): text=text.replace('{'+k+'}',v)
    return text

def ordinal(n):
    if 10<n%100<14: s='th'
    else: s={1:'st',2:'nd',3:'rd'}.get(n%10,'th')
    return f'{n}{s}'

def make_embed(cfg, member=None, guild=None):
    emb=discord.Embed(title=render(cfg.get('title',''),member,guild), description=render(cfg.get('description',''),member,guild))
    if cfg.get('image'): emb.set_image(url=render(cfg['image'],member,guild))
    return emb

def style(name): return {'green':discord.ButtonStyle.success,'red':discord.ButtonStyle.danger,'blue':discord.ButtonStyle.primary,'gray':discord.ButtonStyle.secondary}.get(name,discord.ButtonStyle.primary)

def parse_emoji(s):
    if not s: return None
    try: return discord.PartialEmoji.from_str(s)
    except Exception: return s

class AccessDeniedView(discord.ui.View): pass

class VerifyView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label='VERIFY', style=discord.ButtonStyle.success, custom_id='lightness_verify')
    async def verify(self, interaction, button):
        role=interaction.guild.get_role(DATA.get('verify_role',0)) if interaction.guild else None
        if not role: return await interaction.response.send_message(f'{ERROR} Verification role is not configured.', ephemeral=True)
        if role in interaction.user.roles: return await interaction.response.send_message(f'{VERIFY} **𝐀𝐋𝐑𝐄𝐀𝐃𝐘 𝐕𝐄𝐑𝐈𝐅𝐈𝐄𝐃**', ephemeral=True)
        try:
            await interaction.user.add_roles(role, reason='LIGHTNESS verification')
            await interaction.response.send_message(f'{VERIFY} **𝐕𝐄𝐑𝐈𝐅𝐈𝐄𝐃!** {ARROW} {role.mention}', ephemeral=True)
        except discord.Forbidden: await interaction.response.send_message(f'{ERROR} Bot role must be above the verification role.', ephemeral=True)

class AnnouncementModal(discord.ui.Modal, title='LIGHTNESS — Edit Announcement'):
    title_input=discord.ui.TextInput(label='Title',max_length=256,required=False)
    desc_input=discord.ui.TextInput(label='Description',style=discord.TextStyle.paragraph,max_length=4000,required=False)
    image_input=discord.ui.TextInput(label='Image/GIF URL',max_length=1000,required=False)
    channel_input=discord.ui.TextInput(label='Channel ID',max_length=25,required=False)
    async def on_submit(self,i):
        if not allowed(i.user.id,i): return await i.response.send_message(f'{ERROR} **𝐃𝐀𝐒𝐇𝐁𝐎𝐀𝐑𝐃 𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃**',ephemeral=True)
        old=DATA['announcement']; ch=str(self.channel_input.value).strip();
        old.update(title=str(self.title_input.value),description=str(self.desc_input.value),image=str(self.image_input.value),channel=int(ch) if ch.isdigit() else old.get('channel',DEFAULT_ANNOUNCEMENT_CHANNEL)); save()
        await i.response.send_message(f'{VERIFY} **𝐀𝐍𝐍𝐎𝐔𝐍𝐂𝐄𝐌𝐄𝐍𝐓 𝐒𝐀𝐕𝐄𝐃**',ephemeral=True)

class SimpleModuleModal(discord.ui.Modal):
    def __init__(self,module):
        super().__init__(title=f'LIGHTNESS — Edit {module.title()}'); self.module=module
        cfg=DATA[module]
        self.title_input=discord.ui.TextInput(label='Title',max_length=256,required=False,default=cfg.get('title',''))
        self.desc_input=discord.ui.TextInput(label='Message',style=discord.TextStyle.paragraph,max_length=4000,required=False,default=cfg.get('description',''))
        self.channel_input=discord.ui.TextInput(label='Channel ID',max_length=25,required=False,default=str(cfg.get('channel',0)))
        self.image_input=discord.ui.TextInput(label='Image/GIF URL',max_length=1000,required=False,default=cfg.get('image',''))
        self.add_item(self.title_input); self.add_item(self.desc_input); self.add_item(self.channel_input); self.add_item(self.image_input)
    async def on_submit(self,i):
        if not allowed(i.user.id,i): return await i.response.send_message(f'{ERROR} **𝐃𝐀𝐒𝐇𝐁𝐎𝐀𝐑𝐃 𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃**',ephemeral=True)
        cfg=DATA[self.module]; ch=str(self.channel_input.value).strip(); cfg.update(title=str(self.title_input.value),description=str(self.desc_input.value),image=str(self.image_input.value),channel=int(ch) if ch.isdigit() else cfg.get('channel',0)); save()
        await i.response.send_message(f'{VERIFY} **{self.module.upper()} SAVED**',ephemeral=True)

class ModuleView(discord.ui.View):
    def __init__(self,module): super().__init__(timeout=300); self.module=module
    @discord.ui.button(label='EDIT',style=discord.ButtonStyle.primary)
    async def edit(self,i,b):
        if not allowed(i.user.id,i): return await i.response.send_message(f'{ERROR} **𝐃𝐀𝐒𝐇𝐁𝐎𝐀𝐑𝐃 𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃**',ephemeral=True)
        await i.response.send_modal(SimpleModuleModal(self.module))
    @discord.ui.button(label='TEST',style=discord.ButtonStyle.secondary)
    async def test(self,i,b):
        if not allowed(i.user.id,i): return await i.response.send_message(f'{ERROR} **𝐃𝐀𝐒𝐇𝐁𝐎𝐀𝐑𝐃 𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃**',ephemeral=True)
        await i.response.send_message(embed=make_embed(DATA[self.module],i.user,i.guild),ephemeral=True)
    @discord.ui.button(label='ENABLE',style=discord.ButtonStyle.success)
    async def enable(self,i,b):
        if not allowed(i.user.id,i): return await i.response.send_message(f'{ERROR} **𝐃𝐀𝐒𝐇𝐁𝐎𝐀𝐑𝐃 𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃**',ephemeral=True)
        DATA[self.module]['enabled']=True; save(); await i.response.send_message(f'{VERIFY} **{self.module.upper()} ENABLED**',ephemeral=True)
    @discord.ui.button(label='DISABLE',style=discord.ButtonStyle.danger)
    async def disable(self,i,b):
        if not allowed(i.user.id,i): return await i.response.send_message(f'{ERROR} **𝐃𝐀𝐒𝐇𝐁𝐎𝐀𝐑𝐃 𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃**',ephemeral=True)
        DATA[self.module]['enabled']=False; save(); await i.response.send_message(f'{HAMMER} **{self.module.upper()} DISABLED**',ephemeral=True)

class TicketSetupModal(discord.ui.Modal, title='LIGHTNESS — Ticket Setup'):
    title_input=discord.ui.TextInput(label='Panel Title',max_length=256,required=False)
    desc_input=discord.ui.TextInput(label='Panel Message',style=discord.TextStyle.paragraph,max_length=4000,required=False)
    channel_input=discord.ui.TextInput(label='Panel Channel ID',max_length=25,required=False)
    category_input=discord.ui.TextInput(label='Ticket Category ID (optional)',max_length=25,required=False)
    image_input=discord.ui.TextInput(label='Image/GIF URL (optional)',max_length=1000,required=False)
    async def on_submit(self,i):
        if not allowed(i.user.id,i): return await i.response.send_message(f'{ERROR} **𝐃𝐀𝐒𝐇𝐁𝐎𝐀𝐑𝐃 𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃**',ephemeral=True)
        c=DATA['ticket']; c.update(title=str(self.title_input.value),description=str(self.desc_input.value),image=str(self.image_input.value))
        ch=str(self.channel_input.value); cat=str(self.category_input.value); c['channel']=int(ch) if ch.isdigit() else c.get('channel',0); c['category']=int(cat) if cat.isdigit() else c.get('category',0); save()
        await i.response.send_message(f'{VERIFY} **𝐓𝐈𝐂𝐊𝐄𝐓 𝐒𝐄𝐓𝐔𝐏 𝐒𝐀𝐕𝐄𝐃**',ephemeral=True)

class TicketButtonModal(discord.ui.Modal, title='Add/Edit Ticket Button'):
    slot=discord.ui.TextInput(label='Slot (1-5)',max_length=1,required=True)
    label=discord.ui.TextInput(label='Button Label',max_length=80,required=True)
    emoji=discord.ui.TextInput(label='Emoji (custom or normal)',max_length=100,required=False)
    button_style=discord.ui.TextInput(label='Style: green/red/blue/gray',max_length=10,required=False,default='blue')
    async def on_submit(self,i):
        if not allowed(i.user.id,i): return await i.response.send_message(f'{ERROR} **𝐃𝐀𝐒𝐇𝐁𝐎𝐀𝐑𝐃 𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃**',ephemeral=True)
        try: idx=int(str(self.slot.value))-1
        except: return await i.response.send_message(f'{ERROR} Slot must be 1-5.',ephemeral=True)
        if not 0<=idx<5: return await i.response.send_message(f'{ERROR} Slot must be 1-5.',ephemeral=True)
        arr=DATA['ticket']['buttons'];
        while len(arr)<=idx: arr.append({'label':f'BUTTON {len(arr)+1}','emoji':'🎫','style':'blue'})
        arr[idx]={'label':str(self.label.value),'emoji':str(self.emoji.value),'style':str(self.button_style.value).lower() or 'blue'}; save()
        await i.response.send_message(f'{VERIFY} **𝐁𝐔𝐓𝐓𝐎𝐍 {idx+1} 𝐒𝐀𝐕𝐄𝐃**',ephemeral=True)

class TicketDeleteButtonModal(discord.ui.Modal, title='Remove Ticket Button'):
    slot=discord.ui.TextInput(label='Slot (1-5)',max_length=1,required=True)
    async def on_submit(self,i):
        if not allowed(i.user.id,i): return await i.response.send_message(f'{ERROR} **𝐃𝐀𝐒𝐇𝐁𝐎𝐀𝐑𝐃 𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃**',ephemeral=True)
        try: idx=int(str(self.slot.value))-1
        except: return await i.response.send_message(f'{ERROR} Invalid slot.',ephemeral=True)
        if 0<=idx<len(DATA['ticket']['buttons']): DATA['ticket']['buttons'].pop(idx); save(); await i.response.send_message(f'{HAMMER} Button removed.',ephemeral=True)
        else: await i.response.send_message(f'{ERROR} Button not found.',ephemeral=True)

class TicketManageView(discord.ui.View):
    def __init__(self): super().__init__(timeout=300)
    @discord.ui.button(label='ADD / EDIT BUTTON',style=discord.ButtonStyle.primary)
    async def add(self,i,b): await i.response.send_modal(TicketButtonModal()) if is_master(i) else await i.response.send_message(f'{ERROR} Master access only.',ephemeral=True)
    @discord.ui.button(label='REMOVE BUTTON',style=discord.ButtonStyle.danger)
    async def remove(self,i,b): await i.response.send_modal(TicketDeleteButtonModal()) if is_master(i) else await i.response.send_message(f'{ERROR} Master access only.',ephemeral=True)
    @discord.ui.button(label='VIEW BUTTONS',style=discord.ButtonStyle.secondary)
    async def view(self,i,b):
        if not allowed(i.user.id,i): return await i.response.send_message(f'{ERROR} **𝐃𝐀𝐒𝐇𝐁𝐎𝐀𝐑𝐃 𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃**',ephemeral=True)
        lines=[f"{n}. {x.get('emoji','')} {x.get('label','')} [{x.get('style','blue')}]" for n,x in enumerate(DATA['ticket']['buttons'],1)] or ['None']
        await i.response.send_message('\n'.join(lines),ephemeral=True)

class TicketPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        for n,b in enumerate(DATA['ticket']['buttons'][:5]):
            btn=discord.ui.Button(label=b.get('label','Ticket')[:80],style=style(b.get('style','blue')),emoji=parse_emoji(b.get('emoji')),custom_id=f"lightness_ticket_{n}")
            async def callback(i, n=n): await create_ticket(i,n)
            btn.callback=callback; self.add_item(btn)

class CloseTicketView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label='CLOSE TICKET',style=discord.ButtonStyle.danger,custom_id='lightness_close_ticket')
    async def close(self,i,b):
        if not (i.channel and i.channel.name.startswith('ticket-')): return await i.response.send_message('Not a ticket channel.',ephemeral=True)
        await i.response.send_message(f'{HAMMER} Ticket closing...'); await asyncio.sleep(1); await i.channel.delete(reason='Ticket closed')

async def create_ticket(i, slot):
    if not i.guild: return await i.response.send_message(f'{ERROR} Server only.',ephemeral=True)
    await i.response.defer(ephemeral=True)
    cfg=DATA['ticket']; category=i.guild.get_channel(int(cfg.get('category',0))) if cfg.get('category') else None
    overwrites={i.guild.default_role:discord.PermissionOverwrite(view_channel=False),i.user:discord.PermissionOverwrite(view_channel=True,send_messages=True,read_message_history=True)}
    if i.guild.me: overwrites[i.guild.me]=discord.PermissionOverwrite(view_channel=True,send_messages=True,manage_channels=True,manage_messages=True)
    name=f"ticket-{re.sub(r'[^a-z0-9-]','',i.user.name.lower())[:18]}-{str(i.user.id)[-4:]}"
    try:
        ch=await i.guild.create_text_channel(name,category=category,overwrites=overwrites,reason='LIGHTNESS ticket')
        b=cfg['buttons'][slot] if slot<len(cfg['buttons']) else {'label':'SUPPORT'}
        await ch.send(f'{CROWN} **𝐋𝐈𝐆𝐇𝐓𝐍𝐄𝐒𝐒 𝐓𝐈𝐂𝐊𝐄𝐓**\n{ARROW} **Type:** {b.get("label","Support")}\n{ARROW} **User:** {i.user.mention}',view=CloseTicketView())
        await i.followup.send(f'{VERIFY} Ticket created: {ch.mention}',ephemeral=True)
    except discord.Forbidden: await i.followup.send(f'{ERROR} I need **Manage Channels** permission.',ephemeral=True)

class TicketDashboard(discord.ui.View):
    def __init__(self): super().__init__(timeout=300)
    @discord.ui.button(label='SETUP',style=discord.ButtonStyle.primary)
    async def setup(self,i,b):
        if not allowed(i.user.id,i): return await i.response.send_message(f'{ERROR} **𝐃𝐀𝐒𝐇𝐁𝐎𝐀𝐑𝐃 𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃**',ephemeral=True)
        c=DATA['ticket']; m=TicketSetupModal(); m.title_input.default=c.get('title',''); m.desc_input.default=c.get('description',''); m.channel_input.default=str(c.get('channel',0)); m.category_input.default=str(c.get('category',0)); m.image_input.default=c.get('image',''); await i.response.send_modal(m)
    @discord.ui.button(label='BUTTONS',style=discord.ButtonStyle.secondary)
    async def buttons(self,i,b):
        if not allowed(i.user.id,i): return await i.response.send_message(f'{ERROR} **𝐃𝐀𝐒𝐇𝐁𝐎𝐀𝐑𝐃 𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃**',ephemeral=True)
        await i.response.send_message(f'{CROWN} **𝐓𝐈𝐂𝐊𝐄𝐓 𝐁𝐔𝐓𝐓𝐎𝐍 𝐌𝐀𝐍𝐀𝐆𝐄𝐑**',view=TicketManageView(),ephemeral=True)
    @discord.ui.button(label='TEST',style=discord.ButtonStyle.secondary)
    async def test(self,i,b):
        if not allowed(i.user.id,i): return await i.response.send_message(f'{ERROR} **𝐃𝐀𝐒𝐇𝐁𝐎𝐀𝐑𝐃 𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃**',ephemeral=True)
        c=DATA['ticket']; emb=discord.Embed(title=c.get('title',''),description=c.get('description','')); 
        if c.get('image'): emb.set_image(url=c['image'])
        await i.response.send_message(embed=emb,view=TicketPanelView(),ephemeral=True)
    @discord.ui.button(label='PUBLISH',style=discord.ButtonStyle.success)
    async def publish(self,i,b):
        if not allowed(i.user.id,i): return await i.response.send_message(f'{ERROR} **𝐃𝐀𝐒𝐇𝐁𝐎𝐀𝐑𝐃 𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃**',ephemeral=True)
        c=DATA['ticket']; ch=i.guild.get_channel(int(c.get('channel',0))) if c.get('channel') else None
        if not ch: return await i.response.send_message(f'{ERROR} Set a panel channel first.',ephemeral=True)
        emb=discord.Embed(title=c.get('title',''),description=c.get('description','')); 
        if c.get('image'): emb.set_image(url=c['image'])
        await ch.send(embed=emb,view=TicketPanelView()); c['enabled']=True; save(); await i.response.send_message(f'{VERIFY} Published in {ch.mention}.',ephemeral=True)
    @discord.ui.button(label='ENABLE/DISABLE',style=discord.ButtonStyle.danger)
    async def toggle(self,i,b):
        if not allowed(i.user.id,i): return await i.response.send_message(f'{ERROR} **𝐃𝐀𝐒𝐇𝐁𝐎𝐀𝐑𝐃 𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃**',ephemeral=True)
        DATA['ticket']['enabled']=not DATA['ticket'].get('enabled',False); save(); await i.response.send_message(f"{VERIFY} Ticket system **{'ENABLED' if DATA['ticket']['enabled'] else 'DISABLED'}**.",ephemeral=True)


class SayDashboardModal(discord.ui.Modal, title='LIGHTNESS — Send Message'):
    message=discord.ui.TextInput(label='Message',style=discord.TextStyle.paragraph,max_length=4000)
    image=discord.ui.TextInput(label='Image/GIF URL (optional)',max_length=1000,required=False)
    async def on_submit(self,i):
        if not allowed(i.user.id,i): return await i.response.send_message(f'{ERROR} Access denied.',ephemeral=True)
        await i.response.defer(ephemeral=True)
        if i.channel:
            await i.channel.send(content=str(self.message.value))
        await i.followup.send(f'{VERIFY} Sent.',ephemeral=True)

class VerifyRoleSelect(discord.ui.RoleSelect):
    def __init__(self): super().__init__(placeholder='Select verification role',min_values=1,max_values=1)
    async def callback(self,i):
        if not is_master(i): return await i.response.send_message(f'{ERROR} Master access only.',ephemeral=True)
        DATA['verify_role']=self.values[0].id; save()
        await i.response.send_message(f'{VERIFY} Verification role set to {self.values[0].mention}.',ephemeral=True)

class VerifyDashboardView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300); self.add_item(VerifyRoleSelect())
    @discord.ui.button(label='TEST PANEL', style=discord.ButtonStyle.success)
    async def test(self,i,b):
        if not allowed(i.user.id,i): return await i.response.send_message(f'{ERROR} Access denied.',ephemeral=True)
        role=i.guild.get_role(DATA.get('verify_role',0)) if i.guild else None
        if not role: return await i.response.send_message(f'{ERROR} Verification role is not configured.',ephemeral=True)
        await i.response.send_message(f'{CROWN} **𝐈𝐍𝐃𝐈𝐀𝐍 𝐁𝐋𝐎𝐎𝐃 𝐌𝐎𝐎𝐍 𝐒𝟏**\n{VERIFY} **𝐍𝐎 𝐇𝐀𝐂𝐊 • 𝐍𝐎 𝐄𝐗𝐏𝐋𝐎𝐈𝐓**\n{ARROW} Press **VERIFY** to receive {role.mention}.',view=VerifyView(),ephemeral=True)

class AccessUserSelect(discord.ui.UserSelect):
    def __init__(self,action): super().__init__(placeholder=f'{action.title()} user',min_values=1,max_values=1); self.action=action
    async def callback(self,i):
        if not is_master(i): return await i.response.send_message(f'{ERROR} Master access only.',ephemeral=True)
        u=self.values[0]
        if self.action=='add':
            if u.id not in DATA['users']: DATA['users'].append(u.id); save()
            msg=f'{VERIFY} Access granted to {u.mention}.'
        else:
            if u.id in DATA['users']: DATA['users'].remove(u.id); save()
            msg=f'{HAMMER} Access removed from {u.mention}.'
        await i.response.send_message(msg,ephemeral=True)

class AccessDashboardView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300); self.add_item(AccessUserSelect('add')); self.add_item(AccessUserSelect('remove'))
    @discord.ui.button(label='LIST', style=discord.ButtonStyle.secondary)
    async def list_access(self,i,b):
        if not is_master(i): return await i.response.send_message(f'{ERROR} Master access only.',ephemeral=True)
        users=', '.join(f'<@{x}>' for x in DATA['users']) or 'None'; roles=', '.join(f'<@&{x}>' for x in DATA['roles']) or 'None'
        await i.response.send_message(f'{CROWN} **𝐀𝐂𝐂𝐄𝐒𝐒**\n{ARROW} Users: {users}\n{ARROW} Roles: {roles}',ephemeral=True)

class MainDashboard(discord.ui.View):
    def __init__(self): super().__init__(timeout=300)
    async def guard(self,i):
        if not allowed(i.user.id,i): await i.response.send_message(f'{ERROR} **𝐃𝐀𝐒𝐇𝐁𝐎𝐀𝐑𝐃 𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃**',ephemeral=True); return False
        return True
    @discord.ui.button(label='ANNOUNCEMENT',style=discord.ButtonStyle.primary)
    async def announcement(self,i,b):
        if not await self.guard(i): return
        a=DATA['announcement']; await i.response.send_message(f'{CROWN} **𝐀𝐍𝐍𝐎𝐔𝐍𝐂𝐄𝐌𝐄𝐍𝐓 𝐒𝐄𝐓𝐔𝐏**\n{ARROW} Edit • Test • Publish',view=AnnouncementView(),ephemeral=True)
    @discord.ui.button(label='WELCOME',style=discord.ButtonStyle.success)
    async def welcome(self,i,b):
        if not await self.guard(i): return
        await i.response.send_message(f'{BUTTERFLY} **𝐖𝐄𝐋𝐂𝐎𝐌𝐄 𝐒𝐄𝐓𝐔𝐏**',view=ModuleView('welcome'),ephemeral=True)
    @discord.ui.button(label='GOODBYE',style=discord.ButtonStyle.danger)
    async def goodbye(self,i,b):
        if not await self.guard(i): return
        await i.response.send_message(f'{FIRE} **𝐆𝐎𝐎𝐃𝐁𝐘𝐄 𝐒𝐄𝐓𝐔𝐏**',view=ModuleView('goodbye'),ephemeral=True)
    @discord.ui.button(label='TICKET',style=discord.ButtonStyle.secondary)
    async def ticket(self,i,b):
        if not await self.guard(i): return
        await i.response.send_message(f'{DIAMOND} **𝐓𝐈𝐂𝐊𝐄𝐓 𝐒𝐄𝐓𝐔𝐏**',view=TicketDashboard(),ephemeral=True)
    @discord.ui.button(label='VERIFY',style=discord.ButtonStyle.success)
    async def verify(self,i,b):
        if not await self.guard(i): return
        await i.response.send_message(f'{VERIFY} **𝐕𝐄𝐑𝐈𝐅𝐘 𝐒𝐄𝐓𝐔𝐏**',view=VerifyDashboardView(),ephemeral=True)
    @discord.ui.button(label='ACCESS',style=discord.ButtonStyle.secondary)
    async def access(self,i,b):
        if not await self.guard(i): return
        await i.response.send_message(f'{CROWN} **𝐀𝐂𝐂𝐄𝐒𝐒 𝐌𝐀𝐍𝐀𝐆𝐄𝐑**',view=AccessDashboardView(),ephemeral=True)
    @discord.ui.button(label='SAY',style=discord.ButtonStyle.primary)
    async def say_panel(self,i,b):
        if not await self.guard(i): return
        await i.response.send_modal(SayDashboardModal())

class AnnouncementView(discord.ui.View):
    def __init__(self): super().__init__(timeout=300)
    @discord.ui.button(label='EDIT',style=discord.ButtonStyle.primary)
    async def edit(self,i,b):
        if not allowed(i.user.id,i): return await i.response.send_message(f'{ERROR} **𝐃𝐀𝐒𝐇𝐁𝐎𝐀𝐑𝐃 𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃**',ephemeral=True)
        a=DATA['announcement']; m=AnnouncementModal(); m.title_input.default=a.get('title',''); m.desc_input.default=a.get('description',''); m.image_input.default=a.get('image',''); m.channel_input.default=str(a.get('channel',DEFAULT_ANNOUNCEMENT_CHANNEL)); await i.response.send_modal(m)
    @discord.ui.button(label='TEST',style=discord.ButtonStyle.secondary)
    async def test(self,i,b):
        if not allowed(i.user.id,i): return await i.response.send_message(f'{ERROR} **𝐃𝐀𝐒𝐇𝐁𝐎𝐀𝐑𝐃 𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃**',ephemeral=True)
        await i.response.send_message(embed=make_embed(DATA['announcement'],i.user,i.guild),ephemeral=True)
    @discord.ui.button(label='PUBLISH',style=discord.ButtonStyle.success)
    async def publish(self,i,b):
        if not allowed(i.user.id,i): return await i.response.send_message(f'{ERROR} **𝐃𝐀𝐒𝐇𝐁𝐎𝐀𝐑𝐃 𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃**',ephemeral=True)
        a=DATA['announcement']; ch=i.guild.get_channel(int(a.get('channel',0))) if a.get('channel') else None
        if not ch: return await i.response.send_message(f'{ERROR} Channel not found.',ephemeral=True)
        await ch.send(embed=make_embed(a,i.user,i.guild)); await i.response.send_message(f'{VERIFY} Published in {ch.mention}.',ephemeral=True)
    @discord.ui.button(label='DELETE SAVED',style=discord.ButtonStyle.danger)
    async def delete(self,i,b):
        if not allowed(i.user.id,i): return await i.response.send_message(f'{ERROR} **𝐃𝐀𝐒𝐇𝐁𝐎𝐀𝐑𝐃 𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃**',ephemeral=True)
        DATA['announcement']={'title':'','description':'','image':'','channel':DEFAULT_ANNOUNCEMENT_CHANNEL}; save(); await i.response.send_message(f'{HAMMER} Saved announcement cleared.',ephemeral=True)

@bot.event
async def on_ready():
    bot.add_view(VerifyView()); bot.add_view(TicketPanelView()); bot.add_view(CloseTicketView())
    try:
        synced=await bot.tree.sync(); print(f'LIGHTNESS online as {bot.user} | synced {len(synced)} commands')
    except Exception as ex: print('Sync error:',ex)

@bot.event
async def on_member_join(member):
    c=DATA.get('welcome',{})
    if not c.get('enabled'): return
    ch=member.guild.get_channel(int(c.get('channel',0))) if c.get('channel') else None
    if ch:
        try: await ch.send(embed=make_embed(c,member,member.guild))
        except Exception as ex: print('Welcome error:',ex)

@bot.event
async def on_member_remove(member):
    c=DATA.get('goodbye',{})
    if not c.get('enabled'): return
    ch=member.guild.get_channel(int(c.get('channel',0))) if c.get('channel') else None
    if ch:
        try: await ch.send(embed=make_embed(c,member,member.guild))
        except Exception as ex: print('Goodbye error:',ex)

@bot.tree.command(name='dashboard',description='Open the LIGHTNESS setup dashboard.')
async def dashboard(i):
    if not allowed(i.user.id,i): return await i.response.send_message(f'{ERROR} **𝐃𝐀𝐒𝐇𝐁𝐎𝐀𝐑𝐃 𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃**',ephemeral=True)
    await i.response.send_message(f'{CROWN} **𝐋𝐈𝐆𝐇𝐓𝐍𝐄𝐒𝐒 𝐃𝐀𝐒𝐇𝐁𝐎𝐀𝐑𝐃**\n{ARROW} Select a module below.',view=MainDashboard(),ephemeral=True)

@bot.tree.command(name='say',description='Send a message, optionally with an image/GIF.')
@app_commands.describe(message='Message to send',image='Optional image/GIF upload')
async def say(i,message:str,image:discord.Attachment|None=None):
    if not allowed(i.user.id,i): return await i.response.send_message(f'{ERROR} **ACCESS DENIED**',ephemeral=True)
    await i.response.defer(ephemeral=True); files=[]
    if image: files.append(await image.to_file())
    await i.channel.send(content=message,files=files); await i.followup.send(f'{VERIFY} Sent.',ephemeral=True)

@bot.tree.command(name='verify_setup',description='Set verification role and post panel.')
@app_commands.describe(role='Role granted after verification')
async def verify_setup(i,role:discord.Role):
    if not is_master(i): return await i.response.send_message(f'{ERROR} Master access only.',ephemeral=True)
    DATA['verify_role']=role.id; save(); await i.response.send_message(f'{CROWN}\n**𝐈𝐍𝐃𝐈𝐀𝐍 𝐁𝐋𝐎𝐎𝐃 𝐌𝐎𝐎𝐍 𝐒𝟏**\n{VERIFY} **𝐍𝐎 𝐇𝐀𝐂𝐊 • 𝐍𝐎 𝐄𝐗𝐏𝐋𝐎𝐈𝐓**\n{ARROW} Press **VERIFY** to receive {role.mention}.',view=VerifyView())

@bot.tree.command(name='add_access',description='Grant LIGHTNESS bot access to a user.')
async def add_access(i,user:discord.Member):
    if not is_master(i): return await i.response.send_message(f'{ERROR} Master access only.',ephemeral=True)
    if user.id not in DATA['users']: DATA['users'].append(user.id); save()
    await i.response.send_message(f'{VERIFY} Access granted to {user.mention}.',ephemeral=True)

@bot.tree.command(name='remove_access',description='Remove LIGHTNESS bot access from a user.')
async def remove_access(i,user:discord.Member):
    if not is_master(i): return await i.response.send_message(f'{ERROR} Master access only.',ephemeral=True)
    if user.id in DATA['users']: DATA['users'].remove(user.id); save()
    await i.response.send_message(f'{HAMMER} Access removed from {user.mention}.',ephemeral=True)

@bot.tree.command(name='add_role',description='Allow a role to use LIGHTNESS.')
async def add_role(i,role:discord.Role):
    if not is_master(i): return await i.response.send_message(f'{ERROR} Master access only.',ephemeral=True)
    if role.id not in DATA['roles']: DATA['roles'].append(role.id); save()
    await i.response.send_message(f'{VERIFY} Bot access granted to {role.mention}.',ephemeral=True)

@bot.tree.command(name='remove_role',description='Remove bot access from a role.')
async def remove_role(i,role:discord.Role):
    if not is_master(i): return await i.response.send_message(f'{ERROR} Master access only.',ephemeral=True)
    if role.id in DATA['roles']: DATA['roles'].remove(role.id); save()
    await i.response.send_message(f'{HAMMER} Bot access removed from {role.mention}.',ephemeral=True)

@bot.tree.command(name='access_list',description='Show authorized users and roles.')
async def access_list(i):
    if not is_master(i): return await i.response.send_message(f'{ERROR} Master access only.',ephemeral=True)
    users=', '.join(f'<@{x}>' for x in DATA['users']) or 'None'; roles=', '.join(f'<@&{x}>' for x in DATA['roles']) or 'None'
    await i.response.send_message(f'{CROWN} **𝐋𝐈𝐆𝐇𝐓𝐍𝐄𝐒𝐒 𝐀𝐂𝐂𝐄𝐒𝐒**\n{ARROW} Users: {users}\n{ARROW} Roles: {roles}\n{ARROW} Master: <@{MASTER_ID}>',ephemeral=True)

if not TOKEN: raise RuntimeError('DISCORD_TOKEN is not set.')
bot.run(TOKEN)
