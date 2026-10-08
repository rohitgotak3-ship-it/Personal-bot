import discord
from discord import app_commands
from discord.ext import commands
import json
import os
import re
import random
from pathlib import Path

# =========================
# LIGHTNESS BOT
# =========================
BOT_TOKEN = os.getenv("DISCORD_TOKEN", "PUT_YOUR_BOT_TOKEN_HERE")
OWNER_ID = 1433457392917676138
ACCESS_FILE = Path("main_dashboard_access.json")

# LIGHTNESS custom emoji set
EMOJIS = [
    "<a:BS_crown:1549137817341268058>",
    "<a:INFAMOUS_Verify:1549136346902175754>",
    "<a:Arrow_White:1549136782971379712>",
    "<a:Fire:1549138871537639507>",
    "<a:diomond:1549139140803563644>",
    "<a:CH_Butterfly:1549136722686644336>",
    "<a:brat_dence:1549138072694689943>",
    "<a:bot:1549139254712606830>",
    "<a:hammer_time:1549138507539288126>",
    "<a:asskick:1549138352618471434>",
    "<a:DOT:1544406593351844012>",
    "<a:dot:1549136875283816608>",
    "<a:CH_IconLoading:1549136416250921060>",
]


def load_access():
    try:
        return set(int(x) for x in json.loads(ACCESS_FILE.read_text(encoding="utf-8")))
    except (FileNotFoundError, json.JSONDecodeError, TypeError, ValueError):
        return set()


def save_access(access):
    tmp = ACCESS_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(sorted(access), indent=2), encoding="utf-8")
    tmp.replace(ACCESS_FILE)


MAIN_ACCESS = load_access()

intents = discord.Intents.default()
intents.guilds = True
intents.members = True


class LightnessBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents, help_command=None)

    async def setup_hook(self):
        # Register persistent dashboard buttons.
        self.add_view(MainDashboardView())
        self.add_view(AdminDashboardView())

        # Register commands globally so /op, /add-role, dashboards, etc. work
        # in every server where this bot is installed. Discord may take some
        # time to propagate global application commands.
        synced = await self.tree.sync()
        names = ", ".join(sorted(c.name for c in synced))
        print(f"Global slash commands synced: {names}")


bot = LightnessBot()


def is_bot_owner(user_id: int) -> bool:
    return user_id == OWNER_ID


def is_server_owner(interaction: discord.Interaction) -> bool:
    return bool(interaction.guild and interaction.guild.owner_id == interaction.user.id)


def is_privileged(interaction: discord.Interaction) -> bool:
    return is_bot_owner(interaction.user.id) or is_server_owner(interaction)


def has_main_access(user_id: int) -> bool:
    return is_bot_owner(user_id) or user_id in MAIN_ACCESS


async def deny(interaction: discord.Interaction):
    msg = (
        "╭━━〔 <a:INFAMOUS_Verify:1549136346902175754> 𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃 〕━━╮\n"
        "┃ <a:Arrow_White:1549136782971379712> Main Dashboard access nahi hai.\n"
        "╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯"
    )
    if interaction.response.is_done():
        return await interaction.followup.send(msg, ephemeral=True)
    return await interaction.response.send_message(msg, ephemeral=True)


# =========================
# OP FORMATTER
# =========================

def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text.strip())
    return text[:3500]


def title_from_text(text: str) -> str:
    words = re.findall(r"[A-Za-z0-9₹$]+", text)
    if not words:
        return "𝐋𝐈𝐆𝐇𝐓𝐍𝐄𝐒𝐒 𝐔𝐏𝐃𝐀𝐓𝐄"
    # Keep a short premium heading; do not change the user's actual details.
    if any(w.lower() in {"giveaway", "give", "winner", "prize"} for w in words):
        return "𝐆𝐈𝐕𝐄𝐀𝐖𝐀𝐘 𝐔𝐏𝐃𝐀𝐓𝐄"
    if any(w.lower() in {"sale", "sell", "selling", "package", "pack", "price", "buy", "purchase"} for w in words):
        return "𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐒𝐓𝐎𝐂𝐊"
    if any(w.lower() in {"rule", "rules", "information", "info"} for w in words):
        return "𝐈𝐌𝐏𝐎𝐑𝐓𝐀𝐍𝐓 𝐈𝐍𝐅𝐎"
    return "𝐋𝐈𝐆𝐇𝐓𝐍𝐄𝐒𝐒 𝐀𝐍𝐍𝐎𝐔𝐍𝐂𝐄𝐌𝐄𝐍𝐓"


