import os
from dotenv import load_dotenv
from llama_index.core import (
    PropertyGraphIndex, 
    VectorStoreIndex, 
    SimpleDirectoryReader, 
    StorageContext, 
    load_index_from_storage
)
from llama_index.llms.featherlessai import FeatherlessLLM
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# Load environment variables
load_dotenv(override=True)

def run_comparison(query_str):
    if not os.getenv("FEATHERLESS_API_KEY"):
        print("WARNING: FEATHERLESS_API_KEY not found in .env. Please add it to run the comparison.")
        return

    llm = FeatherlessLLM(
        model=os.getenv("FEATHERLESS_MODEL", "meta-llama/Llama-3-8B-Instruct"),
        api_key=os.getenv("FEATHERLESS_API_KEY")
    )
    # Using local embeddings for better reliability
    embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

    print(f"\nQUERY: {query_str}")
    print("-" * 50)

    # 1. Traditional RAG (Vector Search)
    print("\n[Traditional Vector RAG - Results]")
    documents = SimpleDirectoryReader("./source_data").load_data()
    vector_index = VectorStoreIndex.from_documents(documents, embed_model=embed_model)
    vector_query_engine = vector_index.as_query_engine(llm=llm)
    vector_response = vector_query_engine.query(query_str)
    print(vector_response)

    # 2. GraphRAG (Property Graph)
    print("\n[GraphRAG - Results]")
    if not os.path.exists("./storage"):
        print("Error: Index not found. Please run indexer.py first.")
        return

    storage_context = StorageContext.from_defaults(persist_dir="./storage")
    graph_index = PropertyGraphIndex.from_existing(
        storage_context.property_graph_store, 
        vector_store=storage_context.vector_store,
        llm=llm, 
        embed_model=embed_model
    )
    
    # We use a retriever that can traverse relationships
    graph_query_engine = graph_index.as_query_engine(
        include_text=True, 
        similarity_top_k=2
    )
    graph_response = graph_query_engine.query(query_str)
    print(graph_response)
    
    # Optional: Print reasoning path if available (LlamaIndex specific)
    # Note: PropertyGraphIndex doesn't always expose the "path" easily in response, 
    # but the answer should be significantly better at connecting Alice to Charlie.

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        # Example multi-hop question
        query = "How is Alice connected to the unauthorized login on Charlie's server?"
    
    run_comparison(query)
