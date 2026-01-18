import semcache_rs
import math

# Функция для создания вектора (просто нормализуем список)
def create_vec(x, y):
    length = math.sqrt(x**2 + y**2)
    return [x/length, y/length]

cache = semcache_rs.SemCache(0)

# 1. Кладем вектор [1, 0] (направление вправо)
vec_a = create_vec(1.0, 0.0)
cache.put("right", vec_a)
print(f"📥 Put 'right': {vec_a}")

# 2. Ищем вектор [0.99, 0.01] (почти вправо)
# Он должен найтись, так как угол очень маленький
vec_query = create_vec(0.99, 0.05)
print(f"🔎 Querying similar to: {vec_query}")

# Порог 0.9 (очень похожие)
found = cache.get_similar(vec_query, 0.9)
print(f"✅ Found: {found}")

assert found == vec_a

# 3. Ищем вектор [0, 1] (вверх, перпендикулярно)
# Сходство 0. Не должен найтись.
vec_up = create_vec(0.0, 1.0)
miss = cache.get_similar(vec_up, 0.9)
print(f"❌ Miss check: {miss}")

assert miss is None
print("🎉 Semantic Search Works!")