def op_format(text: str) -> str:
    """Turn plain text into a compact LIGHTNESS-style Discord post."""
    text = clean_text(text)
    parts = [p.strip(" -•|\t") for p in re.split(r"\n|(?<=\.)\s+(?=[A-Z0-9₹])", text) if p.strip()]
    if not parts:
        parts = [text]

    # Fresh random emoji order on every OP post. An emoji is not reused
    # within the same normal-sized post, so each generated OP looks different.
    emoji_pool = random.sample(EMOJIS, k=len(EMOJIS))
    lines = [
        f"{emoji_pool[0]} ═══ **{title_from_text(text)}** ═══ {emoji_pool[1]}",
        "",
    ]
    for i, part in enumerate(parts):
        emoji = emoji_pool[2 + (i % (len(emoji_pool) - 2))]
        # If the user already used bold markers, preserve them rather than doubling.
        if part.startswith("**") and part.endswith("**"):
            body = part
        else:
            body = f"**{part}**"
        lines.append(f"{emoji} {body}")
    lines += [
        "",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"{emoji_pool[-1]} **𝐋𝐈𝐆𝐇𝐓𝐍𝐄𝐒𝐒 • 𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐔𝐏𝐃𝐀𝐓𝐄**",
    ]
    return "\n".join(lines)


class OpMessageModal(discord.ui.Modal, title="LIGHTNESS • OP MESSAGE"):
    message = discord.ui.TextInput(
        label="Test / Message",
        placeholder="Yaha simple text dalo... LIGHTNESS usko OP format me bana dega.",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=3500,
    )

    async def on_submit(self, interaction: discord.Interaction):
        if not has_main_access(interaction.user.id):
            return await deny(interaction)
        await interaction.response.send_message(
            f"{EMOJIS[2]} **𝐏𝐑𝐄𝐕𝐈𝐄𝐖**\n\n{op_format(str(self.message))}\n\n{EMOJIS[1]} **𝐒𝐄𝐍𝐃 𝐓𝐇𝐈𝐒 𝐎𝐏 𝐌𝐄𝐒𝐒𝐀𝐆𝐄?**",
            view=OpConfirmView(op_format(str(self.message))),
            ephemeral=True,
        )


class OpConfirmView(discord.ui.View):
    def __init__(self, content: str):
        super().__init__(timeout=300)
        self.content = content

    @discord.ui.button(label="SEND", style=discord.ButtonStyle.success, emoji="<a:INFAMOUS_Verify:1549136346902175754>")
    async def send(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not has_main_access(interaction.user.id):
            return await deny(interaction)
        await interaction.response.send_message(
            f"{EMOJIS[3]} **𝐂𝐇𝐎𝐎𝐒𝐄 𝐂𝐇𝐀𝐍𝐍𝐄𝐋**\nSelect the channel where LIGHTNESS should post this message.",
            view=OpChannelView(self.content),
            ephemeral=True,
        )

    @discord.ui.button(label="CANCEL", style=discord.ButtonStyle.danger, emoji="<a:dot:1549136875283816608>")
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content=f"{EMOJIS[4]} **𝐎𝐏 𝐌𝐄𝐒𝐒𝐀𝐆𝐄 𝐂𝐀𝐍𝐂𝐄𝐋𝐋𝐄𝐃**", view=None)


