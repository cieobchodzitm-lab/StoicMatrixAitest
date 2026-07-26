# Stoic-Matrix-Layer4

Layer 4 of the Stoic Matrix architecture — the **Transport & Persistence Layer**.

This module handles data transport, event streaming, and persistence coordination between the higher-level governance layers (L5–L7) and the foundational infrastructure (Layers 1–3).

## Role in the Stoic Matrix Architecture

```
L7  — Rzeczpospolita CNOTA Dashboard   (Virtue Governance UI)
L6  — Crisis Agents & Orchestration
L5  — Scoring & NFT Passport Engine
L4  — Transport & Persistence Layer    ← this module
L3  — Vector Memory (Chroma)
L2  — LLM Interface (Ollama/qwen)
L1  — Core Infrastructure (PostgreSQL, Solana RPC)
```

## Responsibilities

- **Event Bus** — Relays virtue-score updates, NFT mint events, and crisis signals between layers
- **Data Persistence** — Manages write-through caching and durable storage of CNOTA scores and passport metadata
- **Protocol Bridge** — Translates between the FastAPI HTTP layer and the on-chain Solana transaction format
- **Stream Processing** — Buffers and batches incoming activity data before it reaches the scoring engine

## Directory Structure

```
Stoic-Matrix-Layer4/
├── README.md
├── .gitignore
├── config/
│   └── layer4.yaml          # Service configuration
├── src/
│   ├── event_bus.py         # Inter-layer event routing
│   ├── persistence.py       # Write-through cache + DB bridge
│   ├── protocol_bridge.py   # HTTP ↔ Solana transaction translator
│   └── stream_processor.py  # Activity data buffering & batching
└── tests/
    └── test_layer4.py
```

## Configuration

Copy `config/layer4.yaml.example` and adjust for your environment:

```bash
cp config/layer4.yaml.example config/layer4.yaml
```

Key settings:

| Key | Default | Description |
|-----|---------|-------------|
| `event_bus.backend` | `redis` | Backend for event streaming |
| `persistence.db_url` | `postgresql://localhost:5432/stoic` | PostgreSQL connection |
| `protocol_bridge.rpc_url` | `http://localhost:8899` | Solana RPC endpoint |
| `stream_processor.batch_size` | `50` | Activity records per batch |

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/

# Start Layer4 services
python src/event_bus.py
```

## Integration with the StoicMatrix Stack

Layer4 is consumed by the L5 scoring engine (see `backend/routers/rewards_processor.py`) and exposes the following internal interfaces:

- `POST /internal/events` — Publish a virtue event
- `GET  /internal/events/{stream}` — Subscribe to an event stream
- `POST /internal/persist` — Durably store a scored record
- `GET  /internal/health` — Layer4 health check

## License

MIT — see [`../LICENSE`](../LICENSE)
