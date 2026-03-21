export const APP_VERSION = '2.0.0';
export const GITHUB_URL = 'https://github.com/alexander-pv/eurygaster_recognition/releases';
export const ISSUES_URL = 'https://github.com/alexander-pv/eurygaster_recognition/issues';

export const SUPPORTED_LANGUAGES: Array<'en' | 'ru'> = ['en', 'ru'];

/** Namespaced window key for config errors (avoids collision and tampering from other scripts) */
export const CONFIG_ERROR_KEY = '__EURYGASTER_CONFIG_ERROR__';

export type ConfigErrorMessages = string[];

interface ConfigValidationResult {
  valid: boolean;
  errors: string[];
}

export const validateConfig = (): ConfigValidationResult => {
  const errors: string[] = [];
  
  const inferenceServer = import.meta.env.VITE_INFERENCE_SERVER_ADDRESS;
  const entriesServer = import.meta.env.VITE_ENTRIES_SERVER_ADDRESS;
  const authUrl = import.meta.env.VITE_AUTH_URL;
  const authRealm = import.meta.env.VITE_AUTH_REALM;
  const authClientId = import.meta.env.VITE_AUTH_CLIENT_ID;
  
  if (!inferenceServer) {
    errors.push('VITE_INFERENCE_SERVER_ADDRESS is not set');
  } else if (!inferenceServer.startsWith('http://') && !inferenceServer.startsWith('https://')) {
    errors.push('VITE_INFERENCE_SERVER_ADDRESS must start with http:// or https://');
  }
  
  if (!entriesServer) {
    errors.push('VITE_ENTRIES_SERVER_ADDRESS is not set');
  } else if (!entriesServer.startsWith('http://') && !entriesServer.startsWith('https://')) {
    errors.push('VITE_ENTRIES_SERVER_ADDRESS must start with http:// or https://');
  }
  
  const binaryThreshold = parseFloat(import.meta.env.VITE_BINARY_THRESHOLD || '0.5');
  if (isNaN(binaryThreshold) || binaryThreshold < 0 || binaryThreshold > 1) {
    errors.push('VITE_BINARY_THRESHOLD must be a number between 0 and 1');
  }
  
  // Auth is optional, but if one is set, all should be set
  const authVars = [authUrl, authRealm, authClientId].filter(Boolean);
  if (authVars.length > 0 && authVars.length < 3) {
    errors.push('If authentication is enabled, VITE_AUTH_URL, VITE_AUTH_REALM, and VITE_AUTH_CLIENT_ID must all be set');
  }
  
  return {
    valid: errors.length === 0,
    errors,
  };
};

export const DEFAULT_CONFIG = {
  inferenceServer: import.meta.env.VITE_INFERENCE_SERVER_ADDRESS || 'http://127.0.0.1:3000',
  entriesServer: import.meta.env.VITE_ENTRIES_SERVER_ADDRESS || 'http://127.0.0.1:8884',
  binaryThreshold: parseFloat(import.meta.env.VITE_BINARY_THRESHOLD || '0.5'),
  authUrl: import.meta.env.VITE_AUTH_URL || undefined,
  authRealm: import.meta.env.VITE_AUTH_REALM || undefined,
  authClientId: import.meta.env.VITE_AUTH_CLIENT_ID || undefined,
};

// Validate configuration on module load
const validation = validateConfig();
if (!validation.valid) {
  const errorMessage = `Configuration validation errors: ${validation.errors.join(', ')}`;
  console.error(errorMessage);
  // In production, show user-friendly error (use namespaced key)
  if (import.meta.env.PROD) {
    try {
      (window as unknown as Record<string, ConfigErrorMessages>)[CONFIG_ERROR_KEY] = validation.errors;
    } catch {
      // Ignore if window is unavailable (e.g. in some SSR/build contexts)
    }
  }
}

