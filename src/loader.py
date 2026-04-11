import os

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