class OpChannelSelect(discord.ui.ChannelSelect):
    def __init__(self, content: str):
        self.content = content
        super().__init__(
            placeholder="Select a text channel...",
            channel_types=[discord.ChannelType.text, discord.ChannelType.news],
            min_values=1,
            max_values=1,
        )

    async def callback(self, interaction: discord.Interaction):
        if not has_main_access(interaction.user.id):
            return await deny(interaction)
        channel = self.values[0]
        if not isinstance(channel, (discord.TextChannel, discord.NewsChannel)):
            return await interaction.response.send_message("Invalid text channel.", ephemeral=True)
        try:
            await channel.send(self.content)
        except discord.Forbidden:
            return await interaction.response.send_message(
                f"{EMOJIS[1]} Bot ko {channel.mention} me **Send Messages** permission nahi hai.", ephemeral=True
            )
        await interaction.response.edit_message(
            content=f"{EMOJIS[0]} **𝐎𝐏 𝐌𝐄𝐒𝐒𝐀𝐆𝐄 𝐒𝐄𝐍𝐓**\n{EMOJIS[2]} Channel: {channel.mention}",
            view=None,
        )


class OpChannelView(discord.ui.View):
    def __init__(self, content: str):
        super().__init__(timeout=300)
        self.add_item(OpChannelSelect(content))


class OpDashboardView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="MESSAGE", style=discord.ButtonStyle.primary, emoji="<a:Arrow_White:1549136782971379712>", custom_id="lightness:op_message")
    async def message(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not has_main_access(interaction.user.id):
            return await deny(interaction)
        await interaction.response.send_modal(OpMessageModal())

    @discord.ui.button(label="GIF", style=discord.ButtonStyle.secondary, emoji="<a:Fire:1549138871537639507>", custom_id="lightness:op_gif")
    async def gif(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not has_main_access(interaction.user.id):
            return await deny(interaction)
        await interaction.response.send_modal(OpGifModal())


class OpGifModal(discord.ui.Modal, title="LIGHTNESS • OP GIF"):
    gif = discord.ui.TextInput(label="GIF URL", placeholder="Paste a GIF URL here...", required=True, max_length=1000)
    caption = discord.ui.TextInput(label="Caption (optional)", style=discord.TextStyle.paragraph, required=False, max_length=1000)

    async def on_submit(self, interaction: discord.Interaction):
        if not has_main_access(interaction.user.id):
            return await deny(interaction)
        url = str(self.gif).strip()
        caption = clean_text(str(self.caption)) if str(self.caption).strip() else ""
        if not re.match(r"^https?://", url):
            return await interaction.response.send_message(f"{EMOJIS[1]} Valid GIF URL dalo.", ephemeral=True)
        content = op_format(caption) if caption else f"{EMOJIS[0]} **𝐋𝐈𝐆𝐇𝐓𝐍𝐄𝐒𝐒 𝐆𝐈𝐅** {EMOJIS[0]}"
        await interaction.response.send_message(
            f"{content}\n\n{url}\n\n{EMOJIS[1]} **𝐂𝐇𝐎𝐎𝐒𝐄 𝐂𝐇𝐀𝐍𝐍𝐄𝐋**",
            view=OpChannelView(content + f"\n\n{url}"),
            ephemeral=True,
        )


# =========================
# MAIN / ADMIN DASHBOARD
# =========================
class MainDashboardView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="ANNOUNCEMENT", emoji="<a:Fire:1549138871537639507>", style=discord.ButtonStyle.primary, custom_id="lightness:announcement")
    async def announcement(self, interaction, button):
        if not has_main_access(interaction.user.id): return await deny(interaction)
        await interaction.response.send_message("Announcement module opened.", ephemeral=True)

    @discord.ui.button(label="WELCOME", emoji="<a:CH_Butterfly:1549136722686644336>", style=discord.ButtonStyle.success, custom_id="lightness:welcome")
    async def welcome(self, interaction, button):
        if not has_main_access(interaction.user.id): return await deny(interaction)
        await interaction.response.send_message("Welcome module opened.", ephemeral=True)

    @discord.ui.button(label="GOODBYE", emoji="<a:dot:1549136875283816608>", style=discord.ButtonStyle.danger, custom_id="lightness:goodbye")
    async def goodbye(self, interaction, button):
        if not has_main_access(interaction.user.id): return await deny(interaction)
        await interaction.response.send_message("Goodbye module opened.", ephemeral=True)

    @discord.ui.button(label="TICKET", emoji="<a:asskick:1549138352618471434>", style=discord.ButtonStyle.secondary, custom_id="lightness:ticket")
    async def ticket(self, interaction, button):
        if not has_main_access(interaction.user.id): return await deny(interaction)
        await interaction.response.send_message("Ticket module opened.", ephemeral=True)

    @discord.ui.button(label="VERIFY", emoji="<a:INFAMOUS_Verify:1549136346902175754>", style=discord.ButtonStyle.secondary, custom_id="lightness:verify")
    async def verify(self, interaction, button):
        if not has_main_access(interaction.user.id): return await deny(interaction)
        await interaction.response.send_message("Verify module opened.", ephemeral=True)


class AdminDashboardView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)

    @discord.ui.button(label="GIVE MAIN ACCESS", emoji="<a:INFAMOUS_Verify:1549136346902175754>", style=discord.ButtonStyle.success, custom_id="lightness:give_access")
    async def give_access(self, interaction, button):
        if not is_bot_owner(interaction.user.id): return await deny(interaction)
        await interaction.response.send_modal(GiveAccessModal())

    @discord.ui.button(label="REMOVE ACCESS", emoji="<a:dot:1549136875283816608>", style=discord.ButtonStyle.danger, custom_id="lightness:remove_access")
    async def remove_access(self, interaction, button):
        if not is_bot_owner(interaction.user.id): return await deny(interaction)
        await interaction.response.send_modal(RemoveAccessModal())

    @discord.ui.button(label="ACCESS LIST", emoji="<a:DOT:1544406593351844012>", style=discord.ButtonStyle.primary, custom_id="lightness:access_list")
    async def access_list(self, interaction, button):
        if not is_bot_owner(interaction.user.id): return await deny(interaction)
        text = "No users currently have Main Dashboard access." if not MAIN_ACCESS else "\n".join(f"• <@{uid}> (`{uid}`)" for uid in sorted(MAIN_ACCESS))
        await interaction.response.send_message(embed=discord.Embed(title="MAIN DASHBOARD ACCESS LIST", description=text), ephemeral=True)


