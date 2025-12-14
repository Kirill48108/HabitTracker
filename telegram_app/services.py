import os
import requests

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_DEFAULT_PARSE_MODE = os.getenv("TELEGRAM_DEFAULT_PARSE_MODE", "HTML")

def send_telegram_message(chat_id: str, text: str, parse_mode: str | None = None) -> None:
    if not TELEGRAM_BOT_TOKEN:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode or TELEGRAM_DEFAULT_PARSE_MODE,
        "disable_web_page_preview": True,
    }
    try:
        requests.post(url, json=payload, timeout=5)
    except requests.RequestException:
        # intentionally swallow errors
        pass
