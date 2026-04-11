import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema import StrOutputParser

def get_answer(query: str, context_chunks: list, chat_history: list = None) -> str:
    """
    Takes a query, retrieved chunks, and chat history, formats them as context, 
    and gets an answer from Google Gemini.
    """
    if chat_history is None:
        chat_history = []
        
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is missing.")
        
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=api_key, temperature=0.2)
    
    # Format the context chunks into a readable string
    context_text = ""
    for i, doc in enumerate(context_chunks):
        file_path = doc.metadata.get("file_path", "Unknown File")
        context_text += f"\\n--- Snippet {i+1} from {file_path} ---\\n"
        context_text += doc.page_content
        context_text += "\\n"
        
    history_text = ""
    for msg in chat_history:
        role = "User" if msg["role"] == "user" else "Assistant"
        history_text += f"{role}: {msg['content']}\\n"
        
    prompt_template = """You are an expert software engineer assistant helping a user understand a codebase.
    
Use the following pieces of retrieved code context to answer the user's question.
If you don't know the answer based on the context, just say that you don't know, don't try to make up an answer.
Always cite the file names/paths you are referencing in your answer.

Chat History:
{history}

Context:
{context}

Question: {question}

Answer:"""
    
    prompt = PromptTemplate.from_template(prompt_template)
    
    chain = (
        prompt
        | llm
        | StrOutputParser()
    )
    
    response = chain.invoke({"context": context_text, "question": query, "history": history_text})
    return response
