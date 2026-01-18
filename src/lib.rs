use chrono::{DateTime, Utc};
use dashmap::DashMap;
use pyo3::prelude::*;
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use simsimd::SpatialSimilarity;
use std::f64;
use std::fs::File;
use std::io::{BufReader, BufWriter};
use std::sync::Arc;

// Struct of vector and timestamp
#[derive(Serialize, Deserialize, Clone)]
struct CacheEntry {
    vector: Vec<f64>,
    created_at: DateTime<Utc>,
}

// Struct of SemCache
#[pyclass]
struct SemCache {
    store: Arc<DashMap<String, CacheEntry>>,
    ttl_seconds: u64,
}

#[pymethods]
impl SemCache {
    // Initialize SemCache
    #[new]
    #[pyo3(signature = (ttl = 0))]
    fn new(ttl: Option<u64>) -> Self {
        SemCache {
            store: Arc::new(DashMap::new()),
            ttl_seconds: ttl.unwrap_or(0),
        }
    }

    // Calculate SHA256 hash of input string
    fn _hash(&self, text: &str) -> String {
        let mut hasher = Sha256::new();
        hasher.update(text.as_bytes());
        hex::encode(hasher.finalize())
    }

    // Save (vector, timestamp) to cache
    fn put(&self, text: &str, vector: Vec<f64>) {
        let hash = self._hash(text);
        let entry = CacheEntry {
            vector,
            created_at: Utc::now(),
        };
        self.store.insert(hash, entry);
    }

    // Get vector from cache
    fn get(&self, text: &str) -> Option<Vec<f64>> {
        let hash = self._hash(text);

        if let Some(entry) = self.store.get(&hash) {
            if self.ttl_seconds > 0 {
                let age = Utc::now() - entry.value().created_at;
                if age.num_seconds() as u64 > self.ttl_seconds {
                    return None;
                }
            }
            return Some(entry.value().vector.clone());
        }
        None
    }

    // Get size of cache
    fn size(&self) -> usize {
        self.store.len()
    }

    // Clean cache
    fn clean(&self) {
        self.store.clear();
    }

    /// Method: if cache is empty, call python-function (callback) generator
    fn get_or_compute(
        &self,
        py: Python<'_>,
        text: &str,
        generator: Py<PyAny>,
    ) -> PyResult<Vec<f64>> {
        let hash = self._hash(text);

        // Check with ttl
        if let Some(entry) = self.store.get(&hash) {
            let is_valid = if self.ttl_seconds > 0 {
                let age = Utc::now() - entry.value().created_at;
                (age.num_seconds() as u64) < self.ttl_seconds
            } else {
                true
            };

            if is_valid {
                return Ok(entry.value().vector.clone());
            }
        }

        // Call generator
        let result_obj = generator.call1(py, (&text,))?;
        let vector: Vec<f64> = result_obj.extract(py)?;

        // Entry to cache
        let entry = CacheEntry {
            vector: vector.clone(),
            created_at: Utc::now(),
        };
        self.store.insert(hash, entry);

        Ok(vector)
    }

    // Dump cache to file (bincode)
    fn dump(&self, path: String) -> PyResult<()> {
        let file = File::create(path).map_err(|e| {
            pyo3::exceptions::PyIOError::new_err(format!("Failed to create file: {}", e))
        })?;

        let writer = BufWriter::new(file);
        let snapshot: std::collections::HashMap<_, _> = self
            .store
            .iter()
            .map(|r| (r.key().clone(), r.value().clone()))
            .collect();

        bincode::serialize_into(writer, &snapshot).map_err(|e| {
            pyo3::exceptions::PyIOError::new_err(format!("Bincode write error: {}", e))
        })?;

        Ok(())
    }

    // Load cache from file (Bincode)
    fn load(&self, path: String) -> PyResult<usize> {
        let file = File::open(path).map_err(|e| {
            pyo3::exceptions::PyIOError::new_err(format!("Failed to open file: {}", e))
        })?;

        let reader = BufReader::new(file);
        let snapshot: std::collections::HashMap<String, CacheEntry> =
            bincode::deserialize_from(reader).map_err(|e| {
                pyo3::exceptions::PyIOError::new_err(format!("JSON read error: {}", e))
            })?;

        let count = snapshot.len();

        // Load to DashMap
        self.store.clear();
        for (k, v) in snapshot {
            self.store.insert(k, v);
        }

        Ok(count)
    }

    // Semantic search
    fn get_similar(&self, query_vec: Vec<f64>, threshold: f64) -> Option<Vec<f64>> {
        let mut best_sim = -1.0;
        let mut best_vec = None;

        for r in self.store.iter() {
            let entry = r.value();

            if self.ttl_seconds > 0 {
                let age = Utc::now() - entry.created_at;
                if age.num_seconds() as u64 > self.ttl_seconds {
                    continue;
                }
            }

            let distance = f64::cosine(&query_vec, &entry.vector).unwrap_or(2.0);
            let sim = 1.0 - distance;

            if sim > best_sim {
                best_sim = sim;
                best_vec = Some(entry.vector.clone());
            }
        }

        if best_sim > threshold {
            return best_vec;
        }

        None
    }
}

#[pymodule]
fn semcache_rs(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<SemCache>()?;
    Ok(())
}
