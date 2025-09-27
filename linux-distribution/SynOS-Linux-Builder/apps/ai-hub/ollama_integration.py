#!/usr/bin/env python3

"""
SynOS Ollama Integration - Local AI Model Support
Adds local AI capabilities to AI Hub
"""

import requests
import subprocess
import json
import time
from typing import List, Dict, Optional

class OllamaManager:
    def __init__(self):
        self.base_url = "http://localhost:11434"
        self.available_models = []

    def is_ollama_running(self) -> bool:
        """Check if Ollama service is running"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False

    def install_ollama(self):
        """Install Ollama if not present"""
        print("Installing Ollama...")
        subprocess.run([
            "curl", "-fsSL", "https://ollama.ai/install.sh"
        ], shell=True)

    def pull_security_models(self):
        """Download security-focused AI models"""
        security_models = [
            "codellama:7b",     # Code analysis
            "mistral:7b",       # General security analysis
            "llama2:7b"         # Log analysis
        ]

        for model in security_models:
            print(f"Pulling {model}...")
            subprocess.run(["ollama", "pull", model])

    def analyze_security_log(self, log_content: str) -> str:
        """Analyze security logs with local AI"""
        prompt = f"""
        Analyze this security log for threats:

        {log_content}

        Identify:
        1. Potential threats
        2. Anomalies
        3. Recommended actions
        """

        try:
            response = requests.post(f"{self.base_url}/api/generate", json={
                "model": "mistral:7b",
                "prompt": prompt,
                "stream": False
            })
            return response.json().get('response', 'Analysis failed')
        except:
            return "Local AI unavailable"

if __name__ == "__main__":
    manager = OllamaManager()
    if manager.is_ollama_running():
        print("✅ Ollama is running")
    else:
        print("❌ Ollama not running - installing...")
        manager.install_ollama()
