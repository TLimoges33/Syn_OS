local BasePlugin = require "kong.plugins.base_plugin"
local http = require "resty.http"
local cjson = require "cjson"

local VaultAuthHandler = BasePlugin:extend()

VaultAuthHandler.VERSION = "1.0.0"
VaultAuthHandler.PRIORITY = 1500

function VaultAuthHandler:new()
    VaultAuthHandler.super.new(self, "vault-auth")
end

function VaultAuthHandler:access(conf)
    VaultAuthHandler.super.access(self)
    
    -- Get the API key from request header
    local api_key = kong.request.get_header(conf.key_header or "X-API-Key")
    
    if not api_key then
        return kong.response.exit(401, { message = "No API key provided" })
    end
    
    -- Validate against Vault
    local vault_client = http.new()
    vault_client:set_timeout(conf.timeout or 5000)
    
    local vault_url = conf.vault_addr .. "/v1/" .. conf.secret_path
    
    local res, err = vault_client:request_uri(vault_url, {
        method = "GET",
        headers = {
            ["X-Vault-Token"] = conf.vault_token,
            ["Content-Type"] = "application/json"
        }
    })
    
    if not res then
        kong.log.err("Failed to connect to Vault: ", err)
        return kong.response.exit(500, { message = "Authentication service unavailable" })
    end
    
    if res.status ~= 200 then
        kong.log.err("Vault returned status: ", res.status)
        return kong.response.exit(500, { message = "Authentication service error" })
    end
    
    local vault_data = cjson.decode(res.body)
    local valid_keys = vault_data.data.data.api_keys or {}
    
    -- Check if the provided key is valid
    local is_valid = false
    local consumer_id = nil
    
    for _, key_data in pairs(valid_keys) do
        if key_data.key == api_key then
            is_valid = true
            consumer_id = key_data.consumer_id
            break
        end
    end
    
    if not is_valid then
        return kong.response.exit(401, { message = "Invalid API key" })
    end
    
    -- Set consumer information for downstream services
    kong.service.request.set_header("X-Consumer-ID", consumer_id)
    kong.service.request.set_header("X-Authenticated-Via", "vault")
    
    -- Log successful authentication
    kong.log.info("Successfully authenticated consumer: ", consumer_id)
end

return VaultAuthHandler