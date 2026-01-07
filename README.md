# OptiBot Auto - AI Assistant for OptiSigns Knowledge Base

OptiBot Auto là một công cụ tự động để scrape dữ liệu từ trang hỗ trợ OptiSigns, upload lên OpenAI Vector Store, và tạo AI Assistant để trả lời câu hỏi dựa trên kiến thức đó. Dự án này giúp bạn có một chatbot thông minh cho OptiSigns mà không cần code nhiều.

## 🚀 Tính năng chính
- **Tự động scrape**: Lấy dữ liệu từ API OptiSigns và lưu thành file Markdown.
- **Upload thông minh**: Chỉ upload file mới hoặc thay đổi, tránh trùng lặp.
- **AI Assistant**: Tạo bot trên OpenAI để trả lời câu hỏi.
- **Docker ready**: Chạy dễ dàng với Docker, không cần cài Python trên máy.
- **Zero config**: Tự động setup vector store và assistant lần đầu.

## 📋 Yêu cầu
- **Docker**: Phiên bản mới nhất (có thể tải từ [docker.com](https://www.docker.com/)).
- **OpenAI API Key**: Đăng ký tài khoản OpenAI và lấy API key từ [platform.openai.com](https://platform.openai.com/account/api-keys). Bạn cần có credit để dùng API (khoảng $0.01-0.05 cho mỗi lần chạy).

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

## 📊 Output mẫu
Khi chạy, bạn sẽ thấy:
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
```

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

## 📁 Cấu trúc project
```
os-mini-clone/
├── ai_manager.py      # Quản lý OpenAI (vector store, assistant)
├── main.py            # Script chính (scrape + upload)
├── scraper.py         # Scrape data từ OptiSigns
├── data/              # Thư mục lưu file Markdown (tự động tạo)
├── memory/            # Thư mục lưu state (tạo sau lần đầu)
├── Dockerfile         # Docker setup
├── requirements.txt   # Python dependencies
├── .dockerignore      # Ignore files khi build Docker
└── README.md          # File này
```

## 🤝 Đóng góp
Nếu bạn muốn cải tiến, fork repo và tạo PR. Issues welcome!

## 📄 License
MIT License. Sử dụng tự do, nhưng nhớ credit nếu share.

---

**Lưu ý**: Đây là project demo. Không dùng cho production mà không test kỹ. OpenAI API có giới hạn rate, nên không chạy quá 1 lần/phút.