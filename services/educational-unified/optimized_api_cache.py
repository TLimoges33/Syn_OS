#!/usr/bin/env python3
"""
Optimized Educational Platform API with Rate Limiting and Caching
High-performance caching layer for educational platform APIs
"""

import asyncio
import time
import json
import logging
import hashlib
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import aioredis
import pickle
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class CacheStrategy(Enum):
    """Cache strategies for different data types"""
    LRU = "lru"
    LFU = "lfu"
    TTL = "ttl"
    HYBRID = "hybrid"

class RateLimitStrategy(Enum):
    """Rate limiting strategies"""
    TOKEN_BUCKET = "token_bucket"
    SLIDING_WINDOW = "sliding_window"
    FIXED_WINDOW = "fixed_window"

@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    key: str
    data: Any
    created_at: float
    last_accessed: float
    access_count: int = 0
    ttl_seconds: Optional[int] = None
    
    def is_expired(self) -> bool:
        """Check if entry is expired"""
        if self.ttl_seconds is None:
            return False
        return time.time() - self.created_at > self.ttl_seconds
    
    def touch(self):
        """Update access metadata"""
        self.last_accessed = time.time()
        self.access_count += 1

@dataclass
class RateLimitBucket:
    """Token bucket for rate limiting"""
    capacity: int
    tokens: int
    refill_rate: float  # tokens per second
    last_refill: float
    
    def consume(self, tokens: int = 1) -> bool:
        """Try to consume tokens from bucket"""
        self._refill()
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False
    
    def _refill(self):
        """Refill tokens based on time elapsed"""
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + (elapsed * self.refill_rate))
        self.last_refill = now

class OptimizedAPICache:
    """High-performance API cache with multiple strategies"""
    
    def __init__(self, max_size: int = 10000, default_ttl: int = 300):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: Dict[str, CacheEntry] = {}
        self.access_order = deque()  # For LRU
        self.access_frequency = defaultdict(int)  # For LFU
        self.size_estimate = 0
        self.hit_count = 0
        self.miss_count = 0
        self.redis_client: Optional[aioredis.Redis] = None
        
        # Initialize Redis connection
        asyncio.create_task(self._init_redis())
    
    async def _init_redis(self):
        """Initialize Redis connection for distributed caching"""
        try:
            self.redis_client = await aioredis.from_url("redis://localhost:6379", decode_responses=False)
            logger.info("Redis cache backend initialized")
        except Exception as e:
            logger.warning(f"Redis unavailable, using in-memory cache only: {e}")
    
    async def get(self, key: str, strategy: CacheStrategy = CacheStrategy.HYBRID) -> Optional[Any]:
        """Get cached value with specified strategy"""
        # Try local cache first
        local_result = await self._get_local(key)
        if local_result is not None:
            self.hit_count += 1
            return local_result
        
        # Try Redis cache
        if self.redis_client:
            redis_result = await self._get_redis(key)
            if redis_result is not None:
                # Store back in local cache for faster future access
                await self._set_local(key, redis_result, self.default_ttl)
                self.hit_count += 1
                return redis_result
        
        self.miss_count += 1
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None, 
                  strategy: CacheStrategy = CacheStrategy.HYBRID):
        """Set cached value with specified strategy"""
        ttl = ttl or self.default_ttl
        
        # Set in local cache
        await self._set_local(key, value, ttl)
        
        # Set in Redis cache for distribution
        if self.redis_client:
            await self._set_redis(key, value, ttl)
    
    async def _get_local(self, key: str) -> Optional[Any]:
        """Get from local memory cache"""
        if key in self.cache:
            entry = self.cache[key]
            if entry.is_expired():
                await self._evict_local(key)
                return None
            
            entry.touch()
            self._update_access_order(key)
            return entry.data
        return None
    
    async def _set_local(self, key: str, value: Any, ttl: int):
        """Set in local memory cache"""
        # Evict if at capacity
        if len(self.cache) >= self.max_size:
            await self._evict_lru()
        
        entry = CacheEntry(
            key=key,
            data=value,
            created_at=time.time(),
            last_accessed=time.time(),
            ttl_seconds=ttl
        )
        
        self.cache[key] = entry
        self._update_access_order(key)
        self._estimate_size_increase(value)
    
    async def _get_redis(self, key: str) -> Optional[Any]:
        """Get from Redis cache"""
        try:
            data = await self.redis_client.get(f"edu_cache:{key}")
            if data:
                return pickle.loads(data)
        except Exception as e:
            logger.error(f"Redis get error: {e}")
        return None
    
    async def _set_redis(self, key: str, value: Any, ttl: int):
        """Set in Redis cache"""
        try:
            serialized = pickle.dumps(value)
            await self.redis_client.setex(f"edu_cache:{key}", ttl, serialized)
        except Exception as e:
            logger.error(f"Redis set error: {e}")
    
    def _update_access_order(self, key: str):
        """Update LRU access order"""
        if key in self.access_order:
            self.access_order.remove(key)
        self.access_order.append(key)
        self.access_frequency[key] += 1
    
    async def _evict_lru(self):
        """Evict least recently used item"""
        if self.access_order:
            lru_key = self.access_order.popleft()
            await self._evict_local(lru_key)
    
    async def _evict_local(self, key: str):
        """Evict item from local cache"""
        if key in self.cache:
            entry = self.cache.pop(key)
            self._estimate_size_decrease(entry.data)
            if key in self.access_order:
                self.access_order.remove(key)
    
    def _estimate_size_increase(self, value: Any):
        """Estimate memory size increase"""
        try:
            self.size_estimate += len(pickle.dumps(value))
        except:
            self.size_estimate += 1000  # Rough estimate
    
    def _estimate_size_decrease(self, value: Any):
        """Estimate memory size decrease"""
        try:
            self.size_estimate -= len(pickle.dumps(value))
        except:
            self.size_estimate = max(0, self.size_estimate - 1000)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.hit_count + self.miss_count
        hit_rate = self.hit_count / total_requests if total_requests > 0 else 0
        
        return {
            'hit_count': self.hit_count,
            'miss_count': self.miss_count,
            'hit_rate': hit_rate,
            'cache_size': len(self.cache),
            'estimated_memory_kb': self.size_estimate / 1024,
            'redis_available': self.redis_client is not None
        }
    
    async def clear(self):
        """Clear all caches"""
        self.cache.clear()
        self.access_order.clear()
        self.access_frequency.clear()
        self.size_estimate = 0
        
        if self.redis_client:
            try:
                keys = await self.redis_client.keys("edu_cache:*")
                if keys:
                    await self.redis_client.delete(*keys)
            except Exception as e:
                logger.error(f"Redis clear error: {e}")

