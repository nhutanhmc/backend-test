import requests
import os
from markdownify import markdownify as md
import re
import hashlib

OUTPUT_DIR = "data"

def calculate_md5(content):
    """Tinh ma Hash MD5 cua noi dung."""
    hash_md5 = hashlib.md5()
    hash_md5.update(content.encode('utf-8'))
    return hash_md5.hexdigest()

def clean_filename(title):
    # Làm sạch tên file để tránh lỗi hệ thống file
    return re.sub(r'[\\/*?:"<>|]', "", title).strip().replace(" ", "_")

def scrape_single_article(url):
    """
    Scrape một bài viết cụ thể từ URL Zendesk.
    URL ví dụ: https://support.optisigns.com/hc/en-us/articles/360012345678-How-to-Setup
    """
    print(f"--- Đang scrape bài viết từ: {url} ---")
    
    try:
        # Kiểm tra URL có phải Zendesk article không
        if "support.optisigns.com/hc/en-us/articles/" not in url:
            return {
                "success": False,
                "message": "❌ URL không hợp lệ. Chỉ hỗ trợ bài viết từ OptiSigns Support."
            }
        
        # Trích xuất article ID từ URL
        # URL pattern: /articles/{id}-{title}
        match = re.search(r'/articles/(\d+)', url)
        if not match:
            return {
                "success": False,
                "message": "❌ Không thể trích xuất ID bài viết từ URL."
            }
        
        article_id = match.group(1)
        
        # Tạo URL API cho bài viết cụ thể
        api_url = f"https://support.optisigns.com/api/v2/help_center/articles/{article_id}.json"
        
        response = requests.get(api_url)
        
        if response.status_code == 200:
            data = response.json()
            article = data['article']
            
            title = article['title']
            html_body = article['body']
            html_url = article['html_url']
            art_id = article['id']
            
            if not html_body:
                return {
                    "success": False,
                    "message": "❌ Bài viết không có nội dung."
                }
            
            # Chuyển đổi HTML -> Markdown
            markdown_body = md(html_body, heading_style="ATX")
            
            # Format nội dung
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
                    return {
                        "success": True,
                        "title": title,
                        "filename": filename,
                        "url": html_url,
                        "status": "skipped"
                    }
                else:
                    print(f"📝 File thay đổi, cập nhật: {filename}")
            else:
                print(f"🆕 File mới: {filename}")
            
            # Đảm bảo thư mục tồn tại
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            
            # Ghi file
            with open(filename, "w", encoding="utf-8") as f:
                f.write(file_content)
            
            print(f"✅ Đã scrape và lưu: {filename}")
            return {
                "success": True,
                "title": title,
                "filename": filename,
                "url": html_url,
                "status": "saved"
            }
        else:
            return {
                "success": False,
                "message": f"❌ Lỗi API: {response.status_code}"
            }
    
    except Exception as e:
        return {
            "success": False,
            "message": f"❌ Lỗi khi scrape: {e}"
        }

if __name__ == "__main__":
    # Test với URL mẫu
    test_url = "https://support.optisigns.com/hc/en-us/articles/31695220475283"
    result = scrape_single_article(test_url)
    print(result)