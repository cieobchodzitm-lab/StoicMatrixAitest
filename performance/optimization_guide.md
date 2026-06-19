# 🚀 StoicMatrix Performance Optimization Guide

## Executive Summary

This guide provides a comprehensive optimization strategy for the StoicMatrix L7 CNOTA Dashboard, focusing on:
- **Latency Reduction** (API response times)
- **Resource Optimization** (CPU, Memory, I/O)
- **Throughput Improvement** (Requests per second)
- **Database Performance** (Query optimization)
- **Frontend Performance** (UI responsiveness)

---

## Architecture Overview

```
L7 — React Dashboard (Frontend)
     ↓
L6 — FastAPI Server (Backend)
     ↓
L5 — Scoring Engine
     ↓
L4 — Event Bus + Persistence
     ↓
L3 — Vector Memory (ChromaDB)
     ↓
L2 — LLM Interface (Ollama)
     ↓
L1 — PostgreSQL + Solana RPC
```

---

## 1. Backend Optimization (FastAPI - L6)

### 1.1 Connection Pooling

**Problem**: Each request creates a new database connection

**Solution**: Implement connection pooling

```python
# backend/config.py
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,                    # Active connections
    max_overflow=40,                 # Additional connections
    pool_pre_ping=True,              # Verify connections before use
    pool_recycle=3600,               # Recycle connections every hour
    echo=False                       # Disable SQL logging in production
)
```

**Expected Improvement**: -30% to -50% latency

### 1.2 Query Optimization

**Problem**: N+1 queries, missing indexes

**Solution**: Use SQLAlchemy eager loading

```python
# backend/routers/cnota.py
from sqlalchemy.orm import joinedload

@router.get("/api/cnota/profile/{user_id}")
async def get_profile(user_id: int, db: Session):
    # Bad: N+1 queries
    # user = db.query(User).filter(User.id == user_id).first()
    # virtues = user.virtues  # Additional query per virtue
    
    # Good: Single query with joins
    user = db.query(User).options(
        joinedload(User.virtues),
        joinedload(User.nft_passport)
    ).filter(User.id == user_id).first()
    
    return user
```

**Database Indexes**:

```sql
-- Add these indexes to PostgreSQL
CREATE INDEX idx_users_id ON users(id);
CREATE INDEX idx_virtues_user_id ON virtues(user_id);
CREATE INDEX idx_scores_user_timestamp ON scores(user_id, timestamp DESC);
CREATE INDEX idx_leaderboard_virtue ON leaderboard_scores(virtue_type, score DESC);
```

**Expected Improvement**: -40% to -70% database latency

### 1.3 Async Operations

**Problem**: Blocking I/O operations

**Solution**: Use async/await throughout

```python
# backend/main.py
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import asyncio

app = FastAPI()

@app.get("/api/cnota/leaderboard")
async def get_leaderboard(db: AsyncSession):
    # Run multiple queries in parallel
    sophia_scores, andreia_scores, dikaiosyne_scores = await asyncio.gather(
        db.execute(select(Virtue).where(Virtue.type == 'sophia')),
        db.execute(select(Virtue).where(Virtue.type == 'andreia')),
        db.execute(select(Virtue).where(Virtue.type == 'dikaiosyne'))
    )
    
    return {
        "sophia": sophia_scores,
        "andreia": andreia_scores,
        "dikaiosyne": dikaiosyne_scores
    }
```

**Expected Improvement**: -20% to -40% response time

### 1.4 Response Caching

**Problem**: Expensive queries run repeatedly

**Solution**: Implement Redis caching

```python
# backend/cache.py
from redis import Redis
from functools import wraps
import json

redis_client = Redis(host='localhost', port=6379, db=0)

def cache(expire: int = 300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key
            cache_key = f"{func.__name__}:{args}:{kwargs}"
            
            # Try to get from cache
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            redis_client.setex(
                cache_key,
                expire,
                json.dumps(result, default=str)
            )
            
            return result
        return wrapper
    return decorator

# Usage
@router.get("/api/cnota/leaderboard")
@cache(expire=300)  # Cache for 5 minutes
async def get_leaderboard(db: AsyncSession):
    ...
```

