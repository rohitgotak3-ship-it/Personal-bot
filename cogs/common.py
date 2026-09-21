import os, json, discord

OWNER_ID = 1433457392917676138
DATA_FILE = "data/settings.json"
QR_FILE = "assets/owner_qr.png"

# Only the custom emojis supplied by the owner are used. No Unicode fallback emojis.
EMOJIS = {
    "arrow": "<a:Arrow_White:1549136782971379712>",
    "crown": "<a:BS_crown:1549137817341268058>",
    "butterfly": "<a:CH_Butterfly:1549136722686644336>",
    "loading": "<a:CH_IconLoading:1549136416250921060>",
    "dot": "<a:DOT:1544406593351844012>",
    "fire": "<a:Fire:1549138871537639507>",
    "hash": "<a:HD_hashy:1544406358152061038>",
    "verify": "<a:INFAMOUS_Verify:1549136346902175754>",
    "asskick": "<a:asskick:1549138352618471434>",
    "banned": "<a:banned:1549138249988182147>",
    "bot": "<a:bot:1549139254712606830>",
    "dance": "<a:brat_dence:1549138072694689943>",
    "confuse": "<a:confuse:1549137286925648012>",
    "diamond": "<a:diomond:1549139140803563644>",
    "small_dot": "<a:dot:1549136875283816608>",
    "error": "<a:error:1549136020094717982>",
    "hammer": "<a:hammer_time:1549138507539288126>",
}

def x(key):
    return EMOJIS.get(key, EMOJIS["dot"])

def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_data(data):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def guild_data(guild_id):
    data = load_data()
    gd = data.setdefault(str(guild_id), {})
    gd.setdefault("permissions", {})
    gd.setdefault("settings", {})
    return gd

def is_master(member):
    return bool(member and member.id == OWNER_ID)

def has_permission(member, feature):
    if not member or not member.guild:
        return False
    if is_master(member):
        return True
    p = guild_data(member.guild.id).get("permissions", {}).get(feature, {})
    if member.id in p.get("users", []):
        return True
    role_ids = {r.id for r in member.roles}
    return bool(role_ids.intersection(set(p.get("roles", []))))

def denied_embed(guild, feature):
    e = discord.Embed(
        title=f"{x('error')} {x('diamond')} ACCESS DENIED",
        description=(
            f"{x('hash')} **PROTECTED LIGHTNESS SYSTEM** {x('hash')}\n\n"
            f"{x('banned')} You are not authorized to use this command or dashboard.\n\n"
            f"{x('crown')} **BOT MASTER**\n<@{OWNER_ID}>\n"
            f"{x('arrow')} **MASTER ID:** `{OWNER_ID}`\n\n"
            f"{x('verify')} Requested: **{feature.upper()}**\n\n"
            f"{x('diamond')} Ask the Bot Master for explicit permission.\n"
            f"{x('butterfly')} **NO ROLE = AUTOMATIC ACCESS.**\n"
            f"{x('fire')} **PRIVATE • PROTECTED • LIGHTNESS**"
        ), color=discord.Color.gold())
    if guild and guild.icon:
        e.set_thumbnail(url=guild.icon.url)
    if os.path.exists(QR_FILE):
        e.set_image(url="attachment://owner_qr.png")
    return e

async def deny(interaction, feature):
    kwargs = {"embed": denied_embed(interaction.guild, feature), "ephemeral": True}
    if os.path.exists(QR_FILE):
        kwargs["file"] = discord.File(QR_FILE, filename="owner_qr.png")
    if interaction.response.is_done():
        await interaction.followup.send(**kwargs)
    else:
        await interaction.response.send_message(**kwargs)

class ProtectedView(discord.ui.View):
    def __init__(self, feature):
        super().__init__(timeout=900)
        self.feature = feature

    async def interaction_check(self, interaction):
        if not has_permission(interaction.user, self.feature):
            await deny(interaction, self.feature)
            return False
        return True

class EditModal(discord.ui.Modal):
    def __init__(self, feature):
        super().__init__(title=f"{x('hash')} Edit {feature.title()}")
        self.feature = feature
        self.text = discord.ui.TextInput(
            label="Message / Content", style=discord.TextStyle.paragraph,
            required=False, max_length=4000,
            placeholder="Write your custom message...")
        self.image = discord.ui.TextInput(
            label="Image URL (optional)", required=False, max_length=500,
            placeholder="https://...")
        self.channel = discord.ui.TextInput(
            label="Channel ID (optional)", required=False, max_length=25,
            placeholder="Paste target channel ID")
        self.add_item(self.text); self.add_item(self.image); self.add_item(self.channel)

    async def on_submit(self, interaction):
        data = load_data()
        gd = data.setdefault(str(interaction.guild.id), {"permissions": {}, "settings": {}})
        cfg = gd["settings"].setdefault(self.feature, {})
        if self.text.value.strip(): cfg["message"] = self.text.value
        if self.image.value.strip(): cfg["image"] = self.image.value.strip()
        if self.channel.value.strip().isdigit(): cfg["channel_id"] = int(self.channel.value.strip())
        cfg["enabled"] = True
        save_data(data)
        await interaction.response.send_message(
            f"{x('verify')} {x('diamond')} **{self.feature.upper()} SAVED**\n"
            f"{x('loading')} Test it, then Publish it.", ephemeral=True)
