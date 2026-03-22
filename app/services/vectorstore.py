import os
from langchain_docling import DoclingLoader
from langchain_docling.loader import ExportType
from docling_core.transforms.chunker import HierarchicalChunker
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.core.config import SOURCE, EMBED_MODEL_ID, QDRANT_URL, COLLECTION_NAME


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
        url=QDRANT_URL,
        collection_name=COLLECTION_NAME,
    )

    return vectorstore

def add_file_to_vectorstore(file_path: str, vectorstore):
    ext = os.path.splitext(file_path)[1].lower()
    
    # Use standard LangChain loaders which are much better at extracting raw text from custom layouts (like resumes)
    if ext == ".pdf":
        loader = PyPDFLoader(file_path)
    elif ext == ".docx":
        loader = Docx2txtLoader(file_path)
    elif ext == ".txt":
        loader = TextLoader(file_path)
    else:
        # Fallback to Docling
        loader = DoclingLoader(file_path, export_type=ExportType.DOC_CHUNKS, chunker=HierarchicalChunker())
        
    documents = loader.load()
    
    # Split text chunks if we used a standard loader
    if ext in [".pdf", ".docx", ".txt"]:
        # Keeps entire resume in one chunk
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=8000, chunk_overlap=500)
        documents = text_splitter.split_documents(documents)
        print(f"Split into {len(documents)} chunks.")

    vectorstore.add_documents(documents)
