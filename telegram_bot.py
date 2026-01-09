import requests
import time
import re
import single_scraper

# Telegram configuration
TELEGRAM_TOKEN = "8183629835:AAHrBeapTCIK33pxUBcWLDmlWawZW0vBeIk"
TELEGRAM_CHAT_ID = "8102277793"  # Có thể không cần nếu reply trong chat

BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

def get_updates(offset=None):
    """Lấy tin nhắn mới từ Telegram."""
    url = f"{BASE_URL}/getUpdates"
    params = {"timeout": 30}
    if offset:
        params["offset"] = offset
    response = requests.get(url, params=params)
    return response.json()

def send_message(chat_id, text):
    """Gửi tin nhắn."""
    url = f"{BASE_URL}/sendMessage"
    data = {"chat_id": chat_id, "text": text}
    requests.post(url, data=data)

def is_valid_url(text):
    """Kiểm tra xem text có chứa URL Zendesk article không."""
    return "support.optisigns.com/hc/en-us/articles/" in text

def extract_url(text):
    """Trích xuất URL từ text."""
    urls = re.findall(r'https?://[^\s]+', text)
    for url in urls:
        if "support.optisigns.com/hc/en-us/articles/" in url:
            return ("article", url)
        elif "support.optisigns.com/api/v2/help_center/articles.json" in url:
            return ("api", url)
    return None

def main():
    print("🤖 Telegram Bot đang chạy... Nhấn Ctrl+C để dừng.")
    last_update_id = None
    
    while True:
        try:
            updates = get_updates(last_update_id)
            
            if updates.get("ok"):
                for update in updates["result"]:
                    update_id = update["update_id"]
                    last_update_id = update_id + 1
                    
                    if "message" in update:
                        message = update["message"]
                        chat_id = message["chat"]["id"]
                        text = message.get("text", "")
                        
                        print(f"📨 Nhận tin nhắn: '{text}' từ chat {chat_id}")
                        
                        if text:
                            url_info = extract_url(text)
                            if url_info:
                                url_type, url = url_info
                                if url_type == "article":
                                    print(f"📥 Nhận URL article: {url}")
                                    result = single_scraper.scrape_single_article(url)
                                    if result["success"]:
                                        if result.get("status") == "skipped":
                                            message = f"ℹ️ Bài viết đã tồn tại và không thay đổi: {result['title']}\nLink: {result['url']}"
                                        else:
                                            message = f"✅ Đã scrape bài viết: {result['title']}\nLink: {result['url']}\nLưu tại: {result['filename']}"
                                    else:
                                        message = result["message"]
                                    send_message(chat_id, message)
                                elif url_type == "api":
                                    print(f"📥 Nhận URL API: {url}")
                                    # Import scraper để gọi scrape_data
                                    import scraper
                                    stats = scraper.scrape_data(url)
                                    if stats:
                                        message = f"✅ Đã scrape tất cả bài viết từ API.\nThống kê: Thêm {stats['added']}, Cập nhật {stats['updated']}, Bỏ qua {stats['skipped']}."
                                    else:
                                        message = "❌ Lỗi khi scrape từ API."
                                    send_message(chat_id, message)
                            else:
                                # Tin nhắn không chứa URL, bỏ qua
                                pass
            time.sleep(1)  # Tránh spam API
        except KeyboardInterrupt:
            print("🛑 Dừng bot.")
            break
        except Exception as e:
            print(f"❌ Lỗi: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()