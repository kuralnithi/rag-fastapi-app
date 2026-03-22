import os
from langchain_docling import DoclingLoader
from langchain_docling.loader import ExportType
from docling_core.transforms.chunker import HierarchicalChunker
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.core.config import SOURCE, EMBED_MODEL_ID, QDRANT_URL, COLLECTION_NAME, QDRANT_API_KEY


def load_documents():
    documents = DoclingLoader(
        file_path=SOURCE,
        export_type=ExportType.DOC_CHUNKS,
        chunker=HierarchicalChunker(),
    ).load()
    return documents


def create_vectorstore():
    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL_ID)
    
    # Just initialize the connection to the existing collection
    # rather than loading and embedding documents on every server startup!
    client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    
    # Ensure collection exists
    if not client.collection_exists(COLLECTION_NAME):
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config={"size": 384, "distance": "Cosine"} # Size for all-MiniLM-L6-v2
        )

    vectorstore = QdrantVectorStore(
        client=client,
        collection_name=COLLECTION_NAME,
        embedding=embeddings,
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
