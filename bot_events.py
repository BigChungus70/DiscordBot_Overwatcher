import asyncio
from datetime import datetime, timedelta
from math import e
from helper_methods import *

import time


async def handle_voice_state_update(member, before, after):
    if member.bot:
        return

    server_list = load_server_list()
    guild_id = str(member.guild.id)

    if guild_id not in server_list:
        return

    tracked_channels = server_list[guild_id].get("tracked_channels_ids", [])

    sessions_data = load_sessions()
    history_data = load_history()
    member_id = str(member.id)

    if guild_id not in sessions_data:
        sessions_data[guild_id] = {}
    if guild_id not in history_data:
        history_data[guild_id] = {}

    if (
        after.channel
        and after.channel.id in tracked_channels
        and member_id not in sessions_data[guild_id]
    ):
        sessions_data[guild_id][member_id] = {"join_time": time.time()}

    if (
        before.channel
        and before.channel.id in tracked_channels
        and member_id in sessions_data[guild_id]
    ):
        if not after.channel or after.channel.id not in tracked_channels:
            duration = time.time() - sessions_data[guild_id][member_id]["join_time"]
            if member_id not in history_data[guild_id]:
                history_data[guild_id][member_id] = {"total_time": 0}
            history_data[guild_id][member_id]["total_time"] += duration
            del sessions_data[guild_id][member_id]
            save_history(history_data)

    save_sessions(sessions_data)


async def checkpoint(bot):
    await bot.wait_until_ready()
    checkpoint_interval = 300  # 5 minutes
    last_checkpoint = time.time()

    while not bot.is_closed():
        channels = []
        for guild, items in load_server_list().items():
            channels.extend(items.get("tracked_channels_ids", []))
        try:
            sessions_data = load_sessions()
            history_data = load_history()
            current_time = time.time()

            for channel_id in channels:
                channel = bot.get_channel(channel_id)
                if not channel:
                    continue

                guild_id = str(channel.guild.id)

                if guild_id not in sessions_data:
                    sessions_data[guild_id] = {}
                if guild_id not in history_data:
                    history_data[guild_id] = {}

                active_member_ids = {
                    str(member.id) for member in channel.members if not member.bot
                }
                session_member_ids = set(sessions_data[guild_id].keys())

                for member in channel.members:
                    if member.bot:
                        continue
                    member_id = str(member.id)
                    if member_id not in sessions_data[guild_id]:
                        sessions_data[guild_id][member_id] = {"join_time": current_time}

                if current_time - last_checkpoint >= checkpoint_interval:
                    for member_id in session_member_ids & active_member_ids:
                        duration = (
                            current_time
                            - sessions_data[guild_id][member_id]["join_time"]
                        )
                        if member_id not in history_data[guild_id]:
                            history_data[guild_id][member_id] = {"total_time": 0}
                        history_data[guild_id][member_id]["total_time"] += duration
                        sessions_data[guild_id][member_id]["join_time"] = current_time

                
                members_who_left = session_member_ids - active_member_ids
                for member_id in members_who_left:
                    duration = (
                        current_time - sessions_data[guild_id][member_id]["join_time"]
                    )
                    if member_id not in history_data[guild_id]:
                        history_data[guild_id][member_id] = {"total_time": 0}
                    history_data[guild_id][member_id]["total_time"] += duration
                    del sessions_data[guild_id][member_id]

                save_sessions(sessions_data)
                save_history(history_data)

            if current_time - last_checkpoint >= checkpoint_interval:
                last_checkpoint = current_time

        except Exception as e:
            print(e)

        await asyncio.sleep(10)
