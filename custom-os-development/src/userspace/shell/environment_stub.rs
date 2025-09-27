//! # Stub implementation of environment

use alloc::{string::String, collections::BTreeMap};

#[derive(Debug)]
pub struct Environment {
    variables: BTreeMap<String, String>,
}

impl Environment {
    pub fn new() -> Self {
        Self {
            variables: BTreeMap::new(),
        }
    }

    pub fn set(&mut self, key: String, value: String) {
        self.variables.insert(key, value);
    }

    pub fn get(&self, key: &str) -> Option<&String> {
        self.variables.get(key)
    }

    pub fn remove(&mut self, key: &str) -> Option<String> {
        self.variables.remove(key)
    }
}
