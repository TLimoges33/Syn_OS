# Service policy - Read-only access to specific service secrets

# n8n service secrets
path "secret/data/n8n/*" {
  capabilities = ["read"]
}

# Context Engine secrets
path "secret/data/context-engine/*" {
  capabilities = ["read"]
}

# JaceAI secrets
path "secret/data/jaceai/*" {
  capabilities = ["read"]
}

# Speechify secrets
path "secret/data/speechify/*" {
  capabilities = ["read"]
}

# Vercel secrets
path "secret/data/vercel/*" {
  capabilities = ["read"]
}

# API keys for services
path "secret/data/api-keys/*" {
  capabilities = ["read"]
}

# Database credentials (read-only)
path "secret/data/database/*" {
  capabilities = ["read"]
}

# Service discovery information
path "secret/data/service-discovery/*" {
  capabilities = ["read", "list"]
}

# Health check endpoint
path "sys/health" {
  capabilities = ["read"]
}

# Token renewal
path "auth/token/renew-self" {
  capabilities = ["update"]
}

# Token lookup
path "auth/token/lookup-self" {
  capabilities = ["read"]
}