# Admin policy - Full access to all secrets and management

# Full access to all secrets
path "secret/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

# Manage auth methods
path "auth/*" {
  capabilities = ["create", "read", "update", "delete", "list", "sudo"]
}

# Manage policies
path "sys/policies/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

# List policies
path "sys/policies" {
  capabilities = ["list"]
}

# Manage mounts
path "sys/mounts/*" {
  capabilities = ["create", "read", "update", "delete", "list", "sudo"]
}

# List mounts
path "sys/mounts" {
  capabilities = ["read", "list"]
}

# Audit management
path "sys/audit/*" {
  capabilities = ["create", "read", "update", "delete", "list", "sudo"]
}

# Health checks
path "sys/health" {
  capabilities = ["read", "sudo"]
}

# Seal management
path "sys/seal" {
  capabilities = ["sudo"]
}

# Token management
path "auth/token/*" {
  capabilities = ["create", "read", "update", "delete", "list", "sudo"]
}