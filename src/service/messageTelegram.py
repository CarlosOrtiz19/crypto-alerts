import requests

TOKEN = "change_me"
CHAT_ID = "change_me"


def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    response = requests.post(url, json=payload)

    return response.json()
