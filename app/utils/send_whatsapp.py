import requests
import os

ACCESS_TOKEN = os.getenv("WHATSAPP_TOKEN")
instance_id = os.getenv("WHATSAPP_INSTANCE_ID")

def send_whatsapp_message(phone: str, message: str):
    url = f"https://api.wapilot.net/api/v2/{instance_id}/send-message"

    headers = {
        "token": ACCESS_TOKEN,
        "Content-Type": "application/json"
    }

    data = {
        "chat_id": "2"+phone,
        "text": message
    }

    res = requests.post(url, headers=headers, json=data)

    return res.json()

def send_messages(numbers, message):
    for phone_number in numbers:
        try:
            res = send_whatsapp_message(phone_number, message)
            print(phone_number, res)
        except Exception as e:
            print("Failed sending to ", phone_number, e)