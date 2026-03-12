import * as Sentry from '@sentry/react';

let isInitialized = false;

export const initErrorMonitoring = () => {
  if (isInitialized) {
    return;
  }

  const dsn = import.meta.env.VITE_GLITCHTIP_DSN || import.meta.env.VITE_SENTRY_DSN;
  const environment = import.meta.env.VITE_GLITCHTIP_ENVIRONMENT || import.meta.env.MODE || 'production';

  if (!dsn) {
    console.log('Error monitoring disabled: No DSN configured');
    isInitialized = true; // Mark as initialized to prevent retries
    return;
  }

  try {
    Sentry.init({
      dsn,
      environment,
      integrations: [
        Sentry.browserTracingIntegration(),
        Sentry.replayIntegration({
          maskAllText: false,
          blockAllMedia: false,
        }),
      ],
      // Performance Monitoring
      tracesSampleRate: environment === 'production' ? 0.1 : 1.0,
      // Session Replay
      replaysSessionSampleRate: environment === 'production' ? 0.1 : 1.0,
      replaysOnErrorSampleRate: 1.0,
      // Filter out common non-actionable errors
      beforeSend(event, hint) {
        // Filter out network errors that are expected
        if (event.exception) {
          const error = hint.originalException;
          if (error instanceof Error) {
            // Don't report network errors that are handled
            if (error.message.includes('Network error') || 
                error.message.includes('Request timeout') ||
                error.message.includes('cancelled')) {
              return null;
            }
          }
        }
        return event;
      },
    });

    isInitialized = true;
    console.log('Error monitoring initialized');
  } catch (error) {
    console.error('Failed to initialize error monitoring:', error);
    isInitialized = true; // Mark as initialized to prevent retries
  }
};

export const captureException = (error: Error, context?: Record<string, unknown>) => {
  if (!isInitialized) {
    return;
  }

  try {
    if (context) {
      Sentry.withScope((scope) => {
        Object.entries(context).forEach(([key, value]) => {
          scope.setContext(key, value as Record<string, unknown>);
        });
        Sentry.captureException(error);
      });
    } else {
      Sentry.captureException(error);
    }
  } catch (err) {
    console.error('Failed to capture exception:', err);
  }
};

export const captureMessage = (message: string, level: Sentry.SeverityLevel = 'info') => {
  if (!isInitialized) {
    return;
  }

  try {
    Sentry.captureMessage(message, level);
  } catch (err) {
    console.error('Failed to capture message:', err);
  }
};

