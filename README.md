# CodeLens — Codebase Q&A Assistant (RAG)

 CodeLens is a locally-run Retrieval-Augmented Generation (RAG) AI assistant built to help you answer questions, understand architecture, and explore code within local or remote repositories. 

 Instead of manually searching through dozens of heavily scattered files, simply drop your codebase in, and chat with it locally using Streamlit and Google Gemini.

---

## ✨ Features
- **Plug-and-Play Ingestion:** Supports raw local directory paths or direct GitHub repository URLs.
- **In-Memory Vector Search:** Leverages `Faiss-CPU` and `SentenceTransformers` (`all-MiniLM-L6-v2`) locally to quickly build embeddings of chunks. No expensive DB backend setup required.
- **Explainable Answers:** Built-in "Explainability Layer" natively tracks source files, chunk relativity, and distance scores, keeping the AI accountable.
- **Intelligent Chunking:** Recursively splits large source code files while seamlessly retaining metadata, effectively tracking exact `.js`, `.py`, `.ts`, `.tsx`, `.jsx`, `.java`, `.cpp`, `.md`, `.txt`, and `.json` imports.
- **ChatGPT-Style Flow:** Implements Chat History allowing you to ask follow-up architecture questions.
- **Advanced Aesthetics:** A sleek custom dark-mode interface built on standard Streamlit.

---

## 🚀 Setup & Execution 

### 1. Prerequisites
- **Python 3.10+**
- A **Google Gemini API Key**: [Google AI Studio](https://aistudio.google.com/app/apikey)

### 2. Configure Environment variables
Create a `.env` file in the root folder (or use the one provided) and fill it in:
```ini
GOOGLE_API_KEY="your-api-key-here"
```

### 3. Local Installation
```bash
# 1. Create a virtual environment
python -m venv .venv
.\.venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch the Assistant!
streamlit run app.py
```

### 4. Optional: Docker Deployment (Fully Isolated)
If you prefer not pulling repositories to your host machine filesystem and want total isolation:
```bash
docker compose up --build
```


## 📂 Architecture overview
- `app.py`: Main Streamlit User Interface and App entrypoint.
- `src/loader.py`: Handles recursively traversing local paths or unpacking remote repositories natively while extracting metadata.
- `src/chunker.py`: Chops large codebase texts into processable embedding context chunks.
- `src/embeddings.py` & `src/vector_store.py`: Local vectorizing logic using FAISS logic.
- `src/generator.py`: Prompt compiler and primary LangChain / GenAI orchestrator connecting custom context to Gemini's Language Models.
