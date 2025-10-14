# 🟢 Syn_OS First Run & AI Tools Verification Checklist

This checklist ensures your Codespace is fully operational, with all AI tools (Claude, Kilo, GitHub Copilot) working as intended. Copy-paste commands are provided for each step.

---

## 1. Validate Environment
```bash
source ~/.bashrc
validate-env
```
- Confirms Rust, Python, Go, Node, and custom commands are available.

## 2. Check VS Code Extensions
- Open the Extensions sidebar (`Ctrl+Shift+X`).
- Confirm these are installed and enabled:
  - GitHub Copilot
  - GitHub Copilot Chat
  - Kilo (Claude)
  - Continue (if used)

## 3. Set Up API Keys/Secrets
- In Codespaces, open the command palette (`Ctrl+Shift+P`), search for `Codespaces: Set Secret`, and add:
  - `GITHUB_TOKEN` (for Copilot)
  - `KILO_API_KEY` (for Kilo/Claude, if required)
- Reload the Codespace after setting secrets.

## 4. Test Copilot
```bash
# In any .py, .rs, or .md file, type a comment and press Tab to accept Copilot suggestion.
```
- You should see Copilot suggestions inline.

## 5. Test Kilo/Claude
- Open the Kilo/Claude sidebar or chat panel.
- Enter a prompt (e.g., "Summarize this file").
- Confirm you get a response.

## 6. Test Continue (if used)
- Open the Continue sidebar.
- Run a test prompt.

## 7. Troubleshooting
```bash
bash .devcontainer/codespace-setup.sh
source ~/.bashrc
validate-env
```
- If extensions are missing, run `code --install-extension <extension-id>`
- If Copilot/Kilo/Claude do not respond, check secrets and reload VS Code.

---

**If all steps succeed, your Codespace is fully ready for Syn_OS development!**
