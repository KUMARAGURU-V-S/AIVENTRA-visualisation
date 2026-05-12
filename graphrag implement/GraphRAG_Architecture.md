# GraphRAG Architecture: Forensic Prototype

This document explains the architecture and operational workflow of the GraphRAG implementation used in this forensic prototype.

## 1. Overview
The prototype demonstrates the superiority of Graph-based Retrieval-Augmented Generation (GraphRAG) over Traditional Vector RAG, particularly in resolving multi-hop forensic queries where evidence is fragmented across multiple sources (chats, server logs, bank records).

## 2. Core Components

### A. Data Generation (`data_generator.py`)
This module simulates a fragmented digital forensic scenario by generating synthetic data:
- **Chats (`chats.txt`)**: Text messages between Alice and Bob showing malicious intent and IP addresses.
- **Server Logs (`server_logs.csv`)**: Records of an unauthorized login and data export from Charlie's server using a specific IP.
- **Bank Records (`bank_records.csv`)**: Financial transactions from Bob to Alice.
- **Emails (`emails.txt`)**: A phishing email sent to Charlie.

### B. Indexing & Knowledge Graph Construction (`indexer.py`)
This is the core of the GraphRAG setup.
- **Library**: Utilizes LlamaIndex's `PropertyGraphIndex`.
- **LLM**: `FeatherlessLLM` (defaulting to `meta-llama/Llama-3-8B-Instruct`) via Featherless AI.
- **Embeddings**: `OpenAIEmbedding` (defaulting to `nomic-ai/nomic-embed-text-v1.5`) via Featherless AI.
- **Process**: It loads the synthetic documents from `./source_data` and uses the LLM to extract entities (e.g., "Alice", "192.168.50.122", "ACC-8822") and their relationships (e.g., "used IP", "transferred money to"). These are stored as a Property Graph in the `./storage` directory.

### C. Dynamic Data Ingestion (`ingest.py`)
Allows for continuous operation by adding new evidence to the existing knowledge graph without rebuilding it from scratch. It loads a specific file, extracts its entities and relationships, and updates the stored Property Graph.

### D. Querying and Comparison (`query.py`)
Demonstrates the difference between approaches using a complex question: *"How is Alice connected to the unauthorized login on Charlie's server?"*
1. **Traditional Vector RAG**: Creates a `VectorStoreIndex` from the raw text. It struggles because no single document contains both "Alice" and "unauthorized login on Charlie's server". It relies purely on text similarity, often failing on complex logic.
2. **GraphRAG**: Loads the `PropertyGraphIndex`. When queried, it traverses the entity relationships (Alice -> Bob -> IP Address -> Server Login). It retrieves the specific graph paths and feeds them to the LLM to formulate a complete, multi-hop answer.

## 3. How the Architecture Solves Multi-Hop Queries

**The Reasoning Path:**
1. **Document 1 (Chat)**: Connects Alice to Bob.
2. **Document 2 (Chat)**: Connects Bob to IP `192.168.50.122`.
3. **Document 3 (Server Log)**: Connects IP `192.168.50.122` to the unauthorized login.

While traditional RAG might only retrieve Document 1 (because it mentions "Alice"), GraphRAG extracts the entities as nodes and connects them with edges. During retrieval, GraphRAG can traverse the graph: `(Alice) -[works with]-> (Bob) -[uses]-> (IP: 192.168.50.122) -[performs]-> (Unauthorized Login)`. This retrieved sub-graph provides the LLM with the exact context needed to answer the complex query accurately.
