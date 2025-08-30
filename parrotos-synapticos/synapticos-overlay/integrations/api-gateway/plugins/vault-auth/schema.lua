local typedefs = require "kong.db.schema.typedefs"

return {
    name = "vault-auth",
    fields = {
        {
            consumer = typedefs.no_consumer
        },
        {
            protocols = typedefs.protocols_http
        },
        {
            config = {
                type = "record",
                fields = {
                    {
                        vault_addr = {
                            type = "string",
                            required = true,
                            default = "http://vault:8200",
                            description = "The address of the Vault server"
                        }
                    },
                    {
                        vault_token = {
                            type = "string",
                            required = true,
                            encrypted = true,
                            description = "The Vault token for authentication"
                        }
                    },
                    {
                        secret_path = {
                            type = "string",
                            required = true,
                            default = "secret/data/api-keys",
                            description = "The path in Vault where API keys are stored"
                        }
                    },
                    {
                        key_header = {
                            type = "string",
                            default = "X-API-Key",
                            description = "The header name for the API key"
                        }
                    },
                    {
                        timeout = {
                            type = "number",
                            default = 5000,
                            description = "Timeout for Vault requests in milliseconds"
                        }
                    },
                    {
                        cache_ttl = {
                            type = "number",
                            default = 60,
                            description = "TTL for caching valid keys in seconds"
                        }
                    }
                }
            }
        }
    }
}