LIGHTNESS — Railway setup

1. Upload these files to GitHub.
2. Deploy the repo on Railway.
3. Add environment variable:
   DISCORD_TOKEN = your Discord bot token
4. Enable Server Members Intent in Discord Developer Portal.
5. Invite the bot with bot + applications.commands scopes.
6. Bot commands:
   /say
   /announcement
   /verify_setup
   /add_access
   /remove_access
   /add_role
   /remove_role
   /access_list

Only MASTER_ID can manage access and verification setup.
Announcement EDIT opens a modal with title, description, image/GIF URL and channel ID.
 /say accepts an optional image/GIF upload.
