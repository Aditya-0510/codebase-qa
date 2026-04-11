import streamlit as st
import os
import subprocess
import tempfile
from dotenv import load_dotenv
from src.loader import load_codebase
from src.chunker import chunk_documents
from src.vector_store import VectorStoreDB
from src.generator import get_answer

# Load environment variables
load_dotenv()

st.set_page_config(page_title="Codebase Q&A MVP", layout="wide")

st.title("🚀 Codebase Q&A Assistant (RAG)")

# Initialize session state for DB
if "vectordb" not in st.session_state:
    st.session_state["vectordb"] = None
    
with st.sidebar:
    st.header("Configuration")
    codebase_input = st.text_input("Local Path or GitHub URL", value="")
    
    if st.button("Ingest Codebase"):
        if not codebase_input:
            st.error("Please enter a valid path or URL.")
        else:
            actual_path = codebase_input
            
            if codebase_input.startswith("http://") or codebase_input.startswith("https://"):
                with st.spinner("Cloning GitHub repository locally into ./repos/..."):
                    repo_name = codebase_input.rstrip("/").split("/")[-1]
                    if repo_name.endswith(".git"):
                        repo_name = repo_name[:-4]
                        
                    repos_dir = os.path.join(os.getcwd(), "repos")
                    os.makedirs(repos_dir, exist_ok=True)
                    
                    target_dir = os.path.join(repos_dir, repo_name)
                    
                    try:
                        import shutil
                        if os.path.exists(target_dir):
                            shutil.rmtree(target_dir) # Remove old if exists
                            
                        subprocess.run(["git", "clone", codebase_input, target_dir], check=True, capture_output=True)
                        actual_path = target_dir
                        st.success(f"Successfully cloned repository into ./repos/{repo_name}!")
                    except subprocess.CalledProcessError as e:
                        st.error(f"Failed to clone repository: {e.stderr.decode('utf-8', errors='ignore')}")
                        actual_path = None
                        
            docs = []
            if actual_path and not os.path.exists(actual_path):
                st.error("The specified local directory does not exist.")
            elif actual_path:
                with st.spinner("Reading files..."):
                    docs = load_codebase(actual_path)
                    st.write(f"Found {len(docs)} supported files.")
                
            if len(docs) > 0:
                with st.spinner("Chunking files..."):
                    chunks = chunk_documents(docs)
                    st.write(f"Created {len(chunks)} chunks.")
                
                with st.spinner("Building Vector Store & Embeddings (Local)..."):
                    db = VectorStoreDB()
                    db.build_index(chunks)
                    st.session_state["vectordb"] = db
                    st.success("✅ Codebase Ingested Successfully!")
            else:
                st.warning("No code files found in the specified directory.")

# Main Query Area
query = st.text_input("Ask a question about the codebase:")

if st.button("Submit Query"):
    if not st.session_state["vectordb"]:
        st.warning("Please ingest a codebase first.")
    elif not query:
        st.warning("Please enter a query.")
    elif not os.getenv("GOOGLE_API_KEY"):
        st.error("GOOGLE_API_KEY environment variable is not set. Please add it to the .env file.")
    else:
        with st.spinner("Retrieving context and generating answer..."):
            # 1. Retrieve
            db: VectorStoreDB = st.session_state["vectordb"]
            try:
                results = db.search(query, top_k=4)
                
                # Context list from Results (Tuple of Document, Score)
                context_chunks = [res[0] for res in results]
                
                # 2. Generate
                answer = get_answer(query, context_chunks)
                
                # 3. Display Results
                st.markdown("### 🤖 Generated Answer")
                st.info(answer)
                
                # 4. Explainability Layer
                st.markdown("### 🔍 Explainability Layer (Retrieved Context)")
                for i, (doc, score) in enumerate(results):
                    file_path = doc.metadata.get('file_path', 'N/A')
                    # FAISS returns L2 distance here by default if used with HF embeddings. Lower is better.
                    with st.expander(f"Snippet {i+1}: {file_path} (Distance Score: {score:.4f})"):
                        st.markdown(f"**Source File:** `{file_path}`")
                        st.code(doc.page_content, language="python")
            except Exception as e:
                st.error(f"An error occurred during query generation: {e}")
