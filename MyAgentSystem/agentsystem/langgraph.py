from langgraph.graph import START, END, StateGraph
from langchain_core.documents import Document
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
from gigachat import GigaChat
from agentsystem.parsers import load_and_split_documents
from agentsystem.chroma_db import create_vectorstore, load_existing_vectorstore, get_retriever

load_dotenv()

gigachat = GigaChat(
    credentials=os.getenv("GIGACHAT_CREDENTIALS"),
    verify_ssl_certs=False
)

class State(BaseModel):
    tech_support_class : str
    question: str
    context: List[Document] = []
    answer: str = ""
    retriever: Optional[object] = None

def retrieve(state: State):
    if state.retriever is None:
        vectorstore = load_existing_vectorstore()
        if vectorstore is None:
            print("📚 Создаем новую векторную базу данных...")
            documents = load_and_split_documents()
            vectorstore = create_vectorstore(documents)
        else:
            print("✅ Загружена существующая векторная база данных")
            
        retriever = get_retriever(vectorstore, k=3)
        state.retriever = retriever
    
    retrieved_docs = state.retriever.invoke(state.question)
    return {'context': retrieved_docs, 'retriever': state.retriever}

def generate(state: State):
    """Генерирует ответ на основе найденного контекста"""
    docs_content = "\n\n".join([doc.page_content for doc in state.context])

    prompt = f"""
    Ты - помощник IT-поддержки. Отвечай на вопросы пользователей на основе предоставленной базы знаний.
    
    База знаний:
    {docs_content}
    
    Вопрос пользователя: {state.question}
    
    Ответь максимально подробно и полезно. Если в базе знаний нет информации, честно скажи об этом.
    """
    
    response = gigachat.chat(prompt)
    
    return {'answer': response.choices[0].message.content}


def classification_support(state : State):
    """ Определяет тип поддержки в которую нужно перенаправить запрос """

    prompt = f"""
    Ты - помощник IT-поддержки. Твоя задача классифицировать вопрос пользователя и определить отдел в который его перенаправить, какая команда и поддержка могла бы помочь решить этот вопрос.
    Отвечай дружелюбно, кратко и по делу.

    Вопрос пользователя:
    {state.question}
    """


    response = gigachat.chat(prompt)


    return {'tech_support_class' : response.choices[0].message.content}


workflow = StateGraph(State)


workflow.add_node("retrieve", retrieve)
workflow.add_node("generate", generate)

workflow.add_edge(START, "retrieve")
workflow.add_edge("retrieve", "generate")
workflow.add_edge("generate", END)

app = workflow.compile()

def run_rag_system(question: str):
    """Запускает RAG систему для ответа на вопрос"""
    initial_state = State(question=question, tech_support_class="")
    result = app.invoke(initial_state)
    return result["answer"]

if __name__ == "__main__":
    test_question = "Как решить проблему с npm ERR! EACCES при сборке?"
    answer = run_rag_system(test_question)
    print(f"Вопрос: {test_question}")
    print(f"Ответ: {answer}")