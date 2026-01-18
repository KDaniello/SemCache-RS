import semcache_rs
import time
import pytest

def expensive_embedding(text: str) -> list[float]:
    # Simulate latency
    time.sleep(0.1) 
    val = float(len(text))
    return [val, val * 2, val * 3]

def test_callback_logic():
    cache = semcache_rs.SemCache(0)
    text = "Hello Callback"

    # 1. First Call (Cache Miss)
    start = time.time()
    vec1 = cache.get_or_compute(text, expensive_embedding)
    duration = time.time() - start
    
    # Assert delay happened (at least 0.1s)
    assert duration >= 0.1
    assert vec1 == [14.0, 28.0, 42.0]

    # 2. Second Call (Cache HIT)
    start = time.time()
    vec2 = cache.get_or_compute(text, expensive_embedding)
    duration_hit = time.time() - start

    # Assert instant response
    assert duration_hit < 0.01 
    assert vec1 == vec2