class RateLimiter:
    """High-performance rate limiter with multiple strategies"""
    
    def __init__(self):
        self.buckets: Dict[str, RateLimitBucket] = {}
        self.sliding_windows: Dict[str, deque] = defaultdict(lambda: deque())
        self.request_counts: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    
    async def is_allowed(self, identifier: str, limit: int, window_seconds: int, 
                        strategy: RateLimitStrategy = RateLimitStrategy.TOKEN_BUCKET) -> bool:
        """Check if request is allowed based on rate limit"""
        if strategy == RateLimitStrategy.TOKEN_BUCKET:
            return self._token_bucket_check(identifier, limit, window_seconds)
        elif strategy == RateLimitStrategy.SLIDING_WINDOW:
            return self._sliding_window_check(identifier, limit, window_seconds)
        elif strategy == RateLimitStrategy.FIXED_WINDOW:
            return self._fixed_window_check(identifier, limit, window_seconds)
        
        return True
    
    def _token_bucket_check(self, identifier: str, capacity: int, refill_rate_per_sec: float) -> bool:
        """Token bucket rate limiting"""
        if identifier not in self.buckets:
            self.buckets[identifier] = RateLimitBucket(
                capacity=capacity,
                tokens=capacity,
                refill_rate=refill_rate_per_sec,
                last_refill=time.time()
            )
        
        return self.buckets[identifier].consume(1)
    
    def _sliding_window_check(self, identifier: str, limit: int, window_seconds: int) -> bool:
        """Sliding window rate limiting"""
        now = time.time()
        window = self.sliding_windows[identifier]
        
        # Remove old requests outside the window
        while window and window[0] <= now - window_seconds:
            window.popleft()
        
        # Check if under limit
        if len(window) < limit:
            window.append(now)
            return True
        
        return False
    
    def _fixed_window_check(self, identifier: str, limit: int, window_seconds: int) -> bool:
        """Fixed window rate limiting"""
        now = time.time()
        window_start = int(now / window_seconds) * window_seconds
        window_key = str(int(window_start))
        
        # Clean old windows
        current_window = int(now / window_seconds)
        to_remove = [k for k in self.request_counts[identifier].keys() 
                    if int(float(k) / window_seconds) < current_window - 1]
        for k in to_remove:
            del self.request_counts[identifier][k]
        
        # Check current window
        current_count = self.request_counts[identifier][window_key]
        if current_count < limit:
            self.request_counts[identifier][window_key] += 1
            return True
        
        return False
    
    def get_stats(self, identifier: str) -> Dict[str, Any]:
        """Get rate limiting stats for identifier"""
        bucket = self.buckets.get(identifier)
        window = self.sliding_windows.get(identifier)
        
        return {
            'identifier': identifier,
            'token_bucket_available': bucket.tokens if bucket else 0,
            'sliding_window_requests': len(window) if window else 0,
            'fixed_window_requests': sum(self.request_counts.get(identifier, {}).values())
        }

