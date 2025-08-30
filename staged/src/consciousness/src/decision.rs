// Decision Making Engine Module

extern crate alloc;

use alloc::string::String;
use alloc::vec::Vec;
use alloc::collections::BTreeMap;

/// Decision criteria
#[derive(Debug, Clone)]
pub struct DecisionCriteria {
    pub priority: u8,
    pub confidence_required: f32,
    pub time_limit_ms: u64,
    pub context: BTreeMap<String, String>,
}

/// Decision option
#[derive(Debug, Clone)]
pub struct DecisionOption {
    pub id: String,
    pub description: String,
    pub confidence: f32,
    pub risk_level: u8,
    pub impact_score: f32,
}

/// Decision result
#[derive(Debug, Clone)]
pub struct DecisionResult {
    pub selected_option: String,
    pub confidence: f32,
    pub reasoning: String,
    pub alternatives: Vec<String>,
}

/// Decision making engine
pub struct DecisionEngine {
    decision_history: Vec<DecisionResult>,
    policies: BTreeMap<String, DecisionPolicy>,
}

/// Decision policy
#[derive(Debug, Clone)]
pub struct DecisionPolicy {
    pub name: String,
    pub min_confidence: f32,
    pub max_risk: u8,
    pub weight_factors: BTreeMap<String, f32>,
}

impl DecisionEngine {
    /// Create new decision engine
    pub fn new() -> Self {
        Self {
            decision_history: Vec::new(),
            policies: BTreeMap::new(),
        }
    }
    
    /// Add decision policy
    pub fn add_policy(&mut self, policy: DecisionPolicy) {
        self.policies.insert(policy.name.clone(), policy);
    }
    
    /// Make a decision
    pub fn make_decision(
        &mut self,
        criteria: &DecisionCriteria,
        options: &[DecisionOption],
        policy_name: &str,
    ) -> Result<DecisionResult, &'static str> {
        if options.is_empty() {
            return Err("No options provided");
        }
        
        let _policy = self.policies.get(policy_name)
            .ok_or("Policy not found")?;
        
        // Simple decision logic - select highest confidence option above threshold
        let mut best_option = None;
        let mut best_confidence = 0.0;
        
        for option in options {
            if option.confidence >= criteria.confidence_required && 
               option.confidence > best_confidence {
                best_option = Some(option);
                best_confidence = option.confidence;
            }
        }
        
        if let Some(selected) = best_option {
            let mut alternatives = Vec::new();
            for option in options {
                if option.id != selected.id {
                    alternatives.push(option.id.clone());
                }
            }
            
            let result = DecisionResult {
                selected_option: selected.id.clone(),
                confidence: selected.confidence,
                reasoning: "Selected highest confidence option above threshold".into(),
                alternatives,
            };
            
            self.decision_history.push(result.clone());
            Ok(result)
        } else {
            Err("No options meet criteria")
        }
    }
    
    /// Get decision history
    pub fn get_history(&self) -> &[DecisionResult] {
        &self.decision_history
    }
    
    /// Clear decision history
    pub fn clear_history(&mut self) {
        self.decision_history.clear();
    }
}

/// Global decision engine
static mut GLOBAL_DECISION_ENGINE: Option<DecisionEngine> = None;

/// Initialize decision module
pub fn init() {
    unsafe {
        let mut engine = DecisionEngine::new();
        
        // Add default policy
        let mut weight_factors = BTreeMap::new();
        weight_factors.insert("confidence".into(), 0.6);
        weight_factors.insert("risk".into(), 0.3);
        weight_factors.insert("impact".into(), 0.1);
        
        let default_policy = DecisionPolicy {
            name: "default".into(),
            min_confidence: 0.7,
            max_risk: 5,
            weight_factors,
        };
        
        engine.add_policy(default_policy);
        GLOBAL_DECISION_ENGINE = Some(engine);
    }
}

/// Make global decision
pub fn make_global_decision(
    criteria: &DecisionCriteria,
    options: &[DecisionOption],
) -> Result<DecisionResult, &'static str> {
    unsafe {
        let engine_ptr = &raw mut GLOBAL_DECISION_ENGINE;
        if let Some(engine) = &mut *engine_ptr {
            engine.make_decision(criteria, options, "default")
        } else {
            Err("Decision engine not initialized")
        }
    }
}
