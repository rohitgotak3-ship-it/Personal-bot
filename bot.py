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
