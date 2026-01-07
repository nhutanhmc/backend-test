import requests
import os
from markdownify import markdownify as md
import re

# URL API lấy bài viết của OptiSigns
ZENDESK_URL = "https://support.optisigns.com/api/v2/help_center/articles.json?per_page=30"
OUTPUT_DIR = "data"

def clean_filename(title):
    # Làm sạch tên file để tránh lỗi hệ thống file
    return re.sub(r'[\\/*?:"<>|]', "", title).strip().replace(" ", "_")

def scrape_data():
    print(f"--- Đang kết nối API: {ZENDESK_URL} ---")
    
    try:
        response = requests.get(ZENDESK_URL)
        
        if response.status_code == 200:
            data = response.json()
            articles = data['articles']
            
            print(f"✅ Tìm thấy {len(articles)} bài viết. Bắt đầu xử lý...")

            # Đảm bảo thư mục data tồn tại
            os.makedirs(OUTPUT_DIR, exist_ok=True)

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

                # Ghi file
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(file_content)
                
                count += 1
                # In dòng này để biết tiến độ (bỏ comment nếu muốn log chi tiết)
                # print(f"[{count}] Đã lưu: {filename}")

            print(f"\n🎉 SCRAPE XONG! Đã lưu {count} file vào thư mục '{OUTPUT_DIR}/'.")
        else:
            print(f"❌ Lỗi kết nối API: {response.status_code}")

    except Exception as e:
        print(f"❌ Có lỗi khi cào dữ liệu: {e}")

if __name__ == "__main__":
    scrape_data()