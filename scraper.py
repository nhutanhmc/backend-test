import requests
import os
from markdownify import markdownify as md
import re
import hashlib

# URL API lấy bài viết của OptiSigns
ZENDESK_URL = "https://support.optisigns.com/api/v2/help_center/articles.json?per_page=30"
OUTPUT_DIR = "data"

def calculate_md5(content):
    """Tinh ma Hash MD5 cua noi dung."""
    hash_md5 = hashlib.md5()
    hash_md5.update(content.encode('utf-8'))
    return hash_md5.hexdigest()

def clean_filename(title):
    # Làm sạch tên file để tránh lỗi hệ thống file
    return re.sub(r'[\\/*?:"<>|]', "", title).strip().replace(" ", "_")

def scrape_data(url=None):
    if url is None:
        url = ZENDESK_URL
    print(f"--- Đang kết nối API: {url} ---")
    
    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            articles = data['articles']
            
            print(f"✅ Tìm thấy {len(articles)} bài viết. Bắt đầu xử lý...")

            # Đảm bảo thư mục data tồn tại
            os.makedirs(OUTPUT_DIR, exist_ok=True)

            stats = {"added": 0, "updated": 0, "skipped": 0}
            count = 0
            for article in articles:
                # Lấy dữ liệu thô
                title = article['title']
                html_body = article['body']
                html_url = article['html_url']
                art_id = article['id']

                if not html_body:
                    continue

                # Chuyển đổi HTML -> Markdown
                markdown_body = md(html_body, heading_style="ATX")

                # Format nội dung: Link gốc + Markdown
                file_content = f"# {title}\nArticle URL: {html_url}\n\n{markdown_body}"

                # Tạo tên file
                safe_title = clean_filename(title)
                filename = f"{OUTPUT_DIR}/{art_id}_{safe_title}.md"

                # Tính hash của nội dung mới
                new_hash = calculate_md5(file_content)

                # Kiểm tra file đã tồn tại chưa
                if os.path.exists(filename):
                    # Tính hash của file cũ
                    with open(filename, "r", encoding="utf-8") as f:
                        old_content = f.read()
                    old_hash = calculate_md5(old_content)
                    
                    if old_hash == new_hash:
                        print(f"✅ File đã tồn tại và không thay đổi: {filename}")
                        stats["skipped"] += 1
                        continue
                    else:
                        print(f"📝 File thay đổi, cập nhật: {filename}")
                        stats["updated"] += 1
                else:
                    print(f"🆕 File mới: {filename}")
                    stats["added"] += 1

                # Ghi file
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(file_content)
                
                count += 1
                # In dòng này để biết tiến độ (bỏ comment nếu muốn log chi tiết)
                # print(f"[{count}] Đã lưu: {filename}")

            print(f"\n🎉 SCRAPE XONG! Đã lưu {count} file vào thư mục '{OUTPUT_DIR}/'.")
            print(f"Thống kê: Thêm {stats['added']}, Cập nhật {stats['updated']}, Bỏ qua {stats['skipped']}.")
            return stats
        else:
            print(f"❌ Lỗi kết nối API: {response.status_code}")
            return None

    except Exception as e:
        print(f"❌ Có lỗi khi cào dữ liệu: {e}")
        return None

if __name__ == "__main__":
    scrape_data()