# SynOS Monitoring System

This directory contains the performance monitoring and metrics collection system for SynOS.

## Components

### `performance_monitor.py`
Core monitoring module that:
- Collects system metrics (CPU, memory, disk, network)
- Monitors consciousness, security, and kernel components
- Exposes Prometheus metrics
- Generates health reports

### `metrics_server.py`
FastAPI server that exposes:
- `/metrics` - Prometheus metrics endpoint
- `/health` - Basic health check
- `/health/detailed` - Comprehensive health report
- `/status` - Current system status
- Component-specific endpoints

### Key Features

1. **Comprehensive Metrics Collection**
   - System resources (CPU, memory, disk, network)
   - Component-specific metrics (consciousness, security, kernel)
   - Performance timings and error rates
   - Health scoring algorithm

2. **Prometheus Integration**
   - Standard Prometheus metrics format
   - Custom metrics for SynOS components
   - Histogram tracking for operation durations
   - Counter tracking for events and operations

3. **Health Monitoring**
   - Overall system health score (0-100)
   - Component health tracking
   - Automatic degradation detection
   - Historical performance analysis

4. **Performance Decorators**
   - `@monitor_consciousness_operation` - Auto-track consciousness operations
   - `@monitor_security_scan` - Auto-track security scans
   - Automatic error detection and reporting

## Usage

### Starting the Metrics Server

```bash
# Install dependencies
pip install -r requirements.txt

# Start the server
python metrics_server.py
```

The server will start on port 9090 and begin collecting metrics.

### Using in Code

```python
from monitoring.performance_monitor import monitor_consciousness_operation, get_monitor

@monitor_consciousness_operation("pattern_analysis")
async def analyze_pattern(data):
    # Your consciousness operation here
    pass

# Manual metric recording
monitor = get_monitor()
monitor.consciousness_monitor.record_operation("custom_op", 1.5, True)
```

### Prometheus Integration

Add to your `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'synos-metrics'
    static_configs:
      - targets: ['localhost:9090']
    metrics_path: '/metrics'
    scrape_interval: 30s
```

### API Endpoints

- `GET /health` - Basic health check
- `GET /metrics` - Prometheus metrics
- `GET /health/detailed` - Full health report
- `GET /status` - Current status
- `GET /components/consciousness` - Consciousness metrics
- `GET /components/security` - Security metrics
- `GET /components/kernel` - Kernel metrics
- `POST /consciousness/operation` - Record operation
- `POST /security/event` - Record security event

### Health Scoring

The system calculates a health score (0-100) based on:
- CPU usage (20% weight)
- Memory usage (20% weight)
- Consciousness health (30% weight)
- Security health (20% weight)
- Kernel health (10% weight)

Scores:
- 80-100: Healthy
- 60-79: Degraded
- 0-59: Critical

## Integration with SynOS Components

The monitoring system is designed to integrate with:
- Consciousness processing modules
- Security scanning systems
- Kernel operations
- Service orchestration

Each component can use decorators or direct API calls to report metrics.

## Docker Integration

The monitoring system can be deployed as a container and integrated with the SynOS docker-compose setup for comprehensive observability.
