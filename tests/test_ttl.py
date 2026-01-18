import semcache_rs
import time
import pytest

def gen(text):
    return [1.0, 2.0]

def test_ttl_expiration():
    # TTL = 1 second
    cache = semcache_rs.SemCache(ttl=1)

    # Put data
    cache.get_or_compute("hello", gen)
    
    # Check immediately
    assert cache.get("hello") == [1.0, 2.0]

    # Sleep longer than TTL
    time.sleep(2.0)

    # Check expiration
    assert cache.get("hello") is None