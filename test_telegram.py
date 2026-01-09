import requests

# Telegram configuration
TELEGRAM_TOKEN = "8183629835:AAHrBeapTCIK33pxUBcWLDmlWawZW0vBeIk"
TELEGRAM_CHAT_ID = "8102277793"

def send_telegram_message(message):
    """Gui thong bao qua Telegram."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print("[SUCCESS] Telegram notification sent.")
        else:
            print(f"[WARNING] Failed to send Telegram message: {response.text}")
    except Exception as e:
        print(f"[ERROR] Exception sending Telegram message: {e}")

# Test the function
send_telegram_message("Test message from os-mini-clone script.")