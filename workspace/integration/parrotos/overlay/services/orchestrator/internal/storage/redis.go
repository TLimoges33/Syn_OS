package storage

import (
	"context"
	"encoding/json"
	"fmt"
	"time"

	"github.com/go-redis/redis/v8"
	"github.com/syn-os/orchestrator/internal/models"
)

// RedisClient wraps the Redis connection and provides caching operations
type RedisClient struct {
	client *redis.Client
	ctx    context.Context
}

// NewRedisClient creates a new Redis client connection
func NewRedisClient(redisURL string) (*RedisClient, error) {
	opts, err := redis.ParseURL(redisURL)
	if err != nil {
		return nil, fmt.Errorf("failed to parse Redis URL: %w", err)
	}

	client := redis.NewClient(opts)
	ctx := context.Background()

	// Test the connection
	if err := client.Ping(ctx).Err(); err != nil {
		return nil, fmt.Errorf("failed to ping Redis: %w", err)
	}

	return &RedisClient{
		client: client,
		ctx:    ctx,
	}, nil
}

// Close closes the Redis connection
func (r *RedisClient) Close() error {
	return r.client.Close()
}

// Service caching operations

// CacheService caches a service with TTL
func (r *RedisClient) CacheService(service *models.Service, ttl time.Duration) error {
	key := fmt.Sprintf("service:%s", service.ID)
	
	data, err := json.Marshal(service)
	if err != nil {
		return fmt.Errorf("failed to marshal service: %w", err)
	}

	return r.client.Set(r.ctx, key, data, ttl).Err()
}

// GetCachedService retrieves a cached service
func (r *RedisClient) GetCachedService(serviceID string) (*models.Service, error) {
	key := fmt.Sprintf("service:%s", serviceID)
	
	data, err := r.client.Get(r.ctx, key).Result()
	if err != nil {
		if err == redis.Nil {
			return nil, nil // Not found
		}
		return nil, fmt.Errorf("failed to get cached service: %w", err)
	}

	var service models.Service
	if err := json.Unmarshal([]byte(data), &service); err != nil {
		return nil, fmt.Errorf("failed to unmarshal service: %w", err)
	}

	return &service, nil
}

// InvalidateServiceCache removes a service from cache
func (r *RedisClient) InvalidateServiceCache(serviceID string) error {
	key := fmt.Sprintf("service:%s", serviceID)
	return r.client.Del(r.ctx, key).Err()
}

// CacheServiceList caches a list of services
func (r *RedisClient) CacheServiceList(services []*models.Service, cacheKey string, ttl time.Duration) error {
	data, err := json.Marshal(services)
	if err != nil {
		return fmt.Errorf("failed to marshal service list: %w", err)
	}

	key := fmt.Sprintf("services:%s", cacheKey)
	return r.client.Set(r.ctx, key, data, ttl).Err()
}

// GetCachedServiceList retrieves a cached service list
func (r *RedisClient) GetCachedServiceList(cacheKey string) ([]*models.Service, error) {
	key := fmt.Sprintf("services:%s", cacheKey)
	
	data, err := r.client.Get(r.ctx, key).Result()
	if err != nil {
		if err == redis.Nil {
			return nil, nil // Not found
		}
		return nil, fmt.Errorf("failed to get cached service list: %w", err)
	}

	var services []*models.Service
	if err := json.Unmarshal([]byte(data), &services); err != nil {
		return nil, fmt.Errorf("failed to unmarshal service list: %w", err)
	}

	return services, nil
}

// Health check caching

// CacheHealthCheck caches a health check result
func (r *RedisClient) CacheHealthCheck(healthCheck *models.HealthCheck, ttl time.Duration) error {
	key := fmt.Sprintf("health:%s", healthCheck.ServiceID)
	
	data, err := json.Marshal(healthCheck)
	if err != nil {
		return fmt.Errorf("failed to marshal health check: %w", err)
	}

	return r.client.Set(r.ctx, key, data, ttl).Err()
}

