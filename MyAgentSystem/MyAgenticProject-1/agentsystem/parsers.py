from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import os

DATA_URL = "./data/Knowledge_base.txt"

def load_and_split_documents(data_url=None, chunk_size=250, chunk_overlap=100):
    """Загружает и разбивает документы на чанки"""
    if data_url is None:
        data_url = DATA_URL
        

    loader = TextLoader(data_url, encoding='utf-8')
    documents = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )
    
    splits = text_splitter.split_documents(documents)
    return splits

def load_multiple_documents(file_paths, chunk_size=250, chunk_overlap=100):
    """Загружает и разбивает несколько документов на чанки"""
    all_documents = []
    
    for file_path in file_paths:
        try:
            loader = TextLoader(file_path, encoding='utf-8')
            documents = loader.load()
            all_documents.extend(documents)
        except Exception as e:
            print(f"❌ Ошибка при загрузке файла {file_path}: {e}")
    
    # Разбиение на чанки
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )
    
    splits = text_splitter.split_documents(all_documents)
    return splits