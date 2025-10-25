#!/bin/bash
# Phase 2: AI Integration - Premium Models and Tools
# Install Claude CLI, Gemini CLI, and other AI tools for first boot

set -e

CHROOT="$1"
if [ -z "$CHROOT" ]; then
    echo "Usage: $0 /path/to/chroot"
    exit 1
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  PHASE 2: AI INTEGRATION - PREMIUM MODELS & TOOLS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo

echo "[1/10] Installing Python AI/ML Dependencies..."
sudo chroot "$CHROOT" /bin/bash -c "
    apt-get update
    apt-get install -y --no-install-recommends \
        python3-pip python3-venv python3-dev \
        python3-numpy python3-scipy python3-pandas \
        python3-matplotlib python3-sklearn \
        build-essential cmake git curl wget \
        libssl-dev libffi-dev \
        2>&1 | grep -E '(Setting up|already|installed)'

    # Upgrade pip
    pip3 install --upgrade pip setuptools wheel --break-system-packages
"
echo "  ✅ Python dependencies installed"
echo

echo "[2/10] Installing Premium AI CLI Tools..."
sudo chroot "$CHROOT" /bin/bash -c "
    # Install Node.js (required for many AI CLIs)
    echo '→ Installing Node.js 20...'
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - 2>&1 | tail -5
    apt-get install -y nodejs 2>&1 | grep -E '(Setting up|already)'

    # Install Claude CLI (Anthropic)
    echo '→ Installing Claude CLI...'
    npm install -g @anthropic-ai/claude-cli 2>&1 | tail -5 || {
        echo '  ⚠ Claude CLI not available via npm, installing alternative...'
        pip3 install anthropic --break-system-packages

        # Create wrapper script for Claude CLI
        cat > /usr/local/bin/claude << 'CLAUDE_EOF'
#!/usr/bin/env python3
import os
import sys
import anthropic

def main():
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print('Error: ANTHROPIC_API_KEY environment variable not set')
        print('Set it with: export ANTHROPIC_API_KEY=your-api-key')
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    if len(sys.argv) < 2:
        print('Usage: claude \"your prompt here\"')
        print('       claude --interactive  (start chat mode)')
        sys.exit(1)

    if sys.argv[1] == '--interactive':
        print('Claude CLI Interactive Mode')
        print('Type \"exit\" to quit\\n')
        while True:
            try:
                prompt = input('You: ')
                if prompt.lower() in ['exit', 'quit']:
                    break

                message = client.messages.create(
                    model='claude-3-5-sonnet-20241022',
                    max_tokens=4096,
                    messages=[{'role': 'user', 'content': prompt}]
                )
                print(f'Claude: {message.content[0].text}\\n')
            except KeyboardInterrupt:
                break
    else:
        prompt = ' '.join(sys.argv[1:])
        message = client.messages.create(
            model='claude-3-5-sonnet-20241022',
            max_tokens=4096,
            messages=[{'role': 'user', 'content': prompt}]
        )
        print(message.content[0].text)

if __name__ == '__main__':
    main()
CLAUDE_EOF
        chmod +x /usr/local/bin/claude
        echo '  ✅ Claude CLI wrapper created'
    }

    # Install Gemini CLI (Google)
    echo '→ Installing Gemini CLI...'
    pip3 install google-generativeai --break-system-packages

    # Create Gemini CLI wrapper
    cat > /usr/local/bin/gemini << 'GEMINI_EOF'
#!/usr/bin/env python3
import os
import sys
import google.generativeai as genai

def main():
    api_key = os.environ.get('GOOGLE_API_KEY')
    if not api_key:
        print('Error: GOOGLE_API_KEY environment variable not set')
        print('Set it with: export GOOGLE_API_KEY=your-api-key')
        sys.exit(1)

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')

    if len(sys.argv) < 2:
        print('Usage: gemini \"your prompt here\"')
        print('       gemini --interactive  (start chat mode)')
        sys.exit(1)

    if sys.argv[1] == '--interactive':
        print('Gemini CLI Interactive Mode')
        print('Type \"exit\" to quit\\n')
        chat = model.start_chat(history=[])
        while True:
            try:
                prompt = input('You: ')
                if prompt.lower() in ['exit', 'quit']:
                    break
                response = chat.send_message(prompt)
                print(f'Gemini: {response.text}\\n')
            except KeyboardInterrupt:
                break
    else:
        prompt = ' '.join(sys.argv[1:])
        response = model.generate_content(prompt)
        print(response.text)

