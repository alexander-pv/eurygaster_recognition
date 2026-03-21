# Eurygaster Webpage v2 - TypeScript Frontend

TypeScript-based frontend for the Eurygaster Recognition application: React + Vite, with the inference and entries backends and optional Keycloak auth.

## Project structure

```
src/webpage_v2/
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

## Environment variables

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
   cd src/webpage_v2
   npm install
   ```
2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit with specific configuration
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

## Deployment

### Building Docker image

```bash
cd src/webpage_v2
source .env
docker build --no-cache --progress=plain \
  --build-arg VITE_INFERENCE_SERVER_ADDRESS=${VITE_INFERENCE_SERVER_ADDRESS} \
  --build-arg VITE_ENTRIES_SERVER_ADDRESS=${VITE_ENTRIES_SERVER_ADDRESS} \
  --build-arg VITE_AUTH_URL=${VITE_AUTH_URL} \
  --build-arg VITE_AUTH_REALM=${VITE_AUTH_REALM} \
  --build-arg VITE_AUTH_CLIENT_ID=${VITE_AUTH_CLIENT_ID} \
  --build-arg VITE_BINARY_THRESHOLD=${VITE_BINARY_THRESHOLD} \
  -t eurygaster-webpage-v2:<tag> .
```
