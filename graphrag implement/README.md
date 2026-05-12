# GraphRAG Forensic Prototype

This prototype demonstrates how GraphRAG (using LlamaIndex Property Graph) excels at "seeing through" complex, multi-hop forensic evidence compared to traditional Vector RAG.

## Problem Statement
In digital forensics, evidence is often fragmented across chat logs, server logs, and financial records. Traditional RAG struggles to connect a person in a chat to an IP address in a log file, and then to a bank account in a transaction record.

## Solution
GraphRAG extracts entities (People, IPs, Accounts) and their relationships into a knowledge graph. This allows the LLM to traverse the "hops" to find hidden connections.

## How to Run

1.  **Set up Environment**:
    ```bash
    # The environment is already set up if you are using the Gemini CLI
    # Just ensure your FEATHERLESS_API_KEY is in the .env file
    ```

2.  **Add API Key**:
    Edit the `.env` file and add your `FEATHERLESS_API_KEY`. You can also configure `FEATHERLESS_MODEL` and `FEATHERLESS_EMBEDDING_MODEL` if desired.

3.  **Run the Full Demo**:
    ```bash
    ./run_demo.sh
    ```

## Scripts
- `data_generator.py`: Creates synthetic forensic data in `./source_data`.
- `indexer.py`: Builds the Property Graph Index.
- `query.py`: Runs a query against both Naive RAG and GraphRAG for comparison.
- `ingest.py`: Allows adding new evidence files on the fly.

## Sample Multi-Hop Query
*"How is Alice connected to the unauthorized login on Charlie's server?"*

**Reasoning Path required:**
Alice (Chat) -> Bob (Chat) -> IP Address (Chat) -> IP Address (Server Log) -> Unauthorized Login.
