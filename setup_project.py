import os

BASE_DIR = "rag-fastapi-app"

files_content = {

# ------------------ CORE ------------------
"app/core/config.py": '''import os

SOURCE = "https://raw.githubusercontent.com/tnahddisttud/sample-doc/refs/heads/main/AtliqAI_HR_Policies.pdf"

EMBED_MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"

QDRANT_PATH = "/tmp/my_lang_vs"
COLLECTION_NAME = "hr_docs"

GROQ_MODEL = "openai/gpt-oss-20b"
''',

# ------------------ VECTOR STORE ------------------
"app/services/vectorstore.py": '''from langchain_docling import DoclingLoader
from langchain_docling.loader import ExportType
from docling_core.transforms.chunker import HierarchicalChunker
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore

from app.core.config import SOURCE, EMBED_MODEL_ID, QDRANT_PATH, COLLECTION_NAME


def load_documents():
    documents = DoclingLoader(
        file_path=SOURCE,
        export_type=ExportType.DOC_CHUNKS,
        chunker=HierarchicalChunker(),
    ).load()
    return documents


def create_vectorstore():
    docs = load_documents()

    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL_ID)

    vectorstore = QdrantVectorStore.from_documents(
        documents=docs,
        embedding=embeddings,
        path=QDRANT_PATH,
        collection_name=COLLECTION_NAME,
    )

    return vectorstore
''',

# ------------------ FORMATTER ------------------
"app/utils/formatter.py": '''def format_docs(docs):
    parts = []
    for i, doc in enumerate(docs, 1):
        dl_meta = doc.metadata.get("dl_meta", {})
        headings = dl_meta.get("headings", [])
        source = " > ".join(headings) if headings else "Unknown"

        parts.append(f"[{i}] {source}\\n{doc.page_content}")

    return "\\n\\n---\\n\\n".join(parts)
''',

# ------------------ RAG SERVICE ------------------
"app/services/rag_service.py": '''from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from app.services.vectorstore import create_vectorstore
from app.utils.formatter import format_docs
from app.core.config import GROQ_MODEL

# Initialize once
vectorstore = create_vectorstore()
retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

RAG_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "Answer using ONLY the context below. Cite section names. Say 'I don't know' if unsure."),
    ("human", "Context:\\n{context}\\n\\nQuestion: {question}")
])

llm = ChatGroq(
    model=GROQ_MODEL,
    temperature=0,
)


def rag(query: str) -> str:
    docs = retriever.invoke(query)
    context = format_docs(docs)

    prompt_value = RAG_PROMPT.invoke({
        "context": context,
        "question": query
    })

    response = llm.invoke(prompt_value)
    return response.content
''',

# ------------------ SCHEMA ------------------
"app/models/schema.py": '''from pydantic import BaseModel

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
''',

# ------------------ ROUTES ------------------
"app/api/routes.py": '''from fastapi import APIRouter
from app.models.schema import QueryRequest, QueryResponse
from app.services.rag_service import rag

router = APIRouter()

@router.post("/ask", response_model=QueryResponse)
def ask_question(payload: QueryRequest):
    answer = rag(payload.question)
    return {"answer": answer}
''',

# ------------------ MAIN ------------------
"app/main.py": '''from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(title="RAG API")

app.include_router(router, prefix="/query", tags=["RAG"])
''',

# ------------------ RUN ------------------
"run.py": '''import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.main:app", reload=True)
''',

# ------------------ REQUIREMENTS ------------------
"requirements.txt": '''fastapi
uvicorn
langchain
langchain-community
langchain-docling
langchain-huggingface
langchain-qdrant
langchain-groq
qdrant-client
sentence-transformers
docling-core
'''
}


def create_project():
    for path, content in files_content.items():
        full_path = os.path.join(BASE_DIR, path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

    print(f"✅ Project '{BASE_DIR}' created successfully!")


if __name__ == "__main__":
    create_project()