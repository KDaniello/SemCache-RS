import semcache_rs
import time

# Cache live for 2 seconds
cache = semcache_rs.SemCache(ttl=2)

def gen(text):
    return [1.0, 2.0]

print("📥 Put data...")
cache.get_or_compute("hello", gen)

print("👀 Check immediately:", cache.get("hello")) # Must return list

print("😴 Sleeping 3 seconds...")
time.sleep(3)

print("👀 Check after sleep:", cache.get("hello")) # Must return None