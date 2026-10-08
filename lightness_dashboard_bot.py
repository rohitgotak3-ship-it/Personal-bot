import discord
from discord import app_commands
from discord.ext import commands
import json
import os

# =========================
# LIGHTNESS DASHBOARD SYSTEM
# =========================

BOT_TOKEN = os.getenv("DISCORD_TOKEN", "PUT_YOUR_BOT_TOKEN_HERE")

# ONLY this ID can open/use the Admin Dashboard
OWNER_ID = 1433457392917676138

ACCESS_FILE = "main_dashboard_access.json"


def load_access():
    try:
        with open(ACCESS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return set(int(x) for x in data)
    except (FileNotFoundError, json.JSONDecodeError, TypeError, ValueError):
        return set()


def save_access(access):
    with open(ACCESS_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(access), f, indent=2)


MAIN_ACCESS = load_access()


intents = discord.Intents.default()
intents.guilds = True
intents.members = True


class LightnessBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )

    async def setup_hook(self):
        await self.tree.sync()


bot = LightnessBot()


def is_owner(user_id: int, guild: discord.Guild | None = None) -> bool:
    # Bot owner OR current Discord server owner.
    return user_id == OWNER_ID or (guild is not None and guild.owner_id == user_id)


def has_main_access(user_id: int, guild: discord.Guild | None = None) -> bool:
    return is_owner(user_id, guild) or user_id in MAIN_ACCESS


async def deny(interaction: discord.Interaction):
    await interaction.response.send_message(
        "╭━━〔 <a:error:1549136020094717982> ACCESS DENIED 〕━━╮\n"
        "┃ You don't have access to this dashboard.\n"
        "┃ Ask the bot owner for Main Dashboard access.\n"
        "╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯",
        ephemeral=True
    )


# -------------------------
# MAIN DASHBOARD
# -------------------------

