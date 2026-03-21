# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Build arguments for environment variables with defaults
ARG VITE_INFERENCE_SERVER_ADDRESS=http://127.0.0.1:3000
ARG VITE_ENTRIES_SERVER_ADDRESS=http://127.0.0.1:8884
ARG VITE_BINARY_THRESHOLD=0.5
ARG VITE_AUTH_URL=
ARG VITE_AUTH_REALM=
ARG VITE_AUTH_CLIENT_ID=
ARG VITE_PREVIEW_N_RECENT=10
ARG VITE_PREVIEW_ICON_SIZE=100
ARG VITE_PREVIEW_ICON_MARGIN=10
ARG VITE_PREVIEW_ICON_BORDER=8
ARG VITE_PREVIEW_CAROUSEL_SPEED_SEC=10
ARG VITE_ENTRIES_N_RECENT=5

# Set environment variables for build
ENV VITE_INFERENCE_SERVER_ADDRESS=${VITE_INFERENCE_SERVER_ADDRESS}
ENV VITE_ENTRIES_SERVER_ADDRESS=${VITE_ENTRIES_SERVER_ADDRESS}
ENV VITE_BINARY_THRESHOLD=${VITE_BINARY_THRESHOLD}
ENV VITE_AUTH_URL=${VITE_AUTH_URL}
ENV VITE_AUTH_REALM=${VITE_AUTH_REALM}
ENV VITE_AUTH_CLIENT_ID=${VITE_AUTH_CLIENT_ID}
ENV VITE_PREVIEW_N_RECENT=${VITE_PREVIEW_N_RECENT}
ENV VITE_PREVIEW_ICON_SIZE=${VITE_PREVIEW_ICON_SIZE}
ENV VITE_PREVIEW_ICON_MARGIN=${VITE_PREVIEW_ICON_MARGIN}
ENV VITE_PREVIEW_ICON_BORDER=${VITE_PREVIEW_ICON_BORDER}
ENV VITE_PREVIEW_CAROUSEL_SPEED_SEC=${VITE_PREVIEW_CAROUSEL_SPEED_SEC}
ENV VITE_ENTRIES_N_RECENT=${VITE_ENTRIES_N_RECENT}

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
# Use npm ci for fast, reproducible builds when package-lock.json exists.
# Without it, npm install resolves the full tree from scratch and can take several minutes.
RUN if [ -f package-lock.json ]; then \
        npm ci; \
    else \
        echo "WARNING: package-lock.json not found. Using npm install. Run 'npm install' locally and commit package-lock.json for faster, reproducible builds."; \
        npm install; \
    fi

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Install wget for health check
RUN apk add --no-cache wget

# Copy built files from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy markdown files
COPY --from=builder /app/public/markdown /usr/share/nginx/html/markdown

# Copy silent-check-sso.html for Keycloak
COPY --from=builder /app/public/silent-check-sso.html /usr/share/nginx/html/silent-check-sso.html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 4452

# Health check (using wget which is available in nginx:alpine)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:4452/health || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]

