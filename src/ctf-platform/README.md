# SynOS CTF Platform

Capture The Flag training platform with educational challenges and leaderboards.

## Features

-   **Challenge Management**: Pre-loaded cybersecurity challenges
-   **Progressive Difficulty**: Beginner to Expert level challenges
-   **Real-time Leaderboards**: Competitive scoring and ranking
-   **Hint System**: Educational scaffolding with point deductions
-   **Multiple Categories**: Web, Pwn, Crypto, Forensics, Reverse Engineering

## Usage

```bash
# List available challenges
synos-ctf list

# Start a challenge
synos-ctf start ctf_crypto_caesar

# Submit a flag
synos-ctf submit ctf_crypto_caesar "SynOS{HELLO_WORLD}"

# Get a hint
synos-ctf hint ctf_crypto_caesar

# View leaderboard
synos-ctf leaderboard

# Check your status
synos-ctf status
```

## Pre-loaded Challenges

1. **Caesar Cipher Cracking** (Crypto, 50 points, Beginner)
2. **SQL Injection Attack** (Web, 100 points, Intermediate)
3. **Buffer Overflow** (Pwn, 250 points, Advanced)

## Educational Focus

The CTF platform is designed for:

-   Cybersecurity education
-   Skill development
-   Hands-on learning
-   Competitive training
-   Progress tracking

## License

MIT License - See LICENSE file for details.
