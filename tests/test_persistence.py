import semcache_rs
import os

CACHE_FILE = "cache_dump.json"

# 1. Создаем кэш и наполняем
cache = semcache_rs.SemCache(0)
cache.put("save_me", [1.1, 2.2, 3.3])
print(f"📦 Created cache with size: {cache.size()}")

# 2. Сохраняем
print("💾 Dumping to disk...")
cache.dump(CACHE_FILE)

# 3. Создаем НОВЫЙ пустой кэш
cache_new = semcache_rs.SemCache(0)
print(f"✨ New cache size: {cache_new.size()}") # Должно быть 0

# 4. Загружаем
print("📂 Loading from disk...")
loaded_count = cache_new.load(CACHE_FILE)
print(f"📊 Loaded items: {loaded_count}")

# 5. Проверяем данные
vec = cache_new.get("save_me")
print(f"🔍 Check data: {vec}")

assert vec == [1.1, 2.2, 3.3]
print("🎉 Persistence works!")

# Чистим за собой
if os.path.exists(CACHE_FILE):
    os.remove(CACHE_FILE)