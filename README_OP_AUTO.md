# LIGHTNESS /op Auto OP Formatter

`/op` opens the existing OP Maker dashboard.

- MESSAGE: enter any plain text; LIGHTNESS automatically wraps it in a premium layout and uses the custom Nitro emojis from the bot config.
- GIF: enter a GIF URL and optional caption.
- Existing access/data code is preserved.
- `/add role` remains restricted to the bot owner or the current Discord server owner.

Note: this formatter is deterministic. It automatically chooses custom emojis based on common words (price/payment, purchase/ticket, admin/owner, giveaway/reward, dinos, skins/grafts/blueprints/TEK, server/verify) and rotates the remaining emojis. It does not call an AI API.
