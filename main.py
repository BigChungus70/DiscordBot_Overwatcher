import discord
from discord import app_commands
from discord.ext import commands, tasks
import asyncio
import config
from helper_methods import *
import bot_events
from bot_commands import check_history, check_status, check_user, remove_log, remove_voice, reset_setup, setup_log, setup_voice, test_setup


# Bot setup
class TrackingBot(commands.Bot):
    async def setup_hook(self):
        self.loop.create_task(bot_events.checkpoint(bot=self))


intents = discord.Intents.default()
intents.voice_states = True
intents.message_content = True
intents.members = True
bot = TrackingBot(command_prefix="!", intents=intents)

# Data
history_data = load_history()
server_list_data = load_server_list()
sessions_data = load_sessions()

# Events
@bot.event
async def on_ready():
    print(f"{bot.user} has logged in and is ready to track!")
    print(f"Bot is in {len(bot.guilds)} guild(s)")


@bot.event
async def on_voice_state_update(member, before, after):
    await bot_events.handle_voice_state_update(member, before, after)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(
            f"Missing required arguments. Use `{bot.command_prefix}help` for command usage."
        )
    elif isinstance(error, commands.CommandNotFound):
        pass
    elif isinstance(error, commands.UserNotFound):
        await ctx.send("User not found.")
    else:
        print(f"An error occurred: {error}")


# Commands
@bot.command(name="status")
async def cmd_check_status(ctx):
    """Check current sessions."""
    await check_status(ctx)


@bot.command(name="history")
async def cmd_check_history(ctx):
    """Check all users' history."""
    await check_history(ctx)


@bot.command(name="check_user")
async def cmd_check_user(ctx, user: discord.User):
    """Check a specific user's history."""
    await check_user(ctx, user)

@bot.command(name="add_voice")
async def cmd_setup_voice(ctx, tracked_channel: discord.VoiceChannel):
    """Add a specific channel to track."""
    await setup_voice(ctx, tracked_channel, bot)


@bot.command(name="add_log")
async def cmd_setup_log(ctx, log_channel: discord.TextChannel):
    """Add a specific channel to write log in."""
    await setup_log(ctx, log_channel, bot)


@bot.command(name="reset_setup")
async def cmd_reset_setup(ctx):
    """Stop tracking all set up channels and loggging."""
    await reset_setup(ctx, bot)


@bot.command(name="rm_voice")
async def cmd_remove_voice(ctx, voice_channel: discord.VoiceChannel):
    """Stop tracking a specific channel."""
    await remove_voice(ctx, voice_channel, bot)


@bot.command(name="rm_log")
async def cmd_remove_log(ctx, log_channel: discord.TextChannel):
    """Remove a specific log channel."""
    await remove_log(ctx, log_channel, bot)


@bot.command(name="test_setup")
async def cmd_test_setup(ctx):
    """See the current setup for this server."""
    await test_setup(ctx, bot)


if __name__ == "__main__":
    bot.run(config.TOKEN)
