import json
import os
from datetime import timedelta

# Base data folder
DATA_FOLDER = os.path.join(os.path.dirname(__file__), "data")


def ensure_path(filename: str) -> str:
    """Ensure the data folder exists and return the full path for a file."""
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)
    return os.path.join(DATA_FOLDER, filename)


def format_duration(seconds):
    total_seconds = int(seconds)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60

    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"


def save_history(data, filename="history.json"):
    path = ensure_path(filename)
    serializable = {}
    for guild_id, members in data.items():
        serializable[str(guild_id)] = {}
        for member_id, info in members.items():
            serializable[str(guild_id)][str(member_id)] = {
                "total_time": info["total_time"]
            }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(serializable, f, indent=4)


def load_history(filename="history.json"):
    path = ensure_path(filename)
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}


def save_server_list(data, filename="server_list.json"):
    path = ensure_path(filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def load_server_list(filename="server_list.json"):
    path = ensure_path(filename)
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}


def save_sessions(data, filename="sessions.json"):
    path = ensure_path(filename)
    serializable = {}
    for guild_id, members in data.items():
        serializable[str(guild_id)] = {}
        for member_id, info in members.items():
            serializable[str(guild_id)][str(member_id)] = {
                "join_time": info["join_time"]
            }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(serializable, f, indent=4)


def load_sessions(filename="sessions.json"):
    path = ensure_path(filename)
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                for guild_id, guild_data in data.items():
                    if not isinstance(guild_data, dict):
                        data[guild_id] = {}
                return data
            return {}
    except json.JSONDecodeError:
        return {}
