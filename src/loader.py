import os
import urllib.request
import zipfile
import io

SUPPORTED_EXTENSIONS = {'.py', '.js', '.ts', '.java', '.cpp'}

def load_codebase(directory_path: str):
    """
    Scans the directory for supported files and yields their content and metadata.
    """
    documents = []
    
    if not os.path.exists(directory_path):
        raise ValueError(f"Directory does not exist: {directory_path}")
        
    for root, _, files in os.walk(directory_path):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in SUPPORTED_EXTENSIONS:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        text = f.read()
                    
                    documents.append({
                        "text": text,
                        "metadata": {
                            "file_path": file_path,
                            "file_name": file
                        }
                    })
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
                    
    return documents

def load_github_repo(url: str):
    """
    Downloads a GitHub repo as a zip file in memory and extracts its contents.
    """
    documents = []
    
    parts = url.rstrip('/').split('/')
    if "github.com" not in parts:
        raise ValueError("Not a valid GitHub URL")
        
    idx = parts.index("github.com")
    if idx + 2 >= len(parts):
        raise ValueError("Invalid GitHub URL format. Use https://github.com/owner/repo")
        
    owner = parts[idx+1]
    repo = parts[idx+2]
    
    zip_url = f"https://api.github.com/repos/{owner}/{repo}/zipball"
    
    req = urllib.request.Request(zip_url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            zip_bytes = response.read()
    except Exception as e:
        raise ValueError(f"Failed to download repository from {zip_url}: {e}")
        
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
        for file_info in z.infolist():
            if file_info.is_dir():
                continue
                
            ext = os.path.splitext(file_info.filename)[1].lower()
            if ext in SUPPORTED_EXTENSIONS:
                try:
                    with z.open(file_info) as f:
                        text = f.read().decode('utf-8')
                        
                    documents.append({
                        "text": text,
                        "metadata": {
                            "file_path": file_info.filename,
                            "file_name": os.path.basename(file_info.filename)
                        }
                    })
                except Exception as e:
                    print(f"Error reading {file_info.filename} from zip: {e}")
                    
    return documents
