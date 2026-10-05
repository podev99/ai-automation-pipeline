import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def send_telegram_message(message: str) -> bool:
    """Sends a text message to the configured Telegram chat via Telegram Bot API."""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        print("Error: Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID in environment.")
        return False

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Failed to send Telegram message: {e}")
        return False


if __name__ == "__main__":
    # Test sending a message
    test_message = "**Test Notification**\nThis is a test message from your AI Pipeline Telegram Notifier."
    success = send_telegram_message(test_message)
    print(f"Message sent successfully: {success}")