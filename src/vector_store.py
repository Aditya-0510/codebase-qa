from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

class VectorStoreDB:
    def __init__(self, embedding_model_name: str = "all-MiniLM-L6-v2"):
        """
        Initializes the Vector DB with the specified embedding model.
        """
        self.embeddings = HuggingFaceEmbeddings(model_name=embedding_model_name)
        self.vector_store = None
        
    def build_index(self, chunks):
        """
        Builds the FAISS vector index from the document chunks.
        """
        if not chunks:
            raise ValueError("No chunks provided to build index.")
            
        self.vector_store = FAISS.from_documents(chunks, self.embeddings)
        
    def search(self, query: str, top_k: int = 5):
        """
        Performs similarity search and returns the top_k relevant chunks with scores.
        Returns a list of tuples (Document, score).
        """
        if not self.vector_store:
            raise ValueError("Vector store has not been built yet.")
            
        # similarity_search_with_score returns lower score for better proximity (L2 distance typically)
        results = self.vector_store.similarity_search_with_score(query, k=top_k)
        return results
