# discord-server-backup

A powerful Discord bot that safely creates and restores server configurations, helping server owners maintain backups of their server settings.

## Features

- **Complete Server Backup**
  - Server roles and permissions
  - Categories and channels (text & voice)
  - Channel-specific permissions and settings
  - Server emojis
  - Channel topics and slowmode settings
  - Voice channel settings (bitrate, user limits)

- **Security**
  - Administrator-only commands
  - Confirmation required for restore operations
  - Secure token storage using environment variables
  - Comprehensive error handling

## Requirements

- Python 3.8 or higher
- discord.py (>= 2.3.2)
- python-dotenv (>= 1.0.0)
- aiofiles (>= 23.2.1)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/PierrunoYT/discord-server-backup.git
cd discord-server-backup
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory and add your Discord bot token:
```env
DISCORD_TOKEN=your_bot_token_here
```

## Bot Setup

1. Create a new Discord application at [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a bot for your application
3. Enable the following Privileged Gateway Intents:
   - Message Content Intent
   - Server Members Intent
   - Presence Intent
4. Copy your bot token and paste it in the `.env` file

### Required Permissions and Scopes

When inviting the bot to your server, make sure to include the following:

#### Bot Permissions
The bot requires the following permissions (total permission value: 8)
- Administrator (Includes all permissions below)
  - View Channels
  - Manage Roles
  - Manage Channels
  - Manage Emojis and Stickers
  - Read Message History
  - Send Messages
  - Manage Messages
  - Attach Files
  - Add Reactions

#### Required Scopes
- `bot` - Required to add the bot to servers
- `applications.commands` - Required for slash command functionality

You can use this pre-made invite URL format (replace YOUR_CLIENT_ID with your bot's client ID):
```
https://discord.com/api/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=8&scope=bot%20applications.commands
```

## Commands

- `!backup` - Creates a backup of the current server configuration
  - Only administrators can use this command
  - Saves all server settings to a timestamped JSON file
  - Example output: `✅ Backup created successfully! Backup ID: 123456789_1634567890.json`

- `!restore <backup_id>` - Restores a previously created backup
  - Only administrators can use this command
  - Requires confirmation before proceeding
  - Will overwrite current server configuration
  
  Example usage:
  ```
  !restore 123456789_1634567890.json
  ```
  The bot will then:
  1. Ask for confirmation with a ✅ reaction
  2. Wait for the administrator to confirm
  3. Begin the restore process
  4. Send a completion message when done

  Example interaction:
  ```
  You: !restore 123456789_1634567890.json
  Bot: ⚠️ Warning: This will overwrite the current server configuration. Are you sure? React with ✅ to confirm.
  You: *react with ✅*
  Bot: ✅ Backup restored successfully!
  ```

## Backup Storage

- Backups are stored in a `backups` folder (automatically created)
- Each backup file is named with the format: `server_id_timestamp.json`
- Backups contain all server configuration data in JSON format

## Safety Features

1. **Permission Checks**
   - Only server administrators can create/restore backups
   - Bot requires appropriate permissions to function

2. **Restore Protection**
   - Confirmation required before restoration
   - 30-second timeout for confirmation
   - Detailed error messages

3. **Error Handling**
   - Comprehensive error catching and reporting
   - User-friendly error messages
   - Failed operations are safely rolled back

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Copyright (c) 2024 PierrunoYT

## Disclaimer

Always test the backup and restore functionality in a test server before using in a production environment. While the bot is designed to be safe, it's recommended to maintain multiple backups of important server configurations.

Last Updated: December 16, 2024
