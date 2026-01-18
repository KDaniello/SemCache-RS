import semcache_rs
import os
import pytest

CACHE_FILE = "cache_dump.bin"

@pytest.fixture
def cleanup_dump():
    # Setup
    yield
    # Teardown
    if os.path.exists(CACHE_FILE):
        os.remove(CACHE_FILE)

def test_persistence(cleanup_dump):
    # 1. Create and fill
    cache = semcache_rs.SemCache(0)
    test_vec = [1.1, 2.2, 3.3]
    cache.put("save_me", test_vec)
    assert cache.size() == 1

    # 2. Dump
    cache.dump(CACHE_FILE)
    assert os.path.exists(CACHE_FILE)

    # 3. Load into NEW cache
    cache_new = semcache_rs.SemCache(0)
    assert cache_new.size() == 0
    
    loaded_count = cache_new.load(CACHE_FILE)
    
    # 4. Verify
    assert loaded_count == 1
    assert cache_new.size() == 1
    vec = cache_new.get("save_me")
    assert vec == test_vec