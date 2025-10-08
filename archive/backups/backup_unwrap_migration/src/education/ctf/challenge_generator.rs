/// AI-Powered Challenge Generator
/// Automatically creates CTF challenges using templates and AI

use alloc::vec::Vec;
use alloc::string::String;
use super::{ChallengeCategory, ChallengeFile, DeploymentInfo, FileType};

/// Generated challenge content
pub struct GeneratedChallenge {
    pub name: String,
    pub description: String,
    pub hints: Vec<String>,
    pub files: Vec<ChallengeFile>,
    pub deployment_info: Option<DeploymentInfo>,
}

pub struct ChallengeGenerator {
    template_count: u32,
}

impl ChallengeGenerator {
    pub fn new() -> Self {
        Self {
            template_count: 0,
        }
    }

    /// Generate challenge based on category and difficulty
    pub fn generate_challenge(
        &mut self,
        category: ChallengeCategory,
        difficulty: crate::education::DifficultyLevel,
    ) -> Result<GeneratedChallenge, &'static str> {
        self.template_count += 1;

        match category {
            ChallengeCategory::WebExploitation => self.generate_web_challenge(difficulty),
            ChallengeCategory::BinaryExploitation => self.generate_binary_challenge(difficulty),
            ChallengeCategory::ReverseEngineering => self.generate_reversing_challenge(difficulty),
            ChallengeCategory::Cryptography => self.generate_crypto_challenge(difficulty),
            ChallengeCategory::Forensics => self.generate_forensics_challenge(difficulty),
            _ => self.generate_generic_challenge(category, difficulty),
        }
    }

    fn generate_web_challenge(&self, difficulty: crate::education::DifficultyLevel) -> Result<GeneratedChallenge, &'static str> {
        let (name, desc) = match difficulty {
            crate::education::DifficultyLevel::Beginner => (
                "Simple SQL Injection",
                "A basic login form vulnerable to SQL injection. Find the admin password!",
            ),
            crate::education::DifficultyLevel::Intermediate => (
                "Session Hijacking",
                "Exploit weak session management to gain admin access.",
            ),
            _ => (
                "Advanced XSS Filter Bypass",
                "Bypass multiple XSS filters to execute JavaScript and steal the admin cookie.",
            ),
        };

        Ok(GeneratedChallenge {
            name: name.into(),
            description: desc.into(),
            hints: vec![
                "Try SQL injection in the login form".into(),
                "Common injection: ' OR '1'='1".into(),
            ],
            files: Vec::new(),
            deployment_info: Some(DeploymentInfo {
                host: "challenge.synos.local".into(),
                port: 8080,
                protocol: "HTTP".into(),
                container_id: None,
            }),
        })
    }

    fn generate_binary_challenge(&self, _difficulty: crate::education::DifficultyLevel) -> Result<GeneratedChallenge, &'static str> {
        Ok(GeneratedChallenge {
            name: "Buffer Overflow 101".into(),
            description: "Exploit a simple buffer overflow to get shell access".into(),
            hints: vec![
                "Find the offset to overwrite the return address".into(),
                "Use pattern_create to find the exact offset".into(),
            ],
            files: vec![
                ChallengeFile {
                    filename: "vuln_binary".into(),
                    file_type: FileType::Binary,
                    download_url: "/files/vuln_binary".into(),
                },
            ],
            deployment_info: Some(DeploymentInfo {
                host: "pwn.synos.local".into(),
                port: 9001,
                protocol: "TCP".into(),
                container_id: None,
            }),
        })
    }

    fn generate_reversing_challenge(&self, _difficulty: crate::education::DifficultyLevel) -> Result<GeneratedChallenge, &'static str> {
        Ok(GeneratedChallenge {
            name: "Reverse Me".into(),
            description: "Analyze this binary to find the hidden flag".into(),
            hints: vec![
                "Use a disassembler like Ghidra or IDA".into(),
                "Look for string comparisons".into(),
            ],
            files: vec![
                ChallengeFile {
                    filename: "crackme".into(),
                    file_type: FileType::Binary,
                    download_url: "/files/crackme".into(),
                },
            ],
            deployment_info: None,
        })
    }

    fn generate_crypto_challenge(&self, _difficulty: crate::education::DifficultyLevel) -> Result<GeneratedChallenge, &'static str> {
        Ok(GeneratedChallenge {
            name: "Weak RSA".into(),
            description: "Decrypt the message encrypted with a weak RSA key".into(),
            hints: vec![
                "The modulus N is small enough to factor".into(),
                "Try factordb.com for known factorizations".into(),
            ],
            files: vec![
                ChallengeFile {
                    filename: "ciphertext.txt".into(),
                    file_type: FileType::Document,
                    download_url: "/files/ciphertext.txt".into(),
                },
                ChallengeFile {
                    filename: "pubkey.pem".into(),
                    file_type: FileType::Document,
                    download_url: "/files/pubkey.pem".into(),
                },
            ],
            deployment_info: None,
        })
    }

    fn generate_forensics_challenge(&self, _difficulty: crate::education::DifficultyLevel) -> Result<GeneratedChallenge, &'static str> {
        Ok(GeneratedChallenge {
            name: "Packet Detective".into(),
            description: "Analyze the network capture to find the stolen data".into(),
            hints: vec![
                "Use Wireshark to analyze the PCAP file".into(),
                "Look for HTTP POST requests".into(),
            ],
            files: vec![
                ChallengeFile {
                    filename: "capture.pcap".into(),
                    file_type: FileType::PCAP,
                    download_url: "/files/capture.pcap".into(),
                },
            ],
            deployment_info: None,
        })
    }

    fn generate_generic_challenge(
        &self,
        category: ChallengeCategory,
        _difficulty: crate::education::DifficultyLevel,
    ) -> Result<GeneratedChallenge, &'static str> {
        Ok(GeneratedChallenge {
            name: format!("{:?} Challenge", category),
            description: format!("A {:?} challenge for you to solve!", category),
            hints: vec!["Think creatively!".into()],
            files: Vec::new(),
            deployment_info: None,
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_web_generation() {
        let mut gen = ChallengeGenerator::new();
        let result = gen.generate_web_challenge(crate::education::DifficultyLevel::Beginner);
        assert!(result.is_ok());
    }
}
