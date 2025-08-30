FROM kong:3.4-alpine

# Install custom plugins
USER root
RUN apk add --no-cache git gcc musl-dev

# Copy custom plugins
COPY plugins/ /usr/local/share/lua/5.1/kong/plugins/

# Copy configuration
COPY config/ /kong/declarative/

USER kong