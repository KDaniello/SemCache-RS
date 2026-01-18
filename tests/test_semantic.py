import semcache_rs
import math
import pytest

def create_vec(x, y):
    length = math.sqrt(x**2 + y**2)
    return [x/length, y/length]

def test_semantic_search():
    cache = semcache_rs.SemCache(0)

    # 1. Put vector [1, 0] (Right)
    vec_right = create_vec(1.0, 0.0)
    cache.put("right", vec_right)

    # 2. Query similar [0.99, 0.05] (Almost Right)
    vec_query = create_vec(0.99, 0.05)
    
    # Threshold 0.9 should match
    found = cache.get_similar(vec_query, 0.9)
    assert found is not None
    # Compare with small tolerance (floating point issues)
    assert found == vec_right 

    # 3. Query orthogonal [0, 1] (Up)
    vec_up = create_vec(0.0, 1.0)
    
    # Threshold 0.9 should NOT match
    miss = cache.get_similar(vec_up, 0.9)
    assert miss is None