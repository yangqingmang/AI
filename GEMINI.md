# Enterprise Brain (GEMINI Context)

## Project Overview
**Enterprise Brain** is an enterprise-grade autonomous AI agent solution capable of RAG (Retrieval-Augmented Generation), web search, code execution, and file management. It is designed to act as an AI employee with access to internal knowledge bases.

**Key Features:**
*   **Dual Mode Engine:**
    *   **Free Mode:** Pure RAG for internal knowledge base Q&A.
    *   **Pro Mode:** Agentic capabilities (Web Search, Code Execution, File Management).
*   **Architecture:** Decoupled Client/Server (Streamlit Frontend + FastAPI Backend + ChromaDB Vector Store).
*   **Performance:** Semantic Caching (Redis/Vector similarity) for faster responses.
*   **Model Agnostic:** Configurable to work with DeepSeek, OpenAI, vLLM, etc.

## Tech Stack
*   **Language:** Python 3.10+
*   **Orchestration:** LangChain, LangGraph
*   **LLM:** DeepSeek-V3 (via OpenAI SDK)
*   **Vector DB:** ChromaDB (Containerized or Local)
*   **Backend:** FastAPI (`src/api`)
*   **Frontend:** Streamlit (`src/app.py`, `src/pages/`)
*   **Containerization:** Docker, Docker Compose

## Directory Structure
```text
D:\AI\
├── enterprise-brain/       # Main application directory
│   ├── .env                # Environment variables (API Keys, Config)
│   ├── docker-compose.yml  # Service orchestration
│   ├── requirements.txt    # Python dependencies
│   ├── data/               # Raw documents (Markdown/PDF) for ingestion
│   ├── chroma_db/          # Persistent Vector DB storage
│   └── src/                # Source Code
│       ├── app.py          # [Frontend] Main Streamlit Chat Interface
│       ├── ingest.py       # [Script] Manual Data Ingestion Script
│       ├── api/            # [Backend] FastAPI Application
│       │   └── main.py     # API Entry Point
│       ├── config/
│       │   └── settings.py # Global Configuration (Pydantic)
│       ├── core/           # Core Logic (Agent, DB, LLM, Memory)
│       ├── pages/          # Streamlit Pages (Admin Interface)
│       └── tools/          # Agent Tools (Search, Files, Python)
├── deploy.sh               # Docker deployment script
├── run_local.bat/ps1/sh    # Local run scripts
└── README.md               # Project documentation
```

## Setup & Running

### 1. Prerequisites
*   Python 3.10+ installed.
*   Docker & Docker Compose (for containerized deployment).
*   `.env` file configured (copy from `.env.example`).

### 2. Local Development (No Docker)
To run the services locally on the host machine:
```powershell
# 1. Create and activate virtual environment
cd enterprise-brain
python -m venv .venv
.\.venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the automated start script (starts Backend + Frontend)
..\run_local.ps1
```
*   Frontend: `http://localhost:8501`
*   Backend Docs: `http://localhost:8000/docs`

### 3. Docker Deployment
To run the full stack (ChromaDB + Backend + Frontend) in containers:
```bash
docker-compose up -d --build
```

## Key Workflows

### Data Ingestion
*   **Manual:** Place `.md` or `.pdf` files in `enterprise-brain/data/` and run `python src/ingest.py`.
*   **UI:** Use the **Admin** page in the Streamlit interface to upload files and trigger a rebuild.

### Configuration
*   Edit `enterprise-brain/src/config/settings.py` for app defaults.
*   Edit `.env` for secrets (API Keys) and environment-specific overrides.

## Testing
*   **Unit/Integration Tests:** Located in `enterprise-brain/tests/`.
    ```powershell
    pytest enterprise-brain/tests
    ```
