from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from app.services.vectorstore import create_vectorstore, add_file_to_vectorstore
from app.utils.formatter import format_docs
from app.core.config import GROQ_MODEL,GROQ_API_KEY
import os

from dotenv import load_dotenv
load_dotenv()

_vectorstore = None
_retriever = None

def get_vectorstore():
    global _vectorstore
    if _vectorstore is None:
        _vectorstore = create_vectorstore()
    return _vectorstore

def get_retriever():
    global _retriever
    if _retriever is None:
        _retriever = get_vectorstore().as_retriever(search_kwargs={"k": 5})
    return _retriever

RAG_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "Answer using ONLY the context below. Cite section names. Say 'I don't know' if unsure."),
    ("human", "Context:\n{context}\n\nQuestion: {question}")
])

llm = ChatGroq(
    model=GROQ_MODEL,
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)


def rag(query: str) -> str:
    print("query---",query)
    retriever_instance = get_retriever()
    docs = retriever_instance.invoke(query)
    context = format_docs(docs)

    prompt_value = RAG_PROMPT.invoke({
        "context": context,
        "question": query
    })

    response = llm.invoke(prompt_value)
    return response.content

def add_document(file_path: str):
    print(f"Adding new document to vectorstore: {file_path}")
    add_file_to_vectorstore(file_path, get_vectorstore())
