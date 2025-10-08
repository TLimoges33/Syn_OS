# SynOS Service Orchestrator

A lightweight Go-based service orchestrator for SynOS microservices architecture.

## Overview

The Service Orchestrator manages the lifecycle of SynOS services, providing:

- Service registration and discovery
- Health monitoring and recovery
- Load balancing and routing
- Configuration management
- Security and authentication

## Features

- **Service Management**: Register, start, stop, and monitor services
- **Health Checks**: Automated health monitoring with recovery
- **Load Balancing**: Distribute requests across service instances
- **Configuration**: Centralized configuration management
- **Security**: JWT authentication and API key management
- **Metrics**: Performance monitoring and metrics collection

## Quick Start

### Prerequisites

- Go 1.21+
- Docker and Docker Compose
- NATS server
- PostgreSQL database
- Redis cache

### Development

```bash
# Build the orchestrator
go build -o orchestrator cmd/main.go

# Run with development configuration
./orchestrator --config config/development.yaml

# Or use Docker
docker build -t synos-orchestrator .
docker run -p 8080:8080 synos-orchestrator
```

### Configuration

Environment variables:

- `ENV`: Environment (development/production)
- `HTTP_PORT`: HTTP server port (default: 8080)
- `NATS_URL`: NATS server URL
- `POSTGRES_HOST`: Database host
- `REDIS_HOST`: Cache host
- `LOG_LEVEL`: Logging level (debug/info/warn/error)

## API Endpoints

### Service Management

- `POST /api/v1/services` - Register service
- `GET /api/v1/services` - List services
- `GET /api/v1/services/{id}` - Get service
- `PUT /api/v1/services/{id}` - Update service
- `DELETE /api/v1/services/{id}` - Unregister service

### Service Control

- `POST /api/v1/services/{id}/start` - Start service
- `POST /api/v1/services/{id}/stop` - Stop service
- `POST /api/v1/services/{id}/restart` - Restart service

### Health and Monitoring

- `GET /health` - Orchestrator health
- `GET /api/v1/services/{id}/health` - Service health
- `GET /api/v1/metrics` - System metrics

## License

MIT License - See LICENSE file for details.
