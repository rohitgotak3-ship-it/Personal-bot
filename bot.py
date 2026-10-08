import discord
from discord import app_commands
from discord.ext import commands
import json
import os
import random

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


def is_owner(user_id: int) -> bool:
    return user_id == OWNER_ID


def has_main_access(user_id: int) -> bool:
    return is_owner(user_id) or user_id in MAIN_ACCESS


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
        if not has_main_access(interaction.user.id):
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
        if not has_main_access(interaction.user.id):
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
        if not has_main_access(interaction.user.id):
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
        if not has_main_access(interaction.user.id):
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
        if not has_main_access(interaction.user.id):
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
        if not is_owner(interaction.user.id):
            return await deny(interaction)
        await interaction.response.send_modal(GiveAccessModal())

    @discord.ui.button(
        label="REMOVE ACCESS",
        emoji="➖",
        style=discord.ButtonStyle.danger,
        custom_id="lightness:remove_access"
    )
    async def remove_access(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not is_owner(interaction.user.id):
            return await deny(interaction)
        await interaction.response.send_modal(RemoveAccessModal())

    @discord.ui.button(
        label="ACCESS LIST",
        emoji="📋",
        style=discord.ButtonStyle.primary,
        custom_id="lightness:access_list"
    )
    async def access_list(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not is_owner(interaction.user.id):
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
        if not is_owner(interaction.user.id):
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
        if not is_owner(interaction.user.id):
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
# OP COMMAND
# -------------------------
# Use the custom LIGHTNESS emojis already configured in the bot.
OP_EMOJIS = [
    "<a:BS_crown:1549137817341268058>",
    "<a:INFAMOUS_Verify:1549136346902175754>",
    "<a:Arrow_White:1549136782971379712>",
    "<a:Fire:1549138871537639507>",
    "<a:diomond:1549139140803563644>",
    "<a:bot:1549139254712606830>",
    "<a:hammer_time:1549138507539288126>",
    "<a:asskick:1549138352618471434>",
    "<a:DOT:1544406593351844012>",
    "<a:dot:1549136875283816608>",
    "<a:CH_IconLoading:1549136416250921060>",
    "<a:CH_Butterfly:1549136722686644336>",
    "<a:brat_dence:1549138072694689943>",
]


def make_op_text(raw: str) -> str:
    """Turn plain input into a compact LIGHTNESS-style OP post.

    Keeps line breaks/bullets supplied by the user, while decorating each
    meaningful line with a different shuffled custom emoji. The emoji pool is
    reshuffled on every call so consecutive posts look different.
    """
    lines = [line.strip() for line in raw.splitlines() if line.strip()]
    if not lines:
        return ""

    pool = OP_EMOJIS[:]
    random.shuffle(pool)
    while len(pool) < len(lines):
        extra = OP_EMOJIS[:]
        random.shuffle(extra)
        pool.extend(extra)

    title_words = {"giveaway", "admin", "pack", "package", "sale", "stock", "rules", "payment"}
    formatted = []
    for i, line in enumerate(lines):
        emoji = pool[i]
        clean = line.strip()
        # Preserve an existing list marker, but don't stack another one on it.
        if clean.startswith(("- ", "• ", "➜ ", "→ ")):
            clean = clean[2:].strip()
        if i == 0 or any(w in clean.lower() for w in title_words):
            formatted.append(f"{emoji} **{clean.upper()}**")
        else:
            formatted.append(f"{emoji} **{clean}**")

    return "\n".join(formatted)


class OPView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(label="MESSAGE / TEST", style=discord.ButtonStyle.primary)
    async def message(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not has_main_access(interaction.user.id):
            return await deny(interaction)
        await interaction.response.send_modal(OPMessageModal())

    @discord.ui.button(label="IMAGE", style=discord.ButtonStyle.secondary)
    async def image(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not has_main_access(interaction.user.id):
            return await deny(interaction)
        await interaction.response.send_modal(OPImageModal())


class OPMessageModal(discord.ui.Modal, title="LIGHTNESS • OP TEST"):
    text = discord.ui.TextInput(
        label="TEST / MESSAGE",
        placeholder="Sirf apna normal message likho...",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=4000,
    )

    async def on_submit(self, interaction: discord.Interaction):
        formatted = make_op_text(str(self.text.value))
        if not formatted:
            return await interaction.response.send_message("Message empty hai.", ephemeral=True)

        # Send the generated OP post automatically into the same channel where
        # /op was opened, instead of leaving only an ephemeral preview.
        await interaction.response.defer(ephemeral=True)
        try:
            await interaction.channel.send(formatted, allowed_mentions=discord.AllowedMentions.none())
            await interaction.followup.send(
                f"<a:INFAMOUS_Verify:1549136346902175754> **OP TEST SENT**\n"
                f"<a:diomond:1549139140803563644> Har post me emoji combination automatically shuffle hota hai.",
                ephemeral=True,
            )
        except discord.Forbidden:
            await interaction.followup.send(
                "Bot ke paas is channel me message send karne ki permission nahi hai.",
                ephemeral=True,
            )


class OPImageModal(discord.ui.Modal, title="LIGHTNESS • OP IMAGE"):
    image_url = discord.ui.TextInput(label="Image URL", placeholder="https://...", required=True)
    caption = discord.ui.TextInput(label="Caption / Test", required=False, max_length=1000)

    async def on_submit(self, interaction: discord.Interaction):
        caption = str(self.caption.value).strip()
        embed = discord.Embed(
            description=make_op_text(caption) if caption else None,
            color=discord.Color.dark_purple(),
        )
        embed.set_image(url=str(self.image_url.value).strip())
        await interaction.response.defer(ephemeral=True)
        try:
            await interaction.channel.send(embed=embed, allowed_mentions=discord.AllowedMentions.none())
            await interaction.followup.send(
                "<a:INFAMOUS_Verify:1549136346902175754> **OP IMAGE SENT**",
                ephemeral=True,
            )
        except discord.Forbidden:
            await interaction.followup.send(
                "Bot ke paas is channel me message send karne ki permission nahi hai.",
                ephemeral=True,
            )


@bot.tree.command(name="op", description="Open the LIGHTNESS OP maker")
async def op(interaction: discord.Interaction):
    if not has_main_access(interaction.user.id):
        return await deny(interaction)

    embed = discord.Embed(
        title="<a:BS_crown:1549137817341268058> 𝐋𝐈𝐆𝐇𝐓𝐍𝐄𝐒𝐒 • 𝐎𝐏 𝐌𝐀𝐊𝐄𝐑",
        description=(
            "<a:INFAMOUS_Verify:1549136346902175754> **𝐓𝐄𝐒𝐓 / 𝐌𝐄𝐒𝐒𝐀𝐆𝐄**\n"
            "Sirf normal text dalo. Bot khud usko LIGHTNESS OP style me convert karke isi channel me bhejega.\n\n"
            "<a:Arrow_White:1549136782971379712> **𝐄𝐌𝐎𝐉𝐈 𝐌𝐎𝐃𝐄**\n"
            "Har post me custom LIGHTNESS Nitro emojis ka order automatically alag hoga.\n\n"
            "<a:diomond:1549139140803563644> **𝐈𝐌𝐀𝐆𝐄**\n"
            "Image + optional caption ko bhi OP style me post karo."
        ),
        color=discord.Color.dark_purple(),
    )
    await interaction.response.send_message(embed=embed, view=OPView(), ephemeral=True)

# -------------------------
# COMMANDS
# -------------------------

@bot.tree.command(name="dashboard", description="Open the LIGHTNESS Main Dashboard")
async def dashboard(interaction: discord.Interaction):
    if not has_main_access(interaction.user.id):
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
    if not is_owner(interaction.user.id):
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