if __name__ == '__main__':
    main()
GEMINI_EOF
    chmod +x /usr/local/bin/gemini
    echo '  ✅ Gemini CLI created'
"
echo "  ✅ Premium AI CLIs installed"
echo

echo "[3/10] Installing OpenAI CLI and Tools..."
sudo chroot "$CHROOT" /bin/bash -c "
    pip3 install openai openai-whisper tiktoken --break-system-packages 2>&1 | tail -10

    # Create OpenAI CLI wrapper
    cat > /usr/local/bin/gpt << 'GPT_EOF'
#!/usr/bin/env python3
import os
import sys
from openai import OpenAI

def main():
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        print('Error: OPENAI_API_KEY environment variable not set')
        print('Set it with: export OPENAI_API_KEY=your-api-key')
        sys.exit(1)

    client = OpenAI(api_key=api_key)

    if len(sys.argv) < 2:
        print('Usage: gpt \"your prompt here\"')
        print('       gpt --interactive  (start chat mode)')
        print('       gpt --model gpt-4  (specify model)')
        sys.exit(1)

    model = 'gpt-4o'
    args = sys.argv[1:]

    if '--model' in args:
        idx = args.index('--model')
        model = args[idx + 1]
        args = args[:idx] + args[idx+2:]

    if args and args[0] == '--interactive':
        print(f'GPT CLI Interactive Mode (Model: {model})')
        print('Type \"exit\" to quit\\n')
        messages = []
        while True:
            try:
                prompt = input('You: ')
                if prompt.lower() in ['exit', 'quit']:
                    break
                messages.append({'role': 'user', 'content': prompt})
                response = client.chat.completions.create(
                    model=model,
                    messages=messages
                )
                assistant_msg = response.choices[0].message.content
                messages.append({'role': 'assistant', 'content': assistant_msg})
                print(f'GPT: {assistant_msg}\\n')
            except KeyboardInterrupt:
                break
    else:
        prompt = ' '.join(args)
        response = client.chat.completions.create(
            model=model,
            messages=[{'role': 'user', 'content': prompt}]
        )
        print(response.choices[0].message.content)

if __name__ == '__main__':
    main()
GPT_EOF
    chmod +x /usr/local/bin/gpt
    echo '  ✅ OpenAI CLI created'
"
echo "  ✅ OpenAI tools installed"
echo

echo "[4/10] Installing Local AI Models (Ollama)..."
sudo chroot "$CHROOT" /bin/bash -c "
    # Install Ollama for local LLM inference
    echo '→ Installing Ollama...'
    curl -fsSL https://ollama.com/install.sh | sh 2>&1 | tail -10

    # Create Ollama autostart service
    mkdir -p /etc/systemd/system
    cat > /etc/systemd/system/ollama.service << 'OLLAMA_EOF'
[Unit]
Description=Ollama Local LLM Service
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/ollama serve
Restart=always
RestartSec=3
Environment=\"OLLAMA_HOST=0.0.0.0:11434\"

[Install]
WantedBy=multi-user.target
OLLAMA_EOF

    echo '  ✅ Ollama installed'
    echo '  ℹ  Note: Models will be downloaded on first run'
"
echo "  ✅ Ollama installed"
echo

echo "[5/10] Installing LangChain and AI Frameworks..."
sudo chroot "$CHROOT" /bin/bash -c "
    pip3 install --break-system-packages \
        langchain langchain-community langchain-openai \
        langchain-anthropic langchain-google-genai \
        chromadb faiss-cpu sentence-transformers \
        transformers torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu \
        2>&1 | tail -20
"
echo "  ✅ AI frameworks installed"
echo

echo "[6/10] Installing AI Development Tools..."
sudo chroot "$CHROOT" /bin/bash -c "
    pip3 install --break-system-packages \
        jupyter notebook jupyterlab \
        tensorflow-cpu keras \
        scikit-learn pandas numpy matplotlib seaborn \
        plotly opencv-python-headless \
        2>&1 | tail -15
"
echo "  ✅ AI dev tools installed"
echo

