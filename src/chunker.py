from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

def chunk_documents(documents: list, chunk_size: int = 1500, chunk_overlap: int = 150):
    """
    Splits the ingested documents into fixed-size chunks while retaining metadata.
    Returns a list of Langchain Document objects.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""]
    )
    
    chunks = []
    for doc in documents:
        splits = text_splitter.split_text(doc["text"])
        for split in splits:
            chunks.append(Document(page_content=split, metadata=doc["metadata"]))
            
    return chunks
