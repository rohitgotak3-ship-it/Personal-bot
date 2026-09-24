
import os, json, asyncio
from pathlib import Path
import discord
from discord import app_commands
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN", "").strip()
MASTER_ID = 1433457392917676138
SERVER_ID = 1544039840767803412
RULES_CHANNEL = 1547418070878912635
MEET_CHANNEL = 1544397570036474030
ANNOUNCEMENT_CHANNEL = 1544396768601579640

DATA_FILE = Path("lightness_data.json")
if DATA_FILE.exists():
    try:
        DATA = json.loads(DATA_FILE.read_text())
    except Exception:
        DATA = {}
else:
    DATA = {}
DATA.setdefault("users", [])
DATA.setdefault("roles", [])
DATA.setdefault("announcement", {})
DATA.setdefault("verify_role", 0)

def save():
    DATA_FILE.write_text(json.dumps(DATA, indent=2))

def allowed(uid: int, interaction: discord.Interaction) -> bool:
    if uid == MASTER_ID:
        return True
    if uid in DATA["users"]:
        return True
    role_ids = {r.id for r in getattr(interaction.user, "roles", [])}
    return bool(role_ids.intersection(DATA["roles"]))

def e(name, eid):
    return f"<a:{name}:{eid}>"

# User-provided server emojis
ARROW = e("Arrow_White",1549136782971379712)
CROWN = e("BS_crown",1549137817341268058)
BUTTERFLY = e("CH_Butterfly",1549136722686644336)
LOADING = e("CH_IconLoading",1549136416250921060)
FIRE = e("Fire",1549138871537639507)
VERIFY = e("INFAMOUS_Verify",1549136346902175754)
ERROR = e("error",1549136020094717982)
BOT = e("bot",1549139254712606830)
HAMMER = e("hammer_time",1549138507539288126)
DIAMOND = e("diomond",1549139140803563644)
DOT = e("dot",1549136875283816608)

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
bot = commands.Bot(command_prefix="!", intents=intents)

def base_embed(title, description, gif_name=None):
    emb = discord.Embed(title=title, description=description)
    if gif_name:
        path = Path(gif_name)
        if path.exists():
            emb.set_image(url=f"attachment://{path.name}")
    return emb

class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="VERIFY", emoji="🔐", style=discord.ButtonStyle.success, custom_id="lightness_verify")
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):
        role_id = DATA.get("verify_role", 0)
        role = interaction.guild.get_role(role_id) if role_id else None
        if not role:
            return await interaction.response.send_message(
                f"{ERROR} Verification role is not configured.", ephemeral=True
            )
        if role in interaction.user.roles:
            return await interaction.response.send_message(
                f"{VERIFY} You are already verified.", ephemeral=True
            )
        try:
            await interaction.user.add_roles(role, reason="LIGHTNESS verification")
            await interaction.response.send_message(
                f"{VERIFY} **Verification successful!**\n{ARROW} Role granted: {role.mention}",
                ephemeral=True
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                f"{ERROR} I cannot assign that role. Put my bot role above the verification role.",
                ephemeral=True
            )

class AnnouncementModal(discord.ui.Modal, title="LIGHTNESS — Edit Announcement"):
    title_input = discord.ui.TextInput(label="Title", max_length=256, required=False)
    desc_input = discord.ui.TextInput(label="Description", style=discord.TextStyle.paragraph, max_length=4000, required=False)
    image_input = discord.ui.TextInput(label="Image/GIF URL", max_length=1000, required=False)
    channel_input = discord.ui.TextInput(label="Channel ID", max_length=25, required=False)

    async def on_submit(self, interaction: discord.Interaction):
        if not allowed(interaction.user.id, interaction):
            return await interaction.response.send_message(f"{ERROR} Access denied.", ephemeral=True)
        old = DATA["announcement"]
        DATA["announcement"] = {
            "title": str(self.title_input.value or old.get("title","")),
            "description": str(self.desc_input.value or old.get("description","")),
            "image": str(self.image_input.value or old.get("image","")),
            "channel": int(self.channel_input.value) if str(self.channel_input.value).isdigit() else old.get("channel", ANNOUNCEMENT_CHANNEL)
        }
        save()
        await interaction.response.send_message(f"{VERIFY} **Announcement saved successfully.**", ephemeral=True)

