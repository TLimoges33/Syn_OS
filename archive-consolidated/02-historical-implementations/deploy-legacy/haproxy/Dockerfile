FROM haproxy:2.8-alpine

# Install additional tools for health checks and monitoring
RUN apk add --no-cache \
    curl \
    bash \
    openssl

# Create directories for certificates and configurations
RUN mkdir -p /usr/local/etc/haproxy/certs \
    && mkdir -p /var/log/haproxy \
    && touch /var/log/haproxy/haproxy.log

# Copy HAProxy configuration
COPY haproxy.cfg /usr/local/etc/haproxy/haproxy.cfg

# Copy health check script
COPY scripts/health-check.sh /usr/local/bin/health-check.sh
RUN chmod +x /usr/local/bin/health-check.sh

# Create haproxy user and group if they don't exist
RUN addgroup -g 99 -S haproxy || true \
    && adduser -S -D -H -u 99 -s /sbin/nologin -G haproxy haproxy || true

# Set proper permissions
RUN chown -R haproxy:haproxy /var/log/haproxy \
    && chown -R haproxy:haproxy /usr/local/etc/haproxy

# Expose ports
EXPOSE 80 443 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD /usr/local/bin/health-check.sh

# Run as non-root user
USER haproxy

# Start HAProxy
CMD ["haproxy", "-f", "/usr/local/etc/haproxy/haproxy.cfg", "-db"]
