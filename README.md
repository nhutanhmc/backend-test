# OptiBot Auto — AI Assistant for the OptiSigns Knowledge Base

OptiBot Auto is an automation tool that scrapes content from the OptiSigns Support Center, uploads it to an OpenAI Vector Store, and creates an AI Assistant that can answer questions using that knowledge. It helps you build a smart OptiSigns chatbot with minimal coding.

## 🚀 Key Features
- **Automatic scraping**: Fetches articles from the OptiSigns Help Center API and saves them as Markdown files.
- **Smart uploads**: Uploads only new or changed files to avoid duplicates.
- **AI Assistant**: Creates an OpenAI Assistant to answer questions based on the uploaded docs.
- **Docker-ready**: Run easily with Docker—no need to install Python locally.
- **Zero config**: Automatically sets up the vector store and assistant on the first run.

## 📋 Requirements
- **Docker**: Latest version (download from docker.com).
- **OpenAI API Key**: Create an OpenAI account and generate an API key from the OpenAI platform. You need credits to use the API (roughly $0.01–$0.05 per run, depending on uploads and usage).

## 🛠️ Installation

### Step 1: Clone the repo
```bash
git clone https://github.com/your-username/os-mini-clone.git
cd os-mini-clone
```

### Step 2: Run the project

## ✅ Option 1: Run locally (without Docker)

### 1) Create a `.env` file
Create a `.env` file in the **project root** (same level as `main.py`) and add:
```env
OPENAI_API_KEY=your_api_key_here
```

### 2) Create a virtual environment, install dependencies, and run

**Windows (PowerShell)**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

If PowerShell blocks `Activate.ps1`, run this once and try again:
```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

**macOS / Linux**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

## ✅ Option 2: Run with Docker (recommended)

### Build the Docker image
```bash
docker build -t optibot:v1 .
```
- This builds the image `optibot:v1` from the Dockerfile (first build may take a few minutes).

### Run (first run and all future runs: setup + update)
```bash
docker run --rm \
  -e OPENAI_API_KEY="your_api_key_here" \
  -v ${PWD}/memory:/app/memory \
  optibot:v1
```

Notes:
- Replace `your_api_key_here` with your real API key.
- `-v ${PWD}/memory:/app/memory` mounts the `memory` folder to persist state (IDs + file hashes). **Do not remove this**, otherwise you will lose state on each run.

### Next runs (update)
Run the same command again to scrape new data and update the assistant. Only changed files will be uploaded.

## 📊 Sample Output
When you run the script, you should see something like:
```
--- STARTING DAILY JOB (ZERO CONFIG - AUTO MEMORY) ---
[INFO] No IDs found. Setting up new resources...
[SUCCESS] Setup Done. IDs saved to memory/state.json

--- STEP 1: SCRAPING DATA ---
--- Connecting to API: https://support.optisigns.com/api/v2/help_center/articles.json?per_page=30 ---
✅ Found 30 articles. Processing...

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

### Error: `OPENAI_API_KEY not found`
- Make sure you passed `-e OPENAI_API_KEY="sk-..."` correctly (Docker) or set it in `.env` (local).

### Error: `Beta object has no attribute`
- Rebuild the image:
  ```bash
  docker build -t optibot:v1 .
  ```

### `memory/` is empty or not persistent
- Make sure the volume mount is correct:
  ```bash
  -v ${PWD}/memory:/app/memory
  ```

### OpenAI costs
- Uploading new/changed files costs money. If you run often, monitor usage in your OpenAI dashboard.

### `data/` folder is empty
- The script scrapes from the OptiSigns API. If the API changes, the code may need updates.

## 📁 Project Structure
```text
os-mini-clone/
├── ai_manager.py      # OpenAI manager (vector store, assistant)
├── main.py            # Main script (scrape + upload)
├── scraper.py         # Scraper for OptiSigns
├── data/              # Stores Markdown files (auto-created)
├── memory/            # Stores state (created after first run)
├── Dockerfile         # Docker setup
├── requirements.txt   # Python dependencies
├── .dockerignore      # Ignore files during Docker build
└── README.md          # This file
```

## 🤝 Contributing
Want to improve it? Fork the repo and open a PR. Issues are welcome!

## 📄 License
MIT License. Free to use—please include credit if you share.

---

**Note**: This is a demo project. Don’t use it in production without thorough testing. The OpenAI API has rate limits—avoid running more than once per minute.
