import React, { createContext, useContext, useState, useEffect, useMemo, useCallback, ReactNode } from 'react';
import { AuthService } from '../services/auth';
import { DEFAULT_CONFIG } from '../config';
import type { User, Language } from '../types';

interface AuthContextType {
  user: User;
  authService: AuthService;
  login: (lang: Language) => Promise<void>;
  logout: () => Promise<void>;
  refreshAuth: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User>({
    email: 'Unknown',
    name: 'Unnamed',
    authenticated: false,
  });

  // Create authService once using useMemo to avoid recreation on every render
  // DEFAULT_CONFIG is stable and doesn't change, so empty deps array is correct
  const authService = useMemo(
    () =>
      new AuthService(
        DEFAULT_CONFIG.authUrl,
        DEFAULT_CONFIG.authRealm,
        DEFAULT_CONFIG.authClientId
      ),
    []
  );

  const refreshAuth = useCallback(async () => {
    // Ensure token is valid before checking authentication
    await authService.ensureTokenValid();
    
    const authenticated = await authService.init();
    if (authenticated) {
      const userInfo = authService.getUserInfo();
      if (userInfo) {
        setUser({
          ...userInfo,
          authenticated: true,
        });
      } else {
        // Token might be invalid, reset user state
        setUser({
          email: 'Unknown',
          name: 'Unnamed',
          authenticated: false,
        });
      }
    } else {
      setUser({
        email: 'Unknown',
        name: 'Unnamed',
        authenticated: false,
      });
    }
  }, [authService]);

  useEffect(() => {
    refreshAuth();
    
    // Cleanup on unmount
    return () => {
      authService.cleanup();
    };
  }, [authService, refreshAuth]);

  const login = useCallback(async (lang: Language) => {
    await authService.login(lang);
    await refreshAuth();
  }, [authService, refreshAuth]);

  const logout = useCallback(async () => {
    await authService.logout();
    setUser({
      email: 'Unknown',
      name: 'Unnamed',
      authenticated: false,
    });
  }, [authService]);

  return (
    <AuthContext.Provider value={{ user, authService, login, logout, refreshAuth }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

