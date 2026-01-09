import os
import sys
import json
import hashlib
import glob
from dotenv import load_dotenv
import requests

import scraper
import ai_manager

# Telegram configuration
TELEGRAM_TOKEN = "8183629835:AAHrBeapTCIK33pxUBcWLDmlWawZW0vBeIk"
TELEGRAM_CHAT_ID = "8102277793"

# 1. Load cau hinh (Uu tien bien moi truong tu Docker -e)
load_dotenv()

# Dinh nghia duong dan xu ly State (Ky uc)
# Su dung thu muc 'memory' de tranh loi Docker Volume khi file chua ton tai
STATE_DIR = "memory"
STATE_FILE = os.path.join(STATE_DIR, "state.json")
DATA_DIR = "data"

# Bien toan cuc luu ID (Nap tu Env hoac State)
VECTOR_STORE_ID = os.getenv("VECTOR_STORE_ID")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")

def calculate_md5(file_path):
    """Tinh ma Hash MD5 cua file de kiem tra thay doi noi dung."""
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except FileNotFoundError:
        return None

def load_state():
    """
    Doc file state.json tu thu muc memory.
    Neu thu muc chua co -> Tu dong tao.
    """
    if not os.path.exists(STATE_DIR):
        try:
            os.makedirs(STATE_DIR)
        except OSError:
            pass # Bo qua neu da ton tai (tranh race condition)

    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except: return {}
    return {}

def save_state(state):
    """Luu trang thai vao file json."""
    if not os.path.exists(STATE_DIR):
        os.makedirs(STATE_DIR)
        
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=4)

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

def main():
    print("--- STARTING DAILY JOB (ZERO CONFIG - AUTO MEMORY) ---")
    
    # Gui thong bao bat dau qua Telegram
    send_telegram_message("Daily job started.")
    
    global VECTOR_STORE_ID, ASSISTANT_ID

    # 1. Load state hien tai
    current_state = load_state()

    # ---------------------------------------------------------
    # LOGIC 1: TU DONG CAU HINH (AUTO-SETUP)
    # ---------------------------------------------------------
    
    # Buoc 1: Neu Env thieu ID, tim trong state (ky uc cu)
    if not VECTOR_STORE_ID:
        VECTOR_STORE_ID = current_state.get("_system_vector_store_id")
        ASSISTANT_ID = current_state.get("_system_assistant_id")

    # Buoc 2: Neu van thieu -> Chay Setup moi
    if not VECTOR_STORE_ID:
        print("[INFO] No IDs found. Setting up new resources...")
        
        # Goi ham setup tu ai_manager (Tra ve ID chu khong ghi file .env)
        vs_id, asst_id = ai_manager.setup_ai_backend()
        
        if vs_id and asst_id:
            VECTOR_STORE_ID = vs_id
            ASSISTANT_ID = asst_id
            
            # Luu ngay vao state de lan sau khong tao lai
            current_state["_system_vector_store_id"] = VECTOR_STORE_ID
            current_state["_system_assistant_id"] = ASSISTANT_ID
            save_state(current_state)
            print(f"[SUCCESS] Setup Done. IDs saved to {STATE_FILE}")
        else:
            print("[ERROR] Setup failed. Exiting.")
            sys.exit(1) # Thoat bao loi (Exit Code 1)
    else:
        print(f"[INFO] Using Vector Store ID: {VECTOR_STORE_ID}")

    # ---------------------------------------------------------
    # LOGIC 2: SCRAPE & UPLOAD
    # ---------------------------------------------------------

    print("\n--- STEP 1: SCRAPING DATA ---")
    scraper.scrape_data()

    print("\n--- STEP 2: PROCESSING FILES ---")
    
    stats = {"added": 0, "updated": 0, "skipped": 0, "deleted": 0}
    all_files = glob.glob(os.path.join(DATA_DIR, "*.md"))
    
    # Khoi tao state moi, GIU LAI ID HE THONG de khong bi mat
    new_state = {
        "_system_vector_store_id": VECTOR_STORE_ID,
        "_system_assistant_id": ASSISTANT_ID
    }
    
    for file_path in all_files:
        filename = os.path.basename(file_path)
        new_hash = calculate_md5(file_path)
        openai_file_id = None 
        
        is_existing = filename in current_state
        old_entry = current_state.get(filename, {})
        
        # Lay thong tin cu
        if isinstance(old_entry, dict):
            old_hash = old_entry.get("hash")
            old_id = old_entry.get("id")
        else:
            old_hash = None
            old_id = None

        # --- PHAN LOAI ---
        if not is_existing:
            # MOI (New)
            print(f"[NEW] Found new file: {filename}")
            new_id = ai_manager.upload_single_file(file_path, VECTOR_STORE_ID)
            if new_id:
                openai_file_id = new_id
                stats["added"] += 1
            
        elif old_hash != new_hash:
            # UPDATE (Content Changed)
            print(f"[UPDATE] Content changed: {filename}")
            
            # Xoa file cu tren Cloud de tranh rac
            if old_id: 
                if ai_manager.delete_old_file_on_openai(old_id):
                    stats["deleted"] += 1
            
            # Upload file moi
            new_id = ai_manager.upload_single_file(file_path, VECTOR_STORE_ID)
            if new_id:
                openai_file_id = new_id
                stats["updated"] += 1
        
        else:
            # SKIP (No Change)
            openai_file_id = old_id
            stats["skipped"] += 1

        # Cap nhat vao state moi
        if openai_file_id:
            new_state[filename] = {
                "hash": new_hash,
                "id": openai_file_id
            }

    # 3. Luu State
    print("\n--- STEP 3: SAVING STATE ---")
    save_state(new_state)
    print(f"[SUCCESS] State saved to {STATE_FILE}.")

    # 4. Bao cao
    print("\n================ REPORT ================")
    print(f"Total Scanned: {len(all_files)}")
    print(f"Added:         {stats['added']}")
    print(f"Deleted:       {stats['deleted']}")
    print(f"Updated:       {stats['updated']}")
    print(f"Skipped:       {stats['skipped']}")
    print("========================================")

    # Gui thong bao thanh cong qua Telegram
    message = f"Daily job completed successfully!\nTotal Scanned: {len(all_files)}\nAdded: {stats['added']}\nDeleted: {stats['deleted']}\nUpdated: {stats['updated']}\nSkipped: {stats['skipped']}"
    send_telegram_message(message)

if __name__ == "__main__":
    main()
    # Bao hieu cho Docker/Cronjob biet la chay thanh cong (Exit Code 0)
    sys.exit(0)