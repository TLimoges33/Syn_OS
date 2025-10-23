# 🐳 Docker Deployment Guide

**For**: DevOps, Container Enthusiasts  
**Prerequisites**: Docker, docker-compose

Run SynOS in Docker containers for development and production.

---

## Quick Start

```bash
# Pull image
docker pull synos/synos:latest

# Run container
docker run -d \
  --name synos \
  -p 8080:80 \
  -p 8443:443 \
  -v synos-data:/var/lib/synos \
  synos/synos:latest

# Access
http://localhost:8080
```

---

## Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  synos:
    image: synos/synos:latest
    container_name: synos
    restart: unless-stopped
    ports:
      - "8080:80"
      - "8443:443"
    environment:
      - SYNOS_DB_HOST=postgres
      - SYNOS_DB_PASSWORD=changeme
      - SYNOS_REDIS_HOST=redis
    volumes:
      - synos-data:/var/lib/synos
      - synos-config:/etc/synos
    depends_on:
      - postgres
      - redis
    networks:
      - synos-net
  
  postgres:
    image: postgres:14
    container_name: synos-db
    restart: unless-stopped
    environment:
      - POSTGRES_DB=synos
      - POSTGRES_USER=synos
      - POSTGRES_PASSWORD=changeme
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - synos-net
  
  redis:
    image: redis:7
    container_name: synos-redis
    restart: unless-stopped
    volumes:
      - redis-data:/data
    networks:
      - synos-net

volumes:
  synos-data:
  synos-config:
  postgres-data:
  redis-data:

networks:
  synos-net:
    driver: bridge
```

### Start Services

```bash
docker-compose up -d
docker-compose logs -f synos
docker-compose ps
```

---

## Custom Images

### Dockerfile

```dockerfile
FROM synos/base:latest

# Install additional tools
RUN synpkg install nmap metasploit-framework

# Copy custom scripts
COPY scripts/ /opt/synos/scripts/

# Configure
COPY config.yml /etc/synos/config.yml

# Expose ports
EXPOSE 80 443

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost/health || exit 1

CMD ["synos-server", "start"]
```

### Build

```bash
docker build -t mycompany/synos:custom .
docker push mycompany/synos:custom
```

---

## Production Stack

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - synos1
      - synos2
  
  synos1:
    image: synos/synos:latest
    environment:
      - INSTANCE_ID=1
    volumes:
      - synos1-data:/var/lib/synos
  
  synos2:
    image: synos/synos:latest
    environment:
      - INSTANCE_ID=2
    volumes:
      - synos2-data:/var/lib/synos
```

---

## Container Management

```bash
# View logs
docker logs synos -f

# Execute commands
docker exec -it synos bash
docker exec synos synos-cli scan --target example.com

# Restart
docker restart synos

# Stop
docker stop synos

# Remove
docker rm synos

# Prune
docker system prune -a
```

---

## Data Persistence

```bash
# Backup volume
docker run --rm \
  -v synos-data:/data \
  -v $(pwd):/backup \
  ubuntu tar czf /backup/synos-backup.tar.gz /data

# Restore volume
docker run --rm \
  -v synos-data:/data \
  -v $(pwd):/backup \
  ubuntu tar xzf /backup/synos-backup.tar.gz -C /
```

---

**Last Updated**: October 4, 2025
