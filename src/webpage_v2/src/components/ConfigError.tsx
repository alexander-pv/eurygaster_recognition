import React from 'react';
import { AlertTriangle } from 'lucide-react';
import { CONFIG_ERROR_KEY, type ConfigErrorMessages } from '../config';

export const ConfigError: React.FC = () => {
  const configErrors = (window as unknown as Record<string, ConfigErrorMessages | undefined>)[CONFIG_ERROR_KEY];

  if (!configErrors || configErrors.length === 0) {
    return null;
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-6">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-center gap-3 mb-4">
          <AlertTriangle className="text-red-500" size={32} />
          <h1 className="text-2xl font-bold text-gray-800">Configuration Error</h1>
        </div>
        <p className="text-gray-600 mb-4">
          The application is not properly configured. Please check the following:
        </p>
        <ul className="list-disc list-inside space-y-2 mb-4 text-sm text-gray-700">
          {configErrors.map((error, index) => (
            <li key={index}>{error}</li>
          ))}
        </ul>
        <p className="text-sm text-gray-500">
          Please contact the administrator or check the environment variables configuration.
        </p>
      </div>
    </div>
  );
};