class OptimizedEducationalAPI:
    """Optimized educational platform API with caching and rate limiting"""
    
    def __init__(self):
        self.cache = OptimizedAPICache(max_size=50000, default_ttl=300)  # 5 minutes default
        self.rate_limiter = RateLimiter()
        self.api_clients = {}
        self.request_stats = defaultdict(int)
        
        # Performance tracking
        self.response_times = deque(maxlen=1000)
        self.error_counts = defaultdict(int)
    
    async def get_platform_data(self, platform: str, endpoint: str, params: Dict[str, Any],
                              user_id: str = "anonymous") -> Dict[str, Any]:
        """Get platform data with caching and rate limiting"""
        start_time = time.perf_counter()
        
        try:
            # Rate limiting check
            rate_limit_key = f"{platform}:{user_id}"
            if not await self.rate_limiter.is_allowed(
                rate_limit_key, 
                limit=100,  # 100 requests per minute
                window_seconds=60
            ):
                raise Exception(f"Rate limit exceeded for {platform}")
            
            # Generate cache key
            cache_key = self._generate_cache_key(platform, endpoint, params)
            
            # Try cache first
            cached_data = await self.cache.get(cache_key)
            if cached_data is not None:
                processing_time = time.perf_counter() - start_time
                self.response_times.append(processing_time * 1000)  # Store as ms
                self.request_stats[f"{platform}_cache_hits"] += 1
                return {
                    'data': cached_data,
                    'source': 'cache',
                    'processing_time_ms': processing_time * 1000,
                    'platform': platform
                }
            
            # Fetch from API
            fresh_data = await self._fetch_from_platform(platform, endpoint, params)
            
            # Cache the result
            cache_ttl = self._get_cache_ttl(platform, endpoint)
            await self.cache.set(cache_key, fresh_data, ttl=cache_ttl)
            
            processing_time = time.perf_counter() - start_time
            self.response_times.append(processing_time * 1000)
            self.request_stats[f"{platform}_api_calls"] += 1
            
            return {
                'data': fresh_data,
                'source': 'api',
                'processing_time_ms': processing_time * 1000,
                'platform': platform,
                'cached_for': cache_ttl
            }
            
        except Exception as e:
            processing_time = time.perf_counter() - start_time
            self.error_counts[f"{platform}_errors"] += 1
            logger.error(f"Error fetching {platform} data: {e} (took {processing_time*1000:.1f}ms)")
            raise
    
    def _generate_cache_key(self, platform: str, endpoint: str, params: Dict[str, Any]) -> str:
        """Generate deterministic cache key"""
        # Sort params for consistent hashing
        sorted_params = json.dumps(params, sort_keys=True)
        key_content = f"{platform}:{endpoint}:{sorted_params}"
        return hashlib.md5(key_content.encode()).hexdigest()
    
    def _get_cache_ttl(self, platform: str, endpoint: str) -> int:
        """Get cache TTL based on platform and endpoint"""
        # Different TTLs for different data types
        if 'profile' in endpoint.lower():
            return 1800  # 30 minutes for profile data
        elif 'progress' in endpoint.lower():
            return 300   # 5 minutes for progress data
        elif 'challenge' in endpoint.lower():
            return 3600  # 1 hour for challenge data
        else:
            return 600   # 10 minutes default
    
    async def _fetch_from_platform(self, platform: str, endpoint: str, params: Dict[str, Any]) -> Any:
        """Fetch data from specific platform"""
        # Mock implementation - would integrate with actual platform APIs
        await asyncio.sleep(0.1)  # Simulate API delay
        
        return {
            'platform': platform,
            'endpoint': endpoint,
            'data': f"Mock data for {platform} {endpoint}",
            'params': params,
            'timestamp': time.time()
        }
    
    async def bulk_fetch(self, requests: List[Dict[str, Any]], max_concurrent: int = 10) -> List[Dict[str, Any]]:
        """Fetch multiple requests concurrently with performance optimization"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def fetch_single(request):
            async with semaphore:
                return await self.get_platform_data(**request)
        
        # Execute all requests concurrently
        tasks = [fetch_single(req) for req in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    'error': str(result),
                    'request': requests[i],
                    'success': False
                })
            else:
                processed_results.append({
                    **result,
                    'success': True
                })
        
        return processed_results
    
    async def preload_cache(self, platform: str, common_requests: List[Dict[str, Any]]):
        """Preload cache with commonly requested data"""
        logger.info(f"Preloading cache for {platform} with {len(common_requests)} requests")
        
        results = await self.bulk_fetch(common_requests, max_concurrent=5)
        successful_preloads = sum(1 for r in results if r.get('success'))
        
        logger.info(f"Preloaded {successful_preloads}/{len(common_requests)} requests for {platform}")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
        cache_stats = self.cache.get_stats()
        
        return {
            'cache_performance': cache_stats,
            'average_response_time_ms': avg_response_time,
            'total_requests': sum(self.request_stats.values()),
            'request_breakdown': dict(self.request_stats),
            'error_counts': dict(self.error_counts),
            'p95_response_time_ms': sorted(self.response_times)[int(len(self.response_times) * 0.95)] if self.response_times else 0,
            'p99_response_time_ms': sorted(self.response_times)[int(len(self.response_times) * 0.99)] if self.response_times else 0
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check"""
        return {
            'status': 'healthy',
            'cache_size': len(self.cache.cache),
            'redis_available': self.cache.redis_client is not None,
            'recent_avg_response_ms': sum(list(self.response_times)[-10:]) / min(10, len(self.response_times)) if self.response_times else 0,
            'timestamp': datetime.now().isoformat()
        }

# Global optimized API instance
optimized_edu_api = OptimizedEducationalAPI()