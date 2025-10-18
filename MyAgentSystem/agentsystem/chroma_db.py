from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import os

def create_vectorstore(documents, persist_directory="./chroma_db"):
    """Создает векторное хранилище"""
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )
    
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=persist_directory
    )
    
    return vectorstore

def load_existing_vectorstore(persist_directory="./chroma_db"):
    """Загружает существующую векторную базу данных"""
    try:
        
        if not os.path.exists(persist_directory):
            return None
            
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
        
        vectorstore = Chroma(
            persist_directory=persist_directory,
            embedding_function=embeddings
        )
        
        return vectorstore
    except Exception as e:
        print(f"❌ Ошибка при загрузке векторной базы данных: {e}")
        return None

def get_retriever(vectorstore, k=3):
    """Создает ретривер для поиска релевантных документов"""
    return vectorstore.as_retriever(search_kwargs={"k": k})

def add_documents_to_vectorstore(vectorstore, documents):
    """Добавляет новые документы в существующую векторную базу данных"""
    try:
        vectorstore.add_documents(documents)
        return True
    except Exception as e:
        print(f"❌ Ошибка при добавлении документов: {e}")
        return False