**Expected Improvement**: -90% latency for cached queries

---

## 2. Vector Memory Optimization (ChromaDB - L3)

### 2.1 Vector Index Configuration

**Problem**: Slow semantic search on large collections

**Solution**: Optimize ChromaDB indexes

```python
# src/vector_store.py
from chromadb.config import Settings

settings = Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="./chroma_data",
    anonymized_telemetry=False,
    allow_reset=False,
    # Performance tuning
    is_persistent=True,
    persist_path="./chroma_data"
)

client = chromadb.Client(settings)

# Create collection with optimized settings
collection = client.get_or_create_collection(
    name="virtue_events",
    metadata={"hnsw:space": "cosine"},  # Use cosine similarity
    embedding_function=embedding_function
)
```

### 2.2 Batch Embedding

**Problem**: Single embeddings are slow

**Solution**: Batch process embeddings

```python
# src/embedding_client.py
async def batch_embed(
    texts: List[str],
    batch_size: int = 32
) -> List[List[float]]:
    """
    Efficiently embed multiple texts
    """
    embeddings = []
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        batch_embeddings = await embedding_client.embed(batch)
        embeddings.extend(batch_embeddings)
    
    return embeddings
```

**Expected Improvement**: -50% embedding time for multiple texts

---

## 3. Frontend Optimization (React - L7)

### 3.1 Code Splitting

**Problem**: Large bundle size

**Solution**: Lazy load components

```javascript
// frontend/src/App.jsx
import { lazy, Suspense } from 'react';

const Dashboard = lazy(() => import('./components/Dashboard'));
const PassportView = lazy(() => import('./components/PassportView'));
const LeaderboardView = lazy(() => import('./components/LeaderboardView'));

function App() {
  return (
    <Suspense fallback={<Loading />}>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/passport" element={<PassportView />} />
        <Route path="/leaderboard" element={<LeaderboardView />} />
      </Routes>
    </Suspense>
  );
}
```

**Expected Improvement**: -60% initial bundle size

### 3.2 Memoization & Virtualization

```javascript
// frontend/src/components/LeaderboardView.jsx
import { memo, useMemo } from 'react';
import { FixedSizeList as List } from 'react-window';

const LeaderboardRow = memo(({ index, style, data }) => (
  <div style={style} className="leaderboard-row">
    {/* Row content */}
  </div>
));

function LeaderboardView({ users }) {
  // Only re-render when users change
  const sortedUsers = useMemo(
    () => users.sort((a, b) => b.score - a.score),
    [users]
  );

  return (
    <List
      height={600}
      itemCount={sortedUsers.length}
      itemSize={50}
      width="100%"
      itemData={sortedUsers}
    >
      {LeaderboardRow}
    </List>
  );
}

export default memo(LeaderboardView);
```

**Expected Improvement**: -80% for large leaderboards (1000+ items)

### 3.3 Chart Optimization

```javascript
// frontend/src/components/VirtueRadar.jsx
import ChartJS from 'chart.js/auto';

const VirtueRadar = memo(({ data }) => {
  const chartRef = useRef(null);
  const chartInstance = useRef(null);

  useEffect(() => {
    if (!chartRef.current) return;

    // Destroy previous chart
    if (chartInstance.current) {
      chartInstance.current.destroy();
    }

    // Create new chart with optimization
    chartInstance.current = new ChartJS(chartRef.current, {
      type: 'radar',
      data,
      options: {
        responsive: true,
        animation: {
          duration: 0  // Disable animation for performance
        },
        plugins: {
          legend: {
            labels: {
              usePointStyle: true,
              boxWidth: 6
            }
          }
        }
      }
    });

    return () => {
      if (chartInstance.current) {
        chartInstance.current.destroy();
      }
    };
  }, [data]);

  return <canvas ref={chartRef} />;
}, (prevProps, nextProps) => {
  // Custom comparison for memoization
  return JSON.stringify(prevProps.data) === JSON.stringify(nextProps.data);
});
```

