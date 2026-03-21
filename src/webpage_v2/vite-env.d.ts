/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_INFERENCE_SERVER_ADDRESS?: string;
  readonly VITE_ENTRIES_SERVER_ADDRESS?: string;
  readonly VITE_BINARY_THRESHOLD?: string;
  readonly VITE_AUTH_URL?: string;
  readonly VITE_AUTH_REALM?: string;
  readonly VITE_AUTH_CLIENT_ID?: string;
  readonly VITE_PREVIEW_N_RECENT?: string;
  readonly VITE_PREVIEW_ICON_SIZE?: string;
  readonly VITE_PREVIEW_ICON_MARGIN?: string;
  readonly VITE_PREVIEW_ICON_BORDER?: string;
  readonly VITE_PREVIEW_CAROUSEL_SPEED_SEC?: string;
  readonly VITE_ENTRIES_N_RECENT?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

