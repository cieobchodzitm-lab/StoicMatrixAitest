# Stoic-Matrix-Layer3

Layer 3 of the Stoic Matrix architecture — the **Vector Memory Layer**.

This module provides semantic storage and retrieval capabilities for the Stoic Matrix stack.  It sits between the LLM interface (Layer 2) and the Transport & Persistence layer (Layer 4), supplying long-term vector memory to the higher-level governance and agent layers (L5–L7).

## Role in the Stoic Matrix Architecture

```
L7  — Rzeczpospolita CNOTA Dashboard   (Virtue Governance UI)
L6  — Crisis Agents & Orchestration
L5  — Scoring & NFT Passport Engine
L4  — Transport & Persistence Layer
L3  — Vector Memory (Chroma)           ← this module
L2  — LLM Interface (Ollama/qwen)
L1  — Core Infrastructure (PostgreSQL, Solana RPC)
```

## Responsibilities

- **Vector Store** — Manages ChromaDB collections that hold document embeddings for citizens, virtue events, and crisis signals
- **Semantic Search** — Nearest-neighbour retrieval; finds the most contextually similar records for a given query
- **Memory Manager** — Dual-tier memory: a bounded FIFO *working memory* for short-lived context and a persistent *long-term memory* backed by the vector store
- **Embedding Client** — Calls the Ollama `/api/embeddings` endpoint (Layer 2) to convert text into dense vectors

## Directory Structure

```
Stoic-Matrix-Layer3/
├── README.md
├── .gitignore
├── config/
│   └── layer3.yaml.example      # Service configuration template
├── requirements.txt
├── src/
│   ├── vector_store.py          # ChromaDB collection management
│   ├── embedding_client.py      # Embedding API client (→ L2 Ollama)
│   ├── semantic_search.py       # Nearest-neighbour semantic retrieval
│   └── memory_manager.py        # Short-term + long-term memory abstraction
└── tests/
    └── test_layer3.py
```

## Configuration

Copy `config/layer3.yaml.example` and adjust for your environment:

```bash
cp config/layer3.yaml.example config/layer3.yaml
```

Key settings:

| Key | Default | Description |
|-----|---------|-------------|
| `chroma.host` | `localhost` | ChromaDB server host |
| `chroma.port` | `8000` | ChromaDB server port |
| `chroma.persist_directory` | `./chroma_data` | Local persistence path (dev) |
| `embedding_client.base_url` | `http://localhost:11434` | Ollama (L2) endpoint |
| `embedding_client.model` | `nomic-embed-text` | Embedding model name |
| `memory_manager.short_term_capacity` | `100` | Working memory size |

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests (no external services required)
pytest tests/

# Optional: start a local ChromaDB server
docker run -p 8000:8000 chromadb/chroma
```

## Integration with the StoicMatrix Stack

Layer 3 is consumed by the L6 Crisis Agents (see `backend/routers/`) and exposes the following internal interfaces:

- `POST /internal/memory/index` — Embed and store a document
- `POST /internal/memory/search` — Semantic nearest-neighbour query
- `GET  /internal/memory/{doc_id}` — Retrieve a stored document by ID
- `DELETE /internal/memory/{doc_id}` — Remove a document from the store
- `GET  /internal/health` — Layer3 health check

## License

MIT — see [`../LICENSE`](../LICENSE)
