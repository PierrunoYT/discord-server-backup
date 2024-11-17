import discord
from discord.ext import commands
import json
import os
from datetime import datetime
import asyncio
import aiofiles
from typing import Dict, List

# Bot setup with necessary intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

class BackupSystem:
    def __init__(self):
        self.backup_folder = "backups"
        # Create backup folder if it doesn't exist
        if not os.path.exists(self.backup_folder):
            os.makedirs(self.backup_folder)

    async def save_backup(self, guild: discord.Guild) -> str:
        """Create a backup of the server configuration"""
        backup_data = {
            "server_name": guild.name,
            "backup_timestamp": str(datetime.now()),
            "server_id": guild.id,
            "roles": [],
            "categories": [],
            "channels": [],
            "emojis": [],
        }

        # Backup roles (excluding @everyone)
        for role in guild.roles[1:]:  # Skip @everyone role
            role_data = {
                "name": role.name,
                "permissions": role.permissions.value,
                "color": role.color.value,
                "hoist": role.hoist,
                "mentionable": role.mentionable,
                "position": role.position
            }
            backup_data["roles"].append(role_data)

        # Backup categories
        for category in guild.categories:
            category_data = {
                "name": category.name,
                "position": category.position,
                "overwrites": []
            }
            for target, overwrite in category.overwrites.items():
                category_data["overwrites"].append({
                    "id": target.id,
                    "type": "role" if isinstance(target, discord.Role) else "member",
                    "allow": overwrite.pair()[0].value,
                    "deny": overwrite.pair()[1].value
                })
            backup_data["categories"].append(category_data)

        # Backup channels
        for channel in guild.channels:
            if isinstance(channel, discord.TextChannel):
                channel_data = {
                    "name": channel.name,
                    "type": "text",
                    "position": channel.position,
                    "category": channel.category.id if channel.category else None,
                    "topic": channel.topic,
                    "slowmode_delay": channel.slowmode_delay,
                    "nsfw": channel.is_nsfw(),
                    "overwrites": []
                }
            elif isinstance(channel, discord.VoiceChannel):
                channel_data = {
                    "name": channel.name,
                    "type": "voice",
                    "position": channel.position,
                    "category": channel.category.id if channel.category else None,
                    "user_limit": channel.user_limit,
                    "bitrate": channel.bitrate,
                    "overwrites": []
                }
            else:
                continue

            for target, overwrite in channel.overwrites.items():
                channel_data["overwrites"].append({
                    "id": target.id,
                    "type": "role" if isinstance(target, discord.Role) else "member",
                    "allow": overwrite.pair()[0].value,
                    "deny": overwrite.pair()[1].value
                })
            backup_data["channels"].append(channel_data)

        # Backup emojis
        for emoji in guild.emojis:
            emoji_data = {
                "name": emoji.name,
                "url": str(emoji.url)
            }
            backup_data["emojis"].append(emoji_data)

        # Save backup to file
        backup_filename = f"{self.backup_folder}/{guild.id}_{int(datetime.now().timestamp())}.json"
        async with aiofiles.open(backup_filename, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(backup_data, indent=4))

        return backup_filename

    async def load_backup(self, backup_id: str, guild: discord.Guild) -> bool:
        """Load and apply a backup to the server"""
        try:
            backup_file = f"{self.backup_folder}/{backup_id}.json"
            async with aiofiles.open(backup_file, 'r', encoding='utf-8') as f:
                backup_data = json.loads(await f.read())

            # Clear existing roles (except @everyone)
            for role in guild.roles[1:]:
                try:
                    await role.delete()
                except discord.Forbidden:
                    continue

            # Recreate roles
            for role_data in reversed(backup_data["roles"]):
                try:
                    await guild.create_role(
                        name=role_data["name"],
                        permissions=discord.Permissions(role_data["permissions"]),
                        color=discord.Color(role_data["color"]),
                        hoist=role_data["hoist"],
                        mentionable=role_data["mentionable"]
                    )
                except discord.Forbidden:
                    continue

            # Clear existing channels
            for channel in guild.channels:
                try:
                    await channel.delete()
                except discord.Forbidden:
                    continue

            # Recreate categories
            for category_data in backup_data["categories"]:
                try:
                    await guild.create_category(name=category_data["name"])
                except discord.Forbidden:
                    continue

            # Recreate channels
            for channel_data in backup_data["channels"]:
                try:
                    if channel_data["type"] == "text":
                        await guild.create_text_channel(
                            name=channel_data["name"],
                            topic=channel_data["topic"],
                            nsfw=channel_data["nsfw"],
                            slowmode_delay=channel_data["slowmode_delay"]
                        )
                    elif channel_data["type"] == "voice":
                        await guild.create_voice_channel(
                            name=channel_data["name"],
                            bitrate=channel_data["bitrate"],
                            user_limit=channel_data["user_limit"]
                        )
                except discord.Forbidden:
                    continue

            return True
        except Exception as e:
            print(f"Error loading backup: {e}")
            return False

backup_system = BackupSystem()

@bot.event
async def on_ready():
    print(f'Bot is ready! Logged in as {bot.user.name}')

@bot.command(name='backup')
@commands.has_permissions(administrator=True)
async def create_backup(ctx):
    """Create a backup of the server configuration"""
    try:
        async with ctx.typing():
            backup_file = await backup_system.save_backup(ctx.guild)
            await ctx.send(f"✅ Backup created successfully! Backup ID: `{os.path.basename(backup_file)}`\n"
                          f"Use `!restore <backup_id>` to restore this backup.")
    except Exception as e:
        await ctx.send(f"❌ An error occurred while creating the backup: {str(e)}")

@bot.command(name='restore')
@commands.has_permissions(administrator=True)
async def restore_backup(ctx, backup_id: str):
    """Restore a server backup"""
    try:
        async with ctx.typing():
            confirmation_message = await ctx.send("⚠️ Warning: This will overwrite the current server configuration. "
                                               "Are you sure? React with ✅ to confirm.")
            await confirmation_message.add_reaction("✅")

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) == "✅"

            try:
                await bot.wait_for('reaction_add', timeout=30.0, check=check)
            except asyncio.TimeoutError:
                await ctx.send("Restoration cancelled - timeout reached.")
                return

            success = await backup_system.load_backup(backup_id, ctx.guild)
            if success:
                await ctx.send("✅ Backup restored successfully!")
            else:
                await ctx.send("❌ Failed to restore backup.")
    except Exception as e:
        await ctx.send(f"❌ An error occurred while restoring the backup: {str(e)}")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command!")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Unknown command!")
    else:
        await ctx.send(f"❌ An error occurred: {str(error)}")

# Add your bot token in a .env file
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    bot.run(os.getenv('DISCORD_TOKEN'))
