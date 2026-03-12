# Eurygaster Webpage v2 - TypeScript Frontend

This is the new TypeScript-based frontend for the Eurygaster Recognition application. It replaces the Streamlit-based
frontend (v1) with a modern React + TypeScript implementation while maintaining full compatibility with existing backend
services.

## Features

- **Modern UI**: Built with React 18, TypeScript, and Tailwind CSS
- **Type Safety**: Full TypeScript implementation for better code quality
- **Responsive Design**: Mobile-friendly interface with adaptive layouts
- **Multi-language Support**: English and Russian (EN/RU)
- **Keycloak Authentication**: Seamless integration with existing auth system
- **Image Classification**: Full support for binary and multiclass Eurygaster recognition
- **Data Visualization**: Interactive charts using Recharts
- **Performance**: Optimized build with Vite for fast loading times

## Technology Stack

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Routing**: React Router DOM
- **Charts**: Recharts
- **Markdown**: React Markdown
- **HTTP Client**: Axios
- **Authentication**: Keycloak JS
- **Icons**: Lucide React

## Project Structure

```
webpage_v2/
├── src/
│   ├── components/       # Reusable UI components
│   ├── contexts/         # React contexts (Auth, Language)
│   ├── pages/            # Page components
│   ├── services/         # API services
│   ├── translations/     # Translation files
│   ├── types/            # TypeScript type definitions
│   ├── utils/            # Utility functions
│   ├── config/           # Configuration
│   ├── App.tsx           # Main app component
│   └── main.tsx          # Entry point
├── public/
│   └── markdown/         # Markdown content files (EN/RU)
├── Dockerfile            # Docker build configuration
├── nginx.conf            # Nginx server configuration
├── package.json          # Dependencies and scripts
└── vite.config.ts        # Vite configuration
```

## Environment Variables

The application uses environment variables for configuration. Create a `.env` file based on `.env.example`:

| Variable                          | Description                     | Default                 |
|-----------------------------------|---------------------------------|-------------------------|
| `VITE_INFERENCE_SERVER_ADDRESS`   | Inference server HTTP address   | `http://127.0.0.1:3000` |
| `VITE_ENTRIES_SERVER_ADDRESS`     | Entries server HTTP address     | `http://127.0.0.1:8884` |
| `VITE_BINARY_THRESHOLD`           | Binary classification threshold | `0.5`                   |
| `VITE_AUTH_URL`                   | Keycloak server URL             | -                       |
| `VITE_AUTH_REALM`                 | Keycloak realm name             | -                       |
| `VITE_AUTH_CLIENT_ID`             | Keycloak client ID              | -                       |
| `VITE_PREVIEW_N_RECENT`           | Number of recent icons on login | `10`                    |
| `VITE_PREVIEW_ICON_SIZE`          | Icon size in pixels             | `100`                   |
| `VITE_PREVIEW_ICON_MARGIN`        | Icon margin in pixels           | `10`                    |
| `VITE_PREVIEW_ICON_BORDER`        | Icon border radius              | `8`                     |
| `VITE_PREVIEW_CAROUSEL_SPEED_SEC` | Carousel animation speed        | `10`                    |
| `VITE_ENTRIES_N_RECENT`           | Number of recent entries        | `5`                     |

## Development

### Prerequisites

- Node.js 20+ and npm
- Access to inference server and entries server
- Keycloak instance (for authentication)

### Setup

1. **Install dependencies:**
   ```bash
   cd webpage_v2
   npm install
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```

   The application will be available at `http://localhost:4452`

4. **Build for production:**
   ```bash
   npm run build
   ```

   The built files will be in the `dist/` directory.

## Docker Deployment

### Building the Docker Image

```bash
cd webpage_v2
docker build -t eurygaster-webpage-v2:latest .
```

**Faster Docker builds**: Commit `package-lock.json` so the image uses `npm ci` instead of `npm install`. Without the lock file, the install step resolves the full dependency tree from scratch and can take several minutes. Run `npm install` once in `webpage_v2` and commit the generated `package-lock.json`.

### Running the Container