**Expected Improvement**: -50% chart rendering time

---

## 4. Database Optimization (PostgreSQL - L1)

### 4.1 Partitioning

**Problem**: Large tables slow down queries

**Solution**: Partition by time

```sql
-- Partition scores table by month
CREATE TABLE scores_2026_01 PARTITION OF scores
  FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');

CREATE TABLE scores_2026_02 PARTITION OF scores
  FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');
```

### 4.2 Query Analysis

```sql
-- Enable query analysis
EXPLAIN ANALYZE
SELECT u.id, u.username, AVG(v.score)
FROM users u
JOIN virtues v ON u.id = v.user_id
WHERE v.timestamp > NOW() - INTERVAL '7 days'
GROUP BY u.id, u.username
ORDER BY AVG(v.score) DESC
LIMIT 100;
```

---

## 5. Docker & Infrastructure Optimization

### 5.1 Multi-stage Build

```dockerfile
# Dockerfile - Multi-stage build
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci && npm run build

FROM python:3.11-slim AS final
WORKDIR /app

# Copy compiled frontend
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Install backend dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend ./backend
EXPOSE 7860
CMD ["python", "backend/main.py"]
```

**Expected Improvement**: -70% Docker image size

### 5.2 Resource Limits

```yaml
# docker-compose.yml
version: '3.8'
services:
  backend:
    image: stoic-matrix:latest
    ports:
      - "7860:7860"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/stoic
      - REDIS_URL=redis://redis:6379/0
    resources:
      limits:
        cpus: '2'
        memory: 4G
      reservations:
        cpus: '1'
        memory: 2G
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:7860/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

---

## 6. Monitoring & Profiling

### 6.1 Performance Monitoring

```python
# backend/monitoring.py
from prometheus_client import Counter, Histogram, generate_latest
import time
from functools import wraps

request_count = Counter('requests_total', 'Total requests')
request_duration = Histogram('request_duration_seconds', 'Request duration')
db_query_time = Histogram('db_query_seconds', 'Database query time')

def track_performance(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.time()
        request_count.inc()
        
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            duration = time.time() - start
            request_duration.observe(duration)
    
    return wrapper

@app.get("/metrics")
def metrics():
    return generate_latest()
```

### 6.2 Load Testing

```bash
# Use Apache Bench
ab -n 10000 -c 100 http://localhost:7860/api/health

# Use wrk
wrk -t4 -c100 -d30s http://localhost:7860/api/cnota/leaderboard
```

---

## 7. Implementation Checklist

- [ ] **Week 1**: Connection pooling + Query optimization
- [ ] **Week 2**: Redis caching + Async operations
- [ ] **Week 3**: Frontend code splitting + Memoization
- [ ] **Week 4**: Database partitioning + Monitoring
- [ ] **Week 5**: Load testing + Fine-tuning

---

## 8. Expected Performance Gains

| Optimization | Before | After | Improvement |
|--------------|--------|-------|-------------|
| API Latency | 500ms | 80ms | **84%** |
| Database Queries | 400ms | 100ms | **75%** |
| Frontend Load | 3s | 800ms | **73%** |
| Throughput | 100 req/s | 500 req/s | **400%** |
| Memory Usage | 2GB | 1.2GB | **40%** |
| Docker Image | 1.5GB | 500MB | **67%** |

---

## 9. References

- [FastAPI Performance](https://fastapi.tiangolo.com/deployment/concepts/)
- [PostgreSQL Optimization](https://wiki.postgresql.org/wiki/Performance_Optimization)
- [React Performance](https://react.dev/reference/react/memo)
- [ChromaDB Best Practices](https://docs.trychroma.com/)

---

## 10. Support

For questions or issues:
- 📧 Email: support@stoicmatrix.dev
- 🐛 GitHub Issues: [issues](https://github.com/cieobchodzitm-lab/StoicMatrixAitest/issues)
- 💬 Discussions: [discussions](https://github.com/cieobchodzitm-lab/StoicMatrixAitest/discussions)