class AnnouncementView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(label="EDIT", style=discord.ButtonStyle.primary)
    async def edit(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not allowed(interaction.user.id, interaction):
            return await interaction.response.send_message(f"{ERROR} Access denied.", ephemeral=True)
        m = AnnouncementModal()
        a = DATA["announcement"]
        m.title_input.default = a.get("title","")
        m.desc_input.default = a.get("description","")
        m.image_input.default = a.get("image","")
        m.channel_input.default = str(a.get("channel", ANNOUNCEMENT_CHANNEL))
        await interaction.response.send_modal(m)

    @discord.ui.button(label="TEST", style=discord.ButtonStyle.secondary)
    async def test(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not allowed(interaction.user.id, interaction):
            return await interaction.response.send_message(f"{ERROR} Access denied.", ephemeral=True)
        a = DATA["announcement"]
        emb = discord.Embed(title=a.get("title") or "LIGHTNESS ANNOUNCEMENT",
                            description=a.get("description") or "No announcement saved.")
        if a.get("image"):
            emb.set_image(url=a["image"])
        await interaction.response.send_message(embed=emb, ephemeral=True)

    @discord.ui.button(label="PUBLISH", style=discord.ButtonStyle.success)
    async def publish(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not allowed(interaction.user.id, interaction):
            return await interaction.response.send_message(f"{ERROR} Access denied.", ephemeral=True)
        a = DATA["announcement"]
        channel = interaction.guild.get_channel(int(a.get("channel", ANNOUNCEMENT_CHANNEL)))
        if not channel:
            return await interaction.response.send_message(f"{ERROR} Channel not found.", ephemeral=True)
        emb = discord.Embed(title=a.get("title") or "LIGHTNESS ANNOUNCEMENT",
                            description=a.get("description") or "")
        if a.get("image"):
            emb.set_image(url=a["image"])
        await channel.send(embed=emb)
        await interaction.response.send_message(f"{VERIFY} Published in {channel.mention}.", ephemeral=True)

class SetupView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(label="EDIT", style=discord.ButtonStyle.primary)
    async def edit(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not allowed(interaction.user.id, interaction):
            return await interaction.response.send_message(f"{ERROR} Access denied.", ephemeral=True)
        m = AnnouncementModal()
        a = DATA["announcement"]
        m.title_input.default = a.get("title","")
        m.desc_input.default = a.get("description","")
        m.image_input.default = a.get("image","")
        m.channel_input.default = str(a.get("channel", ANNOUNCEMENT_CHANNEL))
        await interaction.response.send_modal(m)

@bot.event
async def on_ready():
    bot.add_view(VerifyView())
    try:
        synced = await bot.tree.sync()
        print(f"LIGHTNESS online as {bot.user} | synced {len(synced)} commands")
    except Exception as ex:
        print("Sync error:", ex)

@bot.tree.command(name="say", description="Send a message, optionally with an image/GIF attachment.")
@app_commands.describe(message="Message to send", image="Optional image/GIF upload")
async def say(interaction: discord.Interaction, message: str, image: discord.Attachment | None = None):
    if not allowed(interaction.user.id, interaction):
        return await interaction.response.send_message(f"{ERROR} **ACCESS DENIED**", ephemeral=True)
    await interaction.response.defer(ephemeral=True)
    files = []
    if image:
        files.append(await image.to_file())
    await interaction.channel.send(content=message, files=files)
    await interaction.followup.send(f"{VERIFY} Sent.", ephemeral=True)

@bot.tree.command(name="announcement", description="Open the LIGHTNESS announcement dashboard.")
async def announcement(interaction: discord.Interaction):
    if not allowed(interaction.user.id, interaction):
        return await interaction.response.send_message(f"{ERROR} **ACCESS DENIED**", ephemeral=True)
    text = (
        f"{CROWN} **𝐋𝐈𝐆𝐇𝐓𝐍𝐄𝐒𝐒 — 𝐀𝐍𝐍𝐎𝐔𝐍𝐂𝐄𝐌𝐄𝐍𝐓** {CROWN}\n\n"
        f"{ARROW} Edit title, description, image/GIF and channel.\n"
        f"{ARROW} Test before publishing.\n"
        f"{ARROW} Publish to the configured channel."
    )
    await interaction.response.send_message(text, view=AnnouncementView(), ephemeral=True)

@bot.tree.command(name="verify_setup", description="Set the verification role and post the verification panel.")
@app_commands.describe(role="Role granted after verification")
async def verify_setup(interaction: discord.Interaction, role: discord.Role):
    if interaction.user.id != MASTER_ID:
        return await interaction.response.send_message(f"{ERROR} Master access only.", ephemeral=True)
    DATA["verify_role"] = role.id
    save()
    text = (
        f"{CROWN}\n**𝐈𝐍𝐃𝐈𝐀𝐍 𝐁𝐋𝐎𝐎𝐃 𝐌𝐎𝐎𝐍 𝐒𝟏**\n"
        f"**𝐕𝐄𝐑𝐈𝐅𝐈𝐂𝐀𝐓𝐈𝐎𝐍 𝐒𝐘𝐒𝐓𝐄𝐌**\n\n"
        f"{VERIFY} **𝐍𝐎 𝐇𝐀𝐂𝐊 • 𝐍𝐎 𝐄𝐗𝐏𝐋𝐎𝐈𝐓 • 𝐍𝐎 𝐁𝐎𝐓 𝐀𝐁𝐔𝐒𝐄**\n\n"
        f"{ARROW} Press **VERIFY** to receive {role.mention}.\n\n"
        f"{FIRE} **𝐏𝐋𝐀𝐘 𝐅𝐀𝐈𝐑 • 𝐑𝐄𝐒𝐏𝐄𝐂𝐓 𝐓𝐇𝐄 𝐒𝐄𝐑𝐕𝐄𝐑**\n\n"
        f"{BOT} **𝐏𝐎𝐖𝐄𝐑𝐄𝐃 𝐁𝐘 𝐋𝐈𝐆𝐇𝐓𝐍𝐄𝐒𝐒**"
    )
    await interaction.response.send_message(text, view=VerifyView())

@bot.tree.command(name="add_access", description="Grant LIGHTNESS bot access to a user.")
@app_commands.describe(user="User to authorize")
async def add_access(interaction: discord.Interaction, user: discord.Member):
    if interaction.user.id != MASTER_ID:
        return await interaction.response.send_message(f"{ERROR} Master access only.", ephemeral=True)
    if user.id not in DATA["users"]:
        DATA["users"].append(user.id)
        save()
    await interaction.response.send_message(f"{VERIFY} Access granted to {user.mention}.", ephemeral=True)

@bot.tree.command(name="remove_access", description="Remove LIGHTNESS bot access from a user.")
@app_commands.describe(user="User to remove")
async def remove_access(interaction: discord.Interaction, user: discord.Member):
    if interaction.user.id != MASTER_ID:
        return await interaction.response.send_message(f"{ERROR} Master access only.", ephemeral=True)
    if user.id in DATA["users"]:
        DATA["users"].remove(user.id)
        save()
    await interaction.response.send_message(f"{HAMMER} Access removed from {user.mention}.", ephemeral=True)

@bot.tree.command(name="add_role", description="Allow a role to use LIGHTNESS.")
@app_commands.describe(role="Role to authorize")
async def add_role(interaction: discord.Interaction, role: discord.Role):
    if interaction.user.id != MASTER_ID:
        return await interaction.response.send_message(f"{ERROR} Master access only.", ephemeral=True)
    if role.id not in DATA["roles"]:
        DATA["roles"].append(role.id)
        save()
    await interaction.response.send_message(f"{VERIFY} Bot access granted to {role.mention}.", ephemeral=True)

@bot.tree.command(name="remove_role", description="Remove bot access from a role.")
@app_commands.describe(role="Role to de-authorize")
async def remove_role(interaction: discord.Interaction, role: discord.Role):
    if interaction.user.id != MASTER_ID:
        return await interaction.response.send_message(f"{ERROR} Master access only.", ephemeral=True)
    if role.id in DATA["roles"]:
        DATA["roles"].remove(role.id)
        save()
    await interaction.response.send_message(f"{HAMMER} Bot access removed from {role.mention}.", ephemeral=True)

@bot.tree.command(name="access_list", description="Show authorized users and roles.")
async def access_list(interaction: discord.Interaction):
    if interaction.user.id != MASTER_ID:
        return await interaction.response.send_message(f"{ERROR} Master access only.", ephemeral=True)
    users = ", ".join(f"<@{x}>" for x in DATA["users"]) or "None"
    roles = ", ".join(f"<@&{x}>" for x in DATA["roles"]) or "None"
    await interaction.response.send_message(
        f"{CROWN} **𝐋𝐈𝐆𝐇𝐓𝐍𝐄𝐒𝐒 𝐀𝐂𝐂𝐄𝐒𝐒**\n\n"
        f"{ARROW} **Users:** {users}\n{ARROW} **Roles:** {roles}\n"
        f"{ARROW} **Master:** <@{MASTER_ID}>",
        ephemeral=True
    )

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN is not set.")
bot.run(TOKEN)
