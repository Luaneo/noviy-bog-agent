from langchain_community.document_loaders import TextLoader, PyPDFLoader, UnstructuredHTMLLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import os
import markdown
from bs4 import BeautifulSoup

DATA_URL = "./data/Knowledge_base.txt"

def parse_pdf_documents(file_paths, chunk_size=250, chunk_overlap=100):
    """Парсит PDF файлы и разбивает на чанки"""
    all_documents = []
    
    for file_path in file_paths:
        try:
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            all_documents.extend(documents)
            print(f"✅ Успешно загружен PDF: {file_path}")
        except Exception as e:
            print(f"❌ Ошибка при загрузке PDF {file_path}: {e}")
    
    # Разбиение на чанки
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )
    
    splits = text_splitter.split_documents(all_documents)
    return splits

def parse_html_documents(file_paths, chunk_size=250, chunk_overlap=100):
    """Парсит HTML файлы и разбивает на чанки"""
    all_documents = []
    
    for file_path in file_paths:
        try:
            loader = UnstructuredHTMLLoader(file_path)
            documents = loader.load()
            all_documents.extend(documents)
            print(f"✅ Успешно загружен HTML: {file_path}")
        except Exception as e:
            print(f"❌ Ошибка при загрузке HTML {file_path}: {e}")
    
    # Разбиение на чанки
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )
    
    splits = text_splitter.split_documents(all_documents)
    return splits

def parse_markdown_documents(file_paths, chunk_size=250, chunk_overlap=100):
    """Парсит Markdown файлы и разбивает на чанки"""
    all_documents = []
    
    for file_path in file_paths:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Конвертируем markdown в HTML, затем извлекаем текст
            html = markdown.markdown(content)
            soup = BeautifulSoup(html, 'html.parser')
            text_content = soup.get_text()
            
            # Создаем документ
            document = Document(
                page_content=text_content,
                metadata={"source": file_path, "type": "markdown"}
            )
            all_documents.append(document)
            print(f"✅ Успешно загружен Markdown: {file_path}")
        except Exception as e:
            print(f"❌ Ошибка при загрузке Markdown {file_path}: {e}")
    
    # Разбиение на чанки
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )
    
    splits = text_splitter.split_documents(all_documents)
    return splits

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

def parse_documents_by_type(file_paths, chunk_size=250, chunk_overlap=100):
    """Универсальная функция для парсинга документов различных типов"""
    all_documents = []
    
    for file_path in file_paths:
        if not os.path.exists(file_path):
            print(f"❌ Файл не найден: {file_path}")
            continue
            
        file_extension = os.path.splitext(file_path)[1].lower()
        
        try:
            if file_extension == '.pdf':
                documents = parse_pdf_documents([file_path], chunk_size, chunk_overlap)
            elif file_extension in ['.html', '.htm']:
                documents = parse_html_documents([file_path], chunk_size, chunk_overlap)
            elif file_extension in ['.md', '.markdown']:
                documents = parse_markdown_documents([file_path], chunk_size, chunk_overlap)
            elif file_extension in ['.txt', '.text']:
                documents = load_multiple_documents([file_path], chunk_size, chunk_overlap)
            else:
                print(f"⚠️ Неподдерживаемый формат файла: {file_extension} для {file_path}")
                continue
                
            all_documents.extend(documents)
            
        except Exception as e:
            print(f"❌ Ошибка при обработке файла {file_path}: {e}")
    
    return all_documents

def get_supported_extensions():
    """Возвращает список поддерживаемых расширений файлов"""
    return ['.pdf', '.html', '.htm', '.md', '.markdown', '.txt', '.text']