class GiveAccessModal(discord.ui.Modal, title="Give Main Dashboard Access"):
    user_id = discord.ui.TextInput(label="Discord User ID", placeholder="123456789012345678", max_length=20)
    async def on_submit(self, interaction):
        if not is_bot_owner(interaction.user.id): return await deny(interaction)
        try: uid = int(str(self.user_id).strip())
        except ValueError: return await interaction.response.send_message("Invalid Discord User ID.", ephemeral=True)
        MAIN_ACCESS.add(uid); save_access(MAIN_ACCESS)
        await interaction.response.send_message(f"{EMOJIS[1]} <@{uid}> can now use Main Dashboard.", ephemeral=True)


class RemoveAccessModal(discord.ui.Modal, title="Remove Main Dashboard Access"):
    user_id = discord.ui.TextInput(label="Discord User ID", placeholder="123456789012345678", max_length=20)
    async def on_submit(self, interaction):
        if not is_bot_owner(interaction.user.id): return await deny(interaction)
        try: uid = int(str(self.user_id).strip())
        except ValueError: return await interaction.response.send_message("Invalid Discord User ID.", ephemeral=True)
        MAIN_ACCESS.discard(uid); save_access(MAIN_ACCESS)
        await interaction.response.send_message(f"{EMOJIS[4]} Main Dashboard access removed from <@{uid}>.", ephemeral=True)


# =========================
# COMMANDS
# =========================
@bot.tree.command(name="dashboard", description="Open the LIGHTNESS Main Dashboard")
async def dashboard(interaction):
    if not has_main_access(interaction.user.id): return await deny(interaction)
    embed = discord.Embed(title="<a:BS_crown:1549137817341268058> 𝐋𝐈𝐆𝐇𝐓𝐍𝐄𝐒𝐒 — 𝐌𝐀𝐈𝐍 𝐃𝐀𝐒𝐇𝐁𝐎𝐀𝐑𝐃 <a:BS_crown:1549137817341268058>", description=f"{EMOJIS[1]} **Select a module below.**\n\n{EMOJIS[2]} Main access is required.")
    await interaction.response.send_message(embed=embed, view=MainDashboardView(), ephemeral=True)


