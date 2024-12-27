use std::collections::HashMap;
use std::time::{Duration, SystemTime};

#[derive(Debug, Clone)]
pub struct CachedPage {
    pub content: String,
    pub timestamp: SystemTime,
}

#[derive(Debug, Default)]
pub struct PageCache {
    cache: HashMap<String, CachedPage>,
    max_age: Duration,
}

impl PageCache {
    pub fn new(max_age_secs: u64) -> Self {
        Self {
            cache: HashMap::new(),
            max_age: Duration::from_secs(max_age_secs),
        }
    }

    pub fn get(&self, url: &str) -> Option<String> {
        if let Some(cached) = self.cache.get(url) {
            if cached.timestamp.elapsed().unwrap_or(self.max_age) < self.max_age {
                return Some(cached.content.clone());
            }
        }
        None
    }

    pub fn set(&mut self, url: String, content: String) {
        self.cache.insert(
            url,
            CachedPage {
                content,
                timestamp: SystemTime::now(),
            },
        );
    }

    pub fn clear(&mut self) {
        self.cache.clear();
    }

    pub fn remove(&mut self, url: &str) {
        self.cache.remove(url);
    }
} 