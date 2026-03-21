import React, { ReactNode } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useLanguage } from '../contexts/LanguageContext';
import { getTranslation } from '../translations';
import { APP_VERSION, GITHUB_URL, ISSUES_URL } from '../config';
import { Menu, X, User, LogOut, HelpCircle, BookOpen } from 'lucide-react';

const BIBTEX = `@article{popkov2025web,
  title={A web-based app for sunn pest species recognition (Hemiptera: Scutelleridae: Eurygaster) using machine learning},
  author={Popkov, Alexander and Neimorovets, Vladimir and Konstantinov, Fedor},
  journal={Agricultural and Forest Entomology},
  year={2025},
  publisher={Wiley Online Library}
}`;

interface LayoutProps {
  children: ReactNode;
  currentPage: string;
  onPageChange: (page: string) => void;
}

export const Layout: React.FC<LayoutProps> = ({ children, currentPage, onPageChange }) => {
  const { user, logout, authService } = useAuth();
  const accountConsoleUrl = authService.getAccountConsoleUrl();
  const { language, setLanguage } = useLanguage();
  const t = getTranslation(language);
  const [sidebarOpen, setSidebarOpen] = React.useState(false);
  const [citeModalOpen, setCiteModalOpen] = React.useState(false);

  const pages = [
    { key: 'about', label: t.nav.ABOUT },
    { key: 'how-to', label: t.nav.HOW_TO },
    { key: 'best-photo', label: t.nav.GET_ACC_REC },
    { key: 'identify', label: t.nav.IDENTIFY },
  ];

  const handleLogout = async () => {
    // logout() redirects to Keycloak then back to redirectUri (app root); no need to set location here
    await logout();
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top bar: title; on mobile only: language selector (top right) and menu toggle */}
      <div className="fixed top-0 left-0 right-0 z-50 bg-white shadow-md p-4 flex items-center justify-between gap-3">
        <h1 className="text-xl font-bold text-primary-700 truncate">{t.nav.NAV}</h1>
        <div className="flex items-center gap-2 shrink-0">
          <label className="sr-only" htmlFor="header-lang-select">
            {t.nav.LANG}
          </label>
          <select
            id="header-lang-select"
            value={language}
            onChange={(e) => setLanguage(e.target.value as 'en' | 'ru')}
            className="lg:hidden px-3 py-2 text-sm border border-gray-300 rounded-lg bg-white text-gray-700 focus:outline-none focus:ring-2 focus:ring-primary-500"
            aria-label={t.nav.LANG}
          >
            <option value="en">English</option>
            <option value="ru">Русский</option>
          </select>
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="lg:hidden p-2 rounded-md text-gray-600 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500"
            aria-label={sidebarOpen ? 'Close menu' : 'Open menu'}
            aria-expanded={sidebarOpen}
          >
            {sidebarOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
      </div>

      <div className="flex">
        {/* Sidebar */}
        <aside
          className={`${
            sidebarOpen ? 'translate-x-0' : '-translate-x-full'
          } lg:translate-x-0 fixed lg:static inset-y-0 left-0 z-40 w-64 bg-white shadow-lg transition-transform duration-300 ease-in-out flex flex-col max-h-full lg:max-h-none`}
        >
          <div className="h-full min-h-0 flex flex-col overflow-y-auto">
            <div className="p-6 border-b">
              <h2 className="text-2xl font-bold text-primary-700">{t.nav.NAV}</h2>
            </div>

            {user.authenticated && (
              <div className="p-4 border-b bg-primary-50">
                <div className="flex items-center gap-3 mb-3">
                  {accountConsoleUrl ? (
                    <a
                      href={accountConsoleUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="w-10 h-10 rounded-full bg-primary-500 flex items-center justify-center text-white shrink-0 hover:bg-primary-600 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-colors"
                      title={t.account.ACCOUNT_SETTINGS}
                      aria-label={t.account.ACCOUNT_SETTINGS}
                    >
                      <User size={20} />
                    </a>
                  ) : (
                    <div className="w-10 h-10 rounded-full bg-primary-500 flex items-center justify-center text-white shrink-0">
                      <User size={20} />
                    </div>
                  )}
                  <div className="min-w-0">
                    <p className="font-semibold text-gray-800 truncate">{t.account.GREET}, {user.name}!</p>
                    <p className="text-sm text-gray-600 truncate">{user.email}</p>
                  </div>
                </div>
                <button
                  onClick={handleLogout}
                  className="w-full flex items-center gap-2 px-4 py-2 text-sm text-red-600 hover:bg-red-50 rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
                  aria-label={t.account.SIGN_OUT}
                >
                  <LogOut size={16} />
                  {t.account.SIGN_OUT}
                </button>
              </div>
            )}

            <nav className="flex-1 p-4 space-y-2" role="navigation" aria-label={t.nav.NAV}>
              {pages.map((page) => (
                <button
                  key={page.key}
                  onClick={() => {
                    onPageChange(page.key);
                    setSidebarOpen(false);
                  }}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      e.preventDefault();
                      onPageChange(page.key);
                      setSidebarOpen(false);
                    }
                  }}
                  className={`w-full text-left px-4 py-3 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 ${
                    currentPage === page.key
                      ? 'bg-primary-100 text-primary-700 font-semibold'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                  aria-current={currentPage === page.key ? 'page' : undefined}
                  aria-label={`${page.label}${currentPage === page.key ? ' (current page)' : ''}`}
                >
                  {page.label}
                </button>
              ))}
            </nav>

            <div className="p-4 border-t space-y-3">
              <button
                type="button"
                onClick={() => {
                  setCiteModalOpen(true);
                  setSidebarOpen(false);
                }}
                className="w-full flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500"
                aria-label={t.nav.CITE}
              >
                <BookOpen size={16} />
                {t.nav.CITE}
              </button>
              {/* Language selector */}
              <div className="mb-3">
                <label className="block text-xs font-medium text-gray-500 mb-1">
                  {t.nav.LANG}
                </label>
                <select
                  value={language}
                  onChange={(e) => setLanguage(e.target.value as 'en' | 'ru')}
                  className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg bg-white text-gray-700 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  aria-label="Select language"
                >
                  <option value="en">English</option>
                  <option value="ru">Русский</option>
                </select>
              </div>
              
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <HelpCircle size={16} />
                <span>{t.account.HELP}</span>
              </div>
              <div className="text-xs text-gray-500 space-y-1">
                <p>{t.account.VER}: {APP_VERSION}</p>
                <div className="flex flex-col gap-1">
                  <a href={GITHUB_URL} target="_blank" rel="noopener noreferrer" className="text-primary-600 hover:underline">
                    GitHub
                  </a>
                  <a href={ISSUES_URL} target="_blank" rel="noopener noreferrer" className="text-primary-600 hover:underline">
                    Bugs & suggestions
                  </a>
                </div>
                <p className="mt-2">© 2021-{new Date().getFullYear()}</p>
                <p>Designed by A. Popkov</p>
                <p>Text V. Neimorovets</p>
              </div>
            </div>
          </div>
        </aside>

        {/* Main content: top padding so content is not under the fixed top bar (mobile and desktop) */}
        <main className="flex-1 lg:ml-0 pt-24">
          <div className="max-w-6xl mx-auto p-6">
            {children}
          </div>
        </main>
      </div>

      {/* Overlay for mobile */}
      {sidebarOpen && (
        <div
          className="lg:hidden fixed inset-0 bg-black bg-opacity-50 z-30"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Cite modal */}
      {citeModalOpen && (
        <>
          <div
            className="fixed inset-0 bg-black/50 z-50"
            onClick={() => setCiteModalOpen(false)}
            aria-hidden="true"
          />
          <div
            className="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-50 w-full max-w-lg max-h-[85vh] mx-4 bg-white rounded-lg shadow-xl flex flex-col"
            role="dialog"
            aria-modal="true"
            aria-labelledby="cite-modal-title"
          >
            <div className="flex items-center justify-between p-4 border-b">
              <h2 id="cite-modal-title" className="text-lg font-semibold text-gray-800">
                {t.nav.CITE}
              </h2>
              <button
                type="button"
                onClick={() => setCiteModalOpen(false)}
                className="p-2 rounded-md text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500"
                aria-label={t.nav.CLOSE}
              >
                <X size={20} />
              </button>
            </div>
            <div className="p-4 overflow-auto min-h-0">
              <pre className="p-4 bg-gray-50 rounded-lg text-sm font-mono text-gray-800 whitespace-pre-wrap break-words">
                {BIBTEX}
              </pre>
            </div>
            <div className="p-4 border-t flex justify-end">
              <button
                type="button"
                onClick={() => setCiteModalOpen(false)}
                className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
              >
                {t.nav.CLOSE}
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

