import Keycloak from 'keycloak-js';
import type { Language } from '../types';

const LOGIN_MESSAGES = {
  en: {
    SIGN_IN: 'Sign In',
    SIGN_OUT: 'Sign Out',
    LABEL_LOGIN: 'Please, sign in to your account',
    ERR_NOPOPUP: 'Unable to open the authentication popup. Allow popups and refresh the page to proceed',
    ERR_POPUPCLOSED: 'Authentication popup was closed manually',
    ERR_FATAL: 'Unable to connect to auth system using the current configuration',
  },
  ru: {
    SIGN_IN: 'Войти',
    SIGN_OUT: 'Выйти',
    LABEL_LOGIN: 'Пожалуйста, войдите в свой аккаунт',
    ERR_NOPOPUP: 'Невозможно открыть всплывающее окно аутентификации. Разрешите всплывающие окна и обновите страницу, чтобы продолжить',
    ERR_POPUPCLOSED: 'Всплывающее окно аутентификации было закрыто вручную',
    ERR_FATAL: 'Невозможно подключиться к системе аутентификации, используя текущую конфигурацию',
  },
};

export class AuthService {
  private keycloak: Keycloak | null = null;
  private initialized = false;
  private tokenRefreshInterval: number | null = null;

  constructor(
    private authUrl: string | undefined,
    private authRealm: string | undefined,
    private authClientId: string | undefined
  ) {}

  async init(): Promise<boolean> {
    if (!this.authUrl || !this.authRealm || !this.authClientId) {
      console.warn('Auth configuration missing, authentication disabled');
      return false;
    }

    try {
      this.keycloak = new Keycloak({
        url: this.authUrl,
        realm: this.authRealm,
        clientId: this.authClientId,
      });

      // silentCheckSsoRedirectUri: required so check-sso uses an iframe instead of a full redirect.
      // Without it, keycloak-js calls doLogin(false) on every load, causing a redirect loop after logout
      // in Firefox/Safari (user keeps being sent back to the app as "logged in"). The iframe triggers a
      // browser sandbox warning (we cannot change that); CSP for that page allows the script via hash or 'self'.
      const authenticated = await this.keycloak.init({
        onLoad: 'check-sso',
        silentCheckSsoRedirectUri: window.location.origin + '/silent-check-sso.html',
        pkceMethod: 'S256',
      });

      this.initialized = true;
      
      // Set up token refresh
      if (authenticated && this.keycloak) {
        this.setupTokenRefresh();
      }
      
      return authenticated;
    } catch (error) {
      console.error('Keycloak initialization failed:', error);
      return false;
    }
  }

  async login(lang: Language = 'en'): Promise<boolean> {
    if (!this.keycloak || !this.initialized) {
      const initSuccess = await this.init();
      if (!initSuccess || !this.keycloak) {
        throw new Error(LOGIN_MESSAGES[lang].ERR_FATAL);
      }
    }

    try {
      await this.keycloak.login({
        locale: lang,
      });
      return this.keycloak.authenticated || false;
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  }

  /**
   * Clear Keycloak adapter state from localStorage so that after redirect back from Keycloak logout,
   * the new page load does not see stale tokens (fixes Firefox/Safari staying "logged in" after sign out).
   */
  private clearKeycloakStorage(): void {
    try {
      const keys: string[] = [];
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key && (key.startsWith('kc-callback-') || key.startsWith('keycloak-'))) {
          keys.push(key);
        }
      }
      keys.forEach((k) => localStorage.removeItem(k));
    } catch {
      // ignore
    }
  }

  async logout(): Promise<void> {
    if (this.keycloak && this.initialized) {
      this.clearKeycloakStorage();
      const frontPageUrl = window.location.origin + '/';
      await this.keycloak.logout({
        redirectUri: frontPageUrl,
      });
    }
  }

  isAuthenticated(): boolean {
    return this.keycloak?.authenticated || false;
  }

  getUserInfo(): { email: string; name: string } | null {
    if (!this.keycloak?.authenticated || !this.keycloak.tokenParsed) {
      return null;
    }

    const token = this.keycloak.tokenParsed as Record<string, unknown>;
    return {
      email: (token.email as string) || 'Unknown',
      name: (token.name as string) || (token.preferred_username as string) || 'Unnamed',
    };
  }

  getToken(): string | undefined {
    return this.keycloak?.token;
  }

  getSignOutLink(_lang: Language = 'en'): string | null {
    if (!this.keycloak?.authenticated || !this.keycloak.idToken) {
      return null;
    }

    const params = new URLSearchParams({
      post_logout_redirect_uri: window.location.origin + '/',
      id_token_hint: this.keycloak.idToken,
    });

    return `${this.authUrl}/realms/${this.authRealm}/protocol/openid-connect/logout?${params.toString()}`;
  }

  private setupTokenRefresh(): void {
    if (!this.keycloak) return;

    // Clear existing interval if any
    if (this.tokenRefreshInterval !== null) {
      window.clearInterval(this.tokenRefreshInterval);
      this.tokenRefreshInterval = null;
    }

    // Refresh token every 5 minutes (300000ms)
    // Keycloak tokens typically expire after 5-15 minutes
    this.tokenRefreshInterval = window.setInterval(async () => {
      if (this.keycloak?.authenticated) {
        try {
          const refreshed = await this.keycloak.updateToken(30); // Refresh if expires within 30 seconds
          if (refreshed) {
            console.log('Token refreshed successfully');
          }
        } catch (error) {
          console.error('Token refresh failed:', error);
          // If refresh fails, user will need to re-authenticate
          // Clear interval before logout to prevent multiple logout attempts
          if (this.tokenRefreshInterval !== null) {
            window.clearInterval(this.tokenRefreshInterval);
            this.tokenRefreshInterval = null;
          }
          try {
            await this.keycloak.logout();
          } catch (logoutError) {
            console.error('Logout after token refresh failure failed:', logoutError);
          }
        }
      } else {
        // If not authenticated, clear the interval
        if (this.tokenRefreshInterval !== null) {
          window.clearInterval(this.tokenRefreshInterval);
          this.tokenRefreshInterval = null;
        }
      }
    }, 5 * 60 * 1000); // 5 minutes
  }

  async updateToken(minValidity: number = 5): Promise<boolean> {
    if (!this.keycloak || !this.initialized) {
      return false;
    }
    try {
      return await this.keycloak.updateToken(minValidity);
    } catch (error) {
      console.error('Token update failed:', error);
      return false;
    }
  }

  cleanup(): void {
    if (this.tokenRefreshInterval !== null) {
      window.clearInterval(this.tokenRefreshInterval);
      this.tokenRefreshInterval = null;
    }
  }

  // Check if token is about to expire and refresh if needed
  async ensureTokenValid(): Promise<boolean> {
    if (!this.keycloak || !this.initialized || !this.keycloak.authenticated) {
      return false;
    }

    try {
      // Check if token needs refresh (expires within 5 seconds)
      const refreshed = await this.keycloak.updateToken(5);
      if (refreshed) {
        console.log('Token refreshed proactively');
      }
      return true;
    } catch (error) {
      console.error('Failed to ensure token validity:', error);
      return false;
    }
  }
}

