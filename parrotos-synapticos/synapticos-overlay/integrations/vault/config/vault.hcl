# Vault Configuration for SynapticsOS

ui = true
disable_mlock = true

storage "file" {
  path = "/vault/data"
}

listener "tcp" {
  address     = "0.0.0.0:8200"
  tls_disable = "true"  # Enable TLS in production
}

api_addr = "http://0.0.0.0:8200"
cluster_addr = "https://0.0.0.0:8201"

# Enable audit logging
audit {
  enabled = true
  path = "/vault/logs/audit.log"
}

# Default lease duration
default_lease_ttl = "768h"
max_lease_ttl = "8760h"

# Enable telemetry
telemetry {
  prometheus_retention_time = "30s"
  disable_hostname = true
}

# Plugin directory
plugin_directory = "/vault/plugins"