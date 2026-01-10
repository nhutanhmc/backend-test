import os
import glob
from openai import OpenAI
from dotenv import load_dotenv

# Uu tien env var tu Docker (-e), neu khong co thi load tu .env
if not os.getenv('OPENAI_API_KEY'):
    load_dotenv()

client = OpenAI()

DATA_DIR = "data"
VECTOR_STORE_NAME = "OptiSigns Knowledge Base"
ASSISTANT_NAME = "OptiBot"

def setup_ai_backend():
    """
    Khoi tao Vector Store va Assistant (Rong).
    Tra ve ID (Return) de main.py luu vao state.json.
    """
    print("--- STARTING SETUP (SKELETON ONLY) ---")

    try:
        # 1. Tao Vector Store rong
        vector_store = client.vector_stores.create(name=VECTOR_STORE_NAME)
        print(f"Created Vector Store ID: {vector_store.id}")
        
        # 2. Tao Assistant
        assistant = client.beta.assistants.create(
            name=ASSISTANT_NAME,
            instructions=instructions=(
                "You are OptiBot, the customer-support bot for OptiSigns.com.\n"
                "• Tone: helpful, factual, concise.\n"
                "• Only answer using the uploaded docs.\n"
                "• Max 5 bullet points; else link to the doc.\n"
                '• Cite up to 3 "Article URL:" lines per reply.'
            ),
            model="gpt-4o-mini", 
            tools=[{"type": "file_search"}],
            tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}}
        )
        print(f"Created Assistant ID: {assistant.id}")
        
        # [THAY DOI] Thay vi ghi file .env, ta tra ve ID cho main.py xu ly
        return vector_store.id, assistant.id

    except Exception as e:
        print(f"Setup Error: {e}")
        return None, None

def delete_old_file_on_openai(file_id):
    """Xoa file cu tren OpenAI dua vao ID."""
    if not file_id: return
    
    print(f"Deleting old file ID: {file_id} ...")
    try:
        client.files.delete(file_id)
        print("Delete success.")
        return True
    except Exception as e:
        print(f"Delete failed: {e}")
        return False

def upload_single_file(file_path, vector_store_id):
    """Upload 1 file va tra ve ID."""
    try:
        # 1. Upload file len Cloud
        with open(file_path, "rb") as f:
            openai_file = client.files.create(file=f, purpose="assistants")
        
        # 2. Link file vao Vector Store
        client.vector_stores.files.create(
            vector_store_id=vector_store_id,
            file_id=openai_file.id
        )
        
        print(f"Uploaded: {os.path.basename(file_path)} -> ID: {openai_file.id}")
        return openai_file.id 
        
    except Exception as e:
        print(f"Upload Error {file_path}: {e}")
        return None

def delete_resources():
    print("\n--- DELETING ALL RESOURCES ---")
    
    # Do logic moi luu vao state, nen ham xoa nay chi tham khao .env
    # (Ban co the giu nguyen hoac nang cap no doc state.json neu muon)
    assistant_id = os.getenv("ASSISTANT_ID")
    vector_store_id = os.getenv("VECTOR_STORE_ID")

    # 1. Xoa Assistant
    if assistant_id:
        try:
            client.beta.assistants.delete(assistant_id)
            print(f"Deleted Assistant: {assistant_id}")
        except Exception as e:
            print(f"Error deleting Assistant: {e}")
    else:
        print("Assistant ID not found in env.")

    # 2. Xoa Vector Store va File goc
    if vector_store_id:
        try:
            try:
                files_in_store = client.vector_stores.files.list(vector_store_id=vector_store_id)
                for file in files_in_store:
                    client.files.delete(file.id)
                print("Deleted associated original files.")
            except:
                pass 

            client.beta.vector_stores.delete(vector_store_id)
            print(f"Deleted Vector Store: {vector_store_id}")
        except Exception as e:
            print(f"Error deleting Vector Store: {e}")
    else:
        print("Vector Store ID not found in env.")

    # 3. Lam sach file .env va state.json
    try:
        # Xoa file state.json (Quan trong nhat o logic nay)
        if os.path.exists("state.json"):
            os.remove("state.json")
            print("Deleted state.json.")
            
    except Exception as e:
        print(f"Error cleaning files: {e}")

    print("Reset Complete.")

if __name__ == "__main__":
    print("Mode:")
    print("1. SETUP (Create Bot & Store - No Upload)")
    print("2. DELETE (Clean up everything)")
    
    choice = input("Select (1 or 2): ")
    
    if choice == "1":
        setup_ai_backend()
    elif choice == "2":
        delete_resources()
    else:
        print("Invalid choice.")