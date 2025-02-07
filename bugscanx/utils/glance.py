import os
import json
import requests
import threading
from rich.text import Text
from rich.style import Style
from rich.console import Console
from datetime import datetime, timedelta

console = Console()

LOCAL_MESSAGE_FILE = ".message.json"

def fetch_and_store_message():
    url = "https://raw.githubusercontent.com/for-testing-something/test1/refs/heads/main/message.json"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            content = response.text.strip()
            with open(LOCAL_MESSAGE_FILE, "w", encoding="utf-8") as file:
                file.write(content)
            return True, None
    except Exception:
        pass
    return False, None

def load_local_message():
    if not os.path.exists(LOCAL_MESSAGE_FILE):
        return None, None
    try:
        with open(LOCAL_MESSAGE_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
            message = data.get("message", "").strip()
            if not message:
                return None, None
            styles = data.get("styles", [])
            if not styles:
                return Text(message), None
            styled_message = Text(message)
            for style in styles:
                text = style.get("text", "")
                color = style.get("color", "white")
                start_index = message.find(text)
                if start_index != -1:
                    end_index = start_index + len(text)
                    styled_message.stylize(Style(color=color), start_index, end_index)
            return styled_message, None
    except Exception:
        pass
    return None, None

def is_local_message_outdated():
    if not os.path.exists(LOCAL_MESSAGE_FILE):
        return True
    try:
        file_mod_time = datetime.fromtimestamp(os.path.getmtime(LOCAL_MESSAGE_FILE))
        current_time = datetime.now()
        if current_time - file_mod_time > timedelta(hours=3):
            return True
        return False
    except Exception:
        return True

def display_message():
    try:
        message, _ = load_local_message()
        if message:
            console.print(message, style="bold")
            console.print(" ")

        def fetch_and_update():
            if is_local_message_outdated():
                fetch_and_store_message()
        thread = threading.Thread(target=fetch_and_update)
        thread.daemon = True
        thread.start()
    except Exception:
        pass
