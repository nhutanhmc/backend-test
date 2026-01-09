# OptiBot Auto - AI Assistant for OptiSigns Knowledge Base

OptiBot Auto là một công cụ tự động để scrape dữ liệu từ trang hỗ trợ OptiSigns, upload lên OpenAI Vector Store, và tạo AI Assistant để trả lời câu hỏi dựa trên kiến thức đó. Dự án này giúp bạn có một chatbot thông minh cho OptiSigns mà không cần code nhiều.

## 🚀 Tính năng chính
- **Tự động scrape**: Lấy dữ liệu từ API OptiSigns và lưu thành file Markdown.
- **Upload thông minh**: Chỉ upload file mới hoặc thay đổi, tránh trùng lặp.
- **AI Assistant**: Tạo bot trên OpenAI để trả lời câu hỏi.
- **Telegram Chatbot**: Gửi link bài viết vào Telegram, bot sẽ tự động scrape và báo cáo.
- **Docker ready**: Chạy dễ dàng với Docker, không cần cài Python trên máy.
- **Zero config**: Tự động setup vector store và assistant lần đầu.

## 📋 Yêu cầu
- **Docker**: Phiên bản mới nhất (có thể tải từ [docker.com](https://www.docker.com/)).
- **OpenAI API Key**: Đăng ký tài khoản OpenAI và lấy API key từ [platform.openai.com](https://platform.openai.com/account/api-keys). Bạn cần có credit để dùng API (khoảng $0.01-0.05 cho mỗi lần chạy).
- **Telegram Bot Token**: Tạo bot qua [@BotFather](https://t.me/BotFather) trên Telegram để sử dụng Telegram chatbot.

## 🛠️ Cài đặt

### Bước 1: Clone repo
```bash
git clone https://github.com/your-username/os-mini-clone.git
cd os-mini-clone
```

### Bước 2: Build Docker image
```bash
docker build -t optibot:v1 .
```
- Lệnh này sẽ tạo image `optibot:v1` từ Dockerfile. Có thể mất vài phút lần đầu.

## ▶️ Chạy

### Lần đầu (Setup)
Chạy lệnh sau để setup vector store và assistant:
```bash
docker run --rm -e OPENAI_API_KEY="your_api_key_here" -v ${PWD}/memory:/app/memory optibot:v1
```
- Thay `your_api_key_here` bằng API key của bạn.
- `-v ${PWD}/memory:/app/memory`: Mount thư mục `memory` để lưu trạng thái (IDs và file hashes). **Quan trọng**: Không bỏ dòng này, nếu không dữ liệu sẽ mất mỗi lần chạy.

### Lần sau (Update)
Chạy lại lệnh trên để scrape data mới và update assistant. Chỉ file thay đổi mới được upload.

## 💬 Telegram Chatbot

### Cơ chế
- **Scrape bài viết cụ thể**: Gửi link bài viết (vd: `https://support.optisigns.com/hc/en-us/articles/123`) để scrape bài đó.
- **Scrape tất cả từ API**: Gửi link API (vd: `https://support.optisigns.com/api/v2/help_center/articles.json?per_page=40`) để scrape tất cả.
- **Kiểm tra cập nhật**: Bot tự động kiểm tra file có thay đổi không (dùng MD5 hash), nếu không thì skip.
- **Báo cáo chi tiết**: Bot gửi thông báo với thống kê (Thêm, Cập nhật, Bỏ qua).

### Sử dụng

**Bước 1: Cấu hình Telegram**
Mở file `telegram_bot.py` và điền token:
```python
TELEGRAM_TOKEN = "your_bot_token"
TELEGRAM_CHAT_ID = "your_chat_id"
```

**Bước 2: Chạy bot**
```bash
python telegram_bot.py
```

**Bước 3: Gửi lệnh vào chat Telegram**
- Gửi link bài viết: `https://support.optisigns.com/hc/en-us/articles/31695220475283`
  - Bot sẽ scrape bài viết và phản hồi:
  ```
  ✅ Đã scrape bài viết: [Tên bài viết]
  Link: [URL gốc]
  Lưu tại: [Đường dẫn file]
  ```

- Gửi link API để scrape tất cả: `https://support.optisigns.com/api/v2/help_center/articles.json?per_page=30`
  - Bot sẽ scrape tất cả bài viết và báo cáo:
  ```
  ✅ Đã scrape tất cả bài viết từ API.
  Thống kê: Thêm 5, Cập nhật 2, Bỏ qua 23.
  ```

- Gửi link cũ (không thay đổi):
  - Bot sẽ báo: `ℹ️ Bài viết đã tồn tại và không thay đổi: [Tên]`

## 📊 Output mẫu
Khi chạy main.py, bạn sẽ thấy:
```
--- STARTING DAILY JOB (ZERO CONFIG - AUTO MEMORY) ---
[INFO] No IDs found. Setting up new resources...
[SUCCESS] Setup Done. IDs saved to memory/state.json

--- STEP 1: SCRAPING DATA ---
--- Đang kết nối API: https://support.optisigns.com/api/v2/help_center/articles.json?per_page=30 ---
✅ Tìm thấy 30 bài viết. Bắt đầu xử lý...

--- STEP 2: PROCESSING FILES ---
[NEW] Found new file: article1.md
✅ Uploaded: article1.md -> ID: file-xxx
...

================ REPORT ================
Total Scanned: 30
Added:         30
Deleted:       0
Updated:       0
Skipped:       0
=======================================
[SUCCESS] Telegram notification sent.
```

## 🔄 Thay đổi so với phiên bản cũ (trước Telegram)

### File mới
- **telegram_bot.py**: Bot Telegram để gửi link và scrape tự động.
- **single_scraper.py**: Module scrape bài viết cụ thể (dùng bởi telegram_bot.py).

### File sửa đổi
- **scraper.py**:
  - Thêm `calculate_md5()` để kiểm tra hash nội dung.
  - Thêm logic filter: Skip file nếu không thay đổi.
  - Trả về stats dict (added, updated, skipped) thay vì chỉ in log.
  - Hỗ trợ tham số URL tùy chỉnh `scrape_data(url=None)`.

- **main.py**:
  - Thêm import `requests` cho Telegram notification.
  - Thêm hàm `send_telegram_message()` để gửi thông báo.
  - Gọi telegram notification khi bắt đầu và kết thúc.

- **ai_manager.py**:
  - Thêm try-except khi tạo OpenAI client để tránh crash nếu không có API key.

### Cấu trúc dữ liệu
- File `.md` giờ được kiểm tra hash MD5 trước khi ghi, để biết có thay đổi không.
- `memory/state.json` lưu trữ thông tin tương tự.

## 🛠️ Troubleshooting

### Lỗi "OPENAI_API_KEY not found"
- Đảm bảo bạn đã set `-e OPENAI_API_KEY="sk-..."` đúng.

### Lỗi "Beta object has no attribute"
- Rebuild image: `docker build -t optibot:v1 .`

### Không có data trong memory/
- Đảm bảo mount volume đúng: `-v ${PWD}/memory:/app/memory`

### Tốn phí OpenAI
- Mỗi lần chạy upload file mới sẽ tốn phí. Nếu chạy nhiều, monitor usage trên OpenAI dashboard.

### File data/ trống
- Script tự động scrape từ OptiSigns API. Nếu API thay đổi, có thể cần update code.

### Bot Telegram không phản hồi
- Kiểm tra token và chat ID đúng.
- Chắc chắn bot đã được start (`/start`) trong chat Telegram.
- Kiểm tra internet connection.

## 📁 Cấu trúc project
```
os-mini-clone/
├── ai_manager.py       # Quản lý OpenAI (vector store, assistant)
├── main.py             # Script chính (scrape + upload + telegram notify)
├── scraper.py          # Scrape tất cả bài viết từ API (dùng bởi main.py)
├── single_scraper.py   # Scrape bài viết cụ thể (dùng bởi telegram_bot.py)
├── telegram_bot.py     # Bot Telegram chatbot
├── data/               # Thư mục lưu file Markdown (tự động tạo)
├── memory/             # Thư mục lưu state (tạo sau lần đầu)
├── Dockerfile          # Docker setup
├── requirements.txt    # Python dependencies
├── .dockerignore        # Ignore files khi build Docker
└── README.md           # File này
```

## 🤝 Đóng góp
Nếu bạn muốn cải tiến, fork repo và tạo PR. Issues welcome!

## 📄 License
MIT License. Sử dụng tự do, nhưng nhớ credit nếu share.

---

**Lưu ý**: Đây là project demo. Không dùng cho production mà không test kỹ. OpenAI API có giới hạn rate, nên không chạy quá 1 lần/phút.