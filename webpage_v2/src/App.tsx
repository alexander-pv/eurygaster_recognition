import React, { useMemo } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation, useNavigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { LanguageProvider } from './contexts/LanguageContext';
import { ErrorBoundary } from './components/ErrorBoundary';
import { ConfigError } from './components/ConfigError';
import { CONFIG_ERROR_KEY, type ConfigErrorMessages } from './config';
import { Layout } from './components/Layout';
import { LoginPage } from './pages/LoginPage';
import { AboutPage } from './pages/AboutPage';
import { HowToUsePage } from './pages/HowToUsePage';
import { BestPhotoPage } from './pages/BestPhotoPage';
import { IdentifyPage } from './pages/IdentifyPage';

const AppContent: React.FC = () => {
  const { user } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  // Get current page from URL path (memoized for performance)
  const currentPage = useMemo(() => {
    const path = location.pathname;
    if (path === '/' || path === '/about') return 'about';
    if (path === '/how-to') return 'how-to';
    if (path === '/best-photo') return 'best-photo';
    if (path === '/identify') return 'identify';
    return 'about';
  }, [location.pathname]);

  const handlePageChange = (page: string) => {
    const pathMap: Record<string, string> = {
      'about': '/about',
      'how-to': '/how-to',
      'best-photo': '/best-photo',
      'identify': '/identify',
    };
    const path = pathMap[page] || '/about';
    navigate(path);
  };

  if (!user.authenticated) {
    return <LoginPage />;
  }

  return (
    <Routes>
      <Route
        path="/"
        element={
          <Layout currentPage={currentPage} onPageChange={handlePageChange}>
            <Navigate to="/about" replace />
          </Layout>
        }
      />
      <Route
        path="/about"
        element={
          <Layout currentPage={currentPage} onPageChange={handlePageChange}>
            <AboutPage />
          </Layout>
        }
      />
      <Route
        path="/how-to"
        element={
          <Layout currentPage={currentPage} onPageChange={handlePageChange}>
            <HowToUsePage />
          </Layout>
        }
      />
      <Route
        path="/best-photo"
        element={
          <Layout currentPage={currentPage} onPageChange={handlePageChange}>
            <BestPhotoPage />
          </Layout>
        }
      />
      <Route
        path="/identify"
        element={
          <Layout currentPage={currentPage} onPageChange={handlePageChange}>
            <IdentifyPage />
          </Layout>
        }
      />
      <Route path="*" element={<Navigate to="/about" replace />} />
    </Routes>
  );
};

const App: React.FC = () => {
  // Check for configuration errors (namespaced key set at load by config)
  const configErrors = (window as unknown as Record<string, ConfigErrorMessages | undefined>)[CONFIG_ERROR_KEY];
  
  if (configErrors && configErrors.length > 0) {
    return <ConfigError />;
  }

  return (
    <ErrorBoundary>
      <Router>
        <AuthProvider>
          <LanguageProvider>
            <AppContent />
          </LanguageProvider>
        </AuthProvider>
      </Router>
    </ErrorBoundary>
  );
};

export default App;

