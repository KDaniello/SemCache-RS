import semcache_rs
import time
import random
import math
import os

CACHE_FILE = "bench_cache.dump"
N_ITEMS = 100_000 # 100 тысяч векторов (это уже нагрузка)
DIM = 128 # Размерность вектора

def create_random_vec(dim):
    # Просто случайный нормализованный вектор
    vec = [random.random() for _ in range(dim)]
    norm = math.sqrt(sum(x*x for x in vec))
    return [x/norm for x in vec]

def run_benchmark():
    print(f"🔥 Benchmark v1.0 Baseline | Items: {N_ITEMS} | Dim: {DIM}")
    
    # 1. Генерация и Заполнение
    cache = semcache_rs.SemCache(0)
    print("Generating data...")
    # Генерируем данные в Python и пихаем в Rust (это может быть медленно, но нам важно чтение)
    # Для скорости сделаем один вектор и будем пихать его с разными ключами
    vec = create_random_vec(DIM) 
    
    start = time.time()
    for i in range(N_ITEMS):
        cache.put(f"key_{i}", vec)
    print(f"📥 Put time: {time.time() - start:.4f}s")

    # 2. Dump (JSON)
    print("💾 Dumping (JSON)...")
    start = time.time()
    cache.dump(CACHE_FILE)
    dump_time = time.time() - start
    file_size = os.path.getsize(CACHE_FILE) / (1024 * 1024)
    print(f"⏱️ Dump time: {dump_time:.4f}s | Size: {file_size:.2f} MB")

    # 3. Load (JSON)
    print("📂 Loading (JSON)...")
    cache_new = semcache_rs.SemCache(0)
    start = time.time()
    cache_new.load(CACHE_FILE)
    load_time = time.time() - start
    print(f"⏱️ Load time: {load_time:.4f}s")

    # 4. Semantic Search (Linear Scan)
    print("🔎 Semantic Search (10 queries)...")
    query = create_random_vec(DIM)
    start = time.time()
    for _ in range(10):
        cache.get_similar(query, 0.99)
    search_time = (time.time() - start) / 10
    print(f"⏱️ Avg Search time: {search_time:.4f}s")

    # Clean up
    if os.path.exists(CACHE_FILE):
        os.remove(CACHE_FILE)

    return {
        "dump": dump_time,
        "load": load_time,
        "search": search_time,
        "size_mb": file_size
    }

if __name__ == "__main__":
    run_benchmark()