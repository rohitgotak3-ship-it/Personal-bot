# 💎 PRO A2Z / LIGHTNESS Discord Bot

Dashboard-based Discord bot with protected systems.

## Systems
🧭 Dashboard
👋 Welcome
🚪 Goodbye
🎫 Ticket
🎁 Giveaway
📢 Announcement
🏰 Server Info
🛡️ Moderation
🔐 Permissions
❓ Help
⚙️ Settings

## Owner
Bot Owner ID: `1433457392917676138`

The owner and server administrators have full access. Other users need explicit permission.

## Unauthorized access
Protected commands and dashboard buttons return a large ACCESS DENIED embed containing:
👑 Bot Owner
🆔 Owner ID
🖼️ Owner QR

## Custom emojis
The bot automatically tries to use custom emojis already present in the server by common names. The emoji mapping can also be configured in `data/settings.json`.

## Run
1. Install Python 3.11+
2. `pip install -r requirements.txt`
3. Copy `.env.example` to `.env`
4. Add your Discord bot token
5. Run `python bot.py`
