import React, { useEffect, useState, useMemo } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useLanguage } from '../contexts/LanguageContext';
import { EntriesService } from '../services/api';
import { DEFAULT_CONFIG } from '../config';
import { getTranslation } from '../translations';
import { loadMarkdown } from '../utils/markdown';
import ReactMarkdown from 'react-markdown';
import type { Entry } from '../types';

// Validate and parse environment variables with safe defaults
const parseEnvInt = (value: string | undefined, defaultValue: number, min: number = 1, max: number = 1000): number => {
  const parsed = value ? parseInt(value, 10) : defaultValue;
  if (isNaN(parsed) || parsed < min || parsed > max) {
    console.warn(`Invalid environment variable value, using default: ${defaultValue}`);
    return defaultValue;
  }
  return parsed;
};

const PREVIEW_SETTINGS = {
  nRecentIcons: parseEnvInt(import.meta.env.VITE_PREVIEW_N_RECENT, 10, 1, 100),
  iconSize: parseEnvInt(import.meta.env.VITE_PREVIEW_ICON_SIZE, 100, 10, 500),
  iconMargin: parseEnvInt(import.meta.env.VITE_PREVIEW_ICON_MARGIN, 10, 0, 50),
  iconBorder: parseEnvInt(import.meta.env.VITE_PREVIEW_ICON_BORDER, 8, 0, 50),
  speedSec: parseEnvInt(import.meta.env.VITE_PREVIEW_CAROUSEL_SPEED_SEC, 10, 1, 60),
};

const ENTRIES_SETTINGS = {
  nRecentRows: parseEnvInt(import.meta.env.VITE_ENTRIES_N_RECENT, 5, 1, 100),
};

