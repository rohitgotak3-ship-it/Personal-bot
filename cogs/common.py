import os, json, discord

OWNER_ID = 1433457392917676138
DATA_FILE = "data/settings.json"
QR_FILE = "assets/owner_qr.png"

FALLBACK = {
    "diamond":"💎","sparkle":"✨","crown":"👑","shield":"🛡️","lock":"🔐",
    "success":"✅","error":"❌","warning":"⚠️","test":"🧪","edit":"✏️",
    "save":"💾","publish":"🚀","welcome":"👋","goodbye":"🚪","ticket":"🎫",
    "giveaway":"🎁","announcement":"📢","server":"🏰","moderation":"🛡️",
    "help":"❓","settings":"⚙️"
}

def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_data(data):
    os.makedirs("data", exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def guild_data(guild_id):
    data = load_data()
    return data.setdefault(str(guild_id), {
        "permissions": {}, "settings": {}, "emoji_map": {}
    })

def get_custom_emoji(guild, key):
    if guild:
        gd = guild_data(guild.id)
        wanted = gd.get("emoji_map", {}).get(key)
        if wanted:
            try:
                e = guild.get_emoji(int(wanted))
                if e:
                    return str(e)
            except Exception:
                pass

        names = {
            "diamond":["diamond","diomond","gem","premium"],
            "sparkle":["sparkle","sparkles","star"],
            "crown":["crown"],
            "shield":["shield","security"],
            "lock":["lock","locked"],
            "success":["success","check","verify"],
            "error":["error","cross"],
            "warning":["warning","warn"],
            "test":["test","testing"],
            "edit":["edit","pencil"],
            "save":["save"],
            "publish":["publish","rocket"],
            "welcome":["welcome"],
            "goodbye":["goodbye","bye"],
            "ticket":["ticket"],
            "giveaway":["giveaway","gift"],
            "announcement":["announcement","announce"],
            "server":["server"],
            "moderation":["mod","moderation"],
            "help":["help"],
            "settings":["settings","gear"]
        }.get(key, [])
        for e in guild.emojis:
            if e.name.lower() in names:
                return str(e)

    return FALLBACK.get(key, "✨")

def is_admin(member):
    return bool(member.guild and (
        member.id == OWNER_ID or
        member.id == member.guild.owner_id or
        member.guild_permissions.administrator
    ))

def has_permission(member, feature):
    if not member.guild:
        return False
    if is_admin(member):
        return True
    p = guild_data(member.guild.id).get("permissions", {}).get(feature, {})
    if member.id in p.get("users", []):
        return True
    return any(role.id in p.get("roles", []) for role in member.roles)

def denied_embed(guild, feature):
    x = lambda k: get_custom_emoji(guild, k)
    e = discord.Embed(
        title=f"{x('lock')} {x('diamond')} ACCESS DENIED • PROTECTED SYSTEM",
        description=(
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{x('warning')} **ACCESS TO THIS SYSTEM IS RESTRICTED**\n\n"
            f"{x('shield')} You don't have permission to use **this command/dashboard**.\n"
            "Only the Bot Owner, Server Administrators, or explicitly authorized users/roles can use it.\n\n"
            f"{x('crown')} **BOT OWNER**\n"
            f"<@{OWNER_ID}>\n"
            f"🆔 **Owner ID:** `{OWNER_ID}`\n\n"
            f"{x('diamond')} **REQUESTED SYSTEM**\n"
            f"`{feature.upper()}`\n\n"
            f"{x('help')} **Need Access?**\n"
            "Contact the Bot Owner and request permission for this system.\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{x('shield')} **PRIVATE • SECURED • ADMIN CONTROLLED**\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        ),
        color=discord.Color.gold()
    )
    if guild and guild.icon:
        e.set_thumbnail(url=guild.icon.url)
    if os.path.exists(QR_FILE):
        e.set_image(url="attachment://owner_qr.png")
    e.set_footer(text="💎 PRO A2Z / LIGHTNESS • Permission Protection")
    return e

async def deny(interaction, feature):
    kwargs = {"embed": denied_embed(interaction.guild, feature), "ephemeral": True}
    if os.path.exists(QR_FILE):
        kwargs["file"] = discord.File(QR_FILE, filename="owner_qr.png")
    await interaction.response.send_message(**kwargs)

class ProtectedView(discord.ui.View):
    def __init__(self, feature):
        super().__init__(timeout=300)
        self.feature = feature

    async def interaction_check(self, interaction):
        if not has_permission(interaction.user, self.feature):
            await deny(interaction, self.feature)
            return False
        return True

class EditModal(discord.ui.Modal):
    def __init__(self, feature):
        super().__init__(title=f"✏️💎 Edit {feature.title()}")
        self.feature = feature
        self.text = discord.ui.TextInput(
            label="Message / Content",
            style=discord.TextStyle.paragraph,
            required=False,
            max_length=4000,
            placeholder="Write your custom premium message..."
        )
        self.image = discord.ui.TextInput(
            label="Image URL (optional)",
            required=False,
            max_length=500,
            placeholder="https://..."
        )
        self.add_item(self.text)
        self.add_item(self.image)

    async def on_submit(self, interaction):
        data = load_data()
        gd = data.setdefault(str(interaction.guild.id),
            {"permissions":{}, "settings":{}, "emoji_map":{}})
        gd["settings"].setdefault(self.feature, {})
        gd["settings"][self.feature]["message"] = self.text.value
        gd["settings"][self.feature]["image"] = self.image.value
        save_data(data)
        await interaction.response.send_message(
            f"✅💎 **{self.feature.title()} saved!**\n"
            "🧪 Test → 👀 Preview → 💾 Save → 🚀 Publish",
            ephemeral=True
        )
