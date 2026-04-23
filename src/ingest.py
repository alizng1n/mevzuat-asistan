import os
import glob
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv()

RAW_DATA_DIR = os.path.join("data", "raw")
CHROMA_DIR = os.path.join("data", "chroma")

def load_documents():
    documents = []
    
    # Load PDFs
    pdf_files = glob.glob(os.path.join(RAW_DATA_DIR, "*.pdf"))
    for pdf_file in pdf_files:
        print(f"Loading {pdf_file}...")
        loader = PyPDFLoader(pdf_file)
        documents.extend(loader.load())
        
    # Load TXTs
    txt_files = glob.glob(os.path.join(RAW_DATA_DIR, "*.txt"))
    for txt_file in txt_files:
        print(f"Loading {txt_file}...")
        loader = TextLoader(txt_file, encoding='utf-8')
        documents.extend(loader.load())
        
    # Load DOCXs
    docx_files = glob.glob(os.path.join(RAW_DATA_DIR, "*.docx"))
    for docx_file in docx_files:
        print(f"Loading {docx_file}...")
        loader = Docx2txtLoader(docx_file)
        documents.extend(loader.load())
        
    return documents

def main():
    print("Starting ingestion process...")
    documents = load_documents()
    
    if not documents:
        print(f"No documents found in {RAW_DATA_DIR}. Please add some PDFs or TXTs.")
        return

    print(f"Loaded {len(documents)} document pages/sections.")
    
    # Split texts
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        length_function=len
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunks.")
    
    # Embed and store
    print("Initializing embeddings and VectorDB...")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    # Create or update ChromaDB
    db = Chroma.from_documents(
        chunks, 
        embeddings, 
        persist_directory=CHROMA_DIR
    )
    # Chroma in recent versions automatically persists, but we can call db.persist() if using older versions.
    # We are using 0.4.24, persist() might be deprecated, but we'll call it for safety if needed, or rely on automatic.
    
    print(f"Successfully ingested data into ChromaDB at {CHROMA_DIR}.")

if __name__ == "__main__":
    main()