export const LoginPage: React.FC = () => {
  const { user, login } = useAuth();
  const { language, setLanguage } = useLanguage();
  const t = getTranslation(language);
  const [headerMd, setHeaderMd] = useState('');
  const [welcomeMd, setWelcomeMd] = useState('');
  const [icons, setIcons] = useState<string[]>([]);
  const [entries, setEntries] = useState<Entry[]>([]);
  const [loading, setLoading] = useState(true);
  const [loginError, setLoginError] = useState<string | null>(null);

  // Memoize service instance to avoid recreation on every render
  const entriesService = useMemo(
    () => new EntriesService(DEFAULT_CONFIG.entriesServer),
    []
  );

  useEffect(() => {
    if (user.authenticated) return;
    
    let cancelled = false;
    const loadContent = async () => {
      setLoading(true);
      try {
        const [header, welcome] = await Promise.all([
          loadMarkdown(language, 'header.md'),
          loadMarkdown(language, 'welcome.md'),
        ]);
        if (!cancelled) {
          setHeaderMd(header);
          setWelcomeMd(welcome);
        }

        const [iconsData, entriesData] = await Promise.all([
          entriesService.getRecentIcons(PREVIEW_SETTINGS.nRecentIcons, 'login-icons'),
          entriesService.getRecentScores(ENTRIES_SETTINGS.nRecentRows, 'login-entries'),
        ]);
        if (!cancelled) {
          setIcons(iconsData);
          setEntries(entriesData);
        }
      } catch (error) {
        if (!cancelled) {
          if (error instanceof Error && error.message.includes('cancelled')) {
            return; // Don't log cancelled requests
          }
          console.error('Error loading login page content:', error);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    loadContent();
    
    return () => {
      cancelled = true;
      entriesService.cancelRequest('login-icons');
      entriesService.cancelRequest('login-entries');
    };
  }, [language, user.authenticated, entriesService]);

  const handleLogin = async () => {
    setLoginError(null);
    try {
      await login(language);
    } catch (error) {
      console.error('Login failed:', error);
      const errorMessage = error instanceof Error ? error.message : t.login.ERR_FATAL;
      setLoginError(errorMessage);
    }
  };

  if (user.authenticated) {
    return null;
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-white flex items-center justify-center p-6">
      <div className="max-w-4xl w-full space-y-8">
        {/* Language selector */}
        <div className="flex justify-end">
          <label htmlFor="language-select" className="sr-only">
            Select language
          </label>
          <select
            id="language-select"
            value={language}
            onChange={(e) => setLanguage(e.target.value as 'en' | 'ru')}
            className="px-4 py-2 border border-gray-300 rounded-lg bg-white text-gray-700 focus:outline-none focus:ring-2 focus:ring-primary-500"
            aria-label="Select language"
          >
            <option value="en">English</option>
            <option value="ru">Русский</option>
          </select>
        </div>

        {/* Header */}
        {headerMd && (
          <div className="prose prose-lg max-w-none">
            <ReactMarkdown
              components={{
                h1: ({ children }) => <h1 className="text-3xl font-bold text-gray-900 mt-0 mb-4">{children}</h1>,
                h2: ({ children }) => <h2 className="text-2xl font-bold text-gray-900 mt-0 mb-4">{children}</h2>,
                h3: ({ children }) => <h3 className="text-2xl font-bold text-gray-900 mt-0 mb-4">{children}</h3>,
              }}
            >
              {headerMd}
            </ReactMarkdown>
          </div>
        )}

        {/* Welcome */}
        {welcomeMd && (
          <div className="prose prose-lg max-w-none bg-white p-6 rounded-lg shadow-md">
            <ReactMarkdown>{welcomeMd}</ReactMarkdown>
          </div>
        )}

        {/* Login button */}
        <div className="flex flex-col items-center gap-4">
          <button
            onClick={handleLogin}
            className="px-8 py-4 bg-primary-600 text-white rounded-lg font-semibold text-lg hover:bg-primary-700 transition-colors shadow-lg hover:shadow-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
            aria-label={t.account.SIGN_IN}
          >
            {t.account.SIGN_IN}
          </button>
          {loginError && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 max-w-md w-full" role="alert">
              <p className="font-medium">{t.login.ERR_FATAL}</p>
              <p className="text-sm mt-1">{loginError}</p>
            </div>
          )}
        </div>

        {/* Preview carousel */}
        {icons.length > 0 && (
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-xl font-semibold mb-4 text-gray-800">{t.login.RECENT_IMAGES || 'Recent Images'}</h3>
            <div className="overflow-hidden relative bg-gray-100 rounded-lg p-4">
              <div
                className="flex flex-nowrap animate-slide"
                style={{
                  '--carousel-speed': `${PREVIEW_SETTINGS.speedSec}s`,
                  width: `${2 * icons.length * (PREVIEW_SETTINGS.iconSize + PREVIEW_SETTINGS.iconMargin * 2)}px`,
                } as React.CSSProperties}
              >
                {icons.map((icon, idx) => (
                  <img
                    key={idx}
                    src={icon}
                    alt={`Preview ${idx + 1}`}
                    className="flex-shrink-0 rounded-lg shadow-md hover:scale-105 transition-transform cursor-pointer"
                    style={{
                      width: `${PREVIEW_SETTINGS.iconSize}px`,
                      height: `${PREVIEW_SETTINGS.iconSize}px`,
                      margin: `0 ${PREVIEW_SETTINGS.iconMargin}px`,
                      borderRadius: `${PREVIEW_SETTINGS.iconBorder}px`,
                    }}
                    loading="lazy"
                    aria-label={`Recent image ${idx + 1}`}
                  />
                ))}
                {/* Duplicate for seamless loop */}
                {icons.map((icon, idx) => (
                  <img
                    key={`dup-${idx}`}
                    src={icon}
                    alt={`Preview ${idx + 1} (duplicate)`}
                    className="flex-shrink-0 rounded-lg shadow-md hover:scale-105 transition-transform cursor-pointer"
                    style={{
                      width: `${PREVIEW_SETTINGS.iconSize}px`,
                      height: `${PREVIEW_SETTINGS.iconSize}px`,
                      margin: `0 ${PREVIEW_SETTINGS.iconMargin}px`,
                      borderRadius: `${PREVIEW_SETTINGS.iconBorder}px`,
                    }}
                    loading="lazy"
                    aria-hidden="true"
                  />
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Recent entries table */}
        {entries.length > 0 && (
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-xl font-semibold mb-4 text-gray-800">{t.login.RECENT_ENTRIES || 'Recent Entries'}</h3>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      DateTime
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Score
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Recognized
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {entries.map((entry, idx) => (
                    <tr key={idx} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{entry.DateTime ?? '—'}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {entry.Score != null && !Number.isNaN(Number(entry.Score)) ? Number(entry.Score).toFixed(3) : '—'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{entry.Recognized ?? '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

