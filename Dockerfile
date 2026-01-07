# 1. Chọn hệ điều hành nền (Python nhẹ nhất)
FROM python:3.11-slim

# 2. Tạo thư mục làm việc trong container
WORKDIR /app

# 3. Copy file thư viện trước (để tận dụng cache)
COPY requirements.txt .

# 4. Cài đặt thư viện
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy toàn bộ code vào
COPY . .

# 6. Lệnh chạy mặc định
CMD ["python", "main.py"]