@bot.tree.command(name="admin-dashboard", description="Open the Owner-only Admin Dashboard")
async def admin_dashboard(interaction):
    if not is_bot_owner(interaction.user.id): return await deny(interaction)
    embed = discord.Embed(title="<a:BS_crown:1549137817341268058> 𝐋𝐈𝐆𝐇𝐓𝐍𝐄𝐒𝐒 — 𝐀𝐃𝐌𝐈𝐍 <a:BS_crown:1549137817341268058>", description="Owner-only access management.")
    await interaction.response.send_message(embed=embed, view=AdminDashboardView(), ephemeral=True)


@bot.tree.command(name="op", description="Open the LIGHTNESS OP message/GIF maker")
async def op(interaction):
    if not has_main_access(interaction.user.id): return await deny(interaction)
    embed = discord.Embed(
        title="<a:BS_crown:1549137817341268058> ═══ 𝐋𝐈𝐆𝐇𝐓𝐍𝐄𝐒𝐒 ═══ <a:BS_crown:1549137817341268058>",
        description=(
            "\n"
            "<a:INFAMOUS_Verify:1549136346902175754> **𝐎𝐏 𝐌𝐀𝐊𝐄𝐑** <a:INFAMOUS_Verify:1549136346902175754>\n"
            "\n"
            "╭━━━〔 <a:Fire:1549138871537639507> 〕━━━╮\n"
            "┃ **𝐓𝐄𝐒𝐓**                         ┃\n"
            "┃ Apna simple message dalo.         ┃\n"
            "┃ LIGHTNESS khud premium format    ┃\n"
            "┃ + custom Nitro emojis lagayega.   ┃\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯\n"
            "\n"
            "<a:Arrow_White:1549136782971379712> **𝐌𝐄𝐒𝐒𝐀𝐆𝐄** — text ko OP style me convert karo\n"
            "<a:diomond:1549139140803563644> **𝐆𝐈𝐅** — GIF + caption ko OP style me bhejo\n"
            "\n"
            "<a:BS_crown:1549137817341268058> **𝐋𝐈𝐆𝐇𝐓𝐍𝐄𝐒𝐒 • 𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐎𝐏 𝐒𝐓𝐘𝐋𝐄**"
        ),
    )
    await interaction.response.send_message(embed=embed, view=OpDashboardView(), ephemeral=True)


@bot.tree.command(name="add-role", description="Give a Discord role to a member (Owner only)")
@app_commands.describe(member="Member to receive the role", role="Role to give")
async def add_role(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    if not is_privileged(interaction): return await deny(interaction)
    if interaction.guild is None: return await interaction.response.send_message("Server only command.", ephemeral=True)
    me = interaction.guild.me
    if me is None or role >= me.top_role:
        return await interaction.response.send_message(f"{EMOJIS[1]} Bot ka role **{role.name}** se upar hona chahiye.", ephemeral=True)
    try:
        await member.add_roles(role, reason=f"LIGHTNESS /add-role by {interaction.user} ({interaction.user.id})")
    except discord.Forbidden:
        return await interaction.response.send_message(f"{EMOJIS[1]} Discord ne role add karne se mana kiya. Bot hierarchy/Manage Roles check karo.", ephemeral=True)
    await interaction.response.send_message(f"{EMOJIS[0]} **ROLE ADDED**\n{EMOJIS[2]} {member.mention} → {role.mention}", ephemeral=True)


@bot.event
async def on_ready():
    print(f"LIGHTNESS online as {bot.user} | global slash commands enabled for all installed servers")


if BOT_TOKEN == "PUT_YOUR_BOT_TOKEN_HERE":
    print("WARNING: Set DISCORD_TOKEN in Railway Variables.")
else:
    bot.run(BOT_TOKEN)
