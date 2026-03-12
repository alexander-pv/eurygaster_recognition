import React, { createContext, useContext, useState, ReactNode } from 'react';
import type { Language } from '../types';
import { SUPPORTED_LANGUAGES } from '../config';

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export const LanguageProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [language, setLanguage] = useState<Language>(() => {
    try {
      const saved = localStorage.getItem('language') as Language;
      return saved && SUPPORTED_LANGUAGES.includes(saved) ? saved : 'en';
    } catch (error) {
      // localStorage may be unavailable (private browsing, disabled, etc.)
      console.warn('Failed to access localStorage, using default language:', error);
      return 'en';
    }
  });

  const handleSetLanguage = (lang: Language) => {
    const safeLang = SUPPORTED_LANGUAGES.includes(lang) ? lang : 'en';
    setLanguage(safeLang);
    try {
      localStorage.setItem('language', safeLang);
    } catch (error) {
      // localStorage may be unavailable (private browsing, disabled, etc.)
      console.warn('Failed to save language preference to localStorage:', error);
    }
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage: handleSetLanguage }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (context === undefined) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};

