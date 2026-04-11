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

st.markdown("""
<style>
/* Premium Dark Mode & Aesthetics */
.stApp {
    background-color: #0d1117;
    color: #c9d1d9;
}
section[data-testid="stSidebar"] {
    background-color: #161b22;
    border-right: 1px solid #30363d;
}
.stExpander {
    background-color: #161b22;
    border: 1px solid #30363d !important;
    border-radius: 8px !important;
}
.stTextInput input {
    background-color: #0d1117;
    color: #c9d1d9;
    border: 1px solid #30363d;
}
</style>
""", unsafe_allow_html=True)

st.title("🚀 Codebase Q&A Assistant (RAG)")

# Initialize session states
if "vectordb" not in st.session_state:
    st.session_state["vectordb"] = None
    
if "messages" not in st.session_state:
    st.session_state["messages"] = []
    
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
                        import stat
                        
                        def remove_readonly(func, path, _):
                            os.chmod(path, stat.S_IWRITE)
                            func(path)
                            
                        if os.path.exists(target_dir):
                            shutil.rmtree(target_dir, onerror=remove_readonly) # Remove old if exists
                            
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
for msg in st.session_state["messages"]:
    st.chat_message(msg["role"]).write(msg["content"])

if query := st.chat_input("Ask a question about the codebase:"):
    if not st.session_state["vectordb"]:
        st.warning("Please ingest a codebase first.")
    elif not os.getenv("GOOGLE_API_KEY"):
        st.error("GOOGLE_API_KEY environment variable is not set. Please add it to the .env file.")
    else:
        st.session_state["messages"].append({"role": "user", "content": query})
        st.chat_message("user").write(query)
        
        with st.chat_message("assistant"):
            with st.spinner("Retrieving context and generating answer..."):
                db: VectorStoreDB = st.session_state["vectordb"]
                try:
                    results = db.search(query, top_k=4)
                    context_chunks = [res[0] for res in results]
                    
                    answer = get_answer(query, context_chunks, st.session_state["messages"])
                    st.write(answer)
                    
                    st.session_state["messages"].append({"role": "assistant", "content": answer})
                    
                    with st.expander("🔍 View Retrieved Context"):
                        for i, (doc, score) in enumerate(results):
                            file_path = doc.metadata.get('file_path', 'N/A')
                            st.markdown(f"**Snippet {i+1} from `{file_path}` (Distance: {score:.4f})**")
                            st.code(doc.page_content, language="python")
                            
                except Exception as e:
                    st.error(f"An error occurred during query generation: {e}")
