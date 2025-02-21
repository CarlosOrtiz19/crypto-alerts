import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Recuperar las variables de entorno
TOKEN = os.environ.get("TELEGRAM_TOKEN", "change_me")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "change_me")


def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    response = requests.post(url, json=payload)
    print(response.ok)

    return response.json()