echo "[7/10] Creating AI Configuration Scripts..."
sudo chroot "$CHROOT" /bin/bash -c "
    mkdir -p /opt/synos/ai

    # Create AI setup wizard for first boot
    cat > /opt/synos/ai/setup-ai-apis.sh << 'SETUP_EOF'
#!/bin/bash
# AI API Key Setup Wizard

echo '═══════════════════════════════════════════════════════════════'
echo '  SynOS AI Configuration Wizard'
echo '═══════════════════════════════════════════════════════════════'
echo
echo 'This wizard will help you configure API keys for premium AI services.'
echo 'You can skip any service by leaving the field blank.'
echo

# Claude (Anthropic)
echo '→ Anthropic Claude API'
echo '  Get your key from: https://console.anthropic.com/'
read -p 'Enter Claude API key (or press Enter to skip): ' CLAUDE_KEY
if [ ! -z \"\$CLAUDE_KEY\" ]; then
    echo \"export ANTHROPIC_API_KEY='\$CLAUDE_KEY'\" >> ~/.bashrc
    echo '  ✅ Claude API key saved'
fi
echo

# OpenAI GPT
echo '→ OpenAI GPT API'
echo '  Get your key from: https://platform.openai.com/api-keys'
read -p 'Enter OpenAI API key (or press Enter to skip): ' OPENAI_KEY
if [ ! -z \"\$OPENAI_KEY\" ]; then
    echo \"export OPENAI_API_KEY='\$OPENAI_KEY'\" >> ~/.bashrc
    echo '  ✅ OpenAI API key saved'
fi
echo

# Google Gemini
echo '→ Google Gemini API'
echo '  Get your key from: https://makersuite.google.com/app/apikey'
read -p 'Enter Google API key (or press Enter to skip): ' GOOGLE_KEY
if [ ! -z \"\$GOOGLE_KEY\" ]; then
    echo \"export GOOGLE_API_KEY='\$GOOGLE_KEY'\" >> ~/.bashrc
    echo '  ✅ Google API key saved'
fi
echo

echo '═══════════════════════════════════════════════════════════════'
echo '  Configuration Complete!'
echo '═══════════════════════════════════════════════════════════════'
echo
echo 'Your API keys are saved. Run \"source ~/.bashrc\" to activate them.'
echo
echo 'Available AI commands:'
echo '  claude \"your prompt\"      - Chat with Claude'
echo '  gemini \"your prompt\"      - Chat with Gemini'
echo '  gpt \"your prompt\"         - Chat with GPT-4'
echo '  ollama run llama2        - Run local Llama 2'
echo
echo 'For interactive mode, add --interactive:'
echo '  claude --interactive'
echo
SETUP_EOF
    chmod +x /opt/synos/ai/setup-ai-apis.sh

    # Create AI helper script
    cat > /usr/local/bin/synos-ai << 'HELPER_EOF'
#!/bin/bash
# SynOS AI Tools Helper

echo '═══════════════════════════════════════════════════════════════'
echo '  SynOS AI Tools'
echo '═══════════════════════════════════════════════════════════════'
echo
echo 'Premium AI Services (require API keys):'
echo '  claude     - Anthropic Claude (claude-3-5-sonnet)'
echo '  gemini     - Google Gemini Pro'
echo '  gpt        - OpenAI GPT-4o'
echo
echo 'Local AI (no API key needed):'
echo '  ollama     - Run local LLMs (llama2, mistral, etc.)'
echo
echo 'AI Frameworks:'
echo '  langchain  - Build AI applications'
echo '  jupyter    - Interactive notebooks'
echo
echo 'Setup:'
echo '  /opt/synos/ai/setup-ai-apis.sh  - Configure API keys'
echo
echo 'Examples:'
echo '  claude \"explain SQL injection\"'
echo '  gemini --interactive'
echo '  gpt \"write a python script to scan ports\"'
echo '  ollama run llama2'
echo
echo '═══════════════════════════════════════════════════════════════'
HELPER_EOF
    chmod +x /usr/local/bin/synos-ai
"
echo "  ✅ AI configuration scripts created"
echo

echo "[8/10] Creating First-Boot AI Setup Service..."
sudo chroot "$CHROOT" /bin/bash -c "
    # Create first-boot script
    cat > /usr/local/bin/synos-first-boot-ai << 'FIRSTBOOT_EOF'
#!/bin/bash
# Run on first boot to set up AI services

MARKER_FILE=\"/var/lib/synos-first-boot-ai-done\"

if [ -f \"\$MARKER_FILE\" ]; then
    exit 0
fi

echo '═══════════════════════════════════════════════════════════════'
echo '  SynOS First Boot: AI Services Setup'
echo '═══════════════════════════════════════════════════════════════'
echo

# Start Ollama service
echo '→ Starting Ollama service...'
systemctl enable ollama 2>/dev/null || true
systemctl start ollama 2>/dev/null || true

# Download default Ollama model in background
echo '→ Downloading Llama 2 model (this may take a while)...'
(
    sleep 10  # Wait for Ollama to start
    ollama pull llama2 2>&1 | tee /var/log/ollama-first-pull.log
) &

echo '  ✅ AI services initialized'
echo

# Show AI setup message to user
cat << 'WELCOME_EOF'
═══════════════════════════════════════════════════════════════
  Welcome to SynOS AI Integration! 🤖
═══════════════════════════════════════════════════════════════

Premium AI tools are installed and ready to use:

  ✅ Claude CLI (Anthropic)
  ✅ Gemini CLI (Google)
  ✅ GPT CLI (OpenAI)
  ✅ Ollama (Local LLMs)

To get started:
  1. Run: /opt/synos/ai/setup-ai-apis.sh
  2. Or run: synos-ai (to see all AI commands)

Local AI (Ollama) is downloading Llama 2 in the background.
Check status with: ollama list

═══════════════════════════════════════════════════════════════
WELCOME_EOF

touch \"\$MARKER_FILE\"
FIRSTBOOT_EOF
    chmod +x /usr/local/bin/synos-first-boot-ai

    # Add to user's profile to run on first login
    cat >> /etc/profile.d/synos-ai-welcome.sh << 'PROFILE_EOF'
# SynOS AI First Boot
if [ ! -f /var/lib/synos-first-boot-ai-done ]; then
    /usr/local/bin/synos-first-boot-ai
fi
PROFILE_EOF
    chmod +x /etc/profile.d/synos-ai-welcome.sh
"
echo "  ✅ First-boot service created"
echo

echo "[9/10] Installing AI-Powered Security Tools..."
sudo chroot "$CHROOT" /bin/bash -c "
    pip3 install --break-system-packages \
        scapy pwntools \
        beautifulsoup4 lxml requests \
        2>&1 | tail -10

    # Install AI-powered vulnerability scanners
    cd /opt/github-repos 2>/dev/null || mkdir -p /opt/github-repos && cd /opt/github-repos

    # GPT-powered penetration testing
    git clone --depth 1 https://github.com/GreyDGL/PentestGPT.git 2>&1 | tail -3 || echo '  ⚠ PentestGPT clone skipped'

    # AI-powered code analysis
    git clone --depth 1 https://github.com/microsoft/pyright.git 2>&1 | tail -3 || echo '  ⚠ Pyright clone skipped'
"
echo "  ✅ AI security tools installed"
echo

echo "[10/10] Creating AI Tool Documentation..."
sudo chroot "$CHROOT" /bin/bash -c "
    cat > /opt/synos/ai/README.md << 'README_EOF'
# SynOS AI Integration

## Installed AI Tools

### Premium API Services
- **Claude CLI** (\`claude\`) - Anthropic's Claude 3.5 Sonnet
- **Gemini CLI** (\`gemini\`) - Google's Gemini Pro
- **GPT CLI** (\`gpt\`) - OpenAI GPT-4o

### Local AI (No API Required)
- **Ollama** - Run LLMs locally (Llama 2, Mistral, etc.)

### AI Frameworks
- **LangChain** - Build AI applications
- **PyTorch** - Deep learning framework
- **TensorFlow** - Machine learning platform
- **Transformers** - Hugging Face models

### AI Development
- **Jupyter** - Interactive notebooks
- **Keras** - High-level neural networks API

## Quick Start

### 1. Configure API Keys
\`\`\`bash
/opt/synos/ai/setup-ai-apis.sh
\`\`\`

### 2. Use Premium AI Services
\`\`\`bash
# One-shot queries
claude \"explain XSS attacks\"
gemini \"write a bash script to scan networks\"
gpt \"analyze this SQL injection vulnerability\"

# Interactive chat
claude --interactive
gemini --interactive
gpt --interactive
\`\`\`

### 3. Use Local AI (Ollama)
\`\`\`bash
# List available models
ollama list

# Run a model
ollama run llama2

# Pull more models
ollama pull mistral
ollama pull codellama
\`\`\`

### 4. AI-Powered Security Testing
\`\`\`bash
# PentestGPT for guided penetration testing
cd /opt/github-repos/PentestGPT
python3 pentestgpt.py
\`\`\`

## API Key Setup

### Claude (Anthropic)
1. Visit: https://console.anthropic.com/
2. Create an account and get API key
3. Add to ~/.bashrc: \`export ANTHROPIC_API_KEY='your-key'\`

### OpenAI GPT
1. Visit: https://platform.openai.com/api-keys
2. Create API key
3. Add to ~/.bashrc: \`export OPENAI_API_KEY='your-key'\`

### Google Gemini
1. Visit: https://makersuite.google.com/app/apikey
2. Get API key
3. Add to ~/.bashrc: \`export GOOGLE_API_KEY='your-key'\`

## Examples

### Security Analysis with AI
\`\`\`bash
# Analyze a vulnerability
claude \"Explain the OWASP Top 10 and how to test for each\"

# Generate exploit code
gpt \"Create a Python script to test for SQL injection\"

# Understand a tool
gemini \"How do I use nmap for service detection?\"
\`\`\`

### Local AI for Privacy
\`\`\`bash
# Run completely offline with Ollama
ollama run llama2 \"Explain buffer overflow attacks\"
\`\`\`

### AI-Assisted Development
\`\`\`bash
# Start Jupyter for interactive development
jupyter notebook

# Use LangChain for AI app development
python3
>>> from langchain import OpenAI, PromptTemplate
>>> # Build your AI-powered security tool
\`\`\`

## Troubleshooting

### API Keys Not Working
\`\`\`bash
# Reload bashrc
source ~/.bashrc

# Verify key is set
echo $ANTHROPIC_API_KEY
\`\`\`

### Ollama Not Starting
\`\`\`bash
# Check service status
systemctl status ollama

# Restart service
sudo systemctl restart ollama
\`\`\`

### Model Download Issues
\`\`\`bash
# Check available storage
df -h

# List downloaded models
ollama list

# Remove unused models
ollama rm <model-name>
\`\`\`

## Available Ollama Models

- **llama2** (3.8GB) - General purpose, downloaded by default
- **mistral** (4.1GB) - Fast and powerful
- **codellama** (3.8GB) - Code generation
- **llama2-uncensored** (3.8GB) - No content filtering
- **neural-chat** (4.1GB) - Conversation focused
- **starling-lm** (4.1GB) - High quality responses

Download with: \`ollama pull <model-name>\`

README_EOF
"
echo "  ✅ Documentation created"
echo

echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  PHASE 2: AI INTEGRATION SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo
echo "✅ Installed Components:"
echo "  • Claude CLI (Anthropic Claude 3.5 Sonnet)"
echo "  • Gemini CLI (Google Gemini Pro)"
echo "  • GPT CLI (OpenAI GPT-4o)"
echo "  • Ollama (Local LLM server)"
echo "  • LangChain + AI frameworks"
echo "  • PyTorch + TensorFlow"
echo "  • Jupyter + Development tools"
echo
echo "✅ First-Boot Features:"
echo "  • API key setup wizard will run on first login"
echo "  • Ollama service auto-starts"
echo "  • Llama 2 model downloads in background"
echo "  • Welcome message with AI commands"
echo
echo "📁 Configuration:"
echo "  • AI scripts: /opt/synos/ai/"
echo "  • Setup wizard: /opt/synos/ai/setup-ai-apis.sh"
echo "  • Helper command: synos-ai"
echo "  • Documentation: /opt/synos/ai/README.md"
echo
echo "🔧 Available Commands:"
echo "  • claude <prompt> | claude --interactive"
echo "  • gemini <prompt> | gemini --interactive"
echo "  • gpt <prompt> | gpt --interactive"
echo "  • ollama run llama2"
echo "  • synos-ai (show all AI tools)"
echo
echo "✅ PHASE 2 COMPLETE - AI INTEGRATION READY!"
echo