```bash
docker run -d \
  --name eurygaster-webpage-v2 \
  -p 4452:4452 \
  -e VITE_INFERENCE_SERVER_ADDRESS=http://eurygaster-svc:3000 \
  -e VITE_ENTRIES_SERVER_ADDRESS=http://entries_server:8884 \
  -e VITE_AUTH_URL=https://your-keycloak-url.com \
  -e VITE_AUTH_REALM=your-realm \
  -e VITE_AUTH_CLIENT_ID=your-client-id \
  eurygaster-webpage-v2:latest
```

**Note**: Environment variables must be set at build time for Vite applications. See the "Build-time Environment
Variables" section below.

## Integration with Docker Compose

### Option 1: Build-time Environment Variables (Recommended)

Since Vite requires environment variables at build time, you need to pass them during the Docker build:

1. **Create a build script** (`build-docker.sh`):
   ```bash
   #!/bin/bash
   docker build \
     --build-arg VITE_INFERENCE_SERVER_ADDRESS=${INFERENCE_SERVER_ADDRESS:-http://eurygaster-svc:3000} \
     --build-arg VITE_ENTRIES_SERVER_ADDRESS=${ENTRIES_SERVER_ADDRESS:-http://entries_server:8884} \
     --build-arg VITE_BINARY_THRESHOLD=${BINARY_THRESHOLD:-0.5} \
     --build-arg VITE_AUTH_URL=${AUTH_URL} \
     --build-arg VITE_AUTH_REALM=${AUTH_REALM} \
     --build-arg VITE_AUTH_CLIENT_ID=${AUTH_CLIENT_ID} \
     -t eurygaster-webpage-v2:${WEBPAGE_TAG:-latest} \
     .
   ```

2. **Update Dockerfile** to accept build args:
   ```dockerfile
   ARG VITE_INFERENCE_SERVER_ADDRESS
   ARG VITE_ENTRIES_SERVER_ADDRESS
   ARG VITE_BINARY_THRESHOLD
   ARG VITE_AUTH_URL
   ARG VITE_AUTH_REALM
   ARG VITE_AUTH_CLIENT_ID

   ENV VITE_INFERENCE_SERVER_ADDRESS=$VITE_INFERENCE_SERVER_ADDRESS
   ENV VITE_ENTRIES_SERVER_ADDRESS=$VITE_ENTRIES_SERVER_ADDRESS
   ENV VITE_BINARY_THRESHOLD=$VITE_BINARY_THRESHOLD
   ENV VITE_AUTH_URL=$VITE_AUTH_URL
   ENV VITE_AUTH_REALM=$VITE_AUTH_REALM
   ENV VITE_AUTH_CLIENT_ID=$VITE_AUTH_CLIENT_ID
   ```

3. **Update docker-compose.yaml**:
   ```yaml
   eurygaster-webpage-v2:
     build:
       context: ./webpage_v2
       dockerfile: Dockerfile
       args:
         VITE_INFERENCE_SERVER_ADDRESS: ${INFERENCE_SERVER_ADDRESS}
         VITE_ENTRIES_SERVER_ADDRESS: ${ENTRIES_SERVER_ADDRESS}
         VITE_BINARY_THRESHOLD: ${BINARY_THRESHOLD:-0.5}
         VITE_AUTH_URL: ${AUTH_URL}
         VITE_AUTH_REALM: ${AUTH_REALM}
         VITE_AUTH_CLIENT_ID: ${AUTH_CLIENT_ID}
     image: alrdockerhub/eurygaster-webpage-v2:${WEBPAGE_TAG}
     expose:
       - "4452"
     networks:
       - eurygaster
     restart: on-failure
     depends_on:
       - eurygaster-svc
   ```

### Option 2: Runtime Configuration (Alternative)

For runtime configuration, you can use a configuration endpoint or inject a config file:

1. Create a `config.js` file that gets loaded at runtime
2. Serve it from the public directory
3. Load it in the application before initialization

## Migration from v1 (Streamlit) to v2 (TypeScript)

### Step-by-Step Migration Guide

#### 1. **Backup Current Setup**

```bash
# Backup current webpage service
docker-compose stop eurygaster-webpage
docker tag alrdockerhub/eurygaster-webpage:${WEBPAGE_TAG} alrdockerhub/eurygaster-webpage:v1-backup
```

