LIGHTNESS GLOBAL SLASH COMMAND UPDATE

This version syncs slash commands globally, so /op, /add-role, dashboard and
other application commands are available in every server where the bot is
installed and authorized.

No GUILD_ID Railway variable is required.
Keep:
  DISCORD_TOKEN = your bot token

IMPORTANT:
Global Discord slash-command propagation can take some time. Restarting the
bot does not guarantee an immediate global appearance; Discord controls the
propagation window.

Existing main_dashboard_access.json is preserved when present.