class MainDashboardView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="ANNOUNCEMENT",
        emoji="📢",
        style=discord.ButtonStyle.primary,
        custom_id="lightness:announcement"
    )
    async def announcement(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not has_main_access(interaction.user.id, interaction.guild):
            return await deny(interaction)
        await interaction.response.send_message(
            "📢 Announcement module opened.",
            ephemeral=True
        )

    @discord.ui.button(
        label="WELCOME",
        emoji="👋",
        style=discord.ButtonStyle.success,
        custom_id="lightness:welcome"
    )
    async def welcome(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not has_main_access(interaction.user.id, interaction.guild):
            return await deny(interaction)
        await interaction.response.send_message(
            "👋 Welcome module opened.",
            ephemeral=True
        )

    @discord.ui.button(
        label="GOODBYE",
        emoji="🚪",
        style=discord.ButtonStyle.danger,
        custom_id="lightness:goodbye"
    )
    async def goodbye(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not has_main_access(interaction.user.id, interaction.guild):
            return await deny(interaction)
        await interaction.response.send_message(
            "🚪 Goodbye module opened.",
            ephemeral=True
        )

    @discord.ui.button(
        label="TICKET",
        emoji="🎫",
        style=discord.ButtonStyle.secondary,
        custom_id="lightness:ticket"
    )
    async def ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not has_main_access(interaction.user.id, interaction.guild):
            return await deny(interaction)
        await interaction.response.send_message(
            "🎫 Ticket module opened.",
            ephemeral=True
        )

    @discord.ui.button(
        label="VERIFY",
        emoji="🛡️",
        style=discord.ButtonStyle.secondary,
        custom_id="lightness:verify"
    )
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not has_main_access(interaction.user.id, interaction.guild):
            return await deny(interaction)
        await interaction.response.send_message(
            "🛡️ Verify module opened.",
            ephemeral=True
        )


# -------------------------
# ADMIN DASHBOARD
# -------------------------

class AdminDashboardView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="GIVE MAIN ACCESS",
        emoji="➕",
        style=discord.ButtonStyle.success,
        custom_id="lightness:give_access"
    )
    async def give_access(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not is_owner(interaction.user.id, interaction.guild):
            return await deny(interaction)
        await interaction.response.send_modal(GiveAccessModal())

    @discord.ui.button(
        label="REMOVE ACCESS",
        emoji="➖",
        style=discord.ButtonStyle.danger,
        custom_id="lightness:remove_access"
    )
    async def remove_access(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not is_owner(interaction.user.id, interaction.guild):
            return await deny(interaction)
        await interaction.response.send_modal(RemoveAccessModal())

    @discord.ui.button(
        label="ACCESS LIST",
        emoji="📋",
        style=discord.ButtonStyle.primary,
        custom_id="lightness:access_list"
    )
    async def access_list(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not is_owner(interaction.user.id, interaction.guild):
            return await deny(interaction)

        if not MAIN_ACCESS:
            text = "No users currently have Main Dashboard access."
        else:
            text = "\n".join(f"• <@{uid}> (`{uid}`)" for uid in sorted(MAIN_ACCESS))

        embed = discord.Embed(
            title="🔐 MAIN DASHBOARD ACCESS LIST",
            description=text,
            color=discord.Color.blurple()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


class GiveAccessModal(discord.ui.Modal, title="Give Main Dashboard Access"):
    user_id = discord.ui.TextInput(
        label="Discord User ID",
        placeholder="Example: 123456789012345678",
        required=True,
        max_length=20
    )

    async def on_submit(self, interaction: discord.Interaction):
        if not is_owner(interaction.user.id, interaction.guild):
            return await deny(interaction)

        try:
            uid = int(str(self.user_id).strip())
        except ValueError:
            return await interaction.response.send_message(
                "❌ Invalid Discord User ID.",
                ephemeral=True
            )

        if uid == OWNER_ID:
            return await interaction.response.send_message(
                "👑 Owner already has full access.",
                ephemeral=True
            )

        MAIN_ACCESS.add(uid)
        save_access(MAIN_ACCESS)

        await interaction.response.send_message(
            f"✅ <@{uid}> can now use the **Main Dashboard**.\n"
            f"🔒 Admin Dashboard access was NOT granted.",
            ephemeral=True
        )


class RemoveAccessModal(discord.ui.Modal, title="Remove Main Dashboard Access"):
    user_id = discord.ui.TextInput(
        label="Discord User ID",
        placeholder="Example: 123456789012345678",
        required=True,
        max_length=20
    )

    async def on_submit(self, interaction: discord.Interaction):
        if not is_owner(interaction.user.id, interaction.guild):
            return await deny(interaction)

        try:
            uid = int(str(self.user_id).strip())
        except ValueError:
            return await interaction.response.send_message(
                "❌ Invalid Discord User ID.",
                ephemeral=True
            )

        MAIN_ACCESS.discard(uid)
        save_access(MAIN_ACCESS)

        await interaction.response.send_message(
            f"✅ Main Dashboard access removed from <@{uid}>.",
            ephemeral=True
        )


# -------------------------
# ROLE COMMAND (/add role)
# -------------------------

add_group = app_commands.Group(name="add", description="LIGHTNESS admin actions")

@add_group.command(name="role", description="Give a role to a member")
@app_commands.describe(member="Member who will receive the role", role="Role to give")
async def add_role(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    if not is_owner(interaction.user.id, interaction.guild):
        return await deny(interaction)

    if interaction.guild is None:
        return await interaction.response.send_message("Server only command.", ephemeral=True)

    me = interaction.guild.me
    if me is None or role >= me.top_role:
        return await interaction.response.send_message(
            f"{OP_EMOJIS[4] if 'OP_EMOJIS' in globals() else '❌'} **Bot cannot assign a role at or above its highest role. Move the bot role higher.**", ephemeral=True
        )
    if role.is_default():
        return await interaction.response.send_message("❌ @everyone cannot be assigned this way.", ephemeral=True)

    try:
        await member.add_roles(role, reason=f"LIGHTNESS /add role by {interaction.user} ({interaction.user.id})")
    except discord.Forbidden:
        return await interaction.response.send_message("❌ Discord denied the role assignment. Check the bot role hierarchy and Manage Roles permission.", ephemeral=True)
    except discord.HTTPException:
        return await interaction.response.send_message("❌ Discord API error while assigning the role.", ephemeral=True)

    await interaction.response.send_message(
        f"<a:INFAMOUS_Verify:1549136346902175754> **ROLE ADDED**\n"
        f"<a:Arrow_White:1549136782971379712> Member: {member.mention}\n"
        f"<a:diomond:1549139140803563644> Role: {role.mention}",
        allowed_mentions=discord.AllowedMentions(users=True, roles=True),
    )

bot.tree.add_command(add_group)


# -------------------------
# OP MAKER (/op)
# -------------------------

OP_EMOJIS = [
    '<a:BS_crown:1549137817341268058>',
    '<a:Arrow_White:1549136782971379712>',
    '<a:Fire:1549138871537639507>',
    '<a:diomond:1549139140803563644>',
    '<a:INFAMOUS_Verify:1549136346902175754>',
    '<a:bot:1549139254712606830>',
    '<a:hammer_time:1549138507539288126>',
]


def make_op_message(text: str) -> str:
    """Turn plain text into a compact LIGHTNESS-style premium post."""
    lines = [x.strip() for x in text.splitlines() if x.strip()]
    if not lines:
        return ''

    out = [
        f"{OP_EMOJIS[0]} ═══ **𝐋𝐈𝐆𝐇𝐓𝐍𝐄𝐒𝐒 • 𝐏𝐑𝐄𝐌𝐈𝐔𝐌** ═══ {OP_EMOJIS[0]}",
        ''
    ]
    for i, line in enumerate(lines):
        emoji = OP_EMOJIS[(i + 1) % len(OP_EMOJIS)]
        out.append(f"{emoji} **{line}**")
    out += ['', '━━━━━━━━━━━━━━━━━━━━━━━━━━━━', f"{OP_EMOJIS[4]} **𝐌𝐀𝐊𝐄 𝐀 𝐓𝐈𝐂𝐊𝐄𝐓 𝐓𝐎 𝐁𝐔𝐘**"]
    return '\n'.join(out)


class OpMessageModal(discord.ui.Modal, title="LIGHTNESS — OP MESSAGE"):
    message = discord.ui.TextInput(
        label="Test / Message",
        placeholder="Apna koi bhi message yahan likho...",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=4000
    )

    async def on_submit(self, interaction: discord.Interaction):
        if not has_main_access(interaction.user.id, interaction.guild):
            return await deny(interaction)
        formatted = make_op_message(str(self.message))
        await interaction.response.send_message(formatted, allowed_mentions=discord.AllowedMentions.none())


class OpGifModal(discord.ui.Modal, title="LIGHTNESS — OP GIF"):
    gif = discord.ui.TextInput(
        label="GIF URL",
        placeholder="https://media.giphy.com/...",
        required=True,
        max_length=1000
    )

    caption = discord.ui.TextInput(
        label="Message / Caption",
        placeholder="Optional OP text...",
        style=discord.TextStyle.paragraph,
        required=False,
        max_length=1500
    )

    async def on_submit(self, interaction: discord.Interaction):
        if not has_main_access(interaction.user.id, interaction.guild):
            return await deny(interaction)
        url = str(self.gif).strip()
        if not (url.startswith('https://') or url.startswith('http://')):
            return await interaction.response.send_message(
                f"{OP_EMOJIS[4]} **Valid GIF URL required.**", ephemeral=True
            )

        embed = discord.Embed(
            title=f"{OP_EMOJIS[0]} 𝐋𝐈𝐆𝐇𝐓𝐍𝐄𝐒𝐒 • 𝐎𝐏 𝐆𝐈𝐅 {OP_EMOJIS[0]}",
            description=make_op_message(str(self.caption)) if str(self.caption).strip() else f"{OP_EMOJIS[2]} **𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐆𝐈𝐅**",
            color=discord.Color.dark_red()
        )
        embed.set_image(url=url)
        await interaction.response.send_message(embed=embed, allowed_mentions=discord.AllowedMentions.none())


class OpDashboardView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(
        label="MESSAGE",
        style=discord.ButtonStyle.primary,
        custom_id="lightness:op_message"
    )
    async def message_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not has_main_access(interaction.user.id, interaction.guild):
            return await deny(interaction)
        await interaction.response.send_modal(OpMessageModal())

    @discord.ui.button(
        label="GIF",
        style=discord.ButtonStyle.secondary,
        custom_id="lightness:op_gif"
    )
    async def gif_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not has_main_access(interaction.user.id, interaction.guild):
            return await deny(interaction)
        await interaction.response.send_modal(OpGifModal())


@bot.tree.command(name="op", description="Open the LIGHTNESS OP Maker")
async def op(interaction: discord.Interaction):
    if not has_main_access(interaction.user.id, interaction.guild):
        return await deny(interaction)

    embed = discord.Embed(
        title="<a:BS_crown:1549137817341268058> 𝐋𝐈𝐆𝐇𝐓𝐍𝐄𝐒𝐒 — 𝐎𝐏 𝐌𝐀𝐊𝐄𝐑 <a:BS_crown:1549137817341268058>",
        description=(
            "<a:INFAMOUS_Verify:1549136346902175754> **𝐂𝐇𝐎𝐎𝐒𝐄 𝐘𝐎𝐔𝐑 𝐎𝐏𝐓𝐈𝐎𝐍**\n\n"
            "<a:Arrow_White:1549136782971379712> **𝐌𝐄𝐒𝐒𝐀𝐆𝐄** — text ko automatic premium LIGHTNESS style me convert karega.\n"
            "<a:Fire:1549138871537639507> **𝐆𝐈𝐅** — GIF + optional caption ko OP format me bhejega.\n\n"
            "<a:diomond:1549139140803563644> **𝐓𝐄𝐒𝐓:** koi bhi text dalo, LIGHTNESS custom emojis automatically add honge."
        ),
        color=discord.Color.dark_red()
    )
    await interaction.response.send_message(embed=embed, view=OpDashboardView(), ephemeral=True)


# -------------------------
# COMMANDS
# -------------------------

@bot.tree.command(name="dashboard", description="Open the LIGHTNESS Main Dashboard")
async def dashboard(interaction: discord.Interaction):
    if not has_main_access(interaction.user.id, interaction.guild):
        return await deny(interaction)

    embed = discord.Embed(
        title="🏠 LIGHTNESS — MAIN DASHBOARD",
        description=(
            "Select a module below.\n\n"
            "🔒 Only approved users can use this dashboard."
        ),
        color=discord.Color.blurple()
    )
    await interaction.response.send_message(
        embed=embed,
        view=MainDashboardView(),
        ephemeral=True
    )


@bot.tree.command(name="admin-dashboard", description="Open the Owner-only Admin Dashboard")
async def admin_dashboard(interaction: discord.Interaction):
    if not is_owner(interaction.user.id, interaction.guild):
        return await deny(interaction)

    embed = discord.Embed(
        title="👑 LIGHTNESS — ADMIN DASHBOARD",
        description=(
            "🔐 **OWNER ONLY**\n\n"
            "➕ Give Main Dashboard access\n"
            "➖ Remove Main Dashboard access\n"
            "📋 View access list\n\n"
            "⚠️ Main Dashboard access NEVER grants Admin Dashboard access."
        ),
        color=discord.Color.gold()
    )
    await interaction.response.send_message(
        embed=embed,
        view=AdminDashboardView(),
        ephemeral=True
    )


@bot.event
async def on_ready():
    print(f"LIGHTNESS online as {bot.user} ({bot.user.id})")


if BOT_TOKEN == "PUT_YOUR_BOT_TOKEN_HERE":
    print("WARNING: Set DISCORD_TOKEN in Railway Variables or replace BOT_TOKEN.")
else:
    bot.run(BOT_TOKEN)
