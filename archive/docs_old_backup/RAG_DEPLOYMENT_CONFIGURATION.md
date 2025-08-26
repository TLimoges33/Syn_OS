# RAG System Deployment and Configuration
## Comprehensive Deployment Guide for Consciousness-Aware RAG

### Table of Contents

- [RAG System Deployment and Configuration](#rag-system-deployment-and-configuration)
  - [Comprehensive Deployment Guide for Consciousness-Aware RAG](#comprehensive-deployment-guide-for-consciousness-aware-rag)
    - [Table of Contents](#table-of-contents)
  - [Deployment Overview](#deployment-overview)
    - [Architecture Components](#architecture-components)
    - [Deployment Modes](#deployment-modes)
  - [Infrastructure Requirements](#infrastructure-requirements)
    - [Hardware Requirements](#hardware-requirements)
    - [Software Dependencies](#software-dependencies)
  - [Vector Database Setup](#vector-database-setup)
    - [Qdrant Configuration (Recommended)](#qdrant-configuration-recommended)
  - [Configuration Management](#configuration-management)
    - [Main Configuration File](#main-configuration-file)
    - [Environment-Specific Configurations](#environment-specific-configurations)
  - [Docker Deployment](#docker-deployment)
    - [Complete Docker Compose Setup](#complete-docker-compose-setup)
    - [Dockerfiles](#dockerfiles)
  - [Kubernetes Deployment](#kubernetes-deployment)
    - [Kubernetes Manifests](#kubernetes-manifests)
  - [Monitoring and Observability](#monitoring-and-observability)
    - [Prometheus Configuration](#prometheus-configuration)
- [config/prometheus.yml](#configprometheusyml)

- --

## Deployment Overview

### Architecture Components

The RAG system consists of several key components that need to be deployed and configured:

```mermaid
graph TB
    subgraph "Application Layer"
        RAG[RAG Engine]
        LMS[LM Studio RAG]
        API[RAG API Gateway]
    end

    subgraph "Processing Layer"
        EMB[Embedding Service]
        ING[Ingestion Pipeline]
        MEM[Memory System]
    end

    subgraph "Storage Layer"
        VDB[Vector Database]
        PDB[PostgreSQL]
        RDS[Redis Cache]
        FS[File Storage]
    end

    subgraph "Infrastructure"
        LB[Load Balancer]
        MON[Monitoring]
        LOG[Logging]
    end

    RAG --> EMB
    RAG --> VDB
    LMS --> RAG
    API --> RAG

    EMB --> VDB
    ING --> VDB
    MEM --> VDB
    MEM --> PDB

    RAG --> RDS
    ING --> FS

    LB --> API
    MON --> RAG
    LOG --> RAG
```text

    end

    subgraph "Processing Layer"
        EMB[Embedding Service]
        ING[Ingestion Pipeline]
        MEM[Memory System]
    end

    subgraph "Storage Layer"
        VDB[Vector Database]
        PDB[PostgreSQL]
        RDS[Redis Cache]
        FS[File Storage]
    end

    subgraph "Infrastructure"
        LB[Load Balancer]
        MON[Monitoring]
        LOG[Logging]
    end

    RAG --> EMB
    RAG --> VDB
    LMS --> RAG
    API --> RAG

    EMB --> VDB
    ING --> VDB
    MEM --> VDB
    MEM --> PDB

    RAG --> RDS
    ING --> FS

    LB --> API
    MON --> RAG
    LOG --> RAG

```text
    end

    subgraph "Processing Layer"
        EMB[Embedding Service]
        ING[Ingestion Pipeline]
        MEM[Memory System]
    end

    subgraph "Storage Layer"
        VDB[Vector Database]
        PDB[PostgreSQL]
        RDS[Redis Cache]
        FS[File Storage]
    end

    subgraph "Infrastructure"
        LB[Load Balancer]
        MON[Monitoring]
        LOG[Logging]
    end

    RAG --> EMB
    RAG --> VDB
    LMS --> RAG
    API --> RAG

    EMB --> VDB
    ING --> VDB
    MEM --> VDB
    MEM --> PDB

    RAG --> RDS
    ING --> FS

    LB --> API
    MON --> RAG
    LOG --> RAG

```text
        MEM[Memory System]
    end

    subgraph "Storage Layer"
        VDB[Vector Database]
        PDB[PostgreSQL]
        RDS[Redis Cache]
        FS[File Storage]
    end

    subgraph "Infrastructure"
        LB[Load Balancer]
        MON[Monitoring]
        LOG[Logging]
    end

    RAG --> EMB
    RAG --> VDB
    LMS --> RAG
    API --> RAG

    EMB --> VDB
    ING --> VDB
    MEM --> VDB
    MEM --> PDB

    RAG --> RDS
    ING --> FS

    LB --> API
    MON --> RAG
    LOG --> RAG

```text

### Deployment Modes

* *Development Mode**:

- Single-node deployment
- SQLite for metadata
- Local file storage
- Minimal resource requirements

* *Production Mode**:

- Multi-node deployment
- PostgreSQL cluster
- Distributed vector database
- High availability configuration

* *Cloud-Native Mode**:

- Kubernetes orchestration
- Auto-scaling capabilities
- Cloud storage integration
- Managed services utilization

- --

## Infrastructure Requirements

### Hardware Requirements

* *Minimum Requirements (Development)**:

```yaml
- Single-node deployment
- SQLite for metadata
- Local file storage
- Minimal resource requirements

* *Production Mode**:

- Multi-node deployment
- PostgreSQL cluster
- Distributed vector database
- High availability configuration

* *Cloud-Native Mode**:

- Kubernetes orchestration
- Auto-scaling capabilities
- Cloud storage integration
- Managed services utilization

- --

## Infrastructure Requirements

### Hardware Requirements

* *Minimum Requirements (Development)**:

```yaml

- Single-node deployment
- SQLite for metadata
- Local file storage
- Minimal resource requirements

* *Production Mode**:

- Multi-node deployment
- PostgreSQL cluster
- Distributed vector database
- High availability configuration

* *Cloud-Native Mode**:

- Kubernetes orchestration
- Auto-scaling capabilities
- Cloud storage integration
- Managed services utilization

- --

## Infrastructure Requirements

### Hardware Requirements

* *Minimum Requirements (Development)**:

```yaml

* *Production Mode**:

- Multi-node deployment
- PostgreSQL cluster
- Distributed vector database
- High availability configuration

* *Cloud-Native Mode**:

- Kubernetes orchestration
- Auto-scaling capabilities
- Cloud storage integration
- Managed services utilization

- --

## Infrastructure Requirements

### Hardware Requirements

* *Minimum Requirements (Development)**:

```yaml
cpu: 4 cores (2.5GHz)
memory: 16GB RAM
storage: 100GB SSD
network: 1Gbps
gpu: Optional (CUDA-compatible for embeddings)
```text

```text

```text
```text

* *Recommended Requirements (Production)**:

```yaml
```yaml

```yaml

```yaml
cpu: 16 cores (3.0GHz)
memory: 64GB RAM
storage: 1TB NVMe SSD
network: 10Gbps
gpu: NVIDIA A100 or equivalent (for embedding generation)
additional_storage: 10TB for knowledge base
```text

additional_storage: 10TB for knowledge base

```text
additional_storage: 10TB for knowledge base

```text
```text

* *High-Performance Requirements (Enterprise)**:

```yaml
```yaml

```yaml

```yaml
cpu: 32+ cores (3.5GHz)
memory: 128GB+ RAM
storage: 2TB+ NVMe SSD
network: 25Gbps+
gpu: Multiple NVIDIA A100s
distributed_storage: 100TB+ for large knowledge bases
```text

distributed_storage: 100TB+ for large knowledge bases

```text
distributed_storage: 100TB+ for large knowledge bases

```text
```text

### Software Dependencies

* *Core Dependencies**:

```yaml
```yaml

```yaml

```yaml
python: ">=3.9"
pytorch: ">=2.0.0"
transformers: ">=4.30.0"
numpy: ">=1.24.0"
scipy: ">=1.10.0"
scikit-learn: ">=1.3.0"
```text

scikit-learn: ">=1.3.0"

```text
scikit-learn: ">=1.3.0"

```text
```text

* *Vector Database Options**:

```yaml
```yaml

```yaml

```yaml
qdrant: ">=1.3.0"  # Recommended
chroma: ">=0.4.0"  # Alternative
weaviate: ">=1.20.0"  # Enterprise option
milvus: ">=2.3.0"  # Large-scale option
```text

```text

```text
```text

* *Additional Services**:

```yaml
```yaml

```yaml

```yaml
postgresql: ">=14.0"
redis: ">=7.0"
nginx: ">=1.20"
docker: ">=24.0"
kubernetes: ">=1.27"  # For K8s deployment
```text

```text

```text
```text

- --

## Vector Database Setup

### Qdrant Configuration (Recommended)

* *Docker Compose Setup**:

```yaml
### Qdrant Configuration (Recommended)

* *Docker Compose Setup**:

```yaml

### Qdrant Configuration (Recommended)

* *Docker Compose Setup**:

```yaml
```yaml

## docker-compose.qdrant.yml

version: '3.8'

services:
  qdrant:
    image: qdrant/qdrant:v1.3.0
    ports:

      - "6333:6333"
      - "6334:6334"

    volumes:

      - qdrant_storage:/qdrant/storage
      - ./config/qdrant_config.yaml:/qdrant/config/production.yaml

    environment:

      - QDRANT__SERVICE__HTTP_PORT=6333
      - QDRANT__SERVICE__GRPC_PORT=6334
      - QDRANT__LOG_LEVEL=INFO

    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 8G
        reservations:
          memory: 4G

volumes:
  qdrant_storage:
    driver: local
```text

services:
  qdrant:
    image: qdrant/qdrant:v1.3.0
    ports:

      - "6333:6333"
      - "6334:6334"

    volumes:

      - qdrant_storage:/qdrant/storage
      - ./config/qdrant_config.yaml:/qdrant/config/production.yaml

    environment:

      - QDRANT__SERVICE__HTTP_PORT=6333
      - QDRANT__SERVICE__GRPC_PORT=6334
      - QDRANT__LOG_LEVEL=INFO

    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 8G
        reservations:
          memory: 4G

volumes:
  qdrant_storage:
    driver: local

```text
services:
  qdrant:
    image: qdrant/qdrant:v1.3.0
    ports:

      - "6333:6333"
      - "6334:6334"

    volumes:

      - qdrant_storage:/qdrant/storage
      - ./config/qdrant_config.yaml:/qdrant/config/production.yaml

    environment:

      - QDRANT__SERVICE__HTTP_PORT=6333
      - QDRANT__SERVICE__GRPC_PORT=6334
      - QDRANT__LOG_LEVEL=INFO

    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 8G
        reservations:
          memory: 4G

volumes:
  qdrant_storage:
    driver: local

```text
      - "6333:6333"
      - "6334:6334"

    volumes:

      - qdrant_storage:/qdrant/storage
      - ./config/qdrant_config.yaml:/qdrant/config/production.yaml

    environment:

      - QDRANT__SERVICE__HTTP_PORT=6333
      - QDRANT__SERVICE__GRPC_PORT=6334
      - QDRANT__LOG_LEVEL=INFO

    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 8G
        reservations:
          memory: 4G

volumes:
  qdrant_storage:
    driver: local

```text

* *Qdrant Configuration File**:

```yaml
```yaml

```yaml
```yaml

## config/qdrant_config.yaml

service:
  http_port: 6333
  grpc_port: 6334
  enable_cors: true
  max_request_size_mb: 32

storage:
  # Storage configuration
  storage_path: "/qdrant/storage"
  snapshots_path: "/qdrant/snapshots"

  # Performance settings
  wal_capacity_mb: 32
  wal_segments_ahead: 0

  # Optimizations
  optimizers:
    deleted_threshold: 0.2
    vacuum_min_vector_number: 1000
    default_segment_number: 0
    max_segment_size_kb: 5000000
    memmap_threshold_kb: 200000
    indexing_threshold_kb: 20000
    flush_interval_sec: 5
    max_optimization_threads: 1

cluster:
  enabled: false
  # For multi-node setup:
  # p2p_port: 6335
  # consensus_timeout_ms: 1000

telemetry:
  disabled: false
```text

  grpc_port: 6334
  enable_cors: true
  max_request_size_mb: 32

storage:
  # Storage configuration
  storage_path: "/qdrant/storage"
  snapshots_path: "/qdrant/snapshots"

  # Performance settings
  wal_capacity_mb: 32
  wal_segments_ahead: 0

  # Optimizations
  optimizers:
    deleted_threshold: 0.2
    vacuum_min_vector_number: 1000
    default_segment_number: 0
    max_segment_size_kb: 5000000
    memmap_threshold_kb: 200000
    indexing_threshold_kb: 20000
    flush_interval_sec: 5
    max_optimization_threads: 1

cluster:
  enabled: false
  # For multi-node setup:
  # p2p_port: 6335
  # consensus_timeout_ms: 1000

telemetry:
  disabled: false

```text
  grpc_port: 6334
  enable_cors: true
  max_request_size_mb: 32

storage:
  # Storage configuration
  storage_path: "/qdrant/storage"
  snapshots_path: "/qdrant/snapshots"

  # Performance settings
  wal_capacity_mb: 32
  wal_segments_ahead: 0

  # Optimizations
  optimizers:
    deleted_threshold: 0.2
    vacuum_min_vector_number: 1000
    default_segment_number: 0
    max_segment_size_kb: 5000000
    memmap_threshold_kb: 200000
    indexing_threshold_kb: 20000
    flush_interval_sec: 5
    max_optimization_threads: 1

cluster:
  enabled: false
  # For multi-node setup:
  # p2p_port: 6335
  # consensus_timeout_ms: 1000

telemetry:
  disabled: false

```text
  # Storage configuration
  storage_path: "/qdrant/storage"
  snapshots_path: "/qdrant/snapshots"

  # Performance settings
  wal_capacity_mb: 32
  wal_segments_ahead: 0

  # Optimizations
  optimizers:
    deleted_threshold: 0.2
    vacuum_min_vector_number: 1000
    default_segment_number: 0
    max_segment_size_kb: 5000000
    memmap_threshold_kb: 200000
    indexing_threshold_kb: 20000
    flush_interval_sec: 5
    max_optimization_threads: 1

cluster:
  enabled: false
  # For multi-node setup:
  # p2p_port: 6335
  # consensus_timeout_ms: 1000

telemetry:
  disabled: false

```text

* *Collection Initialization**:

```python
```python

```python
```python

## scripts/init_qdrant_collections.py

import asyncio
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, CreateCollection

async def initialize_qdrant_collections():
    client = QdrantClient(host="localhost", port=6333)

    collections = {
        "documents": {
            "vectors": VectorParams(size=1536, distance=Distance.COSINE),
            "optimizers_config": {
                "default_segment_number": 2,
                "max_optimization_threads": 2
            }
        },
        "interactions": {
            "vectors": VectorParams(size=1536, distance=Distance.DOT),
            "optimizers_config": {
                "default_segment_number": 1,
                "max_optimization_threads": 1
            }
        },
        "consciousness_states": {
            "vectors": VectorParams(size=768, distance=Distance.COSINE),
            "optimizers_config": {
                "default_segment_number": 1,
                "max_optimization_threads": 1
            }
        },
        "episodic_memory": {
            "vectors": VectorParams(size=1536, distance=Distance.COSINE),
            "optimizers_config": {
                "default_segment_number": 2,
                "max_optimization_threads": 2
            }
        }
    }

    for collection_name, config in collections.items():
        try:
            client.create_collection(
                collection_name=collection_name,
                vectors_config=config["vectors"],
                optimizers_config=config.get("optimizers_config")
            )
            print(f"Created collection: {collection_name}")
        except Exception as e:
            print(f"Collection {collection_name} might already exist: {e}")

if __name__ == "__main__":
    asyncio.run(initialize_qdrant_collections())
```text

from qdrant_client.models import Distance, VectorParams, CreateCollection

async def initialize_qdrant_collections():
    client = QdrantClient(host="localhost", port=6333)

    collections = {
        "documents": {
            "vectors": VectorParams(size=1536, distance=Distance.COSINE),
            "optimizers_config": {
                "default_segment_number": 2,
                "max_optimization_threads": 2
            }
        },
        "interactions": {
            "vectors": VectorParams(size=1536, distance=Distance.DOT),
            "optimizers_config": {
                "default_segment_number": 1,
                "max_optimization_threads": 1
            }
        },
        "consciousness_states": {
            "vectors": VectorParams(size=768, distance=Distance.COSINE),
            "optimizers_config": {
                "default_segment_number": 1,
                "max_optimization_threads": 1
            }
        },
        "episodic_memory": {
            "vectors": VectorParams(size=1536, distance=Distance.COSINE),
            "optimizers_config": {
                "default_segment_number": 2,
                "max_optimization_threads": 2
            }
        }
    }

    for collection_name, config in collections.items():
        try:
            client.create_collection(
                collection_name=collection_name,
                vectors_config=config["vectors"],
                optimizers_config=config.get("optimizers_config")
            )
            print(f"Created collection: {collection_name}")
        except Exception as e:
            print(f"Collection {collection_name} might already exist: {e}")

if __name__ == "__main__":
    asyncio.run(initialize_qdrant_collections())

```text
from qdrant_client.models import Distance, VectorParams, CreateCollection

async def initialize_qdrant_collections():
    client = QdrantClient(host="localhost", port=6333)

    collections = {
        "documents": {
            "vectors": VectorParams(size=1536, distance=Distance.COSINE),
            "optimizers_config": {
                "default_segment_number": 2,
                "max_optimization_threads": 2
            }
        },
        "interactions": {
            "vectors": VectorParams(size=1536, distance=Distance.DOT),
            "optimizers_config": {
                "default_segment_number": 1,
                "max_optimization_threads": 1
            }
        },
        "consciousness_states": {
            "vectors": VectorParams(size=768, distance=Distance.COSINE),
            "optimizers_config": {
                "default_segment_number": 1,
                "max_optimization_threads": 1
            }
        },
        "episodic_memory": {
            "vectors": VectorParams(size=1536, distance=Distance.COSINE),
            "optimizers_config": {
                "default_segment_number": 2,
                "max_optimization_threads": 2
            }
        }
    }

    for collection_name, config in collections.items():
        try:
            client.create_collection(
                collection_name=collection_name,
                vectors_config=config["vectors"],
                optimizers_config=config.get("optimizers_config")
            )
            print(f"Created collection: {collection_name}")
        except Exception as e:
            print(f"Collection {collection_name} might already exist: {e}")

if __name__ == "__main__":
    asyncio.run(initialize_qdrant_collections())

```text
    collections = {
        "documents": {
            "vectors": VectorParams(size=1536, distance=Distance.COSINE),
            "optimizers_config": {
                "default_segment_number": 2,
                "max_optimization_threads": 2
            }
        },
        "interactions": {
            "vectors": VectorParams(size=1536, distance=Distance.DOT),
            "optimizers_config": {
                "default_segment_number": 1,
                "max_optimization_threads": 1
            }
        },
        "consciousness_states": {
            "vectors": VectorParams(size=768, distance=Distance.COSINE),
            "optimizers_config": {
                "default_segment_number": 1,
                "max_optimization_threads": 1
            }
        },
        "episodic_memory": {
            "vectors": VectorParams(size=1536, distance=Distance.COSINE),
            "optimizers_config": {
                "default_segment_number": 2,
                "max_optimization_threads": 2
            }
        }
    }

    for collection_name, config in collections.items():
        try:
            client.create_collection(
                collection_name=collection_name,
                vectors_config=config["vectors"],
                optimizers_config=config.get("optimizers_config")
            )
            print(f"Created collection: {collection_name}")
        except Exception as e:
            print(f"Collection {collection_name} might already exist: {e}")

if __name__ == "__main__":
    asyncio.run(initialize_qdrant_collections())

```text

- --

## Configuration Management

### Main Configuration File

```yaml
### Main Configuration File

```yaml

### Main Configuration File

```yaml
```yaml

## config/rag_config.yaml

system:
  name: "Consciousness-Aware RAG System"
  version: "1.0.0"
  environment: "production"  # development, staging, production
  debug: false
  log_level: "INFO"

## RAG Engine Configuration

rag_engine:
  max_concurrent_queries: 100
  query_timeout_seconds: 30.0
  cache_enabled: true
  cache_ttl_seconds: 300
  consciousness_influence_weight: 0.3

  # Retrieval settings
  default_max_results: 10
  min_relevance_threshold: 0.5
  enable_hybrid_search: true
  enable_consciousness_patterns: true

## Vector Database Configuration

vector_database:
  provider: "qdrant"  # qdrant, chroma, weaviate, milvus
  host: "localhost"
  port: 6333
  timeout_seconds: 30.0
  max_connections: 20

  # Collection settings
  collections:
    documents:
      vector_size: 1536
      distance_metric: "cosine"
      index_type: "hnsw"
      hnsw_config:
        m: 16
        ef_construct: 200
        ef: 128

    interactions:
      vector_size: 1536
      distance_metric: "dot_product"
      index_type: "hnsw"

    consciousness_states:
      vector_size: 768
      distance_metric: "cosine"
      index_type: "hnsw"

## Embedding Service Configuration

embedding_service:
  provider: "openai"  # openai, huggingface, sentence_transformers
  model_name: "text-embedding-ada-002"
  batch_size: 32
  max_tokens: 8192
  timeout_seconds: 30.0

  # Consciousness-aware embedding settings
  consciousness_contextualization: true
  consciousness_weight: 0.2

  # Model fallbacks
  fallback_models:

    - "sentence-transformers/all-MiniLM-L6-v2"
    - "sentence-transformers/all-mpnet-base-v2"

  # Caching
  cache_embeddings: true
  cache_size: 10000
  cache_ttl_seconds: 3600

## Knowledge Ingestion Configuration

knowledge_ingestion:
  # Processing settings
  chunk_size: 512
  chunk_overlap: 50
  consciousness_aware_chunking: true

  # Supported formats
  supported_formats:

    - "pdf"
    - "docx"
    - "txt"
    - "md"
    - "html"
    - "json"

  # Processing pipeline
  enable_content_enhancement: true
  enable_quality_assessment: true
  enable_consciousness_tagging: true

  # Batch processing
  batch_size: 100
  max_concurrent_jobs: 5

  # Storage
  temp_storage_path: "/tmp/rag_ingestion"
  processed_storage_path: "/data/rag/processed"

## Memory Augmentation Configuration

memory_augmentation:
  # Episodic memory settings
  max_episodes_per_user: 1000
  episode_consolidation_threshold: 0.8
  episode_retention_days: 365

  # Memory consolidation
  consolidation_interval_hours: 24
  consolidation_batch_size: 50

  # Similarity thresholds
  episode_similarity_threshold: 0.7
  memory_retrieval_threshold: 0.6

## Performance Configuration

performance:
  # Caching
  enable_query_cache: true
  query_cache_size: 5000
  query_cache_ttl: 300

  enable_result_cache: true
  result_cache_size: 10000
  result_cache_ttl: 600

  # Concurrency
  max_concurrent_retrievals: 50
  max_concurrent_embeddings: 20

  # Resource limits
  max_memory_usage_gb: 8
  max_cpu_usage_percent: 80

## Integration Configuration

integration:
  # Consciousness system
  consciousness_bus_url: "http://localhost:8080"
  consciousness_sync_interval: 30

  # LM Studio
  lm_studio_url: "http://localhost:1234"
  lm_studio_timeout: 120

  # External APIs
  openai_api_key: "${OPENAI_API_KEY}"
  huggingface_api_key: "${HUGGINGFACE_API_KEY}"

## Monitoring Configuration

monitoring:
  enable_metrics: true
  metrics_port: 9090
  metrics_path: "/metrics"

  enable_health_checks: true
  health_check_interval: 30

  enable_performance_tracking: true
  performance_sample_rate: 0.1

  # Alerting
  enable_alerting: true
  alert_thresholds:
    query_latency_ms: 5000
    error_rate_percent: 5.0
    memory_usage_percent: 90.0
    disk_usage_percent: 85.0

## Security Configuration

security:
  enable_authentication: true
  enable_authorization: true
  enable_encryption_at_rest: true
  enable_encryption_in_transit: true

  # API security
  api_key_required: true
  rate_limiting:
    requests_per_minute: 1000
    burst_size: 100

  # Data privacy
  enable_data_anonymization: true
  pii_detection: true
  data_retention_days: 730

## Logging Configuration

logging:
  level: "INFO"
  format: "json"
  output: "file"
  file_path: "/var/log/rag/rag.log"
  max_file_size_mb: 100
  max_files: 10

  # Component-specific logging
  components:
    rag_engine: "INFO"
    vector_db: "INFO"
    embedding_service: "INFO"
    knowledge_ingestion: "INFO"
    memory_augmentation: "DEBUG"
```text

  version: "1.0.0"
  environment: "production"  # development, staging, production
  debug: false
  log_level: "INFO"

## RAG Engine Configuration

rag_engine:
  max_concurrent_queries: 100
  query_timeout_seconds: 30.0
  cache_enabled: true
  cache_ttl_seconds: 300
  consciousness_influence_weight: 0.3

  # Retrieval settings
  default_max_results: 10
  min_relevance_threshold: 0.5
  enable_hybrid_search: true
  enable_consciousness_patterns: true

## Vector Database Configuration

vector_database:
  provider: "qdrant"  # qdrant, chroma, weaviate, milvus
  host: "localhost"
  port: 6333
  timeout_seconds: 30.0
  max_connections: 20

  # Collection settings
  collections:
    documents:
      vector_size: 1536
      distance_metric: "cosine"
      index_type: "hnsw"
      hnsw_config:
        m: 16
        ef_construct: 200
        ef: 128

    interactions:
      vector_size: 1536
      distance_metric: "dot_product"
      index_type: "hnsw"

    consciousness_states:
      vector_size: 768
      distance_metric: "cosine"
      index_type: "hnsw"

## Embedding Service Configuration

embedding_service:
  provider: "openai"  # openai, huggingface, sentence_transformers
  model_name: "text-embedding-ada-002"
  batch_size: 32
  max_tokens: 8192
  timeout_seconds: 30.0

  # Consciousness-aware embedding settings
  consciousness_contextualization: true
  consciousness_weight: 0.2

  # Model fallbacks
  fallback_models:

    - "sentence-transformers/all-MiniLM-L6-v2"
    - "sentence-transformers/all-mpnet-base-v2"

  # Caching
  cache_embeddings: true
  cache_size: 10000
  cache_ttl_seconds: 3600

## Knowledge Ingestion Configuration

knowledge_ingestion:
  # Processing settings
  chunk_size: 512
  chunk_overlap: 50
  consciousness_aware_chunking: true

  # Supported formats
  supported_formats:

    - "pdf"
    - "docx"
    - "txt"
    - "md"
    - "html"
    - "json"

  # Processing pipeline
  enable_content_enhancement: true
  enable_quality_assessment: true
  enable_consciousness_tagging: true

  # Batch processing
  batch_size: 100
  max_concurrent_jobs: 5

  # Storage
  temp_storage_path: "/tmp/rag_ingestion"
  processed_storage_path: "/data/rag/processed"

## Memory Augmentation Configuration

memory_augmentation:
  # Episodic memory settings
  max_episodes_per_user: 1000
  episode_consolidation_threshold: 0.8
  episode_retention_days: 365

  # Memory consolidation
  consolidation_interval_hours: 24
  consolidation_batch_size: 50

  # Similarity thresholds
  episode_similarity_threshold: 0.7
  memory_retrieval_threshold: 0.6

## Performance Configuration

performance:
  # Caching
  enable_query_cache: true
  query_cache_size: 5000
  query_cache_ttl: 300

  enable_result_cache: true
  result_cache_size: 10000
  result_cache_ttl: 600

  # Concurrency
  max_concurrent_retrievals: 50
  max_concurrent_embeddings: 20

  # Resource limits
  max_memory_usage_gb: 8
  max_cpu_usage_percent: 80

## Integration Configuration

integration:
  # Consciousness system
  consciousness_bus_url: "http://localhost:8080"
  consciousness_sync_interval: 30

  # LM Studio
  lm_studio_url: "http://localhost:1234"
  lm_studio_timeout: 120

  # External APIs
  openai_api_key: "${OPENAI_API_KEY}"
  huggingface_api_key: "${HUGGINGFACE_API_KEY}"

## Monitoring Configuration

monitoring:
  enable_metrics: true
  metrics_port: 9090
  metrics_path: "/metrics"

  enable_health_checks: true
  health_check_interval: 30

  enable_performance_tracking: true
  performance_sample_rate: 0.1

  # Alerting
  enable_alerting: true
  alert_thresholds:
    query_latency_ms: 5000
    error_rate_percent: 5.0
    memory_usage_percent: 90.0
    disk_usage_percent: 85.0

## Security Configuration

security:
  enable_authentication: true
  enable_authorization: true
  enable_encryption_at_rest: true
  enable_encryption_in_transit: true

  # API security
  api_key_required: true
  rate_limiting:
    requests_per_minute: 1000
    burst_size: 100

  # Data privacy
  enable_data_anonymization: true
  pii_detection: true
  data_retention_days: 730

## Logging Configuration

logging:
  level: "INFO"
  format: "json"
  output: "file"
  file_path: "/var/log/rag/rag.log"
  max_file_size_mb: 100
  max_files: 10

  # Component-specific logging
  components:
    rag_engine: "INFO"
    vector_db: "INFO"
    embedding_service: "INFO"
    knowledge_ingestion: "INFO"
    memory_augmentation: "DEBUG"

```text
  version: "1.0.0"
  environment: "production"  # development, staging, production
  debug: false
  log_level: "INFO"

## RAG Engine Configuration

rag_engine:
  max_concurrent_queries: 100
  query_timeout_seconds: 30.0
  cache_enabled: true
  cache_ttl_seconds: 300
  consciousness_influence_weight: 0.3

  # Retrieval settings
  default_max_results: 10
  min_relevance_threshold: 0.5
  enable_hybrid_search: true
  enable_consciousness_patterns: true

## Vector Database Configuration

vector_database:
  provider: "qdrant"  # qdrant, chroma, weaviate, milvus
  host: "localhost"
  port: 6333
  timeout_seconds: 30.0
  max_connections: 20

  # Collection settings
  collections:
    documents:
      vector_size: 1536
      distance_metric: "cosine"
      index_type: "hnsw"
      hnsw_config:
        m: 16
        ef_construct: 200
        ef: 128

    interactions:
      vector_size: 1536
      distance_metric: "dot_product"
      index_type: "hnsw"

    consciousness_states:
      vector_size: 768
      distance_metric: "cosine"
      index_type: "hnsw"

## Embedding Service Configuration

embedding_service:
  provider: "openai"  # openai, huggingface, sentence_transformers
  model_name: "text-embedding-ada-002"
  batch_size: 32
  max_tokens: 8192
  timeout_seconds: 30.0

  # Consciousness-aware embedding settings
  consciousness_contextualization: true
  consciousness_weight: 0.2

  # Model fallbacks
  fallback_models:

    - "sentence-transformers/all-MiniLM-L6-v2"
    - "sentence-transformers/all-mpnet-base-v2"

  # Caching
  cache_embeddings: true
  cache_size: 10000
  cache_ttl_seconds: 3600

## Knowledge Ingestion Configuration

knowledge_ingestion:
  # Processing settings
  chunk_size: 512
  chunk_overlap: 50
  consciousness_aware_chunking: true

  # Supported formats
  supported_formats:

    - "pdf"
    - "docx"
    - "txt"
    - "md"
    - "html"
    - "json"

  # Processing pipeline
  enable_content_enhancement: true
  enable_quality_assessment: true
  enable_consciousness_tagging: true

  # Batch processing
  batch_size: 100
  max_concurrent_jobs: 5

  # Storage
  temp_storage_path: "/tmp/rag_ingestion"
  processed_storage_path: "/data/rag/processed"

## Memory Augmentation Configuration

memory_augmentation:
  # Episodic memory settings
  max_episodes_per_user: 1000
  episode_consolidation_threshold: 0.8
  episode_retention_days: 365

  # Memory consolidation
  consolidation_interval_hours: 24
  consolidation_batch_size: 50

  # Similarity thresholds
  episode_similarity_threshold: 0.7
  memory_retrieval_threshold: 0.6

## Performance Configuration

performance:
  # Caching
  enable_query_cache: true
  query_cache_size: 5000
  query_cache_ttl: 300

  enable_result_cache: true
  result_cache_size: 10000
  result_cache_ttl: 600

  # Concurrency
  max_concurrent_retrievals: 50
  max_concurrent_embeddings: 20

  # Resource limits
  max_memory_usage_gb: 8
  max_cpu_usage_percent: 80

## Integration Configuration

integration:
  # Consciousness system
  consciousness_bus_url: "http://localhost:8080"
  consciousness_sync_interval: 30

  # LM Studio
  lm_studio_url: "http://localhost:1234"
  lm_studio_timeout: 120

  # External APIs
  openai_api_key: "${OPENAI_API_KEY}"
  huggingface_api_key: "${HUGGINGFACE_API_KEY}"

## Monitoring Configuration

monitoring:
  enable_metrics: true
  metrics_port: 9090
  metrics_path: "/metrics"

  enable_health_checks: true
  health_check_interval: 30

  enable_performance_tracking: true
  performance_sample_rate: 0.1

  # Alerting
  enable_alerting: true
  alert_thresholds:
    query_latency_ms: 5000
    error_rate_percent: 5.0
    memory_usage_percent: 90.0
    disk_usage_percent: 85.0

## Security Configuration

security:
  enable_authentication: true
  enable_authorization: true
  enable_encryption_at_rest: true
  enable_encryption_in_transit: true

  # API security
  api_key_required: true
  rate_limiting:
    requests_per_minute: 1000
    burst_size: 100

  # Data privacy
  enable_data_anonymization: true
  pii_detection: true
  data_retention_days: 730

## Logging Configuration

logging:
  level: "INFO"
  format: "json"
  output: "file"
  file_path: "/var/log/rag/rag.log"
  max_file_size_mb: 100
  max_files: 10

  # Component-specific logging
  components:
    rag_engine: "INFO"
    vector_db: "INFO"
    embedding_service: "INFO"
    knowledge_ingestion: "INFO"
    memory_augmentation: "DEBUG"

```text
## RAG Engine Configuration

rag_engine:
  max_concurrent_queries: 100
  query_timeout_seconds: 30.0
  cache_enabled: true
  cache_ttl_seconds: 300
  consciousness_influence_weight: 0.3

  # Retrieval settings
  default_max_results: 10
  min_relevance_threshold: 0.5
  enable_hybrid_search: true
  enable_consciousness_patterns: true

## Vector Database Configuration

vector_database:
  provider: "qdrant"  # qdrant, chroma, weaviate, milvus
  host: "localhost"
  port: 6333
  timeout_seconds: 30.0
  max_connections: 20

  # Collection settings
  collections:
    documents:
      vector_size: 1536
      distance_metric: "cosine"
      index_type: "hnsw"
      hnsw_config:
        m: 16
        ef_construct: 200
        ef: 128

    interactions:
      vector_size: 1536
      distance_metric: "dot_product"
      index_type: "hnsw"

    consciousness_states:
      vector_size: 768
      distance_metric: "cosine"
      index_type: "hnsw"

## Embedding Service Configuration

embedding_service:
  provider: "openai"  # openai, huggingface, sentence_transformers
  model_name: "text-embedding-ada-002"
  batch_size: 32
  max_tokens: 8192
  timeout_seconds: 30.0

  # Consciousness-aware embedding settings
  consciousness_contextualization: true
  consciousness_weight: 0.2

  # Model fallbacks
  fallback_models:

    - "sentence-transformers/all-MiniLM-L6-v2"
    - "sentence-transformers/all-mpnet-base-v2"

  # Caching
  cache_embeddings: true
  cache_size: 10000
  cache_ttl_seconds: 3600

## Knowledge Ingestion Configuration

knowledge_ingestion:
  # Processing settings
  chunk_size: 512
  chunk_overlap: 50
  consciousness_aware_chunking: true

  # Supported formats
  supported_formats:

    - "pdf"
    - "docx"
    - "txt"
    - "md"
    - "html"
    - "json"

  # Processing pipeline
  enable_content_enhancement: true
  enable_quality_assessment: true
  enable_consciousness_tagging: true

  # Batch processing
  batch_size: 100
  max_concurrent_jobs: 5

  # Storage
  temp_storage_path: "/tmp/rag_ingestion"
  processed_storage_path: "/data/rag/processed"

## Memory Augmentation Configuration

memory_augmentation:
  # Episodic memory settings
  max_episodes_per_user: 1000
  episode_consolidation_threshold: 0.8
  episode_retention_days: 365

  # Memory consolidation
  consolidation_interval_hours: 24
  consolidation_batch_size: 50

  # Similarity thresholds
  episode_similarity_threshold: 0.7
  memory_retrieval_threshold: 0.6

## Performance Configuration

performance:
  # Caching
  enable_query_cache: true
  query_cache_size: 5000
  query_cache_ttl: 300

  enable_result_cache: true
  result_cache_size: 10000
  result_cache_ttl: 600

  # Concurrency
  max_concurrent_retrievals: 50
  max_concurrent_embeddings: 20

  # Resource limits
  max_memory_usage_gb: 8
  max_cpu_usage_percent: 80

## Integration Configuration

integration:
  # Consciousness system
  consciousness_bus_url: "http://localhost:8080"
  consciousness_sync_interval: 30

  # LM Studio
  lm_studio_url: "http://localhost:1234"
  lm_studio_timeout: 120

  # External APIs
  openai_api_key: "${OPENAI_API_KEY}"
  huggingface_api_key: "${HUGGINGFACE_API_KEY}"

## Monitoring Configuration

monitoring:
  enable_metrics: true
  metrics_port: 9090
  metrics_path: "/metrics"

  enable_health_checks: true
  health_check_interval: 30

  enable_performance_tracking: true
  performance_sample_rate: 0.1

  # Alerting
  enable_alerting: true
  alert_thresholds:
    query_latency_ms: 5000
    error_rate_percent: 5.0
    memory_usage_percent: 90.0
    disk_usage_percent: 85.0

## Security Configuration

security:
  enable_authentication: true
  enable_authorization: true
  enable_encryption_at_rest: true
  enable_encryption_in_transit: true

  # API security
  api_key_required: true
  rate_limiting:
    requests_per_minute: 1000
    burst_size: 100

  # Data privacy
  enable_data_anonymization: true
  pii_detection: true
  data_retention_days: 730

## Logging Configuration

logging:
  level: "INFO"
  format: "json"
  output: "file"
  file_path: "/var/log/rag/rag.log"
  max_file_size_mb: 100
  max_files: 10

  # Component-specific logging
  components:
    rag_engine: "INFO"
    vector_db: "INFO"
    embedding_service: "INFO"
    knowledge_ingestion: "INFO"
    memory_augmentation: "DEBUG"

```text

### Environment-Specific Configurations

* *Development Configuration**:

```yaml
```yaml

```yaml
```yaml

## config/development.yaml

system:
  environment: "development"
  debug: true
  log_level: "DEBUG"

vector_database:
  host: "localhost"
  port: 6333

embedding_service:
  model_name: "sentence-transformers/all-MiniLM-L6-v2"
  batch_size: 8

performance:
  max_concurrent_retrievals: 10
  max_concurrent_embeddings: 5

monitoring:
  enable_metrics: false
  enable_alerting: false

security:
  enable_authentication: false
  enable_authorization: false
```text

  debug: true
  log_level: "DEBUG"

vector_database:
  host: "localhost"
  port: 6333

embedding_service:
  model_name: "sentence-transformers/all-MiniLM-L6-v2"
  batch_size: 8

performance:
  max_concurrent_retrievals: 10
  max_concurrent_embeddings: 5

monitoring:
  enable_metrics: false
  enable_alerting: false

security:
  enable_authentication: false
  enable_authorization: false

```text
  debug: true
  log_level: "DEBUG"

vector_database:
  host: "localhost"
  port: 6333

embedding_service:
  model_name: "sentence-transformers/all-MiniLM-L6-v2"
  batch_size: 8

performance:
  max_concurrent_retrievals: 10
  max_concurrent_embeddings: 5

monitoring:
  enable_metrics: false
  enable_alerting: false

security:
  enable_authentication: false
  enable_authorization: false

```text
  port: 6333

embedding_service:
  model_name: "sentence-transformers/all-MiniLM-L6-v2"
  batch_size: 8

performance:
  max_concurrent_retrievals: 10
  max_concurrent_embeddings: 5

monitoring:
  enable_metrics: false
  enable_alerting: false

security:
  enable_authentication: false
  enable_authorization: false

```text

* *Production Configuration**:

```yaml
```yaml

```yaml
```yaml

## config/production.yaml

system:
  environment: "production"
  debug: false
  log_level: "INFO"

vector_database:
  host: "qdrant-cluster.internal"
  port: 6333
  max_connections: 100

embedding_service:
  model_name: "text-embedding-ada-002"
  batch_size: 64

performance:
  max_concurrent_retrievals: 200
  max_concurrent_embeddings: 50

monitoring:
  enable_metrics: true
  enable_alerting: true

security:
  enable_authentication: true
  enable_authorization: true
  enable_encryption_at_rest: true
  enable_encryption_in_transit: true
```text

  debug: false
  log_level: "INFO"

vector_database:
  host: "qdrant-cluster.internal"
  port: 6333
  max_connections: 100

embedding_service:
  model_name: "text-embedding-ada-002"
  batch_size: 64

performance:
  max_concurrent_retrievals: 200
  max_concurrent_embeddings: 50

monitoring:
  enable_metrics: true
  enable_alerting: true

security:
  enable_authentication: true
  enable_authorization: true
  enable_encryption_at_rest: true
  enable_encryption_in_transit: true

```text
  debug: false
  log_level: "INFO"

vector_database:
  host: "qdrant-cluster.internal"
  port: 6333
  max_connections: 100

embedding_service:
  model_name: "text-embedding-ada-002"
  batch_size: 64

performance:
  max_concurrent_retrievals: 200
  max_concurrent_embeddings: 50

monitoring:
  enable_metrics: true
  enable_alerting: true

security:
  enable_authentication: true
  enable_authorization: true
  enable_encryption_at_rest: true
  enable_encryption_in_transit: true

```text
  port: 6333
  max_connections: 100

embedding_service:
  model_name: "text-embedding-ada-002"
  batch_size: 64

performance:
  max_concurrent_retrievals: 200
  max_concurrent_embeddings: 50

monitoring:
  enable_metrics: true
  enable_alerting: true

security:
  enable_authentication: true
  enable_authorization: true
  enable_encryption_at_rest: true
  enable_encryption_in_transit: true

```text

- --

## Docker Deployment

### Complete Docker Compose Setup

```yaml
### Complete Docker Compose Setup

```yaml

### Complete Docker Compose Setup

```yaml
```yaml

## docker-compose.yml

version: '3.8'

services:
  # RAG Engine
  rag-engine:
    build:
      context: .
      dockerfile: Dockerfile.rag
    ports:

      - "8000:8000"

    environment:

      - RAG_CONFIG_PATH=/app/config/rag_config.yaml
      - RAG_ENVIRONMENT=production
      - OPENAI_API_KEY=${OPENAI_API_KEY}

    volumes:

      - ./config:/app/config
      - ./data:/app/data
      - rag_logs:/var/log/rag

    depends_on:

      - qdrant
      - postgres
      - redis

    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2.0'
        reservations:
          memory: 2G
          cpus: '1.0'

  # Vector Database (Qdrant)
  qdrant:
    image: qdrant/qdrant:v1.3.0
    ports:

      - "6333:6333"
      - "6334:6334"

    volumes:

      - qdrant_storage:/qdrant/storage
      - ./config/qdrant_config.yaml:/qdrant/config/production.yaml

    environment:

      - QDRANT__SERVICE__HTTP_PORT=6333
      - QDRANT__SERVICE__GRPC_PORT=6334

    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 8G
          cpus: '4.0'
        reservations:
          memory: 4G
          cpus: '2.0'

  # PostgreSQL for metadata
  postgres:
    image: postgres:15
    ports:

      - "5432:5432"

    environment:

      - POSTGRES_DB=rag_metadata
      - POSTGRES_USER=rag_user
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}

    volumes:

      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init_postgres.sql:/docker-entrypoint-initdb.d/init.sql

    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'

  # Redis for caching
  redis:
    image: redis:7-alpine
    ports:

      - "6379:6379"

    command: redis-server --appendonly yes --maxmemory 1gb --maxmemory-policy allkeys-lru
    volumes:

      - redis_data:/data

    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'

  # Embedding Service
  embedding-service:
    build:
      context: .
      dockerfile: Dockerfile.embeddings
    ports:

      - "8001:8001"

    environment:

      - EMBEDDING_CONFIG_PATH=/app/config/embedding_config.yaml
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - HUGGINGFACE_API_KEY=${HUGGINGFACE_API_KEY}

    volumes:

      - ./config:/app/config
      - embedding_cache:/app/cache

    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2.0'
        reservations:
          memory: 2G
          cpus: '1.0'

  # Knowledge Ingestion Service
  ingestion-service:
    build:
      context: .
      dockerfile: Dockerfile.ingestion
    ports:

      - "8002:8002"

    environment:

      - INGESTION_CONFIG_PATH=/app/config/ingestion_config.yaml

    volumes:

      - ./config:/app/config
      - ./data/documents:/app/documents
      - ingestion_temp:/tmp/ingestion

    depends_on:

      - qdrant
      - embedding-service

    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'

  # Nginx Load Balancer
  nginx:
    image: nginx:alpine
    ports:

      - "80:80"
      - "443:443"

    volumes:

      - ./config/nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl

    depends_on:

      - rag-engine

    restart: unless-stopped

  # Monitoring (Prometheus)
  prometheus:
    image: prom/prometheus:latest
    ports:

      - "9090:9090"

    volumes:

      - ./config/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus

    command:

      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'

    restart: unless-stopped

  # Grafana for visualization
  grafana:
    image: grafana/grafana:latest
    ports:

      - "3000:3000"

    environment:

      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}

    volumes:

      - grafana_data:/var/lib/grafana
      - ./config/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./config/grafana/datasources:/etc/grafana/provisioning/datasources

    depends_on:

      - prometheus

    restart: unless-stopped

volumes:
  qdrant_storage:
  postgres_data:
  redis_data:
  embedding_cache:
  ingestion_temp:
  rag_logs:
  prometheus_data:
  grafana_data:

networks:
  default:
    driver: bridge
```text

services:
  # RAG Engine
  rag-engine:
    build:
      context: .
      dockerfile: Dockerfile.rag
    ports:

      - "8000:8000"

    environment:

      - RAG_CONFIG_PATH=/app/config/rag_config.yaml
      - RAG_ENVIRONMENT=production
      - OPENAI_API_KEY=${OPENAI_API_KEY}

    volumes:

      - ./config:/app/config
      - ./data:/app/data
      - rag_logs:/var/log/rag

    depends_on:

      - qdrant
      - postgres
      - redis

    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2.0'
        reservations:
          memory: 2G
          cpus: '1.0'

  # Vector Database (Qdrant)
  qdrant:
    image: qdrant/qdrant:v1.3.0
    ports:

      - "6333:6333"
      - "6334:6334"

    volumes:

      - qdrant_storage:/qdrant/storage
      - ./config/qdrant_config.yaml:/qdrant/config/production.yaml

    environment:

      - QDRANT__SERVICE__HTTP_PORT=6333
      - QDRANT__SERVICE__GRPC_PORT=6334

    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 8G
          cpus: '4.0'
        reservations:
          memory: 4G
          cpus: '2.0'

  # PostgreSQL for metadata
  postgres:
    image: postgres:15
    ports:

      - "5432:5432"

    environment:

      - POSTGRES_DB=rag_metadata
      - POSTGRES_USER=rag_user
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}

    volumes:

      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init_postgres.sql:/docker-entrypoint-initdb.d/init.sql

    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'

  # Redis for caching
  redis:
    image: redis:7-alpine
    ports:

      - "6379:6379"

    command: redis-server --appendonly yes --maxmemory 1gb --maxmemory-policy allkeys-lru
    volumes:

      - redis_data:/data

    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'

  # Embedding Service
  embedding-service:
    build:
      context: .
      dockerfile: Dockerfile.embeddings
    ports:

      - "8001:8001"

    environment:

      - EMBEDDING_CONFIG_PATH=/app/config/embedding_config.yaml
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - HUGGINGFACE_API_KEY=${HUGGINGFACE_API_KEY}

    volumes:

      - ./config:/app/config
      - embedding_cache:/app/cache

    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2.0'
        reservations:
          memory: 2G
          cpus: '1.0'

  # Knowledge Ingestion Service
  ingestion-service:
    build:
      context: .
      dockerfile: Dockerfile.ingestion
    ports:

      - "8002:8002"

    environment:

      - INGESTION_CONFIG_PATH=/app/config/ingestion_config.yaml

    volumes:

      - ./config:/app/config
      - ./data/documents:/app/documents
      - ingestion_temp:/tmp/ingestion

    depends_on:

      - qdrant
      - embedding-service

    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'

  # Nginx Load Balancer
  nginx:
    image: nginx:alpine
    ports:

      - "80:80"
      - "443:443"

    volumes:

      - ./config/nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl

    depends_on:

      - rag-engine

    restart: unless-stopped

  # Monitoring (Prometheus)
  prometheus:
    image: prom/prometheus:latest
    ports:

      - "9090:9090"

    volumes:

      - ./config/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus

    command:

      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'

    restart: unless-stopped

  # Grafana for visualization
  grafana:
    image: grafana/grafana:latest
    ports:

      - "3000:3000"

    environment:

      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}

    volumes:

      - grafana_data:/var/lib/grafana
      - ./config/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./config/grafana/datasources:/etc/grafana/provisioning/datasources

    depends_on:

      - prometheus

    restart: unless-stopped

volumes:
  qdrant_storage:
  postgres_data:
  redis_data:
  embedding_cache:
  ingestion_temp:
  rag_logs:
  prometheus_data:
  grafana_data:

networks:
  default:
    driver: bridge

```text
services:
  # RAG Engine
  rag-engine:
    build:
      context: .
      dockerfile: Dockerfile.rag
    ports:

      - "8000:8000"

    environment:

      - RAG_CONFIG_PATH=/app/config/rag_config.yaml
      - RAG_ENVIRONMENT=production
      - OPENAI_API_KEY=${OPENAI_API_KEY}

    volumes:

      - ./config:/app/config
      - ./data:/app/data
      - rag_logs:/var/log/rag

    depends_on:

      - qdrant
      - postgres
      - redis

    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2.0'
        reservations:
          memory: 2G
          cpus: '1.0'

  # Vector Database (Qdrant)
  qdrant:
    image: qdrant/qdrant:v1.3.0
    ports:

      - "6333:6333"
      - "6334:6334"

    volumes:

      - qdrant_storage:/qdrant/storage
      - ./config/qdrant_config.yaml:/qdrant/config/production.yaml

    environment:

      - QDRANT__SERVICE__HTTP_PORT=6333
      - QDRANT__SERVICE__GRPC_PORT=6334

    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 8G
          cpus: '4.0'
        reservations:
          memory: 4G
          cpus: '2.0'

  # PostgreSQL for metadata
  postgres:
    image: postgres:15
    ports:

      - "5432:5432"

    environment:

      - POSTGRES_DB=rag_metadata
      - POSTGRES_USER=rag_user
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}

    volumes:

      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init_postgres.sql:/docker-entrypoint-initdb.d/init.sql

    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'

  # Redis for caching
  redis:
    image: redis:7-alpine
    ports:

      - "6379:6379"

    command: redis-server --appendonly yes --maxmemory 1gb --maxmemory-policy allkeys-lru
    volumes:

      - redis_data:/data

    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'

  # Embedding Service
  embedding-service:
    build:
      context: .
      dockerfile: Dockerfile.embeddings
    ports:

      - "8001:8001"

    environment:

      - EMBEDDING_CONFIG_PATH=/app/config/embedding_config.yaml
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - HUGGINGFACE_API_KEY=${HUGGINGFACE_API_KEY}

    volumes:

      - ./config:/app/config
      - embedding_cache:/app/cache

    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2.0'
        reservations:
          memory: 2G
          cpus: '1.0'

  # Knowledge Ingestion Service
  ingestion-service:
    build:
      context: .
      dockerfile: Dockerfile.ingestion
    ports:

      - "8002:8002"

    environment:

      - INGESTION_CONFIG_PATH=/app/config/ingestion_config.yaml

    volumes:

      - ./config:/app/config
      - ./data/documents:/app/documents
      - ingestion_temp:/tmp/ingestion

    depends_on:

      - qdrant
      - embedding-service

    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'

  # Nginx Load Balancer
  nginx:
    image: nginx:alpine
    ports:

      - "80:80"
      - "443:443"

    volumes:

      - ./config/nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl

    depends_on:

      - rag-engine

    restart: unless-stopped

  # Monitoring (Prometheus)
  prometheus:
    image: prom/prometheus:latest
    ports:

      - "9090:9090"

    volumes:

      - ./config/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus

    command:

      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'

    restart: unless-stopped

  # Grafana for visualization
  grafana:
    image: grafana/grafana:latest
    ports:

      - "3000:3000"

    environment:

      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}

    volumes:

      - grafana_data:/var/lib/grafana
      - ./config/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./config/grafana/datasources:/etc/grafana/provisioning/datasources

    depends_on:

      - prometheus

    restart: unless-stopped

volumes:
  qdrant_storage:
  postgres_data:
  redis_data:
  embedding_cache:
  ingestion_temp:
  rag_logs:
  prometheus_data:
  grafana_data:

networks:
  default:
    driver: bridge

```text
      dockerfile: Dockerfile.rag
    ports:

      - "8000:8000"

    environment:

      - RAG_CONFIG_PATH=/app/config/rag_config.yaml
      - RAG_ENVIRONMENT=production
      - OPENAI_API_KEY=${OPENAI_API_KEY}

    volumes:

      - ./config:/app/config
      - ./data:/app/data
      - rag_logs:/var/log/rag

    depends_on:

      - qdrant
      - postgres
      - redis

    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2.0'
        reservations:
          memory: 2G
          cpus: '1.0'

  # Vector Database (Qdrant)
  qdrant:
    image: qdrant/qdrant:v1.3.0
    ports:

      - "6333:6333"
      - "6334:6334"

    volumes:

      - qdrant_storage:/qdrant/storage
      - ./config/qdrant_config.yaml:/qdrant/config/production.yaml

    environment:

      - QDRANT__SERVICE__HTTP_PORT=6333
      - QDRANT__SERVICE__GRPC_PORT=6334

    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 8G
          cpus: '4.0'
        reservations:
          memory: 4G
          cpus: '2.0'

  # PostgreSQL for metadata
  postgres:
    image: postgres:15
    ports:

      - "5432:5432"

    environment:

      - POSTGRES_DB=rag_metadata
      - POSTGRES_USER=rag_user
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}

    volumes:

      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init_postgres.sql:/docker-entrypoint-initdb.d/init.sql

    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'

  # Redis for caching
  redis:
    image: redis:7-alpine
    ports:

      - "6379:6379"

    command: redis-server --appendonly yes --maxmemory 1gb --maxmemory-policy allkeys-lru
    volumes:

      - redis_data:/data

    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'

  # Embedding Service
  embedding-service:
    build:
      context: .
      dockerfile: Dockerfile.embeddings
    ports:

      - "8001:8001"

    environment:

      - EMBEDDING_CONFIG_PATH=/app/config/embedding_config.yaml
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - HUGGINGFACE_API_KEY=${HUGGINGFACE_API_KEY}

    volumes:

      - ./config:/app/config
      - embedding_cache:/app/cache

    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2.0'
        reservations:
          memory: 2G
          cpus: '1.0'

  # Knowledge Ingestion Service
  ingestion-service:
    build:
      context: .
      dockerfile: Dockerfile.ingestion
    ports:

      - "8002:8002"

    environment:

      - INGESTION_CONFIG_PATH=/app/config/ingestion_config.yaml

    volumes:

      - ./config:/app/config
      - ./data/documents:/app/documents
      - ingestion_temp:/tmp/ingestion

    depends_on:

      - qdrant
      - embedding-service

    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'

  # Nginx Load Balancer
  nginx:
    image: nginx:alpine
    ports:

      - "80:80"
      - "443:443"

    volumes:

      - ./config/nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl

    depends_on:

      - rag-engine

    restart: unless-stopped

  # Monitoring (Prometheus)
  prometheus:
    image: prom/prometheus:latest
    ports:

      - "9090:9090"

    volumes:

      - ./config/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus

    command:

      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'

    restart: unless-stopped

  # Grafana for visualization
  grafana:
    image: grafana/grafana:latest
    ports:

      - "3000:3000"

    environment:

      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}

    volumes:

      - grafana_data:/var/lib/grafana
      - ./config/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./config/grafana/datasources:/etc/grafana/provisioning/datasources

    depends_on:

      - prometheus

    restart: unless-stopped

volumes:
  qdrant_storage:
  postgres_data:
  redis_data:
  embedding_cache:
  ingestion_temp:
  rag_logs:
  prometheus_data:
  grafana_data:

networks:
  default:
    driver: bridge

```text

### Dockerfiles

* *Main RAG Engine Dockerfile**:

```dockerfile
```dockerfile

```dockerfile
```dockerfile

## Dockerfile.rag

FROM python:3.11-slim

WORKDIR /app

## Install system dependencies

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

## Copy requirements

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

## Copy application code

COPY src/ ./src/
COPY config/ ./config/
COPY scripts/ ./scripts/

## Create necessary directories

RUN mkdir -p /var/log/rag /app/data /app/cache

## Set environment variables

ENV PYTHONPATH=/app/src
ENV RAG_CONFIG_PATH=/app/config/rag_config.yaml

## Health check

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

## Expose port

EXPOSE 8000

## Run the application

CMD ["python", "-m", "consciousness_v2.rag.main"]
```text

WORKDIR /app

## Install system dependencies

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

## Copy requirements

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

## Copy application code

COPY src/ ./src/
COPY config/ ./config/
COPY scripts/ ./scripts/

## Create necessary directories

RUN mkdir -p /var/log/rag /app/data /app/cache

## Set environment variables

ENV PYTHONPATH=/app/src
ENV RAG_CONFIG_PATH=/app/config/rag_config.yaml

## Health check

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

## Expose port

EXPOSE 8000

## Run the application

CMD ["python", "-m", "consciousness_v2.rag.main"]

```text
WORKDIR /app

## Install system dependencies

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

## Copy requirements

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

## Copy application code

COPY src/ ./src/
COPY config/ ./config/
COPY scripts/ ./scripts/

## Create necessary directories

RUN mkdir -p /var/log/rag /app/data /app/cache

## Set environment variables

ENV PYTHONPATH=/app/src
ENV RAG_CONFIG_PATH=/app/config/rag_config.yaml

## Health check

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

## Expose port

EXPOSE 8000

## Run the application

CMD ["python", "-m", "consciousness_v2.rag.main"]

```text
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

## Copy requirements

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

## Copy application code

COPY src/ ./src/
COPY config/ ./config/
COPY scripts/ ./scripts/

## Create necessary directories

RUN mkdir -p /var/log/rag /app/data /app/cache

## Set environment variables

ENV PYTHONPATH=/app/src
ENV RAG_CONFIG_PATH=/app/config/rag_config.yaml

## Health check

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

## Expose port

EXPOSE 8000

## Run the application

CMD ["python", "-m", "consciousness_v2.rag.main"]

```text

* *Embedding Service Dockerfile**:

```dockerfile
```dockerfile

```dockerfile
```dockerfile

## Dockerfile.embeddings

FROM python:3.11-slim

WORKDIR /app

## Install system dependencies

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

## Copy requirements

COPY requirements-embeddings.txt .
RUN pip install --no-cache-dir -r requirements-embeddings.txt

## Copy embedding service code

COPY src/consciousness_v2/rag/embeddings/ ./embeddings/
COPY config/ ./config/

## Create cache directory

RUN mkdir -p /app/cache

## Set environment variables

ENV PYTHONPATH=/app
ENV EMBEDDING_CONFIG_PATH=/app/config/embedding_config.yaml

## Health check

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

## Expose port

EXPOSE 8001

## Run the embedding service

CMD ["python", "-m", "embeddings.service"]
```text

WORKDIR /app

## Install system dependencies

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

## Copy requirements

COPY requirements-embeddings.txt .
RUN pip install --no-cache-dir -r requirements-embeddings.txt

## Copy embedding service code

COPY src/consciousness_v2/rag/embeddings/ ./embeddings/
COPY config/ ./config/

## Create cache directory

RUN mkdir -p /app/cache

## Set environment variables

ENV PYTHONPATH=/app
ENV EMBEDDING_CONFIG_PATH=/app/config/embedding_config.yaml

## Health check

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

## Expose port

EXPOSE 8001

## Run the embedding service

CMD ["python", "-m", "embeddings.service"]

```text
WORKDIR /app

## Install system dependencies

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

## Copy requirements

COPY requirements-embeddings.txt .
RUN pip install --no-cache-dir -r requirements-embeddings.txt

## Copy embedding service code

COPY src/consciousness_v2/rag/embeddings/ ./embeddings/
COPY config/ ./config/

## Create cache directory

RUN mkdir -p /app/cache

## Set environment variables

ENV PYTHONPATH=/app
ENV EMBEDDING_CONFIG_PATH=/app/config/embedding_config.yaml

## Health check

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

## Expose port

EXPOSE 8001

## Run the embedding service

CMD ["python", "-m", "embeddings.service"]

```text
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

## Copy requirements

COPY requirements-embeddings.txt .
RUN pip install --no-cache-dir -r requirements-embeddings.txt

## Copy embedding service code

COPY src/consciousness_v2/rag/embeddings/ ./embeddings/
COPY config/ ./config/

## Create cache directory

RUN mkdir -p /app/cache

## Set environment variables

ENV PYTHONPATH=/app
ENV EMBEDDING_CONFIG_PATH=/app/config/embedding_config.yaml

## Health check

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

## Expose port

EXPOSE 8001

## Run the embedding service

CMD ["python", "-m", "embeddings.service"]

```text

- --

## Kubernetes Deployment

### Kubernetes Manifests

* *Namespace**:

```yaml
### Kubernetes Manifests

* *Namespace**:

```yaml

### Kubernetes Manifests

* *Namespace**:

```yaml
```yaml

## k8s/namespace.yaml

apiVersion: v1
kind: Namespace
metadata:
  name: rag-system
  labels:
    name: rag-system
```text

metadata:
  name: rag-system
  labels:
    name: rag-system

```text
metadata:
  name: rag-system
  labels:
    name: rag-system

```text
```text

* *ConfigMap**:

```yaml
```yaml

```yaml
```yaml

## k8s/configmap.yaml

apiVersion: v1
kind: ConfigMap
metadata:
  name: rag-config
  namespace: rag-system
data:
  rag_config.yaml: |
    system:
      name: "Consciousness-Aware RAG System"
      version: "1.0.0"
      environment: "production"
      log_level: "INFO"

    vector_database:
      provider: "qdrant"
      host: "qdrant-service"
      port: 6333
      timeout_seconds: 30.0
      max_connections: 50

    embedding_service:
      provider: "openai"
      model_name: "text-embedding-ada-002"
      batch_size: 32
      timeout_seconds: 30.0

    # ... rest of configuration
```text

metadata:
  name: rag-config
  namespace: rag-system
data:
  rag_config.yaml: |
    system:
      name: "Consciousness-Aware RAG System"
      version: "1.0.0"
      environment: "production"
      log_level: "INFO"

    vector_database:
      provider: "qdrant"
      host: "qdrant-service"
      port: 6333
      timeout_seconds: 30.0
      max_connections: 50

    embedding_service:
      provider: "openai"
      model_name: "text-embedding-ada-002"
      batch_size: 32
      timeout_seconds: 30.0

    # ... rest of configuration

```text
metadata:
  name: rag-config
  namespace: rag-system
data:
  rag_config.yaml: |
    system:
      name: "Consciousness-Aware RAG System"
      version: "1.0.0"
      environment: "production"
      log_level: "INFO"

    vector_database:
      provider: "qdrant"
      host: "qdrant-service"
      port: 6333
      timeout_seconds: 30.0
      max_connections: 50

    embedding_service:
      provider: "openai"
      model_name: "text-embedding-ada-002"
      batch_size: 32
      timeout_seconds: 30.0

    # ... rest of configuration

```text
    system:
      name: "Consciousness-Aware RAG System"
      version: "1.0.0"
      environment: "production"
      log_level: "INFO"

    vector_database:
      provider: "qdrant"
      host: "qdrant-service"
      port: 6333
      timeout_seconds: 30.0
      max_connections: 50

    embedding_service:
      provider: "openai"
      model_name: "text-embedding-ada-002"
      batch_size: 32
      timeout_seconds: 30.0

    # ... rest of configuration

```text

* *Secrets**:

```yaml
```yaml

```yaml
```yaml

## k8s/secrets.yaml

apiVersion: v1
kind: Secret
metadata:
  name: rag-secrets
  namespace: rag-system
type: Opaque
data:
  openai-api-key: <base64-encoded-key>
  postgres-password: <base64-encoded-password>
  grafana-password: <base64-encoded-password>
```text

metadata:
  name: rag-secrets
  namespace: rag-system
type: Opaque
data:
  openai-api-key: <base64-encoded-key>
  postgres-password: <base64-encoded-password>
  grafana-password: <base64-encoded-password>

```text
metadata:
  name: rag-secrets
  namespace: rag-system
type: Opaque
data:
  openai-api-key: <base64-encoded-key>
  postgres-password: <base64-encoded-password>
  grafana-password: <base64-encoded-password>

```text
  openai-api-key: <base64-encoded-key>
  postgres-password: <base64-encoded-password>
  grafana-password: <base64-encoded-password>

```text

* *RAG Engine Deployment**:

```yaml
```yaml

```yaml
```yaml

## k8s/rag-engine-deployment.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: rag-engine
  namespace: rag-system
  labels:
    app: rag-engine
spec:
  replicas: 3
  selector:
    matchLabels:
      app: rag-engine
  template:
    metadata:
      labels:
        app: rag-engine
    spec:
      containers:

      - name: rag-engine

        image: synapticos/rag-engine:1.0.0
        ports:

        - containerPort: 8000

        env:

        - name: RAG_CONFIG_PATH

          value: "/app/config/rag_config.yaml"

        - name: OPENAI_API_KEY

          valueFrom:
            secretKeyRef:
              name: rag-secrets
              key: openai-api-key
        volumeMounts:

        - name: config-volume

          mountPath: /app/config

        - name: data-volume

          mountPath: /app/data
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:

      - name: config-volume

        configMap:
          name: rag-config

      - name: data-volume

        persistentVolumeClaim:
          claimName: rag-data-pvc

- --

apiVersion: v1
kind: Service
metadata:
  name: rag-engine-service
  namespace: rag-system
spec:
  selector:
    app: rag-engine
  ports:

  - protocol: TCP

    port: 8000
    targetPort: 8000
  type: ClusterIP
```text

metadata:
  name: rag-engine
  namespace: rag-system
  labels:
    app: rag-engine
spec:
  replicas: 3
  selector:
    matchLabels:
      app: rag-engine
  template:
    metadata:
      labels:
        app: rag-engine
    spec:
      containers:

      - name: rag-engine

        image: synapticos/rag-engine:1.0.0
        ports:

        - containerPort: 8000

        env:

        - name: RAG_CONFIG_PATH

          value: "/app/config/rag_config.yaml"

        - name: OPENAI_API_KEY

          valueFrom:
            secretKeyRef:
              name: rag-secrets
              key: openai-api-key
        volumeMounts:

        - name: config-volume

          mountPath: /app/config

        - name: data-volume

          mountPath: /app/data
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:

      - name: config-volume

        configMap:
          name: rag-config

      - name: data-volume

        persistentVolumeClaim:
          claimName: rag-data-pvc

- --

apiVersion: v1
kind: Service
metadata:
  name: rag-engine-service
  namespace: rag-system
spec:
  selector:
    app: rag-engine
  ports:

  - protocol: TCP

    port: 8000
    targetPort: 8000
  type: ClusterIP

```text
metadata:
  name: rag-engine
  namespace: rag-system
  labels:
    app: rag-engine
spec:
  replicas: 3
  selector:
    matchLabels:
      app: rag-engine
  template:
    metadata:
      labels:
        app: rag-engine
    spec:
      containers:

      - name: rag-engine

        image: synapticos/rag-engine:1.0.0
        ports:

        - containerPort: 8000

        env:

        - name: RAG_CONFIG_PATH

          value: "/app/config/rag_config.yaml"

        - name: OPENAI_API_KEY

          valueFrom:
            secretKeyRef:
              name: rag-secrets
              key: openai-api-key
        volumeMounts:

        - name: config-volume

          mountPath: /app/config

        - name: data-volume

          mountPath: /app/data
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:

      - name: config-volume

        configMap:
          name: rag-config

      - name: data-volume

        persistentVolumeClaim:
          claimName: rag-data-pvc

- --

apiVersion: v1
kind: Service
metadata:
  name: rag-engine-service
  namespace: rag-system
spec:
  selector:
    app: rag-engine
  ports:

  - protocol: TCP

    port: 8000
    targetPort: 8000
  type: ClusterIP

```text
spec:
  replicas: 3
  selector:
    matchLabels:
      app: rag-engine
  template:
    metadata:
      labels:
        app: rag-engine
    spec:
      containers:

      - name: rag-engine

        image: synapticos/rag-engine:1.0.0
        ports:

        - containerPort: 8000

        env:

        - name: RAG_CONFIG_PATH

          value: "/app/config/rag_config.yaml"

        - name: OPENAI_API_KEY

          valueFrom:
            secretKeyRef:
              name: rag-secrets
              key: openai-api-key
        volumeMounts:

        - name: config-volume

          mountPath: /app/config

        - name: data-volume

          mountPath: /app/data
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:

      - name: config-volume

        configMap:
          name: rag-config

      - name: data-volume

        persistentVolumeClaim:
          claimName: rag-data-pvc

- --

apiVersion: v1
kind: Service
metadata:
  name: rag-engine-service
  namespace: rag-system
spec:
  selector:
    app: rag-engine
  ports:

  - protocol: TCP

    port: 8000
    targetPort: 8000
  type: ClusterIP

```text

* *Qdrant Deployment**:

```yaml
```yaml

```yaml
```yaml

## k8s/qdrant-deployment.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: qdrant
  namespace: rag-system
spec:
  replicas: 1
  selector:
    matchLabels:
      app: qdrant
  template:
    metadata:
      labels:
        app: qdrant
    spec:
      containers:

      - name: qdrant

        image: qdrant/qdrant:v1.3.0
        ports:

        - containerPort: 6333
        - containerPort: 6334

        env:

        - name: QDRANT__SERVICE__HTTP_PORT

          value: "6333"

        - name: QDRANT__SERVICE__GRPC_PORT

          value: "6334"
        volumeMounts:

        - name: qdrant-storage

          mountPath: /qdrant/storage
        resources:
          requests:
            memory: "4Gi"
            cpu: "2000m"
          limits:
            memory: "8Gi"
            cpu: "4000m"
      volumes:

      - name: qdrant-storage

        persistentVolumeClaim:
          claimName: qdrant-storage-pvc

- --

apiVersion: v1
kind: Service
metadata:
  name: qdrant-service
  namespace: rag-system
spec:
  selector:
    app: qdrant
  ports:

  - name: http

    protocol: TCP
    port: 6333
    targetPort: 6333

  - name: grpc

    protocol: TCP
    port: 6334
    targetPort: 6334
  type: ClusterIP
```text

metadata:
  name: qdrant
  namespace: rag-system
spec:
  replicas: 1
  selector:
    matchLabels:
      app: qdrant
  template:
    metadata:
      labels:
        app: qdrant
    spec:
      containers:

      - name: qdrant

        image: qdrant/qdrant:v1.3.0
        ports:

        - containerPort: 6333
        - containerPort: 6334

        env:

        - name: QDRANT__SERVICE__HTTP_PORT

          value: "6333"

        - name: QDRANT__SERVICE__GRPC_PORT

          value: "6334"
        volumeMounts:

        - name: qdrant-storage

          mountPath: /qdrant/storage
        resources:
          requests:
            memory: "4Gi"
            cpu: "2000m"
          limits:
            memory: "8Gi"
            cpu: "4000m"
      volumes:

      - name: qdrant-storage

        persistentVolumeClaim:
          claimName: qdrant-storage-pvc

- --

apiVersion: v1
kind: Service
metadata:
  name: qdrant-service
  namespace: rag-system
spec:
  selector:
    app: qdrant
  ports:

  - name: http

    protocol: TCP
    port: 6333
    targetPort: 6333

  - name: grpc

    protocol: TCP
    port: 6334
    targetPort: 6334
  type: ClusterIP

```text
metadata:
  name: qdrant
  namespace: rag-system
spec:
  replicas: 1
  selector:
    matchLabels:
      app: qdrant
  template:
    metadata:
      labels:
        app: qdrant
    spec:
      containers:

      - name: qdrant

        image: qdrant/qdrant:v1.3.0
        ports:

        - containerPort: 6333
        - containerPort: 6334

        env:

        - name: QDRANT__SERVICE__HTTP_PORT

          value: "6333"

        - name: QDRANT__SERVICE__GRPC_PORT

          value: "6334"
        volumeMounts:

        - name: qdrant-storage

          mountPath: /qdrant/storage
        resources:
          requests:
            memory: "4Gi"
            cpu: "2000m"
          limits:
            memory: "8Gi"
            cpu: "4000m"
      volumes:

      - name: qdrant-storage

        persistentVolumeClaim:
          claimName: qdrant-storage-pvc

- --

apiVersion: v1
kind: Service
metadata:
  name: qdrant-service
  namespace: rag-system
spec:
  selector:
    app: qdrant
  ports:

  - name: http

    protocol: TCP
    port: 6333
    targetPort: 6333

  - name: grpc

    protocol: TCP
    port: 6334
    targetPort: 6334
  type: ClusterIP

```text
  selector:
    matchLabels:
      app: qdrant
  template:
    metadata:
      labels:
        app: qdrant
    spec:
      containers:

      - name: qdrant

        image: qdrant/qdrant:v1.3.0
        ports:

        - containerPort: 6333
        - containerPort: 6334

        env:

        - name: QDRANT__SERVICE__HTTP_PORT

          value: "6333"

        - name: QDRANT__SERVICE__GRPC_PORT

          value: "6334"
        volumeMounts:

        - name: qdrant-storage

          mountPath: /qdrant/storage
        resources:
          requests:
            memory: "4Gi"
            cpu: "2000m"
          limits:
            memory: "8Gi"
            cpu: "4000m"
      volumes:

      - name: qdrant-storage

        persistentVolumeClaim:
          claimName: qdrant-storage-pvc

- --

apiVersion: v1
kind: Service
metadata:
  name: qdrant-service
  namespace: rag-system
spec:
  selector:
    app: qdrant
  ports:

  - name: http

    protocol: TCP
    port: 6333
    targetPort: 6333

  - name: grpc

    protocol: TCP
    port: 6334
    targetPort: 6334
  type: ClusterIP

```text

* *Persistent Volume Claims**:

```yaml
```yaml

```yaml
```yaml

## k8s/pvc.yaml

apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: qdrant-storage-pvc
  namespace: rag-system
spec:
  accessModes:

    - ReadWriteOnce

  resources:
    requests:
      storage: 100Gi
  storageClassName: fast-ssd

- --

apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: rag-data-pvc
  namespace: rag-system
spec:
  accessModes:

    - ReadWriteMany

  resources:
    requests:
      storage: 50Gi
  storageClassName: shared-storage
```text

metadata:
  name: qdrant-storage-pvc
  namespace: rag-system
spec:
  accessModes:

    - ReadWriteOnce

  resources:
    requests:
      storage: 100Gi
  storageClassName: fast-ssd

- --

apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: rag-data-pvc
  namespace: rag-system
spec:
  accessModes:

    - ReadWriteMany

  resources:
    requests:
      storage: 50Gi
  storageClassName: shared-storage

```text
metadata:
  name: qdrant-storage-pvc
  namespace: rag-system
spec:
  accessModes:

    - ReadWriteOnce

  resources:
    requests:
      storage: 100Gi
  storageClassName: fast-ssd

- --

apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: rag-data-pvc
  namespace: rag-system
spec:
  accessModes:

    - ReadWriteMany

  resources:
    requests:
      storage: 50Gi
  storageClassName: shared-storage

```text

    - ReadWriteOnce

  resources:
    requests:
      storage: 100Gi
  storageClassName: fast-ssd

- --

apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: rag-data-pvc
  namespace: rag-system
spec:
  accessModes:

    - ReadWriteMany

  resources:
    requests:
      storage: 50Gi
  storageClassName: shared-storage

```text

* *Horizontal Pod Autoscaler**:

```yaml
```yaml

```yaml
```yaml

## k8s/hpa.yaml

apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: rag-engine-hpa
  namespace: rag-system
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: rag-engine
  minReplicas: 3
  maxReplicas: 20
  metrics:

  - type: Resource

    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70

  - type: Resource

    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:

      - type: Percent

        value: 10
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:

      - type: Percent

        value: 50
        periodSeconds: 60
```text

metadata:
  name: rag-engine-hpa
  namespace: rag-system
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: rag-engine
  minReplicas: 3
  maxReplicas: 20
  metrics:

  - type: Resource

    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70

  - type: Resource

    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:

      - type: Percent

        value: 10
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:

      - type: Percent

        value: 50
        periodSeconds: 60

```text
metadata:
  name: rag-engine-hpa
  namespace: rag-system
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: rag-engine
  minReplicas: 3
  maxReplicas: 20
  metrics:

  - type: Resource

    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70

  - type: Resource

    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:

      - type: Percent

        value: 10
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:

      - type: Percent

        value: 50
        periodSeconds: 60

```text
    apiVersion: apps/v1
    kind: Deployment
    name: rag-engine
  minReplicas: 3
  maxReplicas: 20
  metrics:

  - type: Resource

    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70

  - type: Resource

    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:

      - type: Percent

        value: 10
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:

      - type: Percent

        value: 50
        periodSeconds: 60

```text

- --

## Monitoring and Observability

### Prometheus Configuration

```yaml
### Prometheus Configuration

```yaml

### Prometheus Configuration

```yaml
```yaml

## config/prometheus.yml

global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:

  - "rag_alerts.yml"

scrape_configs:

  - job_name: 'rag-engine'

    static_configs:

      - targets: ['rag-engine:8000']

    metrics_path: '/metrics'
    scrape_interval: 10s

  - job_name: 'qdrant'

    static_configs:

      - targets: ['qdrant:6333']

    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'embedding-service'

    static_configs:

      - targets: ['embedding-service:8001']

    metrics_path: '/metrics'
  evaluation_interval: 15s

rule_files:

  - "rag_alerts.yml"

scrape_configs:

  - job_name: 'rag-engine'

    static_configs:

      - targets: ['rag-engine:8000']

    metrics_path: '/metrics'
    scrape_interval: 10s

  - job_name: 'qdrant'

    static_configs:

      - targets: ['qdrant:6333']

    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'embedding-service'

    static_configs:

      - targets: ['embedding-service:8001']

    metrics_path: '/metrics'
  evaluation_interval: 15s

rule_files:

  - "rag_alerts.yml"

scrape_configs:

  - job_name: 'rag-engine'

    static_configs:

      - targets: ['rag-engine:8000']

    metrics_path: '/metrics'
    scrape_interval: 10s

  - job_name: 'qdrant'

    static_configs:

      - targets: ['qdrant:6333']

    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'embedding-service'

    static_configs:

      - targets: ['embedding-service:8001']

    metrics_path: '/metrics'
  evaluation_interval: 15s

rule_files:

  - "rag_alerts.yml"

scrape_configs:

  - job_name: 'rag-engine'

    static_configs:

      - targets: ['rag-engine:8000']

    metrics_path: '/metrics'
    scrape_interval: 10s

  - job_name: 'qdrant'

    static_configs:

      - targets: ['qdrant:6333']

    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'embedding-service'

    static_configs:

      - targets: ['embedding-service:8001']

    metrics_path: '/metrics'