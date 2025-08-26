package config

import (
	"fmt"
	"os"
	"strconv"
	"time"
)

// Config holds all configuration for the orchestrator
type Config struct {
	Server   ServerConfig   `yaml:"server"`
	Database DatabaseConfig `yaml:"database"`
	Redis    RedisConfig    `yaml:"redis"`
	NATS     NATSConfig     `yaml:"nats"`
	Vault    VaultConfig    `yaml:"vault"`
	Security SecurityConfig `yaml:"security"`
	Logging  LoggingConfig  `yaml:"logging"`
}

// ServerConfig holds HTTP server configuration
type ServerConfig struct {
	Port         int    `yaml:"port"`
	Mode         string `yaml:"mode"`
	ReadTimeout  int    `yaml:"read_timeout"`
	WriteTimeout int    `yaml:"write_timeout"`
}

// DatabaseConfig holds PostgreSQL configuration
type DatabaseConfig struct {
	URL             string `yaml:"url"`
	MaxOpenConns    int    `yaml:"max_open_conns"`
	MaxIdleConns    int    `yaml:"max_idle_conns"`
	ConnMaxLifetime int    `yaml:"conn_max_lifetime"`
}

// RedisConfig holds Redis configuration
type RedisConfig struct {
	URL      string `yaml:"url"`
	Password string `yaml:"password"`
	DB       int    `yaml:"db"`
}

// NATSConfig holds NATS configuration
type NATSConfig struct {
	URL         string `yaml:"url"`
	ClusterID   string `yaml:"cluster_id"`
	ClientID    string `yaml:"client_id"`
	Username    string `yaml:"username"`
	Password    string `yaml:"password"`
	MaxReconnect int   `yaml:"max_reconnect"`
}

// VaultConfig holds Vault configuration
type VaultConfig struct {
	URL   string `yaml:"url"`
	Token string `yaml:"token"`
}

// SecurityConfig holds security configuration
type SecurityConfig struct {
	JWTSecret     string        `yaml:"jwt_secret"`
	TokenExpiry   time.Duration `yaml:"token_expiry"`
	EnableAuth    bool          `yaml:"enable_auth"`
	EnableTLS     bool          `yaml:"enable_tls"`
	CertFile      string        `yaml:"cert_file"`
	KeyFile       string        `yaml:"key_file"`
}

// LoggingConfig holds logging configuration
type LoggingConfig struct {
	Level  string `yaml:"level"`
	Format string `yaml:"format"`
	Output string `yaml:"output"`
}

// Load loads configuration from environment variables with defaults
func Load() (*Config, error) {
	config := &Config{
		Server: ServerConfig{
			Port:         getEnvAsInt("SYNOS_PORT", 8080),
			Mode:         getEnv("SYNOS_MODE", "development"),
			ReadTimeout:  getEnvAsInt("SYNOS_READ_TIMEOUT", 30),
			WriteTimeout: getEnvAsInt("SYNOS_WRITE_TIMEOUT", 30),
		},
		Database: DatabaseConfig{
			URL:             getEnv("SYNOS_DATABASE_URL", "postgres://postgres:password@localhost:5432/synos?sslmode=disable"),
			MaxOpenConns:    getEnvAsInt("SYNOS_DB_MAX_OPEN_CONNS", 25),
			MaxIdleConns:    getEnvAsInt("SYNOS_DB_MAX_IDLE_CONNS", 5),
			ConnMaxLifetime: getEnvAsInt("SYNOS_DB_CONN_MAX_LIFETIME", 300),
		},
		Redis: RedisConfig{
			URL:      getEnv("SYNOS_REDIS_URL", "redis://localhost:6379"),
			Password: getEnv("SYNOS_REDIS_PASSWORD", ""),
			DB:       getEnvAsInt("SYNOS_REDIS_DB", 0),
		},
		NATS: NATSConfig{
			URL:          getEnv("SYNOS_NATS_URL", "nats://localhost:4222"),
			ClusterID:    getEnv("SYNOS_NATS_CLUSTER_ID", "synos-cluster"),
			ClientID:     getEnv("SYNOS_NATS_CLIENT_ID", "orchestrator"),
			Username:     getEnv("SYNOS_NATS_USERNAME", "orchestrator"),
			Password:     getEnv("SYNOS_NATS_PASSWORD", ""),
			MaxReconnect: getEnvAsInt("SYNOS_NATS_MAX_RECONNECT", 10),
		},
		Vault: VaultConfig{
			URL:   getEnv("SYNOS_VAULT_URL", "http://localhost:8200"),
			Token: getEnv("SYNOS_VAULT_TOKEN", "dev-token"),
		},
		Security: SecurityConfig{
			JWTSecret:   getEnv("SYNOS_JWT_SECRET", "synos-secret-key"),
			TokenExpiry: time.Duration(getEnvAsInt("SYNOS_TOKEN_EXPIRY", 3600)) * time.Second,
			EnableAuth:  getEnvAsBool("SYNOS_ENABLE_AUTH", true),
			EnableTLS:   getEnvAsBool("SYNOS_ENABLE_TLS", false),
			CertFile:    getEnv("SYNOS_CERT_FILE", ""),
			KeyFile:     getEnv("SYNOS_KEY_FILE", ""),
		},
		Logging: LoggingConfig{
			Level:  getEnv("SYNOS_LOG_LEVEL", "info"),
			Format: getEnv("SYNOS_LOG_FORMAT", "json"),
			Output: getEnv("SYNOS_LOG_OUTPUT", "stdout"),
		},
	}

	return config, nil
}

// Validate validates the configuration
func (c *Config) Validate() error {
	if c.Server.Port <= 0 || c.Server.Port > 65535 {
		return fmt.Errorf("invalid server port: %d", c.Server.Port)
	}

	if c.Database.URL == "" {
		return fmt.Errorf("database URL is required")
	}

	if c.NATS.URL == "" {
		return fmt.Errorf("NATS URL is required")
	}

	if c.Security.EnableAuth && c.Security.JWTSecret == "" {
		return fmt.Errorf("JWT secret is required when authentication is enabled")
	}

	if c.Security.EnableTLS && (c.Security.CertFile == "" || c.Security.KeyFile == "") {
		return fmt.Errorf("certificate and key files are required when TLS is enabled")
	}

	return nil
}

// Helper functions for environment variable parsing
func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

func getEnvAsInt(key string, defaultValue int) int {
	if value := os.Getenv(key); value != "" {
		if intValue, err := strconv.Atoi(value); err == nil {
			return intValue
		}
	}
	return defaultValue
}

func getEnvAsBool(key string, defaultValue bool) bool {
	if value := os.Getenv(key); value != "" {
		if boolValue, err := strconv.ParseBool(value); err == nil {
			return boolValue
		}
	}
	return defaultValue
}