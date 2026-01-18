import semcache_rs

def test_basic_crud():
    cache = semcache_rs.SemCache(0)
    text = "Basic Test"
    vec = [0.1, 0.2]

    # Put
    cache.put(text, vec)
    
    # Get Hit
    assert cache.get(text) == vec
    
    # Get Miss
    assert cache.get("Missing") is None
    
    # Size
    assert cache.size() == 1
    
    # Clear
    cache.clean()
    assert cache.size() == 0