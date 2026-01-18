import semcache_rs
import time

cache = semcache_rs.SemCache()

def expensive_embedding(text: str) -> list[float]:
    print(f"   🐢 CALLING EXPENSIVE API for '{text}'...")
    time.sleep(0.5) # Simulate latency of expensive API
    val = float(len(text))
    return [val, val * 2, val * 3]

text = "Hello Callback"

print("1. First Call (Cache Miss)")
start = time.time()
vec1 = cache.get_or_compute(text, expensive_embedding)
print(f"⏱️ Time: {time.time() - start:.4f}s")
print(f"📦 Vector: {vec1}")

print("\n2. Second Call (Cache HIT)")
start = time.time()
vec2 = cache.get_or_compute(text, expensive_embedding)
print(f"⏱️ Time: {time.time() - start:.4f}s")
print(f"📦 Vector: {vec2}")

assert vec1 == vec2
print("\n🎉 Callback Logic Works!")