import os
import shutil
from dotenv import load_dotenv
from llama_index.core import PropertyGraphIndex, SimpleDirectoryReader, StorageContext
from llama_index.core.indices.property_graph import SimpleLLMPathExtractor, ImplicitPathExtractor
from llama_index.llms.featherlessai import FeatherlessLLM
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# Load environment variables
load_dotenv(override=True)

if not os.getenv("FEATHERLESS_API_KEY"):
    print("WARNING: FEATHERLESS_API_KEY not found in .env. Please add it to run the indexer.")
    exit(1)

def build_index():
    print("Loading documents from ./source_data...")
    documents = SimpleDirectoryReader("./source_data").load_data()

    llm = FeatherlessLLM(
        model=os.getenv("FEATHERLESS_MODEL", "meta-llama/Llama-3-8B-Instruct"),
        api_key=os.getenv("FEATHERLESS_API_KEY")
    )
    # Using local embeddings for better reliability
    embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

    print("Building Property Graph Index (this may take a minute and uses LLM calls)...")
    
    # Using the default SchemaLLMPathExtractor which works well for generic entity extraction
    index = PropertyGraphIndex.from_documents(
        documents,
        llm=llm,
        embed_model=embed_model,
        kg_extractors=[
            SimpleLLMPathExtractor(llm=llm, num_workers=1),
            ImplicitPathExtractor()
        ],
        show_progress=True,
        use_async=False
    )

    print("Persisting index to ./storage...")
    if os.path.exists("./storage"):
        shutil.rmtree("./storage")
    index.storage_context.persist(persist_dir="./storage")
    print("Indexing complete.")

if __name__ == "__main__":
    build_index()
