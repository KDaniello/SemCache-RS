# ⚡ SemCache

[![PyPI](https://img.shields.io/pypi/v/semcache-rs.svg)](https://pypi.org/project/semcache-rs/)
[![Downloads](https://img.shields.io/pypi/dm/semcache-rs.svg)](https://pypi.org/project/semcache-rs/)
[![Rust](https://img.shields.io/badge/built_with-Rust-dca282.svg)](https://www.rust-lang.org/)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**SemCache** is a high-performance, in-process caching layer for LLM embeddings, powered by **Rust**.
It is designed to reduce OpenAI/Cohere API costs by up to 90% and eliminate latency for repeated or semantically similar queries.

> **Why not Redis?** Redis requires network round-trips (~1-5ms). SemCache runs inside your Python process, offering **microsecond** access times using Zero-Copy memory mapping.

---

## 🚀 Key Features

*   **⚡ Blazing Fast:** Core logic written in Rust using `DashMap` for lock-free concurrency.
*   **🧠 Smart Callbacks:** `get_or_compute` pattern handles the GIL and calls your Python embedding function *only* on cache misses.
*   **💾 Persistence:** High-speed binary dumps (via **Bincode**) allow loading 100k vectors in ~1 second.
*   **🔍 Semantic Search:** Built-in **SIMD-accelerated** Cosine Similarity search to find similar queries without external vector databases.
*   **⏳ TTL Support:** Automatically expires old entries to manage memory usage effectively.

---

## 📦 Installation

*(Comming soon to PyPI)*. For now, build from source:

```bash
pip install maturin
maturin develop --release
```

## ⚡ Usage Examples

1. Basic: Save Money on API Calls
```python
from semcache import SemCache
import time

# Init cache with 1-hour TTL
cache = SemCache(ttl=3600)

def ask_openai(text: str) -> list[float]:
    print(f"💸 Paying for API call: {text}...")
    # call OpenAI API here ...
    return [0.1, 0.2, 0.3]

# First call: Miss -> Calls Python -> Stores result
vec = cache.get_or_compute("Hello World", ask_openai)

# Second call: Hit -> Returns instantly (No API cost)
vec = cache.get_or_compute("Hello World", ask_openai)
```

2. Advanced: Semantic Search & Persistence
```python
# Save state to disk (Binary format, highly compressed)
cache.dump("backup.bin")

# Load state on startup
new_cache = SemCache()
new_cache.load("backup.bin")

# Find similar queries
# Useful for finding if we already embedded something similar
query_vec = [0.1, 0.2, 0.25] # Similar to [0.1, 0.2, 0.3]
cached_vec = new_cache.get_similar(query_vec, threshold=0.95)
```

## 📊 Benchmarks

### Business Impact (RAG Scenario)
Scenario: 1000 requests, 80% repetition rate (common in chat apps), 50ms API latency.

| Method | Time | Cost |
| :--- | :--- | :--- |
| No Cache | 50.37s | $$$ |
| **SemCache** | **10.17s** | **$** |
| **Speedup** | **4.95x** | **-80%** |

### Technical Performance (100k Vectors)
Comparison between standard JSON serialization and SemCache's optimized Bincode + SIMD engine.
| Operation | Standard (JSON/Python) | SemCache (Bincode/SIMD) | Improvement |
| :--- | :--- | :--- | :--- |
| **Dump to Disk** | 4.70s | **0.79s** | **6x Faster** |
| **Load from Disk** | 10.80s | **1.10s** | **10x Faster** |
| **Semantic Search** | 322ms | **22ms** | **15x Faster** |
| **File Size** | 256 MB | **109 MB** | **2.5x Smaller** |

## 🛠 Tech Stack
- Rust & PyO3: FFI bindings.
- DashMap: Concurrent HashMap for AsyncIO.
- SimSIMD: Hardware-accelerated vector math.
- Bincode: Compact binary serialization.