#### 2. **Build New Frontend**

```bash
cd webpage_v2

# Build with environment variables
docker build \
  --build-arg VITE_INFERENCE_SERVER_ADDRESS=http://eurygaster-svc:3000 \
  --build-arg VITE_ENTRIES_SERVER_ADDRESS=http://entries_server:8884 \
  --build-arg VITE_AUTH_URL=${AUTH_URL} \
  --build-arg VITE_AUTH_REALM=${AUTH_REALM} \
  --build-arg VITE_AUTH_CLIENT_ID=${AUTH_CLIENT_ID} \
  -t alrdockerhub/eurygaster-webpage-v2:${WEBPAGE_TAG} \
  .
```

#### 3. **Update Docker Compose**

Modify your `docker-compose.yaml`:

**Before (v1):**

```yaml
eurygaster-webpage:
  image: alrdockerhub/eurygaster-webpage:${WEBPAGE_TAG}
  environment:
    INFERENCE_SERVER_ADDRESS: ${INFERENCE_SERVER_ADDRESS}
    ENTRIES_SERVER_ADDRESS: ${ENTRIES_SERVER_ADDRESS}
    AUTH_URL: ${AUTH_URL}
    AUTH_REALM: ${AUTH_REALM}
    AUTH_CLIENT_ID: ${AUTH_CLIENT_ID}
  expose:
    - "4452"
```

**After (v2):**

```yaml
eurygaster-webpage-v2:
  build:
    context: ./webpage_v2
    dockerfile: Dockerfile
    args:
      VITE_INFERENCE_SERVER_ADDRESS: ${INFERENCE_SERVER_ADDRESS}
      VITE_ENTRIES_SERVER_ADDRESS: ${ENTRIES_SERVER_ADDRESS}
      VITE_BINARY_THRESHOLD: ${BINARY_THRESHOLD:-0.5}
      VITE_AUTH_URL: ${AUTH_URL}
      VITE_AUTH_REALM: ${AUTH_REALM}
      VITE_AUTH_CLIENT_ID: ${AUTH_CLIENT_ID}
  image: alrdockerhub/eurygaster-webpage-v2:${WEBPAGE_TAG}
  expose:
    - "4452"
  networks:
    - eurygaster
  restart: on-failure
  depends_on:
    - eurygaster-svc
```

#### 4. **Update Nginx Configuration**

Update `webpage/nginx/webpage.conf` to point to the new service:

```nginx
upstream webpage {
    server eurygaster-webpage-v2:4452;  # Changed from eurygaster-webpage
}
```

#### 5. **Deploy New Version**

```bash
# Stop old service
docker-compose stop eurygaster-webpage

# Start new service
docker-compose up -d eurygaster-webpage-v2

# Restart nginx to pick up new upstream
docker-compose restart nginx
```

#### 6. **Verify Deployment**

1. Check service health:
   ```bash
   curl http://localhost:4452/health
   ```

2. Access the application in browser and verify:
    - Login page loads correctly
    - Authentication works
    - Image upload and classification works
    - All pages are accessible
    - Language switching works

#### 7. **Rollback Plan (if needed)**

If issues occur, you can quickly rollback:

```bash
# Stop v2
docker-compose stop eurygaster-webpage-v2

# Start v1 backup
docker-compose up -d eurygaster-webpage

# Update nginx back
# Edit webpage/nginx/webpage.conf to point back to eurygaster-webpage
docker-compose restart nginx
```

### Key Differences Between v1 and v2

| Feature        | v1 (Streamlit)      | v2 (TypeScript)     |
|----------------|---------------------|---------------------|
| Framework      | Python/Streamlit    | React/TypeScript    |
| Build          | Python package      | Node.js/Vite        |
| Port           | 4452                | 4452                |
| Environment    | Runtime env vars    | Build-time env vars |
| Static Files   | Served by Streamlit | Served by Nginx     |
| Authentication | streamlit-keycloak  | keycloak-js         |
| API Calls      | Python requests     | Axios               |
| Charts         | Plotly              | Recharts            |

### Compatibility