// GetCachedHealthCheck retrieves a cached health check
func (r *RedisClient) GetCachedHealthCheck(serviceID string) (*models.HealthCheck, error) {
	key := fmt.Sprintf("health:%s", serviceID)
	
	data, err := r.client.Get(r.ctx, key).Result()
	if err != nil {
		if err == redis.Nil {
			return nil, nil // Not found
		}
		return nil, fmt.Errorf("failed to get cached health check: %w", err)
	}

	var healthCheck models.HealthCheck
	if err := json.Unmarshal([]byte(data), &healthCheck); err != nil {
		return nil, fmt.Errorf("failed to unmarshal health check: %w", err)
	}

	return &healthCheck, nil
}

// Metrics caching

// CacheMetrics caches service metrics
func (r *RedisClient) CacheMetrics(serviceID string, metrics map[string]interface{}, ttl time.Duration) error {
	key := fmt.Sprintf("metrics:%s", serviceID)
	
	data, err := json.Marshal(metrics)
	if err != nil {
		return fmt.Errorf("failed to marshal metrics: %w", err)
	}

	return r.client.Set(r.ctx, key, data, ttl).Err()
}

// GetCachedMetrics retrieves cached metrics
func (r *RedisClient) GetCachedMetrics(serviceID string) (map[string]interface{}, error) {
	key := fmt.Sprintf("metrics:%s", serviceID)
	
	data, err := r.client.Get(r.ctx, key).Result()
	if err != nil {
		if err == redis.Nil {
			return nil, nil // Not found
		}
		return nil, fmt.Errorf("failed to get cached metrics: %w", err)
	}

	var metrics map[string]interface{}
	if err := json.Unmarshal([]byte(data), &metrics); err != nil {
		return nil, fmt.Errorf("failed to unmarshal metrics: %w", err)
	}

	return metrics, nil
}

// Configuration caching

// CacheConfiguration caches service configuration
func (r *RedisClient) CacheConfiguration(serviceID string, config map[string]interface{}, ttl time.Duration) error {
	key := fmt.Sprintf("config:%s", serviceID)
	
	data, err := json.Marshal(config)
	if err != nil {
		return fmt.Errorf("failed to marshal configuration: %w", err)
	}

	return r.client.Set(r.ctx, key, data, ttl).Err()
}

// GetCachedConfiguration retrieves cached configuration
func (r *RedisClient) GetCachedConfiguration(serviceID string) (map[string]interface{}, error) {
	key := fmt.Sprintf("config:%s", serviceID)
	
	data, err := r.client.Get(r.ctx, key).Result()
	if err != nil {
		if err == redis.Nil {
			return nil, nil // Not found
		}
		return nil, fmt.Errorf("failed to get cached configuration: %w", err)
	}

	var config map[string]interface{}
	if err := json.Unmarshal([]byte(data), &config); err != nil {
		return nil, fmt.Errorf("failed to unmarshal configuration: %w", err)
	}

	return config, nil
}

// Session and authentication caching

// CacheSession caches a user session
func (r *RedisClient) CacheSession(sessionID string, sessionData map[string]interface{}, ttl time.Duration) error {
	key := fmt.Sprintf("session:%s", sessionID)
	
	data, err := json.Marshal(sessionData)
	if err != nil {
		return fmt.Errorf("failed to marshal session data: %w", err)
	}

	return r.client.Set(r.ctx, key, data, ttl).Err()
}

// GetCachedSession retrieves a cached session
func (r *RedisClient) GetCachedSession(sessionID string) (map[string]interface{}, error) {
	key := fmt.Sprintf("session:%s", sessionID)
	
	data, err := r.client.Get(r.ctx, key).Result()
	if err != nil {
		if err == redis.Nil {
			return nil, nil // Not found
		}
		return nil, fmt.Errorf("failed to get cached session: %w", err)
	}

	var sessionData map[string]interface{}
	if err := json.Unmarshal([]byte(data), &sessionData); err != nil {
		return nil, fmt.Errorf("failed to unmarshal session data: %w", err)
	}

	return sessionData, nil
}

