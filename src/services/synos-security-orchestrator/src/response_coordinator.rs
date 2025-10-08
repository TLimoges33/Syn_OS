use anyhow::Result;
use std::collections::VecDeque;
use tracing::{debug, info};

pub struct ResponseCoordinator {
    auto_response: bool,
    responses: VecDeque<Response>,
    response_count: u64,
}

#[derive(Debug, Clone)]
struct Response {
    id: uuid::Uuid,
    action: String,
    timestamp: std::time::Instant,
    success: bool,
}

impl ResponseCoordinator {
    pub fn new(auto_response: bool) -> Result<Self> {
        Ok(Self {
            auto_response,
            responses: VecDeque::with_capacity(1000),
            response_count: 0,
        })
    }

    pub async fn coordinate_responses(&mut self) -> Result<()> {
        // Simulate response coordination
        if self.response_count % 1000 == 0 && self.response_count > 0 {
            debug!("Coordinated {} responses", self.response_count);
        }

        // Clean old responses
        while self.responses.len() > 1000 {
            self.responses.pop_front();
        }

        Ok(())
    }

    pub fn execute_response(&mut self, action: String) -> Result<uuid::Uuid> {
        if !self.auto_response {
            info!("Auto-response disabled, manual approval required for: {}", action);
        }

        let response = Response {
            id: uuid::Uuid::new_v4(),
            action: action.clone(),
            timestamp: std::time::Instant::now(),
            success: true,
        };

        let id = response.id;
        self.responses.push_back(response);
        self.response_count += 1;

        info!("Executed security response: {}", action);
        Ok(id)
    }

    pub fn get_response_count(&self) -> u64 {
        self.response_count
    }

    pub fn get_recent_responses(&self, limit: usize) -> Vec<String> {
        self.responses
            .iter()
            .rev()
            .take(limit)
            .map(|r| r.action.clone())
            .collect()
    }
}