- ✅ **API Compatibility**: Fully compatible with existing inference and entries servers
- ✅ **Authentication**: Uses same Keycloak configuration
- ✅ **Data Format**: Same request/response formats
- ✅ **Markdown Content**: Uses same markdown files (copied to public/markdown/)
- ✅ **Environment Variables**: Same configuration options (with VITE_ prefix)

## Nginx Configuration

The new frontend uses Nginx to serve static files. The configuration is included in `nginx.conf`. For production
deployment behind a reverse proxy, ensure:

1. **Static file serving**: All routes except `/markdown/` should serve `index.html` for client-side routing
2. **Markdown files**: Served from `/markdown/` directory
3. **Health check**: Available at `/health` endpoint
4. **Caching**: Static assets are cached for 1 year

## Troubleshooting

### Issue: Environment variables not working

**Solution**: Vite requires environment variables at build time. Ensure you're passing them as build arguments in
Docker.

### Issue: Authentication not working

**Solution**:

1. Verify Keycloak configuration (URL, realm, client ID)
2. Check browser console for CORS errors
3. Ensure Keycloak client allows the frontend origin

### Issue: Sign in does nothing after first login, or console shows CSP / sandbox warnings

**Cause**: Keycloak uses an iframe to load `silent-check-sso.html` for “check-sso”. If that page used an inline script, a strict CSP (`script-src 'self'`) blocks it and the silent check fails; clicking Sign in again can then do nothing or behave oddly. Browsers may also warn: “An iframe which has both allow-scripts and allow-same-origin for its sandbox attribute can remove its sandboxing” — that iframe is created by keycloak-js and cannot be changed.

**Solution** (already applied in this repo): `silent-check-sso.html` uses an external script (`/silent-check-sso.js`) instead of inline script, so CSP `script-src 'self'` allows it without hashes. The sandbox warning is expected and does not block the flow. If you customize `public/silent-check-sso.html`, keep the script external or add the script’s CSP hash in `nginx.conf` for the `silent-check-sso.html` location.

### Issue: API calls failing

**Solution**:

1. Check network connectivity between containers
2. Verify inference and entries server addresses
3. Check browser console for CORS or network errors
4. Ensure services are on the same Docker network

### Issue: Markdown files not loading

**Solution**:

1. Verify markdown files are copied to `public/markdown/` during build
2. Check nginx configuration serves `/markdown/` correctly
3. Verify file paths match language codes (en/ru)

### Issue: CORS errors when calling API servers

**Solution**:

1. Ensure inference and entries servers have CORS enabled
2. Configure servers to allow requests from the frontend origin
3. For development, servers should allow `http://localhost:4452`
4. For production, servers should allow your production domain
5. Example CORS headers needed:
    - `Access-Control-Allow-Origin: <frontend-origin>`
    - `Access-Control-Allow-Methods: GET, POST, OPTIONS`
    - `Access-Control-Allow-Headers: Content-Type, Name, Account`
6. If using a reverse proxy (nginx), configure CORS at the proxy level

## Development Tips

1. **Hot Reload**: Vite provides instant hot module replacement during development
2. **Type Checking**: Run `npm run lint` to check for TypeScript errors
3. **Build Optimization**: Production builds are minified and optimized automatically
4. **Environment Variables**: Use `import.meta.env.VITE_*` to access environment variables

## Adding New Languages

1. Create directory: `public/markdown/<LANG>/`
2. Copy markdown files from `en/` directory
3. Translate content
4. Add language to `SUPPORTED_LANGUAGES` in `src/config/index.ts`
5. Add translations to `src/translations/index.ts`

## Performance Considerations

- **Bundle Size**: Optimized with Vite's tree-shaking
- **Code Splitting**: Automatic route-based code splitting
- **Asset Optimization**: Images and fonts are optimized during build
- **Caching**: Static assets cached for 1 year via Nginx

## Security

- **CSP Headers**: Configured in nginx.conf
- **XSS Protection**: React automatically escapes content
- **Authentication**: Secure Keycloak integration
- **HTTPS**: Should be configured at reverse proxy level

## Support

For issues, bugs, or feature requests:

- GitHub Issues: https://github.com/alexander-pv/eurygaster_recognition/issues
- GitHub Releases: https://github.com/alexander-pv/eurygaster_recognition/releases