// InvalidateSession removes a session from cache
func (r *RedisClient) InvalidateSession(sessionID string) error {
	key := fmt.Sprintf("session:%s", sessionID)
	return r.client.Del(r.ctx, key).Err()
}

// Event caching and pub/sub

// PublishEvent publishes an event to a Redis channel
func (r *RedisClient) PublishEvent(channel string, event *models.Event) error {
	data, err := json.Marshal(event)
	if err != nil {
		return fmt.Errorf("failed to marshal event: %w", err)
	}

	return r.client.Publish(r.ctx, channel, data).Err()
}

// SubscribeToEvents subscribes to events on a Redis channel
func (r *RedisClient) SubscribeToEvents(channel string) *redis.PubSub {
	return r.client.Subscribe(r.ctx, channel)
}

// Rate limiting

// CheckRateLimit checks if a rate limit has been exceeded
func (r *RedisClient) CheckRateLimit(key string, limit int, window time.Duration) (bool, error) {
	pipe := r.client.TxPipeline()
	
	// Increment counter
	incr := pipe.Incr(r.ctx, key)
	pipe.Expire(r.ctx, key, window)
	
	_, err := pipe.Exec(r.ctx)
	if err != nil {
		return false, fmt.Errorf("failed to execute rate limit pipeline: %w", err)
	}

	count := incr.Val()
	return count <= int64(limit), nil
}

// Distributed locking

// AcquireLock acquires a distributed lock
func (r *RedisClient) AcquireLock(lockKey string, ttl time.Duration) (bool, error) {
	result := r.client.SetNX(r.ctx, lockKey, "locked", ttl)
	return result.Val(), result.Err()
}

// ReleaseLock releases a distributed lock
func (r *RedisClient) ReleaseLock(lockKey string) error {
	return r.client.Del(r.ctx, lockKey).Err()
}

// System health and monitoring

// CacheSystemHealth caches overall system health
func (r *RedisClient) CacheSystemHealth(health map[string]interface{}, ttl time.Duration) error {
	key := "system:health"
	
	data, err := json.Marshal(health)
	if err != nil {
		return fmt.Errorf("failed to marshal system health: %w", err)
	}

	return r.client.Set(r.ctx, key, data, ttl).Err()
}

// GetCachedSystemHealth retrieves cached system health
func (r *RedisClient) GetCachedSystemHealth() (map[string]interface{}, error) {
	key := "system:health"
	
	data, err := r.client.Get(r.ctx, key).Result()
	if err != nil {
		if err == redis.Nil {
			return nil, nil // Not found
		}
		return nil, fmt.Errorf("failed to get cached system health: %w", err)
	}

	var health map[string]interface{}
	if err := json.Unmarshal([]byte(data), &health); err != nil {
		return nil, fmt.Errorf("failed to unmarshal system health: %w", err)
	}

	return health, nil
}

// Utility methods

// FlushCache clears all cached data
func (r *RedisClient) FlushCache() error {
	return r.client.FlushDB(r.ctx).Err()
}

// GetCacheStats returns cache statistics
func (r *RedisClient) GetCacheStats() (map[string]interface{}, error) {
	info := r.client.Info(r.ctx, "memory", "stats")
	if info.Err() != nil {
		return nil, fmt.Errorf("failed to get Redis info: %w", info.Err())
	}

	// Parse basic stats from Redis INFO command
	stats := map[string]interface{}{
		"connected": true,
		"info":      info.Val(),
	}

	// Get key count
	dbSize := r.client.DBSize(r.ctx)
	if dbSize.Err() == nil {
		stats["key_count"] = dbSize.Val()
	}

	return stats, nil
}