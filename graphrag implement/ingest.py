import os
import sys
from dotenv import load_dotenv
from llama_index.core import PropertyGraphIndex, SimpleDirectoryReader, StorageContext
from llama_index.llms.featherlessai import FeatherlessLLM
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# Load environment variables
load_dotenv(override=True)

def ingest_new_data(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        return

    if not os.path.exists("./storage"):
        print("Error: Index storage not found. Run indexer.py first.")
        return

    if not os.getenv("FEATHERLESS_API_KEY"):
        print("WARNING: FEATHERLESS_API_KEY not found in .env. Please add it to run the ingester.")
        return

    print(f"Ingesting new evidence: {file_path}...")
    
    # Load specific file
    reader = SimpleDirectoryReader(input_files=[file_path])
    documents = reader.load_data()

    llm = FeatherlessLLM(
        model=os.getenv("FEATHERLESS_MODEL", "meta-llama/Llama-3-8B-Instruct"),
        api_key=os.getenv("FEATHERLESS_API_KEY")
    )
    # Using local embeddings for better reliability
    embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

    # Load existing index
    storage_context = StorageContext.from_defaults(persist_dir="./storage")
    index = PropertyGraphIndex.from_existing_storage(
        storage_context, 
        llm=llm, 
        embed_model=embed_model
    )

    # Insert new documents
    for doc in documents:
        index.insert(doc)

    # Persist updated index
    index.storage_context.persist(persist_dir="./storage")
    print("Ingestion complete and index updated.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ingest.py <path_to_evidence_file>")
    else:
        ingest_new_data(sys.argv[1])
