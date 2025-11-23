import discord
from helper_methods import *
import time
async def check_status(ctx):
    guild_id = str(ctx.guild.id)
    sessions_data = load_sessions()
    sessions = sessions_data.get(guild_id, {})

    if len(sessions) == 0:
        await ctx.send("No sessions found.")
        return

    status = "**Active Sessions:**\n"
    current_time = time.time()
    for member_id, session_info in sessions.items():
        member = ctx.guild.get_member(int(member_id))
        if member:
            duration = int(current_time - session_info["join_time"])
            status += f"- {member.mention}: {format_duration(duration)}\n"

    await ctx.send(status)


async def check_history(ctx):
    guild_id = str(ctx.guild.id)
    history_data = load_history()
    history = history_data.get(guild_id, {})

    if len(history) == 0:
        await ctx.send("No history found.")
        return

    status = "**History:**\n"
    for member_id, member_info in history.items():
        member = ctx.guild.get_member(int(member_id))
        if member:
            status += f"- {member.mention}: {format_duration(member_info['total_time'])}\n"

    await ctx.send(status)


async def check_user(ctx, user):
    guild_id = str(ctx.guild.id)
    history_data = load_history()
    sessions_data = load_sessions()
    member_id = str(user.id)
    
    total_time = 0

    if guild_id in history_data and member_id in history_data[guild_id]:
        total_time += history_data[guild_id][member_id]["total_time"]

    if guild_id in sessions_data and member_id in sessions_data[guild_id]:
        current_time = time.time()
        total_time += current_time - sessions_data[guild_id][member_id]["join_time"]

    if total_time == 0:
        await ctx.send("No history found.")
        return

    await ctx.send(f"{user.mention}: {format_duration(total_time)}")


async def setup_voice(ctx, tracked_channel: discord.VoiceChannel , bot):
    app_info = await bot.application_info()
    owner_id = app_info.owner.id
    if not ctx.author.guild_permissions.administrator and ctx.author.id != owner_id:
        await ctx.send(
            "You need administrator permissions to use this command cuz you aren't the very humungous big chungus."
        )
        return
    server_list_data = load_server_list()
    guild_id = str(ctx.guild.id)
    if guild_id not in server_list_data:
        server_list_data[guild_id] = {"tracked_channels_ids": [], "log_channel_ids": []}
        save_server_list(server_list_data)

    if tracked_channel.id not in server_list_data[guild_id]["tracked_channels_ids"]:
        server_list_data[guild_id]["tracked_channels_ids"].append(tracked_channel.id)
        save_server_list(server_list_data)

    await ctx.send(
        f"Setup completed\nUsers in: {tracked_channel.mention} will be tracked."
    )

async def setup_log(ctx, log_channel: discord.TextChannel, bot):
    app_info = await bot.application_info()
    owner_id = app_info.owner.id
    if not ctx.author.guild_permissions.administrator and ctx.author.id != owner_id:
        await ctx.send(
            "You need administrator permissions to use this command cuz you aren't the very humungous big chungus."
        )
        return
    server_list_data = load_server_list()
    guild_id = str(ctx.guild.id)
    if guild_id not in server_list_data:
        server_list_data[guild_id] = {"tracked_channels_ids": [], "log_channel_ids": []}
        save_server_list(server_list_data)

    if log_channel.id not in server_list_data[guild_id]["log_channel_ids"]:
        server_list_data[guild_id]["log_channel_ids"].append(log_channel.id)
        save_server_list(server_list_data)

    await ctx.send(f"Setup completed\nLogs will be sent to: {log_channel.mention}")


async def reset_setup(ctx, bot):
    guild_id = str(ctx.guild.id)
    app_info = await bot.application_info()
    owner_id = app_info.owner.id

    if not ctx.author.guild_permissions.administrator and ctx.author.id != owner_id:
        await ctx.send(
            "You need administrator permissions or be the bot owner to do this cuz you aren't the very humungous big chungus."
        )
        return

    server_list_data = load_server_list()
    if guild_id in server_list_data:
        save_server_list(server_list_data)
        await ctx.send("All setups for this server have been nuked.")
    else:
        await ctx.send("No setup found for this server. Nothing to nuke.")

async def remove_voice(ctx, voice_channel, bot):
    guild_id = str(ctx.guild.id)
    app_info = await bot.application_info()
    owner_id = app_info.owner.id

    if not ctx.author.guild_permissions.administrator and ctx.author.id != owner_id:
        await ctx.send(
            "You need administrator permissions or be the bot owner to do this cuz you aren't the very humungous big chungus."
        )
        return
    server_list_data = load_server_list()
    if (
        guild_id in server_list_data
        and voice_channel.id in server_list_data[guild_id]["tracked_channels_ids"]
    ):
        server_list_data[guild_id]["tracked_channels_ids"].remove(voice_channel.id)
        save_server_list(server_list_data)
        await ctx.send(f"{voice_channel.mention} has been removed from tracked channels.")
    else:
        await ctx.send("That channel isn't being tracked.")


async def remove_log(ctx, log_channel, bot):
    guild_id = str(ctx.guild.id)
    app_info = await bot.application_info()
    owner_id = app_info.owner.id

    if not ctx.author.guild_permissions.administrator and ctx.author.id != owner_id:
        await ctx.send(
            "You need administrator permissions or be the bot owner to do this cuz you aren't the very humungous big chungus."
        )
        return
    server_list_data = load_server_list()
    if (
        guild_id in server_list_data
        and log_channel.id in server_list_data[guild_id]["log_channel_ids"]
    ):
        server_list_data[guild_id]["log_channel_ids"].remove(log_channel.id)
        save_server_list(server_list_data)
        await ctx.send(f"{log_channel.mention} has been removed from logging channels.")
    else:
        await ctx.send("That channel isn't being logged to.")


async def test_setup(ctx, bot):
    server_list_data = load_server_list()
    server_data = server_list_data.get(str(ctx.guild.id))
    if not server_data:
        await ctx.send(
            f"No configuration found for this server. Use `{bot.command_prefix}setup_voice <tracked_channel>` and `{bot.command_prefix}setup_log <log_channel>` first."
        )
        return

    status = "**Bot Setup Status:**\n"

    status += f"**Tracked Channels:**\n"
    for channel_id in server_data["tracked_channels_ids"]:
        channel = ctx.guild.get_channel(channel_id)
        status += f"- {channel.mention}\n"

    status += f"**Log Channels:**\n"
    for channel_id in server_data["log_channel_ids"]:
        channel = ctx.guild.get_channel(channel_id)
        status += f"- {channel.mention}\n"

    await ctx.send(status)
