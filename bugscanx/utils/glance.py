import os
import threading
from datetime import datetime, timedelta

import requests
from rich.console import Console

console = Console()

LOCAL_MESSAGE_FILE = ".message.txt"
URL = "https://raw.githubusercontent.com/for-testing-something/test1/refs/heads/main/message.txt"

def fetch_and_store_message():
    try:
        response = requests.get(URL, timeout=5)
        if response.ok:
            with open(LOCAL_MESSAGE_FILE, "w", encoding="utf-8") as file:
                file.write(response.text.strip())
    except:
        pass

def get_local_message():
    if os.path.exists(LOCAL_MESSAGE_FILE) and datetime.now() - datetime.fromtimestamp(os.path.getmtime(LOCAL_MESSAGE_FILE)) < timedelta(hours=3):
         with open(LOCAL_MESSAGE_FILE, "r", encoding="utf-8") as file:
            return file.read().strip()
    
    threading.Thread(target=fetch_and_store_message, daemon=True).start()
    return None

def display_message():
    message = get_local_message()
    if message:
        console.print(f"{message}\n")
