import os
import time
from openai import OpenAI
from dotenv import load_dotenv

# Load ID từ .env
load_dotenv()
client = OpenAI()

ASSISTANT_ID = os.getenv("ASSISTANT_ID")

def test_bot_auto():
    print("--- BẮT ĐẦU TEST BOT ---")

    # 1. KIỂM TRA AN TOÀN (Fix lỗi crash của bạn)
    if not ASSISTANT_ID:
        print("❌ LỖI: Không tìm thấy ASSISTANT_ID trong file cấu hình.")
        print("👉 Nguyên nhân: Bạn chưa chạy Setup hoặc đã xóa dữ liệu Bot.")
        print("👉 Cách sửa: Chạy 'python ai_manager.py' và chọn phím 1 để tạo lại Bot.")
        return

    print(f"🤖 Đang test bot ID: {ASSISTANT_ID}")
    print("❓ Câu hỏi: How do I find the Account ID to configure Jamf?")
    
    try:
        # 2. Tạo cuộc hội thoại (Thread)
        thread = client.beta.threads.create()
        
        # 3. Gửi tin nhắn
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content="How do I find the Account ID to configure Jamf?"
        )
        
        # 4. Yêu cầu Bot trả lời (Run)
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=ASSISTANT_ID
        )
        
        # 5. Chờ Bot suy nghĩ (Polling)
        print("⏳ Bot đang đọc tài liệu...", end="", flush=True)
        while True:
            run_status = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            if run_status.status == 'completed':
                break
            elif run_status.status == 'failed':
                print("\n❌ Bot bị lỗi (Failed)!")
                print(run_status.last_error)
                return
            time.sleep(1)
            print(".", end="", flush=True)
            
        # 6. Lấy câu trả lời
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        answer = messages.data[0].content[0].text.value
        
        print("\n\n--- 💡 CÂU TRẢ LỜI CỦA BOT (API) ---")
        print(answer)
        print("------------------------------------")
        
        # Kiểm tra nhanh xem có trích dẫn không
        if "【" in answer or "[" in answer:
            print("✅ KẾT QUẢ: Bot ĐÃ ĐỌC được file (có trích dẫn). Hệ thống hoạt động Tốt!")
        else:
            print("⚠️ CẢNH BÁO: Bot trả lời nhưng không thấy trích dẫn.")
            
    except Exception as e:
        print(f"\n❌ Lỗi hệ thống: {e}")

if __name__ == "__main__":
    test_bot_auto()