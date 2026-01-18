# SemCache: Architecture & Design Document

## 1. Problem Statement
In modern LLM/RAG architectures, obtaining embeddings is a significant bottleneck:
1.  **Latency:** API calls to OpenAI/Cohere take 200-500ms.
2.  **Cost:** Repeated queries incur redundant charges.
3.  **Infrastructure Complexity:** Deploying Redis just for caching embeddings adds operational overhead (network, maintenance).

**SemCache** solves this by providing an **in-process**, high-performance caching layer backed by Rust, eliminating network round-trips entirely.

---

## 2. Core Architecture

### 2.1 Design Principles
*   **Zero-Overhead Reads:** Cache hits should be instantaneous (< 0.1ms).
*   **Transparent Integration:** The library acts as a middleware, automatically invoking the embedding provider only on cache misses.
*   **Thread Safety:** Must support highly concurrent Python web servers (FastAPI/Uvicorn) without global locking.

## 3. Technical Implementation Details
### 3.1 Storage Engine (In-Memory)
We chose DashMap over standard RwLock<HashMap> to reduce contention in async workloads.

- Key: SHA-256 hash of the input text (Hex string).
- Value: CacheEntry struct containing the Vector and Timestamp (for TTL).
- Concurrency: Sharded locking allows multiple threads to read/write simultaneously without blocking the entire cache.

### 3.2 Persistence Layer
- Format: Bincode.
  - Why: Bincode is a compact binary serialization format significantly faster than JSON.
  - Benchmark: 100k vectors load in ~1s (vs ~10s for JSON).
- Strategy: Snapshot-based dumping. Future versions may support Append-Only Logs (AOL).

### 3.3 Semantic Search (SIMD Accelerated)
Unlike traditional key-value caches, SemCache supports finding "similar" queries using Linear Scan with SIMD.

- Algorithm: Cosine Similarity.
- Optimization: We use the simsimd crate to leverage AVX2/AVX-512 CPU instructions.
- Trade-off: Linear scan is O(N). It is extremely fast for caches < 1M items (approx 20ms latency), avoiding the complexity of building HNSW graphs for small datasets.

## API Specification
The API is designed to be Pythonic while hiding Rust complexity.

```python
from semcache import SemCache

# 1. Initialize with TTL (Time-To-Live)
cache = SemCache(ttl=3600)

# 2. Define the expensive operation
def call_openai(text: str) -> list[float]:
    # ... logic to call API ...
    return embedding

# 3. Transparent Caching
# Rust handles the logic: Check Cache -> If Miss, Call Func -> Store -> Return
vector = cache.get_or_compute("Hello World", call_openai)
```

## 5. Performance Goals & Results
| Metric | Target |	Actual (v1.0 Benchmark) |
|:-------|:-------|:------------------------|
| Hit Latency |	< 0.1ms |	0.00ms (Instant) |
| Search (100k items) |	< 100ms |	~22ms (via SIMD) |
| Load Time (100k items) |	< 2s |	1.1s (via Bincode) |
| Throughput |	50k ops/sec |	> 100k ops/sec |

## 6. Future Roadmap

1. Redis Backend: Optional offloading to Redis for distributed deployments.
2. HNSW Index: Integration of hnsw_rs for sub-linear search on datasets > 1M vectors.
3. AsyncIO Support: Native async def callback support for non-blocking misses.